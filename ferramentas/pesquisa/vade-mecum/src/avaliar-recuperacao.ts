import { createRequire } from "module";

import {
  GRUPOS_AVALIACAO,
  avaliarCorpus,
  verificarLimiares,
  type CorpusAvaliacao,
  type MetricasAvaliacao,
} from "./search/avaliacao.js";

const require = createRequire(import.meta.url);
const corpus = require("../avaliacao/consultas.json") as CorpusAvaliacao;

function formatar(metricas: MetricasAvaliacao): string {
  return [
    `casos=${metricas.casos}`,
    `precisão@${corpus.top_k}=${metricas.precisaoAtK.toFixed(4)}`,
    `recall-julgado@${corpus.top_k}=${metricas.recallJulgadoAtK.toFixed(4)}`,
    `cobertura=${metricas.coberturaCasos.toFixed(4)}`,
    `obrigatórios=${metricas.coberturaObrigatorios.toFixed(4)}`,
    `MRR=${metricas.mrr.toFixed(4)}`,
  ].join(" | ");
}

const relatorio = avaliarCorpus(corpus);

console.log(`Vade Mecum — avaliação de recuperação (${corpus.avaliado_em})`);
console.log(`Global | ${formatar(relatorio.metricas)}`);
for (const grupo of GRUPOS_AVALIACAO) {
  console.log(`${grupo} | ${formatar(relatorio.porGrupo[grupo])}`);
}

const falhas = verificarLimiares(corpus, relatorio);
if (falhas.length > 0) {
  console.error("\nFalhas de qualidade:");
  falhas.forEach((falha) => console.error(`- ${falha}`));
  process.exitCode = 1;
}
