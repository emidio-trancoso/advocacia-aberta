import { describe, expect, test } from "bun:test";
import { createRequire } from "module";

import {
  CODIGOS_DISPONIVEIS,
  buscarLegislacao,
  carregarIndiceGerado,
} from "./legislacao.js";

const require = createRequire(import.meta.url);

describe("índice derivado da legislação (BASE-019)", () => {
  test("com o índice curado, cobre todos os dispositivos em relação 1:1", () => {
    const problemas: string[] = [];
    for (const codigo of CODIGOS_DISPONIVEIS) {
      const dados = require(`../../data/lei_${codigo.toLowerCase()}.json`) as {
        artigos: Record<string, unknown>;
        indexes?: { keywords?: Record<string, Array<number | string>> };
      };
      const indice = carregarIndiceGerado(codigo);
      if (!indice) {
        problemas.push(`${codigo}: índice derivado ausente`);
        continue;
      }
      const curados = new Set<string>();
      for (const numeros of Object.values(dados.indexes?.keywords ?? {})) {
        numeros.forEach((numero) => curados.add(String(numero)));
      }
      const artigos = new Set(Object.keys(dados.artigos));
      const uniao = new Set(curados);
      for (const [numero, tokens] of Object.entries(indice.tokens)) {
        if (curados.has(numero)) {
          problemas.push(`${codigo}: ${numero} duplicado no curado e no derivado`);
        }
        if (!artigos.has(numero)) {
          problemas.push(`${codigo}: ${numero} indexado sem dispositivo`);
        }
        if (!tokens) problemas.push(`${codigo}: ${numero} sem token`);
        uniao.add(numero);
      }
      for (const numero of artigos) {
        if (!uniao.has(numero)) {
          problemas.push(`${codigo}: ${numero} invisível à busca textual`);
        }
      }
    }
    expect(problemas).toEqual([]);
  });

  test("dispositivos fora do índice curado do núcleo voltam a ser recuperáveis", () => {
    // Antes do BASE-019, 314 dispositivos dos diplomas com índice curado
    // (ex.: CP 121-B, CPP 3-B a 3-F, CLT 7) eram invisíveis à busca textual.
    const casos = [
      {
        consulta: "juiz das garantias controle da legalidade da investigacao",
        codigo: "CPP",
        alvo: "3-B",
      },
      {
        consulta:
          "matar descendente enteado pessoa sob guarda da mulher razoes condicao sexo feminino",
        codigo: "CP",
        alvo: "121-B",
      },
      {
        consulta: "preceitos da consolidacao nao se aplicam aos empregados domesticos",
        codigo: "CLT",
        alvo: "7",
      },
    ] as const;
    for (const { consulta, codigo, alvo } of casos) {
      const numeros = buscarLegislacao(consulta, codigo).map(
        (resultado) => resultado.artigo.numero,
      );
      expect(numeros).toContain(alvo);
    }
  });
});
