import { buscarTeses } from "./jt.js";
import {
  buscarLegislacao,
  type CodigoCodigo,
} from "./legislacao.js";
import { buscarSumulas, type Tribunal } from "./sumulas.js";
import { buscarTemas } from "./temas.js";
import { buscarTemasRG } from "./temas_rg_stf.js";
import { buscarInformativos } from "./informativo_stf.js";
import { buscarEspelhos } from "./espelhos_stj.js";

export const GRUPOS_AVALIACAO = [
  "sumulas_stj",
  "sumulas_stf",
  "sumulas_vinculantes",
  "jurisprudencia_teses",
  "temas_repetitivos",
  "temas_rg_stf",
  "informativo_stf",
  "espelhos_stj",
  "legislacao",
] as const;

export type GrupoAvaliacao = (typeof GRUPOS_AVALIACAO)[number];

export interface CasoAvaliacao {
  readonly id: string;
  readonly grupo: GrupoAvaliacao;
  readonly consulta: string;
  readonly filtro: {
    readonly tribunal?: Tribunal;
    readonly codigo?: CodigoCodigo;
  };
  readonly relevantes: readonly string[];
  readonly obrigatorios: readonly string[];
  readonly justificativa: string;
}

export interface CorpusAvaliacao {
  readonly schema_version: 1;
  readonly descricao: string;
  readonly avaliado_em: string;
  readonly top_k: number;
  readonly limiares: {
    readonly precisao_at_k: number;
    readonly recall_julgado_at_k: number;
    readonly cobertura_casos: number;
    readonly cobertura_obrigatorios: number;
    readonly mrr: number;
  };
  readonly limiares_precisao_por_grupo: Record<GrupoAvaliacao, number>;
  readonly casos: readonly CasoAvaliacao[];
}

export interface ResultadoCaso {
  readonly id: string;
  readonly grupo: GrupoAvaliacao;
  readonly retornados: readonly string[];
  readonly acertos: readonly string[];
  readonly obrigatoriosAusentes: readonly string[];
  readonly precisaoAtK: number;
  readonly recallJulgadoAtK: number;
  readonly reciprocalRank: number;
}

export interface MetricasAvaliacao {
  readonly casos: number;
  readonly retornados: number;
  readonly relevantesJulgados: number;
  readonly acertos: number;
  readonly precisaoAtK: number;
  readonly recallJulgadoAtK: number;
  readonly coberturaCasos: number;
  readonly coberturaObrigatorios: number;
  readonly mrr: number;
}

export interface RelatorioAvaliacao {
  readonly metricas: MetricasAvaliacao;
  readonly porGrupo: Readonly<Record<GrupoAvaliacao, MetricasAvaliacao>>;
  readonly resultados: readonly ResultadoCaso[];
}

function validarProporcao(valor: number, caminho: string): void {
  if (!Number.isFinite(valor) || valor < 0 || valor > 1) {
    throw new Error(`${caminho} deve estar entre 0 e 1`);
  }
}

function duplicados(valores: readonly string[]): string[] {
  return valores.filter((valor, indice) => valores.indexOf(valor) !== indice);
}

export function validarCorpus(corpus: CorpusAvaliacao): void {
  if (corpus.schema_version !== 1) {
    throw new Error("schema_version de avaliação não suportada");
  }
  if (!Number.isInteger(corpus.top_k) || corpus.top_k < 1) {
    throw new Error("top_k deve ser um inteiro positivo");
  }
  if (corpus.casos.length === 0) {
    throw new Error("o corpus de avaliação não pode estar vazio");
  }

  for (const [nome, valor] of Object.entries(corpus.limiares)) {
    validarProporcao(valor, `limiares.${nome}`);
  }
  for (const grupo of GRUPOS_AVALIACAO) {
    validarProporcao(
      corpus.limiares_precisao_por_grupo[grupo],
      `limiares_precisao_por_grupo.${grupo}`,
    );
  }

  const ids = corpus.casos.map((caso) => caso.id);
  if (duplicados(ids).length > 0) {
    throw new Error(`IDs de caso duplicados: ${duplicados(ids).join(", ")}`);
  }

  for (const caso of corpus.casos) {
    if (!GRUPOS_AVALIACAO.includes(caso.grupo)) {
      throw new Error(`${caso.id}: grupo desconhecido`);
    }
    if (caso.consulta.trim().length < 3 || caso.justificativa.trim().length < 10) {
      throw new Error(`${caso.id}: consulta ou justificativa insuficiente`);
    }
    if (caso.relevantes.length === 0 || caso.obrigatorios.length === 0) {
      throw new Error(`${caso.id}: informe relevantes e obrigatórios`);
    }
    if (duplicados(caso.relevantes).length > 0) {
      throw new Error(`${caso.id}: há IDs relevantes duplicados`);
    }
    if (duplicados(caso.obrigatorios).length > 0) {
      throw new Error(`${caso.id}: há IDs obrigatórios duplicados`);
    }
    const relevantes = new Set(caso.relevantes);
    const obrigatorioInvalido = caso.obrigatorios.find((id) => !relevantes.has(id));
    if (obrigatorioInvalido) {
      throw new Error(`${caso.id}: obrigatório ${obrigatorioInvalido} não é relevante`);
    }

    const tribunalEsperado: Partial<Record<GrupoAvaliacao, Tribunal>> = {
      sumulas_stj: "STJ",
      sumulas_stf: "STF",
      sumulas_vinculantes: "vinculante",
    };
    if (tribunalEsperado[caso.grupo] !== undefined &&
        caso.filtro.tribunal !== tribunalEsperado[caso.grupo]) {
      throw new Error(`${caso.id}: filtro de tribunal incompatível com o grupo`);
    }
    if (caso.grupo === "legislacao" && !caso.filtro.codigo) {
      throw new Error(`${caso.id}: filtro de código é obrigatório para legislação`);
    }
  }
}

export function executarConsulta(caso: CasoAvaliacao, limite: number): string[] {
  switch (caso.grupo) {
    case "sumulas_stj":
    case "sumulas_stf":
    case "sumulas_vinculantes":
      return buscarSumulas(caso.consulta, caso.filtro.tribunal!, limite).map(
        ({ tribunal, sumula }) =>
          `${tribunal === "vinculante" ? "SV" : tribunal}:${sumula.numero}`,
      );
    case "jurisprudencia_teses":
      return buscarTeses(caso.consulta, limite).map((tese) => tese.id);
    case "temas_repetitivos":
      return buscarTemas(caso.consulta, limite).map(
        (tema) => `TEMA:${tema.numero}`,
      );
    case "temas_rg_stf":
      return buscarTemasRG(caso.consulta, limite).map(
        (tema) => `RG:${tema.numero}`,
      );
    case "informativo_stf":
      return buscarInformativos(caso.consulta, limite).map((item) => item.id);
    case "espelhos_stj":
      return buscarEspelhos(caso.consulta, limite).map((item) => `ESP:${item.id}`);
    case "legislacao":
      return buscarLegislacao(
        caso.consulta,
        caso.filtro.codigo!,
        limite,
      ).map(({ codigo, artigo }) => `${codigo}:${artigo.numero}`);
  }
}

export function avaliarCaso(caso: CasoAvaliacao, topK: number): ResultadoCaso {
  const retornados = executarConsulta(caso, topK);
  const relevantes = new Set(caso.relevantes);
  const acertos = retornados.filter((id) => relevantes.has(id));
  const primeiraPosicao = retornados.findIndex((id) => relevantes.has(id));

  return {
    id: caso.id,
    grupo: caso.grupo,
    retornados,
    acertos,
    obrigatoriosAusentes: caso.obrigatorios.filter((id) => !retornados.includes(id)),
    precisaoAtK: retornados.length === 0 ? 0 : acertos.length / retornados.length,
    recallJulgadoAtK: acertos.length / caso.relevantes.length,
    reciprocalRank: primeiraPosicao < 0 ? 0 : 1 / (primeiraPosicao + 1),
  };
}

function agregarMetricas(
  casos: readonly CasoAvaliacao[],
  resultados: readonly ResultadoCaso[],
): MetricasAvaliacao {
  const retornados = resultados.reduce(
    (total, resultado) => total + resultado.retornados.length,
    0,
  );
  const acertos = resultados.reduce(
    (total, resultado) => total + resultado.acertos.length,
    0,
  );
  const relevantesJulgados = casos.reduce(
    (total, caso) => total + caso.relevantes.length,
    0,
  );
  const coberturaCasos = resultados.filter(
    (resultado) => resultado.acertos.length > 0,
  ).length;
  const coberturaObrigatorios = resultados.filter(
    (resultado) => resultado.obrigatoriosAusentes.length === 0,
  ).length;

  return {
    casos: casos.length,
    retornados,
    relevantesJulgados,
    acertos,
    precisaoAtK: retornados === 0 ? 0 : acertos / retornados,
    recallJulgadoAtK:
      relevantesJulgados === 0 ? 0 : acertos / relevantesJulgados,
    coberturaCasos: coberturaCasos / casos.length,
    coberturaObrigatorios: coberturaObrigatorios / casos.length,
    mrr:
      resultados.reduce(
        (total, resultado) => total + resultado.reciprocalRank,
        0,
      ) / casos.length,
  };
}

export function avaliarCorpus(corpus: CorpusAvaliacao): RelatorioAvaliacao {
  validarCorpus(corpus);
  const resultados = corpus.casos.map((caso) =>
    avaliarCaso(caso, corpus.top_k),
  );

  const porGrupo = Object.fromEntries(
    GRUPOS_AVALIACAO.map((grupo) => {
      const casos = corpus.casos.filter((caso) => caso.grupo === grupo);
      if (casos.length === 0) {
        throw new Error(`o corpus não possui casos para ${grupo}`);
      }
      const ids = new Set(casos.map((caso) => caso.id));
      const resultadosGrupo = resultados.filter((resultado) => ids.has(resultado.id));
      return [grupo, agregarMetricas(casos, resultadosGrupo)];
    }),
  ) as Record<GrupoAvaliacao, MetricasAvaliacao>;

  return {
    metricas: agregarMetricas(corpus.casos, resultados),
    porGrupo,
    resultados,
  };
}

export function verificarLimiares(
  corpus: CorpusAvaliacao,
  relatorio: RelatorioAvaliacao,
): string[] {
  const falhas: string[] = [];
  const comparar = (nome: string, atual: number, minimo: number): void => {
    if (atual + Number.EPSILON < minimo) {
      falhas.push(`${nome}: ${atual.toFixed(4)} < ${minimo.toFixed(4)}`);
    }
  };

  comparar("precisão@k", relatorio.metricas.precisaoAtK, corpus.limiares.precisao_at_k);
  comparar(
    "recall julgado@k",
    relatorio.metricas.recallJulgadoAtK,
    corpus.limiares.recall_julgado_at_k,
  );
  comparar(
    "cobertura de casos",
    relatorio.metricas.coberturaCasos,
    corpus.limiares.cobertura_casos,
  );
  comparar(
    "cobertura de obrigatórios",
    relatorio.metricas.coberturaObrigatorios,
    corpus.limiares.cobertura_obrigatorios,
  );
  comparar("MRR", relatorio.metricas.mrr, corpus.limiares.mrr);

  for (const grupo of GRUPOS_AVALIACAO) {
    comparar(
      `precisão@k de ${grupo}`,
      relatorio.porGrupo[grupo].precisaoAtK,
      corpus.limiares_precisao_por_grupo[grupo],
    );
  }

  for (const resultado of relatorio.resultados) {
    if (resultado.obrigatoriosAusentes.length > 0) {
      falhas.push(
        `${resultado.id}: obrigatórios ausentes ${resultado.obrigatoriosAusentes.join(", ")}`,
      );
    }
  }

  return falhas;
}
