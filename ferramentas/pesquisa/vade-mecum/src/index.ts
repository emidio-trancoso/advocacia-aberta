import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";

import {
  buscarSumulas,
  formatSumula,
  TOTAIS_SUMULAS,
  type Tribunal,
} from "./search/sumulas.js";
import {
  buscarTeses,
  formatTese,
  TOTAL_EDICOES_JT,
  TOTAL_TESES_STJ,
} from "./search/jt.js";
import {
  buscarTemas,
  formatTema,
  TOTAL_TEMAS_STJ,
} from "./search/temas.js";
import {
  buscarTemasRG,
  formatTemaRG,
  TOTAL_TEMAS_RG_STF,
} from "./search/temas_rg_stf.js";
import {
  buscarInformativos,
  formatInformativo,
  TOTAL_EDICOES_INFORMATIVO,
  TOTAL_INFORMATIVOS_STF,
} from "./search/informativo_stf.js";
import {
  buscarEspelhos,
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

// ── Server ─────────────────────────────────────────────────────────────────

const server = new Server(
  { name: "vade-mecum", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

// ── Tool definitions ───────────────────────────────────────────────────────

const formatarNumero = new Intl.NumberFormat("pt-BR").format;

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

Use quando o usuário mencionar número de súmula, ou quando a questão jurídica puder ter orientação sumulada.`,
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

Aceita busca por número ("tema 1377", "tema repetitivo 1302") ou palavras-chave.

Use quando a questão puder ser objeto de recurso repetitivo, para verificar se já há tese firmada.`,
      inputSchema: {
        type: "object",
        properties: {
          query: {
            type: "string",
            description: "Número do tema (ex: 'tema 1377') ou palavras-chave (ex: 'honorários sucumbenciais fazenda pública').",
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
    ],
  };
});

// ── Tool handlers ──────────────────────────────────────────────────────────

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "buscar_sumula") {
    const query = String(args?.query ?? "");
    const tribunal = (args?.tribunal ?? "todos") as Tribunal | "todos";
    const limit = Number(args?.limit ?? 5);

    const results = buscarSumulas(query, tribunal, limit);
    if (results.length === 0) {
      return { content: [{ type: "text", text: `Nenhuma súmula encontrada para: "${query}"` }] };
    }
    const text = results.map(formatSumula).join("\n---\n\n");
    return { content: [{ type: "text", text }] };
  }

  if (name === "buscar_tese") {
    const query = String(args?.query ?? "");
    const limit = Number(args?.limit ?? 5);

    const results = buscarTeses(query, limit);
    if (results.length === 0) {
      return { content: [{ type: "text", text: `Nenhuma tese encontrada para: "${query}"` }] };
    }
    const text = results.map(formatTese).join("\n---\n\n");
    return { content: [{ type: "text", text }] };
  }

  if (name === "buscar_tema") {
    const query = String(args?.query ?? "");
    const limit = Number(args?.limit ?? 5);

    const results = buscarTemas(query, limit);
    if (results.length === 0) {
      return { content: [{ type: "text", text: `Nenhum tema encontrado para: "${query}"` }] };
    }
    const text = results.map(formatTema).join("\n---\n\n");
    return { content: [{ type: "text", text }] };
  }

  if (name === "buscar_tema_rg") {
    const query = String(args?.query ?? "");
    const limit = Number(args?.limit ?? 5);

    const results = buscarTemasRG(query, limit);
    if (results.length === 0) {
      return { content: [{ type: "text", text: `Nenhum tema de repercussão geral encontrado para: "${query}"` }] };
    }
    const text = results.map(formatTemaRG).join("\n---\n\n");
    return { content: [{ type: "text", text }] };
  }

  if (name === "buscar_informativo") {
    const query = String(args?.query ?? "");
    const limit = Number(args?.limit ?? 5);

    const results = buscarInformativos(query, limit);
    if (results.length === 0) {
      return { content: [{ type: "text", text: `Nenhum julgado do Informativo encontrado para: "${query}"` }] };
    }
    const text = results.map(formatInformativo).join("\n---\n\n");
    return { content: [{ type: "text", text }] };
  }

  if (name === "buscar_espelho") {
    const query = String(args?.query ?? "");
    const limit = Number(args?.limit ?? 5);

    const results = buscarEspelhos(query, limit);
    if (results.length === 0) {
      return { content: [{ type: "text", text: `Nenhum espelho de acórdão encontrado para: "${query}"` }] };
    }
    const text = results.map(formatEspelho).join("\n---\n\n");
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
      return { content: [{ type: "text", text: `Nenhum artigo encontrado para: "${query}"` }] };
    }
    const text = results.map(({ codigo: cod, artigo }) => formatArtigo(cod, artigo)).join("\n---\n\n");
    return { content: [{ type: "text", text }] };
  }

  return { content: [{ type: "text", text: `Tool desconhecida: ${name}` }] };
});

// ── Start ──────────────────────────────────────────────────────────────────

const transport = new StdioServerTransport();
await server.connect(transport);
