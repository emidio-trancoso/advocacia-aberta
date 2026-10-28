/**
 * Contagem diária de uso — o que a página /privacidade do site promete, feito em código.
 *
 *   - O termo pesquisado nunca entra aqui: só ferramenta, programa, filtros do catálogo
 *     (tribunal, código) e medidas.
 *   - Não existe hora de cada pesquisa. As chamadas são somadas em memória por dia e só
 *     a soma é escrita: na virada do dia e quando o serviço para. O horário que o journald
 *     põe na linha é o da gravação da soma, não o de uma pesquisa.
 *   - A origem fica incompleta: o IP vira a faixa (/24 no IPv4, /32 no IPv6, como no
 *     Caddy) e o identificador de usuário da OpenAI vira um resumo (hash) que permite
 *     contar quem voltou sem guardar o valor original.
 *
 * A linha vai para a saída de ERRO: no transporte stdio a saída padrão é o canal do
 * protocolo MCP. O journald recolhe as duas:
 *   journalctl -u vade-mecum-mcp | grep uso_diario
 */

import { createHash } from "node:crypto";

export interface ContextoDeUso {
  readonly ator: string;
  readonly cliente: string;
  readonly identificaPessoa: boolean;
}

export interface MedidaDeUso {
  readonly tool: string;
  readonly tribunal?: string;
  readonly codigo?: string;
  readonly ms: number;
  readonly bytes: number;
  readonly achou?: boolean;
  readonly falhou: boolean;
}

interface Soma {
  chamadas: number;
  com_resultado: number;
  sem_resultado: number;
  falhas: number;
  bloqueios: number;
  ms: number;
  bytes: number;
}

const FUSO = "America/Sao_Paulo";
const diaDe = (agora: Date): string =>
  new Intl.DateTimeFormat("en-CA", { timeZone: FUSO, year: "numeric", month: "2-digit", day: "2-digit" }).format(agora);

/** Reduz a chave do ator ao que a página de privacidade permite guardar. */
export function origemIncompleta(ator: string | undefined): string | undefined {
  if (!ator) return undefined;
  if (ator.startsWith("openai:")) {
    return `openai:${createHash("sha256").update(ator.slice(7)).digest("hex").slice(0, 16)}`;
  }
  if (ator.startsWith("ip:")) {
    const ip = ator.slice(3);
    const v4 = ip.match(/^(\d+\.\d+\.\d+)\.\d+$/);
    if (v4) return `ip:${v4[1]}.0/24`;
    if (ip.includes(":")) return `ip:${ip.split(":").slice(0, 2).join(":")}::/32`;
    return "ip:?";
  }
  return "?";
}

export class ContadorDiario {
  private dia: string;
  private readonly somas = new Map<string, { chave: Record<string, unknown>; soma: Soma }>();

  constructor(
    private readonly escrever: (linha: string) => void = (linha) => console.error(linha),
    private readonly relogio: () => Date = () => new Date(),
  ) {
    this.dia = diaDe(this.relogio());
  }

  registrar(medida: MedidaDeUso, contexto?: ContextoDeUso): void {
    const soma = this.somaDe({
      tool: medida.tool,
      tribunal: medida.tribunal,
      codigo: medida.codigo,
      ator: origemIncompleta(contexto?.ator),
      cliente: contexto?.cliente,
      pessoa: contexto ? contexto.identificaPessoa : undefined,
    });
    soma.chamadas += 1;
    if (medida.falhou) soma.falhas += 1;
    else if (medida.achou === true) soma.com_resultado += 1;
    else if (medida.achou === false) soma.sem_resultado += 1;
    soma.ms += medida.ms;
    soma.bytes += medida.bytes;
  }

  /** Requisição recusada pelo limite de taxa: conta por dia, como o resto. */
  registrarBloqueio(contexto: ContextoDeUso): void {
    this.somaDe({
      tool: "(limite excedido)",
      ator: origemIncompleta(contexto.ator),
      cliente: contexto.cliente,
      pessoa: contexto.identificaPessoa,
    }).bloqueios += 1;
  }

  /** Escreve as somas e zera. Chamado na virada do dia e ao encerrar. */
  descarregar(): void {
    for (const { chave, soma } of this.somas.values()) {
      this.escrever(JSON.stringify({ evento: "uso_diario", dia: this.dia, ...chave, ...soma, ms: Math.round(soma.ms) }));
    }
    this.somas.clear();
  }

  /** Se o dia virou, grava a soma do dia anterior antes de começar a nova. */
  conferirVirada(): void {
    const hoje = diaDe(this.relogio());
    if (hoje !== this.dia) {
      this.descarregar();
      this.dia = hoje;
    }
  }

  private somaDe(chave: Record<string, unknown>): Soma {
    this.conferirVirada();
    const id = JSON.stringify(chave);
    let item = this.somas.get(id);
    if (!item) {
      item = { chave, soma: { chamadas: 0, com_resultado: 0, sem_resultado: 0, falhas: 0, bloqueios: 0, ms: 0, bytes: 0 } };
      this.somas.set(id, item);
    }
    return item.soma;
  }
}

export const contador = new ContadorDiario();

// A soma do dia não pode se perder num restart (o deploy reinicia o serviço). Sem
// tráfego, a virada do dia não aconteceria até a próxima chamada: o relógio confere.
let instalado = false;
export function instalarDescarga(): void {
  if (instalado) return;
  instalado = true;
  setInterval(() => contador.conferirVirada(), 10 * 60 * 1000).unref();
  process.on("exit", () => contador.descarregar());
  for (const sinal of ["SIGTERM", "SIGINT"] as const) {
    process.on(sinal, () => {
      contador.descarregar();
      process.exit(0);
    });
  }
}
