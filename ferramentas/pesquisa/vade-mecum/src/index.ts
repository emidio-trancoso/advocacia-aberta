/**
 * Entrypoint stdio do servidor MCP do Vade Mecum (uso local).
 *
 * Para Claude Code / Codex rodando sobre o repositório. As tool defs e handlers ficam em
 * server.ts; para o servidor HTTP hospedado (Claude connector remoto + Codex/OpenAI), ver
 * http.ts.
 */

import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { buildServer } from "./server.js";

const server = buildServer();
const transport = new StdioServerTransport();
await server.connect(transport);
