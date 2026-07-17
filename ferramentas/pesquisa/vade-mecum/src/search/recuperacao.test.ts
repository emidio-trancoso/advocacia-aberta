import { describe, expect, test } from "bun:test";
import { createRequire } from "module";

import {
  GRUPOS_AVALIACAO,
  avaliarCorpus,
  validarCorpus,
  verificarLimiares,
  type CorpusAvaliacao,
} from "./avaliacao.js";

const require = createRequire(import.meta.url);
const corpus = require("../../avaliacao/consultas.json") as CorpusAvaliacao;

describe("qualidade da recuperação", () => {
  test("o corpus é diverso, justificado e válido", () => {
    expect(() => validarCorpus(corpus)).not.toThrow();
    expect(corpus.casos.length).toBeGreaterThanOrEqual(20);

    for (const grupo of GRUPOS_AVALIACAO) {
      expect(
        corpus.casos.filter((caso) => caso.grupo === grupo).length,
      ).toBeGreaterThanOrEqual(3);
    }
  });

  test("a busca satisfaz os limiares e preserva os resultados canônicos", () => {
    const relatorio = avaliarCorpus(corpus);
    expect(verificarLimiares(corpus, relatorio)).toEqual([]);
  });
});
