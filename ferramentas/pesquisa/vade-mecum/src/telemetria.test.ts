import { expect, test } from "bun:test";

import { ContadorDiario, origemIncompleta } from "./telemetria.js";

const medida = { tool: "buscar_sumula", ms: 10, bytes: 100, achou: true, falhou: false };

test("o IP fica só com a faixa e o identificador da OpenAI vira resumo", () => {
  expect(origemIncompleta("ip:189.4.12.77")).toBe("ip:189.4.12.0/24");
  expect(origemIncompleta("ip:2804:14c:5b81:8f00::1")).toBe("ip:2804:14c::/32");
  const resumo = origemIncompleta("openai:v1/ABCDEF");
  expect(resumo).toMatch(/^openai:[0-9a-f]{16}$/);
  expect(resumo).not.toContain("ABCDEF");
  expect(origemIncompleta(undefined)).toBeUndefined();
});

test("as chamadas do dia viram uma linha só, sem hora nem IP completo", () => {
  const linhas: string[] = [];
  const contador = new ContadorDiario((l) => linhas.push(l), () => new Date("2026-10-28T15:00:00Z"));
  const ctx = { ator: "ip:189.4.12.77", cliente: "Claude Code", identificaPessoa: true };
  contador.registrar(medida, ctx);
  contador.registrar({ ...medida, achou: false }, ctx);
  contador.registrar({ ...medida, falhou: true }, ctx);
  expect(linhas).toEqual([]);

  contador.descarregar();
  expect(linhas).toHaveLength(1);
  const soma = JSON.parse(linhas[0]);
  expect(soma).toMatchObject({
    evento: "uso_diario", dia: "2026-10-28", tool: "buscar_sumula", ator: "ip:189.4.12.0/24",
    chamadas: 3, com_resultado: 1, sem_resultado: 1, falhas: 1,
  });
  expect(linhas[0]).not.toContain("189.4.12.77");
  expect("ts" in soma).toBe(false);
});

test("a virada do dia grava a soma do dia anterior, no fuso de Brasília", () => {
  const linhas: string[] = [];
  let agora = new Date("2026-10-29T02:30:00Z"); // 23h30 de 28/10 em Brasília
  const contador = new ContadorDiario((l) => linhas.push(l), () => agora);
  contador.registrar(medida);
  agora = new Date("2026-10-29T03:30:00Z"); // 0h30 de 29/10
  contador.conferirVirada();
  expect(linhas.map((l) => JSON.parse(l).dia)).toEqual(["2026-10-28"]);
});
