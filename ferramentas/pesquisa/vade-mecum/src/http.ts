/**
 * Entrypoint HTTP do servidor MCP do Vade Mecum (uso hospedado).
 *
 * Transporte Streamable HTTP com SESSÃO (stateful), o padrão consumido por Claude
 * (connector remoto) e Codex/OpenAI: o cliente faz `initialize`, recebe um `mcp-session-id`
 * e o reutiliza nas chamadas seguintes. As sessões vivem em memória (single-instance).
 *
 * Acesso aberto — o conteúdo é público e as ferramentas são só de leitura — com rate limit
 * por IP. HTTPS e o /.well-known/openai-apps-challenge ficam a cargo de um reverse proxy
 * HTTPS (ex.: Caddy), configurado fora deste repositório.
 *
 * Variáveis de ambiente:
 *   PORT            porta HTTP (default 8080)
 *   MCP_PATH        caminho do endpoint MCP (default "/mcp")
 *   RATE_LIMIT_RPM  requisições por minuto por IP (default 60)
 */

import { randomUUID } from "node:crypto";
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { isInitializeRequest } from "@modelcontextprotocol/sdk/types.js";
import { buildServer } from "./server.js";

const PORT = Number(process.env.PORT ?? 8080);
const MCP_PATH = process.env.MCP_PATH ?? "/mcp";
const RATE_LIMIT_RPM = Number(process.env.RATE_LIMIT_RPM ?? 60);
const JANELA_MS = 60_000;

// Sessões vivas: mcp-session-id → transporte.
const transportes = new Map<string, StreamableHTTPServerTransport>();

// ── Rate limit por IP (janela deslizante em memória) ─────────────────────────

const acessos = new Map<string, number[]>();

function clientIp(req: IncomingMessage): string {
  const xff = req.headers["x-forwarded-for"];
  if (typeof xff === "string" && xff.length > 0) return xff.split(",")[0]!.trim();
  return req.socket.remoteAddress ?? "desconhecido";
}

function excedeuLimite(ip: string): boolean {
  const agora = Date.now();
  const historico = (acessos.get(ip) ?? []).filter((t) => agora - t < JANELA_MS);
  historico.push(agora);
  acessos.set(ip, historico);
  return historico.length > RATE_LIMIT_RPM;
}

// Limpeza periódica para não vazar memória com IPs inativos.
const limpeza = setInterval(() => {
  const agora = Date.now();
  for (const [ip, historico] of acessos) {
    const vivos = historico.filter((t) => agora - t < JANELA_MS);
    if (vivos.length === 0) acessos.delete(ip);
    else acessos.set(ip, vivos);
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
  if (excedeuLimite(ip)) {
    return responderJson(res, 429, erroRpc("Limite de requisições excedido. Tente novamente em instantes."));
  }

  const sessionId = req.headers["mcp-session-id"] as string | undefined;

  try {
    // Sessão existente: GET (stream SSE), POST (requisições) ou DELETE (encerrar).
    if (sessionId && transportes.has(sessionId)) {
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
          },
        });
        transport.onclose = () => {
          if (transport.sessionId) transportes.delete(transport.sessionId);
        };
        const server = buildServer();
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
