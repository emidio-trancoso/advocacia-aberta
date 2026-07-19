import { createRequire } from "module";
import { FONTE_OFICIAL, NATUREZAS_DOCUMENTAIS } from "./taxonomia.js";
import { normalizeText } from "./utils.js";

const require = createRequire(import.meta.url);

// ── Types ──────────────────────────────────────────────────────────────────

export interface Artigo {
  readonly numero: string;
  readonly texto: string;
  readonly url: string;
  readonly keywords?: string[];
}

interface CodigoJSON {
  _meta: {
    codigo: string;
    nome: string;
    lei: string;
    url_base: string;
    total_artigos: number;
  };
  artigos: Record<string, Artigo>;
  indexes?: { keywords?: Record<string, number[]> };
}

const REGISTRO_CODIGOS = {
  CPC: {
    arquivo: "../../data/lei_cpc.json",
    rotulo: "Código de Processo Civil (Lei 13.105/2015)",
  },
  CC: {
    arquivo: "../../data/lei_cc.json",
    rotulo: "Código Civil (Lei 10.406/2002)",
  },
  CP: {
    arquivo: "../../data/lei_cp.json",
    rotulo: "Código Penal (Decreto-Lei 2.848/1940)",
  },
  CPP: {
    arquivo: "../../data/lei_cpp.json",
    rotulo: "Código de Processo Penal (Decreto-Lei 3.689/1941)",
  },
  CDC: {
    arquivo: "../../data/lei_cdc.json",
    rotulo: "Código de Defesa do Consumidor (Lei 8.078/1990)",
  },
  CF: {
    arquivo: "../../data/lei_cf.json",
    rotulo: "Constituição Federal de 1988",
  },
  CLT: {
    arquivo: "../../data/lei_clt.json",
    rotulo: "Consolidação das Leis do Trabalho",
  },
  ADCT: {
    arquivo: "../../data/lei_adct.json",
    rotulo: "Ato das Disposições Constitucionais Transitórias",
  },
  CE: {
    arquivo: "../../data/lei_ce.json",
    rotulo: "Código Eleitoral (Lei 4.737/1965)",
  },
  CTB: {
    arquivo: "../../data/lei_ctb.json",
    rotulo: "Código de Trânsito Brasileiro (Lei 9.503/1997)",
  },
  CTN: {
    arquivo: "../../data/lei_ctn.json",
    rotulo: "Código Tributário Nacional (Lei 5.172/1966)",
  },
  ECA: {
    arquivo: "../../data/lei_eca.json",
    rotulo: "Estatuto da Criança e do Adolescente (Lei 8.069/1990)",
  },
  LBPS: {
    arquivo: "../../data/lei_lbps.json",
    rotulo: "Lei de Benefícios da Previdência Social (Lei 8.213/1991)",
  },
  LD: {
    arquivo: "../../data/lei_ld.json",
    rotulo: "Lei de Drogas (Lei 11.343/2006)",
  },
  LEP: {
    arquivo: "../../data/lei_lep.json",
    rotulo: "Lei de Execução Penal (Lei 7.210/1984)",
  },
  LGPD: {
    arquivo: "../../data/lei_lgpd.json",
    rotulo: "Lei Geral de Proteção de Dados Pessoais (Lei 13.709/2018)",
  },
  LINDB: {
    arquivo: "../../data/lei_lindb.json",
    rotulo: "Lei de Introdução às Normas do Direito Brasileiro (Decreto-Lei 4.657/1942)",
  },
  LLC: {
    arquivo: "../../data/lei_llc.json",
    rotulo: "Lei de Licitações e Contratos Administrativos (Lei 14.133/2021)",
  },
  LMP: {
    arquivo: "../../data/lei_lmp.json",
    rotulo: "Lei Maria da Penha (Lei 11.340/2006)",
  },
} as const;

export type CodigoCodigo = keyof typeof REGISTRO_CODIGOS;

export const CODIGOS_DISPONIVEIS = Object.freeze(
  Object.keys(REGISTRO_CODIGOS) as CodigoCodigo[],
);

export interface LegislacaoDisponivel {
  readonly codigo: CodigoCodigo;
  readonly rotulo: string;
  readonly registros: number;
  readonly urlBase: string;
}

// ── Carregamento lazy ──────────────────────────────────────────────────────

const cache = new Map<CodigoCodigo, CodigoJSON>();

function loadCodigo(codigo: CodigoCodigo): CodigoJSON {
  if (cache.has(codigo)) return cache.get(codigo)!;
  const data = require(REGISTRO_CODIGOS[codigo].arquivo) as CodigoJSON;
  cache.set(codigo, data);
  return data;
}

// ── Public API ─────────────────────────────────────────────────────────────

export function isCodigoDisponivel(valor: string): valor is CodigoCodigo {
  return Object.hasOwn(REGISTRO_CODIGOS, valor);
}

export function normalizarCodigo(
  valor: string,
): CodigoCodigo | "todos" | null {
  const normalizado = valor.trim().toUpperCase();
  if (normalizado === "TODOS") return "todos";
  return isCodigoDisponivel(normalizado) ? normalizado : null;
}

export function resolverCodigos(
  codigo: CodigoCodigo | "todos",
): readonly CodigoCodigo[] {
  return codigo === "todos" ? CODIGOS_DISPONIVEIS : [codigo];
}

export function listarLegislacaoDisponivel(): LegislacaoDisponivel[] {
  return CODIGOS_DISPONIVEIS.map((codigo) => {
    const dados = loadCodigo(codigo);
    return {
      codigo,
      rotulo: REGISTRO_CODIGOS[codigo].rotulo,
      registros: Object.keys(dados.artigos).length,
      urlBase: dados._meta.url_base,
    };
  });
}

export function buscarArtigo(
  codigo: CodigoCodigo,
  artigo: number | string,
): Artigo | null {
  const data = loadCodigo(codigo);
  return data.artigos[String(artigo)] ?? null;
}

export function buscarLegislacao(
  query: string,
  codigo: CodigoCodigo | "todos",
  limit = 5,
): Array<{ codigo: CodigoCodigo; artigo: Artigo }> {
  const codigos = resolverCodigos(codigo);

  // Tenta lookup direto "art. 702", "artigo 702", "702"
  const artMatch = query.match(/(?:art(?:igo)?\.?\s*)?(\d+)/i);
  if (artMatch && codigos.length === 1) {
    const art = buscarArtigo(codigos[0], artMatch[1]);
    if (art) return [{ codigo: codigos[0], artigo: art }];
  }

  // Busca por keywords
  const words = normalizeText(query)
    .split(/\s+/)
    .filter((word) => word.length > 2);
  if (words.length === 0) return [];

  const results: Array<{
    codigo: CodigoCodigo;
    artigo: Artigo;
    score: number;
  }> = [];

  for (const cod of codigos) {
    const data = loadCodigo(cod);
    const kwIdx = data.indexes?.keywords;

    if (kwIdx) {
      // Usa índice pré-computado
      const scores = new Map<string, number>();
      for (const word of words) {
        (kwIdx[word] ?? []).forEach((numero) => {
          const key = String(numero);
          scores.set(key, (scores.get(key) ?? 0) + 2);
        });
        // Match parcial
        for (const [indexWord, numeros] of Object.entries(kwIdx)) {
          const prefixoCompativel =
            indexWord.length >= 4 &&
            word.length >= 4 &&
            (indexWord.startsWith(word.slice(0, 4)) ||
              word.startsWith(indexWord.slice(0, 4)));
          if (prefixoCompativel) {
            numeros.forEach((numero) => {
              const key = String(numero);
              scores.set(key, (scores.get(key) ?? 0) + 1);
            });
          }
        }
      }
      [...scores.entries()]
        .sort((a, b) => b[1] - a[1])
        .slice(0, limit)
        .forEach(([numero, score]) => {
          const artigo = data.artigos[numero];
          if (artigo) results.push({ codigo: cod, artigo, score });
        });
    } else {
      // Fulltext fallback
      for (const artigo of Object.values(data.artigos)) {
        const normalizado = normalizeText(artigo.texto);
        let score = 0;
        let matched = 0;
        for (const word of words) {
          if (normalizado.includes(word)) {
            score += 1;
            matched += 1;
          }
        }
        const minMatches = Math.max(1, Math.ceil(words.length * 0.4));
        if (matched >= minMatches) {
          results.push({ codigo: cod, artigo, score });
        }
      }
    }
  }

  return results
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(({ codigo: cod, artigo }) => ({ codigo: cod, artigo }));
}

export function formatArtigo(
  codigo: CodigoCodigo,
  artigo: Artigo,
): string {
  const proveniencia = artigo.url
    ? `\n**Proveniência:** ${FONTE_OFICIAL} — texto compilado no Planalto\n**Consulta oficial:** ${artigo.url}\n`
    : `\n**Proveniência:** link oficial indisponível neste snapshot\n`;
  return `## 📋 ${NATUREZAS_DOCUMENTAIS.textoNormativo} | LEGISLAÇÃO | ${codigo}

**${REGISTRO_CODIGOS[codigo].rotulo}**
**Art. ${artigo.numero}**
**Efeito jurídico:** A CONFIRMAR — verifique vigência, redação e aplicabilidade ao caso
${proveniencia}
${artigo.texto}
`;
}
