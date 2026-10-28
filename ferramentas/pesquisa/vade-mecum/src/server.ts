/**
 * Fábrica do servidor MCP do Vade Mecum.
 *
 * `buildServer()` monta um servidor com as 7 ferramentas de busca, a ferramenta de
 * cobertura declarada e seus handlers,
 * SEM conectar transporte. Os entrypoints escolhem o transporte:
 *   - index.ts  → stdio  (uso local: Claude Code, Codex sobre o repo)
 *   - http.ts   → Streamable HTTP (uso hospedado: Claude connector remoto + Codex/OpenAI)
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  type CallToolRequest,
  type CallToolResult,
} from "@modelcontextprotocol/sdk/types.js";

import { ICONES_DA_MARCA } from "./marca.js";
import { contador, type ContextoDeUso } from "./telemetria.js";

import {
  buscarSumulasAmpliado,
  formatSumula,
  normalizarTribunal,
  TOTAIS_SUMULAS,
  TRIBUNAIS_DISPONIVEIS,
} from "./search/sumulas.js";
import {
  buscarTesesAmpliado,
  formatTese,
  TOTAL_EDICOES_JT,
  TOTAL_TESES_STJ,
} from "./search/jt.js";
import {
  buscarTemasAmpliado,
  formatTema,
  TOTAL_TEMAS_STJ,
} from "./search/temas.js";
import {
  buscarTemasRGAmpliado,
  formatTemaRG,
  TOTAL_TEMAS_RG_STF,
} from "./search/temas_rg_stf.js";
import {
  buscarInformativosAmpliado,
  formatInformativo,
  TOTAL_EDICOES_INFORMATIVO,
  TOTAL_INFORMATIVOS_STF,
} from "./search/informativo_stf.js";
import {
  buscarEspelhosAmpliado,
  formatEspelho,
  TOTAL_ESPELHOS_STJ,
  TOTAL_ORGAOS_ESPELHOS,
} from "./search/espelhos_stj.js";
import {
  buscarLegislacao,
  CODIGOS_DISPONIVEIS,
  formatArtigo,
  listarLegislacaoDisponivel,
  normalizarCodigo,
} from "./search/legislacao.js";
import {
  formatCobertura,
  rodapeSnapshot,
  rodapeSnapshotLegislacao,
} from "./search/cobertura.js";
import { montarResposta, totalExibido } from "./search/lexico.js";

const formatarNumero = new Intl.NumberFormat("pt-BR").format;

// Todas as ferramentas são de leitura sobre um snapshot curado local: não alteram estado,
// são idempotentes e não consultam a web aberta.
const ANOTACOES_LEITURA = {
  readOnlyHint: true,
  destructiveHint: false,
  idempotentHint: true,
  openWorldHint: false,
} as const;

// ── Telemetria de uso ────────────────────────────────────────────────────────
//
// Conta QUAL ferramenta foi chamada, se houve resultado e quanto demorou. Serve
// para saber que partes do acervo são realmente usadas e onde a busca falha.
//
// O termo pesquisado NUNCA é registrado: a consulta de um advogado revela a matéria
// e, muitas vezes, o caso — isso é sigilo (ver SIGILO-E-DADOS.md). Só saem daqui
// categorias fixas do próprio catálogo (tribunal, código) e medidas, somadas por dia
// (ver telemetria.ts).
const SEM_RESULTADO = /^Nenhum[ao]?\s/;

export type { ContextoDeUso };

function registrarUso(
  request: CallToolRequest,
  medida: { ms: number; bytes: number; achou?: boolean; falhou: boolean },
  contexto?: ContextoDeUso,
): void {
  const args = request.params.arguments ?? {};
  const facetaTexto = (valor: unknown): string | undefined =>
    typeof valor === "string" && valor.length > 0 ? valor : undefined;

  contador.registrar(
    {
      tool: request.params.name,
      tribunal: facetaTexto(args.tribunal),
      codigo: facetaTexto(args.codigo),
      ...medida,
    },
    contexto,
  );
}

export function buildServer(contexto?: ContextoDeUso): Server {
  const server = new Server(
    {
      // `name` é o identificador programático e não muda: clientes já conectados
      // guardam o servidor por ele. O nome de exibição vai em `title`.
      name: "vade-mecum",
      title: "Advocacia Aberta",
      version: "1.0.0",
      description:
        "Consulta ao acervo jurídico brasileiro — súmulas, teses, temas repetitivos e de repercussão geral, informativos e legislação — sempre com a fonte oficial.",
      websiteUrl: "https://advocaciaaberta.org",
      icons: ICONES_DA_MARCA,
    },
    { capabilities: { tools: {} } }
  );

  server.setRequestHandler(ListToolsRequestSchema, async () => {
    const legislacoes = listarLegislacaoDisponivel();
    const descricaoLegislacao = legislacoes
      .map(
        ({ codigo, rotulo, registros }) =>
          `- ${codigo}: ${rotulo} — ${formatarNumero(registros)} registros`,
      )
      .join("\n");

    return {
      tools: [
        {
          name: "buscar_sumula",
          description: `Busca enunciados sumulares do STJ, STF e Súmulas Vinculantes STF em publicações oficiais curadas (${formatarNumero(TOTAIS_SUMULAS.STJ)} STJ + ${formatarNumero(TOTAIS_SUMULAS.STF)} STF + ${formatarNumero(TOTAIS_SUMULAS.vinculantes)} vinculantes).

Aceita busca por número ("365") ou por palavras-chave ("dano moral cadastro crédito").

Súmulas Vinculantes aprovadas e vigentes têm efeito vinculante nos termos do art. 103-A da CF; estados não ativos são sinalizados separadamente.
Súmulas comuns do STJ e STF não são vinculantes por si sós; confira vigência e aplicabilidade.

As súmulas vinculantes trazem os precedentes representativos declarados pelo STF na página do enunciado, com link do inteiro teor e, quando a citação oficial os menciona, o tema de repercussão geral correspondente.

Use quando o usuário mencionar número de súmula, ou quando a questão jurídica puder ter orientação sumulada.`,
          annotations: ANOTACOES_LEITURA,
          inputSchema: {
            type: "object",
            properties: {
              query: {
                type: "string",
                description: "Número da súmula (ex: '365') ou palavras-chave (ex: 'dano moral cadastro negativação').",
              },
              tribunal: {
                type: "string",
                enum: ["STJ", "STF", "vinculante", "todos"],
                description: "Tribunal a buscar. Use 'todos' para buscar em todos. Default: 'todos'.",
                default: "todos",
              },
              limit: {
                type: "number",
                description: "Máximo de resultados por tribunal. Default: 5.",
                default: 5,
              },
            },
            required: ["query"],
          },
        },
        {
          name: "buscar_tese",
          description: `Busca jurisprudência em teses do STJ (${formatarNumero(TOTAL_TESES_STJ)} teses de ${formatarNumero(TOTAL_EDICOES_JT)} edições).

Jurisprudência em Teses é uma compilação institucional do STJ que reúne teses e os julgados que as sustentam.
O produto não é vinculante por si só; examine os julgados indicados antes de aplicar o entendimento.

Aceita busca por palavras-chave ou por número de edição ("edição 142", "JT 142").

Use para localizar uma síntese institucional e partir dela para os julgados correspondentes.`,
          annotations: ANOTACOES_LEITURA,
          inputSchema: {
            type: "object",
            properties: {
              query: {
                type: "string",
                description: "Palavras-chave (ex: 'plano de saúde cobertura') ou número de edição (ex: 'edição 142').",
              },
              limit: {
                type: "number",
                description: "Máximo de resultados. Default: 5.",
                default: 5,
              },
            },
            required: ["query"],
          },
        },
        {
          name: "buscar_tema",
          description: `Busca temas repetitivos do STJ (${formatarNumero(TOTAL_TEMAS_STJ)} temas).

O registro informa a situação de temas submetidos ao rito dos recursos repetitivos.
Quando houver tese firmada vigente e aplicável, sua observância é obrigatória nos termos do art. 927, III, do CPC; temas afetados, cancelados ou em revisão exigem tratamento distinto.

Aceita busca por número ("1377", "tema 1377", "tema repetitivo 1302") ou palavras-chave.
A busca por número devolve o tema pedido ou nada — nunca outro tema.

Use quando a questão puder ser objeto de recurso repetitivo, para verificar se já há tese firmada.`,
          annotations: ANOTACOES_LEITURA,
          inputSchema: {
            type: "object",
            properties: {
              query: {
                type: "string",
                description: "Número do tema (ex: '1377', 'tema 1377') ou palavras-chave (ex: 'honorários sucumbenciais fazenda pública').",
              },
              limit: {
                type: "number",
                description: "Máximo de resultados. Default: 5.",
                default: 5,
              },
            },
            required: ["query"],
          },
        },
        {
          name: "buscar_tema_rg",
          description: `Busca temas de repercussão geral do STF (${formatarNumero(TOTAL_TEMAS_RG_STF)} temas).

O registro informa a situação de temas submetidos ao regime da repercussão geral do STF (o par vinculante dos temas repetitivos do STJ).
Quando o mérito foi julgado e há tese firmada vigente e aplicável, sua observância é obrigatória nos termos do art. 927, III, do CPC; temas apenas com repercussão geral reconhecida, cancelados ou em julgamento exigem tratamento distinto.

Aceita busca por número ("tema 69", "RG 69", "repercussão geral 660") ou palavras-chave.

Use quando a questão constitucional puder ser objeto de repercussão geral, para verificar se o STF já firmou tese.`,
          annotations: ANOTACOES_LEITURA,
          inputSchema: {
            type: "object",
            properties: {
              query: {
                type: "string",
                description: "Número do tema (ex: 'tema 69') ou palavras-chave (ex: 'ICMS base de cálculo PIS COFINS').",
              },
              limit: {
                type: "number",
                description: "Máximo de resultados. Default: 5.",
                default: 5,
              },
            },
            required: ["query"],
          },
        },
        {
          name: "buscar_informativo",
          description: `Busca julgados resumidos no Informativo STF (${formatarNumero(TOTAL_INFORMATIVOS_STF)} julgados de ${formatarNumero(TOTAL_EDICOES_INFORMATIVO)} edições).

O Informativo STF é uma compilação institucional que resume julgados relevantes do Tribunal.
O resumo não é vinculante por si só; examine o inteiro teor e a situação atual no link oficial da edição antes de aplicar.

Aceita busca por palavras-chave ("insignificância tráfico", "ICMS energia") ou por número de edição ("informativo 1222", "inf 1000").

Use para localizar um julgado do STF por tema e chegar ao texto oficial da edição.`,
          annotations: ANOTACOES_LEITURA,
          inputSchema: {
            type: "object",
            properties: {
              query: {
                type: "string",
                description: "Palavras-chave (ex: 'princípio da insignificância') ou número de edição (ex: 'informativo 1222').",
              },
              limit: {
                type: "number",
                description: "Máximo de resultados. Default: 5.",
                default: 5,
              },
            },
            required: ["query"],
          },
        },
        {
          name: "buscar_espelho",
          description: `Busca espelhos de acórdãos do STJ (${formatarNumero(TOTAL_ESPELHOS_STJ)} acórdãos de ${formatarNumero(TOTAL_ORGAOS_ESPELHOS)} órgãos, desde 2022).

Espelhos são fichas de acórdãos selecionados pela Secretaria de Jurisprudência do STJ por trazerem novidades quanto a teses jurídicas.
Um acórdão isolado não é vinculante por si só; confira o inteiro teor no link oficial e verifique se há tese qualificada (tema repetitivo). A ementa completa fica no link.

Aceita busca por palavras-chave (tese, ramo, classe) ou por número de registro.

Use para localizar precedentes recentes do STJ por tema e chegar ao acórdão oficial.`,
          annotations: ANOTACOES_LEITURA,
          inputSchema: {
            type: "object",
            properties: {
              query: {
                type: "string",
                description: "Palavras-chave (ex: 'honorários apreciação equitativa') ou número de registro do processo.",
              },
              limit: {
                type: "number",
                description: "Máximo de resultados. Default: 5.",
                default: 5,
              },
            },
            required: ["query"],
          },
        },
        {
          name: "buscar_legislacao",
          description: `Busca artigos em ${legislacoes.length} diplomas da legislação brasileira.

Aceita busca por número de artigo ("art. 702", "artigo 186") ou por palavras-chave.
Retorna texto normativo extraído da compilação oficial do Planalto. Confirme vigência, redação e aplicabilidade no link apresentado.

Códigos disponíveis:
${descricaoLegislacao}

Use para verificar o texto exato de um dispositivo legal antes de citar.`,
          annotations: ANOTACOES_LEITURA,
          inputSchema: {
            type: "object",
            properties: {
              query: {
                type: "string",
                description: "Número do artigo (ex: '186', 'art. 702') ou palavras-chave (ex: 'responsabilidade civil dano').",
              },
              codigo: {
                type: "string",
                enum: [...CODIGOS_DISPONIVEIS, "todos"],
                description: "Código a buscar. Se informar número de artigo, especifique o código. Default: 'todos'.",
                default: "todos",
              },
              limit: {
                type: "number",
                description: "Máximo de resultados. Default: 5.",
                default: 5,
              },
            },
            required: ["query"],
          },
        },
        {
          name: "cobertura_da_base",
          description: `Declara o que este acervo cobre e o que não cobre: famílias disponíveis, quantos registros, a data em que cada snapshot foi capturado e as limitações conhecidas.

Use antes de concluir que algo "não existe": resultado vazio pode ser lacuna de cobertura, não ausência de norma ou de precedente. Use também quando precisar dizer ao usuário de quando é o dado que sustenta a resposta.`,
          annotations: ANOTACOES_LEITURA,
          inputSchema: { type: "object", properties: {} },
        },
      ],
    };
  });

  const despacharTool = async (request: CallToolRequest): Promise<CallToolResult> => {
    const { name, arguments: args } = request.params;

    if (name === "buscar_sumula") {
      const query = String(args?.query ?? "");
      const tribunalInformado = String(args?.tribunal ?? "todos");
      const tribunal = normalizarTribunal(tribunalInformado);
      const limit = Number(args?.limit ?? 5);

      if (!tribunal) {
        const disponiveis = [...TRIBUNAIS_DISPONIVEIS, "todos"].join(", ");
        return {
          content: [
            {
              type: "text",
              text: `Tribunal indisponível: "${tribunalInformado}". Use: ${disponiveis}.`,
            },
          ],
          isError: true,
        };
      }

      const chavesSumulas: Record<string, string> = {
        STJ: "sumulas_stj",
        STF: "sumulas_stf",
        vinculante: "sumulas_vinculantes",
      };

      const busca = buscarSumulasAmpliado(query, tribunal, limit);
      const results = [...busca.diretos, ...busca.porEquivalencia];
      if (totalExibido(busca) === 0) {
        const alcance =
          tribunal === "todos"
            ? Object.values(chavesSumulas)
            : [chavesSumulas[tribunal]!];
        return {
          content: [
            {
              type: "text",
              text: `Nenhuma súmula encontrada para: "${query}"\n\n${rodapeSnapshot(alcance)}`,
            },
          ],
        };
      }
      const consultadas = [
        ...new Set(results.map(({ tribunal: t }) => chavesSumulas[t]!)),
      ];
      const text = `${montarResposta(busca, formatSumula)}\n${rodapeSnapshot(consultadas)}`;
      return { content: [{ type: "text", text }] };
    }

    if (name === "buscar_tese") {
      const query = String(args?.query ?? "");
      const limit = Number(args?.limit ?? 5);

      const rodape = rodapeSnapshot("jurisprudencia_teses_stj");
      const busca = buscarTesesAmpliado(query, limit);
      if (totalExibido(busca) === 0) {
        return {
          content: [
            { type: "text", text: `Nenhuma tese encontrada para: "${query}"\n\n${rodape}` },
          ],
        };
      }
      const text = `${montarResposta(busca, formatTese)}\n${rodape}`;
      return { content: [{ type: "text", text }] };
    }

    if (name === "buscar_tema") {
      const query = String(args?.query ?? "");
      const limit = Number(args?.limit ?? 5);

      const rodape = rodapeSnapshot("temas_repetitivos_stj");
      const busca = buscarTemasAmpliado(query, limit);
      if (totalExibido(busca) === 0) {
        return {
          content: [
            { type: "text", text: `Nenhum tema encontrado para: "${query}"\n\n${rodape}` },
          ],
        };
      }
      const text = `${montarResposta(busca, formatTema)}\n${rodape}`;
      return { content: [{ type: "text", text }] };
    }

    if (name === "buscar_tema_rg") {
      const query = String(args?.query ?? "");
      const limit = Number(args?.limit ?? 5);

      const rodape = rodapeSnapshot("temas_rg_stf");
      const busca = buscarTemasRGAmpliado(query, limit);
      if (totalExibido(busca) === 0) {
        return {
          content: [
            {
              type: "text",
              text: `Nenhum tema de repercussão geral encontrado para: "${query}"\n\n${rodape}`,
            },
          ],
        };
      }
      const text = `${montarResposta(busca, formatTemaRG)}\n${rodape}`;
      return { content: [{ type: "text", text }] };
    }

    if (name === "buscar_informativo") {
      const query = String(args?.query ?? "");
      const limit = Number(args?.limit ?? 5);

      const rodape = rodapeSnapshot("informativo_stf");
      const busca = buscarInformativosAmpliado(query, limit);
      if (totalExibido(busca) === 0) {
        return {
          content: [
            {
              type: "text",
              text: `Nenhum julgado do Informativo encontrado para: "${query}"\n\n${rodape}`,
            },
          ],
        };
      }
      const text = `${montarResposta(busca, formatInformativo)}\n${rodape}`;
      return { content: [{ type: "text", text }] };
    }

    if (name === "buscar_espelho") {
      const query = String(args?.query ?? "");
      const limit = Number(args?.limit ?? 5);

      const rodape = rodapeSnapshot("espelhos_stj");
      const busca = buscarEspelhosAmpliado(query, limit);
      if (totalExibido(busca) === 0) {
        return {
          content: [
            {
              type: "text",
              text: `Nenhum espelho de acórdão encontrado para: "${query}"\n\n${rodape}`,
            },
          ],
        };
      }
      const text = `${montarResposta(busca, formatEspelho)}\n${rodape}`;
      return { content: [{ type: "text", text }] };
    }

    if (name === "buscar_legislacao") {
      const query = String(args?.query ?? "");
      const codigoInformado = String(args?.codigo ?? "todos");
      const codigo = normalizarCodigo(codigoInformado);
      const limit = Number(args?.limit ?? 5);

      if (!codigo) {
        const disponiveis = [...CODIGOS_DISPONIVEIS, "todos"].join(", ");
        return {
          content: [
            {
              type: "text",
              text: `Código de legislação indisponível: "${codigoInformado}". Use: ${disponiveis}.`,
            },
          ],
          isError: true,
        };
      }

      const results = buscarLegislacao(query, codigo, limit);
      if (results.length === 0) {
        const alcance = codigo === "todos" ? [] : [codigo];
        return {
          content: [
            {
              type: "text",
              text: `Nenhum artigo encontrado para: "${query}"\n\n${rodapeSnapshotLegislacao(alcance)}`,
            },
          ],
        };
      }
      const rodape = rodapeSnapshotLegislacao(results.map(({ codigo: cod }) => cod));
      const text = `${results
        .map(({ codigo: cod, artigo }) => formatArtigo(cod, artigo))
        .join("\n---\n\n")}\n${rodape}`;
      return { content: [{ type: "text", text }] };
    }

    if (name === "cobertura_da_base") {
      return { content: [{ type: "text", text: formatCobertura() }] };
    }

    return { content: [{ type: "text", text: `Tool desconhecida: ${name}` }] };
  };

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const inicio = performance.now();
    let achou: boolean | undefined;
    let falhou = false;
    let bytes = 0;
    try {
      const resposta = await despacharTool(request);
      falhou = resposta.isError === true;
      const primeiro = resposta.content?.[0];
      const texto = primeiro?.type === "text" ? primeiro.text : "";
      // Peso da resposta: é o que o consumo de banda realmente mede.
      bytes = Buffer.byteLength(texto, "utf8");
      // Busca sem acerto responde com "Nenhuma súmula encontrada…" e afins — é o
      // sinal de que a pergunta não achou nada, e é o que mais interessa medir.
      // Chamada malformada não conta como busca: não houve pesquisa para achar algo.
      if (!falhou) {
        achou = !SEM_RESULTADO.test(texto);
      }
      return resposta;
    } catch (erro) {
      falhou = true;
      throw erro;
    } finally {
      registrarUso(
        request,
        { ms: Math.round((performance.now() - inicio) * 10) / 10, bytes, achou, falhou },
        contexto,
      );
    }
  });

  return server;
}
