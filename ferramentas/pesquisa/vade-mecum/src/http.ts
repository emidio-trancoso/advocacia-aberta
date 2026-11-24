/**
 * Entrypoint HTTP do servidor MCP do Vade Mecum (uso hospedado).
 *
 * Transporte Streamable HTTP com SESSÃO (stateful), o padrão consumido por Claude
 * (connector remoto) e Codex/OpenAI: o cliente faz `initialize`, recebe um `mcp-session-id`
 * e o reutiliza nas chamadas seguintes. As sessões vivem em memória (single-instance).
 *
 * Acesso aberto — o conteúdo é público e as ferramentas são só de leitura — com rate limit
 * por IP. HTTPS e o /.well-known/openai-apps-challenge ficam a cargo do reverse proxy
 * (Caddy); ver deploy/.
 *
 * Variáveis de ambiente:
 *   PORT             porta HTTP (default 8080)
 *   MCP_PATH         caminho do endpoint MCP (default "/mcp")
 *   RATE_LIMIT_RPM   requisições por minuto por IP (default 60)
 *   SESSION_TTL_MIN  minutos sem requisição até a sessão ser encerrada (default 30)
 */

import { randomUUID } from "node:crypto";
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { isInitializeRequest } from "@modelcontextprotocol/sdk/types.js";
import { buildServer } from "./server.js";
import { identificarAtor } from "./identidade.js";
import { contador, instalarDescarga } from "./telemetria.js";

instalarDescarga();

const PORT = Number(process.env.PORT ?? 8080);
const MCP_PATH = process.env.MCP_PATH ?? "/mcp";
const RATE_LIMIT_RPM = Number(process.env.RATE_LIMIT_RPM ?? 60);
const JANELA_MS = 60_000;
const SESSAO_OCIOSA_MIN = Number(process.env.SESSION_TTL_MIN ?? 30);
const SESSAO_OCIOSA_MS = SESSAO_OCIOSA_MIN * 60_000;

// Sessões vivas: mcp-session-id → transporte.
const transportes = new Map<string, StreamableHTTPServerTransport>();

// Instante da última requisição de cada sessão.
//
// Sem isto a sessão só saía do mapa quando o cliente encerrava (DELETE) ou o stream
// fechava — e na prática os clientes simplesmente somem: em um dia inteiro de tráfego
// real não houve um único DELETE. Cada sessão abandonada custa ~128 KB que nunca
// voltavam, o que numa VM de 1 GB, com a base jurídica já ocupando ~550 MB, encurta o
// tempo até a máquina entrar em swap.
const ultimaAtividade = new Map<string, number>();

// ── Rate limit por IP (janela deslizante em memória) ─────────────────────────

const acessos = new Map<string, number[]>();

function clientIp(req: IncomingMessage): string {
  const xff = req.headers["x-forwarded-for"];
  if (typeof xff === "string" && xff.length > 0) return xff.split(",")[0]!.trim();
  return req.socket.remoteAddress ?? "desconhecido";
}

/**
 * Conta requisições por ATOR, não por IP.
 *
 * Por IP, todos os usuários do claude.ai caem no mesmo balde — eles chegam pelo mesmo
 * endereço da Anthropic. Um único usuário pesado consumia a cota de todos os outros, e
 * barrá-lo significava barrar todo mundo junto. Quando o cliente identifica o usuário
 * (hoje só o ChatGPT/Codex, via X-Openai-Subject), o limite passa a valer por pessoa;
 * nos demais casos a chave continua sendo o IP, como antes.
 */
function excedeuLimite(chave: string): boolean {
  const agora = Date.now();
  const historico = (acessos.get(chave) ?? []).filter((t) => agora - t < JANELA_MS);
  historico.push(agora);
  acessos.set(chave, historico);
  return historico.length > RATE_LIMIT_RPM;
}

// ── Encerramento de sessões ociosas ──────────────────────────────────────────

/** Fecha e esquece as sessões sem requisição há mais de SESSAO_OCIOSA_MS. */
function encerrarSessoesOciosas(agora: number): number {
  let encerradas = 0;
  for (const [sid, visto] of ultimaAtividade) {
    if (agora - visto < SESSAO_OCIOSA_MS) continue;
    const transporte = transportes.get(sid);
    ultimaAtividade.delete(sid);
    transportes.delete(sid);
    encerradas++;
    // O close() dispara onclose, que já remove do mapa — apagar antes evita
    // depender dessa ordem, e o erro é engolido porque a sessão vai embora de todo jeito.
    void Promise.resolve(transporte?.close()).catch(() => {});
  }
  return encerradas;
}

// Limpeza periódica: IPs inativos do rate limit e sessões abandonadas.
const limpeza = setInterval(() => {
  const agora = Date.now();
  for (const [ip, historico] of acessos) {
    const vivos = historico.filter((t) => agora - t < JANELA_MS);
    if (vivos.length === 0) acessos.delete(ip);
    else acessos.set(ip, vivos);
  }

  const encerradas = encerrarSessoesOciosas(agora);
  if (encerradas > 0) {
    console.log(
      JSON.stringify({
        evento: "sessoes_encerradas",
        ts: new Date().toISOString(),
        quantidade: encerradas,
        vivas: transportes.size,
      }),
    );
  }
}, JANELA_MS);
limpeza.unref?.();

// ── Utilidades HTTP ──────────────────────────────────────────────────────────

function lerCorpo(req: IncomingMessage): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const partes: Buffer[] = [];
    req.on("data", (c) => partes.push(c as Buffer));
    req.on("end", () => {
      const bruto = Buffer.concat(partes).toString("utf8");
      if (!bruto) return resolve(undefined);
      try {
        resolve(JSON.parse(bruto));
      } catch (e) {
        reject(e);
      }
    });
    req.on("error", reject);
  });
}

function responderJson(res: ServerResponse, status: number, corpo: unknown): void {
  res.writeHead(status, { "content-type": "application/json" });
  res.end(JSON.stringify(corpo));
}

function erroRpc(mensagem: string, code = -32000): unknown {
  return { jsonrpc: "2.0", error: { code, message: mensagem }, id: null };
}

// ── Servidor HTTP ────────────────────────────────────────────────────────────

const httpServer = createServer(async (req, res) => {
  const url = new URL(req.url ?? "/", `http://${req.headers.host ?? "localhost"}`);

  // Healthcheck (systemd/monitoramento e raiz).
  if (req.method === "GET" && (url.pathname === "/health" || url.pathname === "/")) {
    return responderJson(res, 200, { status: "ok", service: "vade-mecum-mcp" });
  }

  if (url.pathname !== MCP_PATH) {
    return responderJson(res, 404, { error: "not found" });
  }

  const ip = clientIp(req);
  const ator = identificarAtor(req, ip);
  if (excedeuLimite(ator.chave)) {
    contador.registrarBloqueio({ ator: ator.chave, cliente: ator.cliente, identificaPessoa: ator.identificaPessoa });
    return responderJson(res, 429, erroRpc("Limite de requisições excedido. Tente novamente em instantes."));
  }

  const sessionId = req.headers["mcp-session-id"] as string | undefined;

  try {
    // Sessão existente: GET (stream SSE), POST (requisições) ou DELETE (encerrar).
    if (sessionId && transportes.has(sessionId)) {
      ultimaAtividade.set(sessionId, Date.now());
      const corpo = req.method === "POST" ? await lerCorpo(req) : undefined;
      await transportes.get(sessionId)!.handleRequest(req, res, corpo);
      return;
    }

    // Nova sessão: apenas via POST com `initialize`.
    if (req.method === "POST") {
      const corpo = await lerCorpo(req);
      if (isInitializeRequest(corpo)) {
        const transport: StreamableHTTPServerTransport = new StreamableHTTPServerTransport({
          sessionIdGenerator: () => randomUUID(),
          onsessioninitialized: (sid) => {
            transportes.set(sid, transport);
            ultimaAtividade.set(sid, Date.now());
          },
        });
        transport.onclose = () => {
          if (transport.sessionId) {
            transportes.delete(transport.sessionId);
            ultimaAtividade.delete(transport.sessionId);
          }
        };
        const server = buildServer({
          ator: ator.chave,
          cliente: ator.cliente,
          identificaPessoa: ator.identificaPessoa,
        });
        await server.connect(transport);
        await transport.handleRequest(req, res, corpo);
        return;
      }
      return responderJson(res, 400, erroRpc("Sem sessão MCP válida. Envie 'initialize' primeiro."));
    }

    // GET/DELETE sem sessão válida.
    return responderJson(res, 400, erroRpc("Sessão MCP inválida ou ausente."));
  } catch {
    if (!res.headersSent) {
      responderJson(res, 500, erroRpc("Erro interno do servidor.", -32603));
    }
  }
});

httpServer.listen(PORT, () => {
  console.log(
    `Vade Mecum MCP (HTTP) ouvindo em :${PORT}${MCP_PATH} — rate limit ${RATE_LIMIT_RPM} req/min/IP`,
  );
});
