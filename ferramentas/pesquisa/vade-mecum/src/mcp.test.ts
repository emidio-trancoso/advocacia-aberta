import { expect, test } from "bun:test";

import { CODIGOS_DISPONIVEIS } from "./search/legislacao.js";
import { normalizarTribunal } from "./search/sumulas.js";

interface ToolMCP {
  name: string;
  description: string;
  inputSchema: {
    properties?: {
      codigo?: { enum?: string[] };
    };
  };
}

interface RespostaMCP {
  id?: number;
  result?: {
    tools?: ToolMCP[];
    serverInfo?: { name?: string; version?: string };
    content?: Array<{ type: string; text?: string }>;
    isError?: boolean;
  };
}

test("MCP anuncia cobertura e contagens derivadas dos dados", async () => {
  const raizMotor = new URL("..", import.meta.url).pathname;
  const processo = Bun.spawn(["bun", "run", "src/index.ts"], {
    cwd: raizMotor,
    stdin: "pipe",
    stdout: "pipe",
    stderr: "pipe",
  });

  const mensagens = [
    {
      jsonrpc: "2.0",
      id: 1,
      method: "initialize",
      params: {
        protocolVersion: "2025-06-18",
        capabilities: {},
        clientInfo: { name: "teste", version: "1.0" },
      },
    },
    { jsonrpc: "2.0", method: "notifications/initialized" },
    { jsonrpc: "2.0", id: 2, method: "tools/list", params: {} },
  ];

  processo.stdin.write(mensagens.map((item) => JSON.stringify(item)).join("\n"));
  processo.stdin.write("\n");
  processo.stdin.end();

  const [stdout, stderr, exitCode] = await Promise.all([
    new Response(processo.stdout).text(),
    new Response(processo.stderr).text(),
    processo.exited,
  ]);
  expect(exitCode, stderr).toBe(0);

  const respostas = stdout
    .trim()
    .split("\n")
    .map((linha) => JSON.parse(linha) as RespostaMCP);
  const tools = respostas.find((resposta) => resposta.id === 2)?.result?.tools;
  expect(tools).toBeDefined();

  const servidor = respostas.find((resposta) => resposta.id === 1)?.result?.serverInfo;
  expect(servidor?.name).toBe("vade-mecum");

  const legislacao = tools!.find((tool) => tool.name === "buscar_legislacao");
  expect(legislacao?.inputSchema.properties?.codigo?.enum).toEqual([
    ...CODIGOS_DISPONIVEIS,
    "todos",
  ]);
  expect(legislacao?.description).toContain("277 diplomas");

  const teses = tools!.find((tool) => tool.name === "buscar_tese");
  expect(teses?.description).toContain("3.526 teses de 284 edições");
  expect(teses?.description).toContain("compilação institucional");
  expect(teses?.description).toContain("não é vinculante por si só");

  const sumulas = tools!.find((tool) => tool.name === "buscar_sumula");
  expect(sumulas?.description).toContain("não são vinculantes por si sós");

  const temas = tools!.find((tool) => tool.name === "buscar_tema");
  expect(temas?.description).toContain("art. 927, III, do CPC");

  const temasRG = tools!.find((tool) => tool.name === "buscar_tema_rg");
  expect(temasRG?.description).toContain("repercussão geral do STF");
  expect(temasRG?.description).toContain("art. 927, III, do CPC");

  const informativo = tools!.find((tool) => tool.name === "buscar_informativo");
  expect(informativo?.description).toContain("11.593 julgados");
  expect(informativo?.description).toContain("compilação institucional");
  expect(informativo?.description).toContain("não é vinculante por si só");

  const espelho = tools!.find((tool) => tool.name === "buscar_espelho");
  expect(espelho?.description).toContain("11.486 acórdãos");
  expect(espelho?.description).toContain("Secretaria de Jurisprudência do STJ");
  expect(espelho?.description).toContain("não é vinculante por si só");

  const cobertura = tools!.find((tool) => tool.name === "cobertura_da_base");
  expect(cobertura?.description).toContain("não cobre");
  expect(cobertura?.description).toContain("limitações conhecidas");

  const descricoes = tools!.map((tool) => tool.description).join("\n");
  expect(descricoes).not.toContain("fontes primárias");
  expect(descricoes).not.toContain("Força: ORIENTATIVA");
  expect(descricoes).not.toContain("força persuasiva");
});

test("filtro de tribunal aceita qualquer caixa e recusa valor desconhecido", () => {
  expect(normalizarTribunal("stj")).toBe("STJ");
  expect(normalizarTribunal("STJ")).toBe("STJ");
  expect(normalizarTribunal(" Stj ")).toBe("STJ");
  expect(normalizarTribunal("stf")).toBe("STF");
  expect(normalizarTribunal("VINCULANTE")).toBe("vinculante");
  expect(normalizarTribunal("todos")).toBe("todos");
  expect(normalizarTribunal("")).toBe("todos");
  // Valor irreconhecível precisa virar erro explícito, não busca em tudo.
  expect(normalizarTribunal("tjpr")).toBeNull();
  expect(normalizarTribunal("supremo")).toBeNull();
});

test("buscar_sumula com tribunal em minúsculas devolve o mesmo que em maiúsculas", async () => {
  const raizMotor = new URL("..", import.meta.url).pathname;
  const processo = Bun.spawn(["bun", "run", "src/index.ts"], {
    cwd: raizMotor,
    stdin: "pipe",
    stdout: "pipe",
    stderr: "pipe",
  });

  const chamada = (id: number, tribunal: string) => ({
    jsonrpc: "2.0",
    id,
    method: "tools/call",
    params: { name: "buscar_sumula", arguments: { query: "dano moral", tribunal, limit: 1 } },
  });

  const mensagens = [
    {
      jsonrpc: "2.0",
      id: 1,
      method: "initialize",
      params: {
        protocolVersion: "2025-06-18",
        capabilities: {},
        clientInfo: { name: "teste", version: "1.0" },
      },
    },
    { jsonrpc: "2.0", method: "notifications/initialized" },
    chamada(2, "STJ"),
    chamada(3, "stj"),
    chamada(4, "tjpr"),
  ];

  processo.stdin.write(mensagens.map((item) => JSON.stringify(item)).join("\n"));
  processo.stdin.write("\n");
  processo.stdin.end();

  const [stdout, stderr, exitCode] = await Promise.all([
    new Response(processo.stdout).text(),
    new Response(processo.stderr).text(),
    processo.exited,
  ]);
  expect(exitCode, stderr).toBe(0);

  const respostas = stdout
    .trim()
    .split("\n")
    .map((linha) => JSON.parse(linha) as RespostaMCP);
  const texto = (id: number) => respostas.find((r) => r.id === id)?.result?.content?.[0]?.text ?? "";

  expect(texto(2)).toContain("SÚMULA STJ");
  expect(texto(3)).toBe(texto(2));
  expect(texto(3)).not.toContain("Nenhuma súmula");

  // Tribunal inexistente avisa, em vez de devolver busca vazia como se nada existisse.
  expect(texto(4)).toContain("Tribunal indisponível");
  expect(respostas.find((r) => r.id === 4)?.result?.isError).toBe(true);

  // A telemetria vai para stderr; o stdout do stdio é só protocolo.
  expect(stderr).toContain("uso_ferramenta");
});
