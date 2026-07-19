import { createRequire } from "module";
import { FONTE_OFICIAL, NATUREZAS_DOCUMENTAIS } from "./taxonomia.js";
import { tokenize } from "./utils.js";

const require = createRequire(import.meta.url);

// ── Types ──────────────────────────────────────────────────────────────────

export interface EspelhoAcordao {
  readonly id: string;
  readonly orgao: string;
  readonly classe: string;
  readonly descricaoClasse: string;
  readonly numeroProcesso: string;
  readonly numeroRegistro: string;
  readonly relator: string;
  readonly dataPublicacao: string;
  readonly ementa: string;
  readonly teseJuridica: string;
  readonly tema: string;
  readonly jurisprudenciaCitada: string;
  readonly referenciasLegislativas: readonly string[];
  readonly links: {
    readonly consultaProcessual?: string;
    readonly jurisprudencia?: string;
  };
}

// ── Data loading ───────────────────────────────────────────────────────────

const raw = require("../../data/espelhos_stj.json") as {
  _meta: { totalEspelhos: number; orgaos: Record<string, number> };
  espelhos: Record<string, EspelhoAcordao>;
};

const { espelhos } = raw;

export const TOTAL_ESPELHOS_STJ = Object.keys(espelhos).length;
export const TOTAL_ORGAOS_ESPELHOS = new Set(
  Object.values(espelhos).map((item) => item.orgao),
).size;

// ── Índice textual em memória ──────────────────────────────────────────────
// Sobre os campos curados publicados (a ementa fica no link oficial); cobre
// todos os espelhos. A tese e o tema, quando presentes, recebem mais peso.

const INDICE = new Map<string, Map<string, number>>();

function indexar(id: string, texto: string, peso: number): void {
  for (const token of tokenize(texto)) {
    let posting = INDICE.get(token);
    if (!posting) {
      posting = new Map();
      INDICE.set(token, posting);
    }
    posting.set(id, (posting.get(id) ?? 0) + peso);
  }
}

for (const item of Object.values(espelhos)) {
  indexar(item.id, item.teseJuridica, 3);
  indexar(item.id, item.tema, 2);
  indexar(item.id, item.ementa, 2);
  indexar(item.id, item.descricaoClasse, 1);
  indexar(item.id, item.jurisprudenciaCitada, 1);
  indexar(item.id, item.referenciasLegislativas.join(" "), 1);
  indexar(item.id, item.relator, 1);
}

// ── Public API ─────────────────────────────────────────────────────────────

export function buscarEspelhos(query: string, limit = 5): EspelhoAcordao[] {
  // Lookup direto por número de registro (12+ dígitos) quando a consulta é só isso.
  const registro = query.replace(/\D/g, "");
  if (registro.length >= 11 && registro === query.trim().replace(/\D/g, "")) {
    const achados = Object.values(espelhos).filter(
      (item) => item.numeroRegistro.replace(/\D/g, "") === registro,
    );
    if (achados.length > 0) return achados.slice(0, limit);
  }

  const tokens = tokenize(query);
  if (tokens.length === 0) return [];

  const scores = new Map<string, number>();
  for (const token of tokens) {
    const posting = INDICE.get(token);
    if (!posting) continue;
    for (const [id, peso] of posting) {
      scores.set(id, (scores.get(id) ?? 0) + peso);
    }
  }

  return [...scores.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .slice(0, limit)
    .map(([id]) => espelhos[id])
    .filter((item): item is EspelhoAcordao => item !== undefined);
}

export function formatEspelho(item: EspelhoAcordao): string {
  const processo = [item.classe, item.numeroProcesso].filter(Boolean).join(" ");
  const ementa = item.ementa?.trim() ? `\n**Ementa:**\n> ${item.ementa}\n` : "";
  const tese = item.teseJuridica?.trim()
    ? `\n**Tese jurídica:**\n> ${item.teseJuridica}\n`
    : "";
  const tema = item.tema?.trim() ? `\n**Tema/situação:** ${item.tema}` : "";
  const refs = item.referenciasLegislativas.length
    ? `\n**Referências legislativas:** ${item.referenciasLegislativas.join(" | ")}`
    : "";
  const jurisprudencia = item.jurisprudenciaCitada?.trim()
    ? `\n**Jurisprudência citada:** ${item.jurisprudenciaCitada}`
    : "";
  const links = [
    ["Consulta processual", item.links.consultaProcessual],
    ["Jurisprudência do STJ", item.links.jurisprudencia],
  ]
    .filter((entry): entry is [string, string] => Boolean(entry[1]))
    .map(([rotulo, url]) => `- ${rotulo}: ${url}`)
    .join("\n");
  const fonte = links
    ? `\n**Proveniência:** ${FONTE_OFICIAL} — STJ\n${links}\n`
    : "\n**Proveniência:** links oficiais não disponíveis neste snapshot.\n";

  return `## 📋 ${NATUREZAS_DOCUMENTAIS.espelhoDeAcordao} | STJ — ${item.orgao}

**${processo || "Acórdão"}** | **Relator(a):** ${item.relator || "não informado"}${item.dataPublicacao ? ` | **Publicação:** ${item.dataPublicacao}` : ""}
**Efeito jurídico:** NÃO VINCULANTE POR SI SÓ — espelho de acórdão selecionado pela Secretaria de Jurisprudência do STJ; confira o inteiro teor e eventual tese qualificada${tema}
${ementa}${tese}${refs}${jurisprudencia}${fonte}`;
}
