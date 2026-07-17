import { createRequire } from "module";
import {
  descreverEfeitoTema,
  FONTE_OFICIAL,
  NATUREZAS_DOCUMENTAIS,
} from "./taxonomia.js";
import { normalizeText } from "./utils.js";

const require = createRequire(import.meta.url);

// ── Types ──────────────────────────────────────────────────────────────────

export interface TemaData {
  readonly numero: number;
  readonly situacao: string;
  readonly ramo: string;
  readonly assuntos: readonly string[];
  readonly questao: string;
  readonly teseFirmada?: string;
  readonly orgaoJulgador?: string;
  readonly processo?: string;
  readonly relator?: string;
  readonly dataAfetacao?: string;
  readonly dataJulgamento?: string;
  readonly links: {
    readonly scon?: string;
    readonly consultaProcessual?: string;
    readonly paginaTema?: string;
  };
}

// ── Data loading ───────────────────────────────────────────────────────────

const raw = require("../../data/flash_temas_stj.json") as {
  _meta: { totalTemas: number; generatedAt: string };
  temas: Record<string, TemaData>;
  keywords: Record<string, readonly number[]>;
  terms: Record<string, readonly number[]>;
};

export const TOTAL_TEMAS_STJ = Object.keys(raw.temas).length;

// ── Sinônimos ──────────────────────────────────────────────────────────────

const SYNONYMS: Record<string, string[]> = {
  whatsapp: ["aplicativo", "mensagens", "redes", "sociais"],
  pix: ["transferencia", "pagamento", "instantaneo"],
  uber: ["transporte", "aplicativo", "motorista"],
  selic: ["juros", "correcao", "monetaria"],
  cdi: ["juros", "financeiro"],
  citacao: ["intimacao", "notificacao"],
  intimacao: ["citacao", "notificacao"],
};

function expandTokens(tokens: string[]): string[] {
  const expanded = new Set(tokens);
  for (const t of tokens) {
    (SYNONYMS[t] ?? []).forEach(s => expanded.add(s));
  }
  return [...expanded];
}

function tokenize(text: string): string[] {
  return normalizeText(text)
    .split(" ")
    .filter(w => w.length > 2);
}

// ── Public API ─────────────────────────────────────────────────────────────

export function buscarTemas(query: string, limit = 5): TemaData[] {
  // Tenta lookup por número ("tema 1377", "tema repetitivo 1302")
  const numMatch = query.match(/tema\s*(?:repetitivo)?\s*n?[º°.]?\s*(\d+)/i);
  if (numMatch) {
    const tema = raw.temas[numMatch[1]];
    if (tema) return [tema];
  }

  const tokens = expandTokens(tokenize(query));
  if (tokens.length === 0) return [];

  const scores = new Map<number, number>();

  for (const t of tokens) {
    (raw.keywords[t] ?? []).forEach(n => scores.set(n, (scores.get(n) ?? 0) + 2));
    (raw.terms[t] ?? []).forEach(n => scores.set(n, (scores.get(n) ?? 0) + 1));
  }

  return [...scores.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([n]) => raw.temas[String(n)])
    .filter((t): t is TemaData => t !== undefined);
}

export function formatTema(tema: TemaData): string {
  const tese = tema.teseFirmada
    ? `\n**Tese firmada:**\n> ${tema.teseFirmada}\n`
    : "\n**Tese firmada:** não registrada neste snapshot\n";
  const links = [
    ["Página do tema", tema.links.paginaTema],
    ["Jurisprudência do STJ", tema.links.scon],
    ["Consulta processual", tema.links.consultaProcessual],
  ]
    .filter((item): item is [string, string] => Boolean(item[1]))
    .map(([rotulo, url]) => `- ${rotulo}: ${url}`)
    .join("\n");
  const fontes = links
    ? `\n**Proveniência:** ${FONTE_OFICIAL}\n${links}\n`
    : "\n**Proveniência:** links oficiais não disponíveis neste snapshot.\n";
  const efeito = descreverEfeitoTema(tema.situacao, tema.teseFirmada);

  return `## 📋 ${NATUREZAS_DOCUMENTAIS.registroPrecedenteQualificado} | TEMA REPETITIVO STJ

**Tema ${tema.numero} STJ**
**Situação:** ${tema.situacao} | **Ramo:** ${tema.ramo}
**Efeito jurídico:** ${efeito}

**Questão submetida:**
> ${tema.questao}
${tese}
**Assuntos:** ${tema.assuntos.join(", ")}${tema.orgaoJulgador ? `\n**Órgão:** ${tema.orgaoJulgador}` : ""}${tema.dataJulgamento ? ` | **Julgamento:** ${tema.dataJulgamento}` : ""}${fontes}
`;
}
