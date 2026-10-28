/**
 * Identidade do ator por trás de uma chamada — para administrar consumo.
 *
 * O serviço é aberto e sem cadastro, então "quem está usando" só pode ser respondido
 * com o que o cliente manda. O que existe hoje, por cliente:
 *
 *   ChatGPT/Codex  X-Openai-Subject — identificador de usuário, ESTÁVEL entre sessões.
 *                  É o único caso em que dá para dizer "esta pessoa consumiu tanto".
 *   claude.ai      nada. As requisições saem da infraestrutura da Anthropic, e não há
 *                  header de usuário: todos os usuários chegam pelo mesmo IP. Aqui a
 *                  granularidade máxima é a sessão MCP, que morre a cada conversa.
 *   Claude Code    nada, mas a chamada sai da máquina da pessoa, então o IP serve.
 *
 * Consequência prática, que não dá para contornar do lado do servidor: um consumo
 * excessivo vindo do claude.ai é atribuível a uma sessão, nunca a uma pessoa.
 *
 * A chave completa (IP ou identificador da OpenAI) só existe em memória, para o limite
 * de taxa. Nada a grava como veio: a telemetria (telemetria.ts) guarda a faixa do IP e
 * um resumo do identificador, e o log de acesso do Caddy mascara os dois.
 */

import type { IncomingMessage } from "node:http";

export interface Ator {
  /** Chave de agrupamento e de rate limit. Ex.: "openai:v1/FGIA…" ou "ip:203.0.113.7". */
  readonly chave: string;
  /** De onde veio a identidade, para o relatório saber o que a chave vale. */
  readonly origem: "openai-subject" | "ip";
  /** Família do cliente, para leitura humana. */
  readonly cliente: string;
  /** true quando a chave identifica uma pessoa; false quando identifica só uma origem de rede. */
  readonly identificaPessoa: boolean;
}

function primeiro(valor: string | string[] | undefined): string | undefined {
  if (Array.isArray(valor)) return valor[0];
  return valor;
}

/** Classifica o cliente pela assinatura do User-Agent. */
export function familiaDoCliente(userAgent: string): string {
  const ua = userAgent.toLowerCase();
  if (ua.includes("openai-mcp")) return ua.includes("codex") ? "Codex" : "ChatGPT";
  if (ua.includes("claude-user")) return "claude.ai";
  if (ua.includes("claude-code")) return "Claude Code";
  if (ua === "") return "(sem identificação)";
  return "outro";
}

/**
 * Deriva o ator de uma requisição.
 *
 * `ipDoCliente` é injetado porque quem sabe ler X-Forwarded-For com segurança é o
 * servidor HTTP, não este módulo.
 */
export function identificarAtor(req: IncomingMessage, ipDoCliente: string): Ator {
  const userAgent = primeiro(req.headers["user-agent"]) ?? "";
  const cliente = familiaDoCliente(userAgent);

  const subject = primeiro(req.headers["x-openai-subject"]);
  if (subject && subject.length > 0) {
    return {
      chave: `openai:${subject}`,
      origem: "openai-subject",
      cliente,
      identificaPessoa: true,
    };
  }

  return {
    chave: `ip:${ipDoCliente}`,
    origem: "ip",
    cliente,
    // O IP só vale como pessoa quando a chamada sai da máquina dela. Vindo de claude.ai,
    // é o IP da Anthropic e agrupa usuários que não têm relação entre si.
    identificaPessoa: cliente !== "claude.ai",
  };
}
