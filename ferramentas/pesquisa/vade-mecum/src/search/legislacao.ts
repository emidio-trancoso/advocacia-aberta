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
  // [expansao:inicio] entradas geradas por gerar_expansao_legislacao.py — não edite à mão
  CAG: {
    arquivo: "../../data/lei_cag.json",
    rotulo: "Código de Águas (Decreto 24.643/1934)",
  },
  CBA: {
    arquivo: "../../data/lei_cba.json",
    rotulo: "Código Brasileiro de Aeronáutica (Lei 7.565/1986)",
  },
  CBT: {
    arquivo: "../../data/lei_cbt.json",
    rotulo: "Código Brasileiro de Telecomunicações (Lei 4.117/1962)",
  },
  CFLO: {
    arquivo: "../../data/lei_cflo.json",
    rotulo: "Código Florestal (Lei 12.651/2012)",
  },
  CMIN: {
    arquivo: "../../data/lei_cmin.json",
    rotulo: "Código de Minas (Decreto-Lei 227/1967)",
  },
  CPM: {
    arquivo: "../../data/lei_cpm.json",
    rotulo: "Código Penal Militar (Decreto-Lei 1.001/1969)",
  },
  CPPM: {
    arquivo: "../../data/lei_cppm.json",
    rotulo: "Código de Processo Penal Militar (Decreto-Lei 1.002/1969)",
  },
  D3413: {
    arquivo: "../../data/lei_d3413.json",
    rotulo: "Convenção de Haia – Sequestro Internacional de Crianças (promulgação) (Decreto 3.413/2000)",
  },
  D70235: {
    arquivo: "../../data/lei_d70235.json",
    rotulo: "Processo Administrativo Fiscal (PAF) Federal (Decreto 70.235/1972)",
  },
  DL1598: {
    arquivo: "../../data/lei_dl1598.json",
    rotulo: "IRPJ – Normas Gerais (conceitos e apuração) (Decreto-Lei 1.598/1977)",
  },
  ECID: {
    arquivo: "../../data/lei_ecid.json",
    rotulo: "Estatuto da Cidade (Lei 10.257/2001)",
  },
  ED: {
    arquivo: "../../data/lei_ed.json",
    rotulo: "Estatuto do Desarmamento (Lei 10.826/2003)",
  },
  EDT: {
    arquivo: "../../data/lei_edt.json",
    rotulo: "Estatuto de Defesa do Torcedor (Lei 10.671/2003)",
  },
  EI: {
    arquivo: "../../data/lei_ei.json",
    rotulo: "Estatuto da Pessoa Idosa (Lei 10.741/2003)",
  },
  EIND: {
    arquivo: "../../data/lei_eind.json",
    rotulo: "Estatuto do Índio (Lei 6.001/1973)",
  },
  EIR: {
    arquivo: "../../data/lei_eir.json",
    rotulo: "Estatuto da Igualdade Racial (Lei 12.288/2010)",
  },
  EJUV: {
    arquivo: "../../data/lei_ejuv.json",
    rotulo: "Estatuto da Juventude (Lei 12.852/2013)",
  },
  EMET: {
    arquivo: "../../data/lei_emet.json",
    rotulo: "Estatuto da Metrópole (Lei 13.089/2015)",
  },
  EMIL: {
    arquivo: "../../data/lei_emil.json",
    rotulo: "Estatuto dos Militares (Lei 6.880/1980)",
  },
  EMUS: {
    arquivo: "../../data/lei_emus.json",
    rotulo: "Estatuto dos Museus (Lei 11.904/2009)",
  },
  EOAB: {
    arquivo: "../../data/lei_eoab.json",
    rotulo: "Estatuto da Advocacia e a Ordem dos Advogados do Brasil (Lei 8.906/1994)",
  },
  EPC: {
    arquivo: "../../data/lei_epc.json",
    rotulo: "Estatuto da Pessoa com Câncer (Lei 14.238/2021)",
  },
  EPD: {
    arquivo: "../../data/lei_epd.json",
    rotulo: "Estatuto da Pessoa com Deficiência (Lei 13.146/2015)",
  },
  EREF: {
    arquivo: "../../data/lei_eref.json",
    rotulo: "Estatuto dos Refugiados (Lei 9.474/1997)",
  },
  ET: {
    arquivo: "../../data/lei_et.json",
    rotulo: "Estatuto da Terra (Lei 4.504/1964)",
  },
  FGTS: {
    arquivo: "../../data/lei_fgts.json",
    rotulo: "FGTS (Lei 8.036/1990)",
  },
  L10101: {
    arquivo: "../../data/lei_l10101.json",
    rotulo: "Participação nos Lucros ou Resultados (PLR) (Lei 10.101/2000)",
  },
  L10259: {
    arquivo: "../../data/lei_l10259.json",
    rotulo: "Juizados Especiais Federais (JEFs) (Lei 10.259/2001)",
  },
  L10522: {
    arquivo: "../../data/lei_l10522.json",
    rotulo: "CADIN – Cadastro Informativo de Créditos não Quitados (Lei 10.522/2002)",
  },
  L10637: {
    arquivo: "../../data/lei_l10637.json",
    rotulo: "PIS (não cumulativo) (Lei 10.637/2002)",
  },
  L10666: {
    arquivo: "../../data/lei_l10666.json",
    rotulo: "Disposições Previdenciárias Diversas (inclui cooperados) (Lei 10.666/2003)",
  },
  L10684: {
    arquivo: "../../data/lei_l10684.json",
    rotulo: "Parcelamento Especial – PAES (Lei 10.684/2003)",
  },
  L10779: {
    arquivo: "../../data/lei_l10779.json",
    rotulo: "Seguro-Defeso do Pescador Artesanal (Lei 10.779/2003)",
  },
  L10833: {
    arquivo: "../../data/lei_l10833.json",
    rotulo: "COFINS (não cumulativa) (Lei 10.833/2003)",
  },
  L10865: {
    arquivo: "../../data/lei_l10865.json",
    rotulo: "PIS/COFINS na Importação (Lei 10.865/2004)",
  },
  L10887: {
    arquivo: "../../data/lei_l10887.json",
    rotulo: "Cálculo/Contribuição de Servidor Federal (RPPS União) (Lei 10.887/2004)",
  },
  L11441: {
    arquivo: "../../data/lei_l11441.json",
    rotulo: "Inventários Extrajudiciais (Lei 11.441/2007)",
  },
  L11770: {
    arquivo: "../../data/lei_l11770.json",
    rotulo: "Programa Empresa Cidadã (licenças) (Lei 11.770/2008)",
  },
  L11788: {
    arquivo: "../../data/lei_l11788.json",
    rotulo: "Lei do Estágio (Lei 11.788/2008)",
  },
  L11804: {
    arquivo: "../../data/lei_l11804.json",
    rotulo: "Alimentos Gravídicos (Lei 11.804/2008)",
  },
  L12010: {
    arquivo: "../../data/lei_l12010.json",
    rotulo: "Adoção (Lei 12.010/2009)",
  },
  L12318: {
    arquivo: "../../data/lei_l12318.json",
    rotulo: "Alienação Parental (Lei 12.318/2010)",
  },
  L12506: {
    arquivo: "../../data/lei_l12506.json",
    rotulo: "Aviso Prévio Proporcional (Lei 12.506/2011)",
  },
  L12618: {
    arquivo: "../../data/lei_l12618.json",
    rotulo: "Funpresp / Regime de Previdência Complementar do Servidor (Lei 12.618/2012)",
  },
  L12815: {
    arquivo: "../../data/lei_l12815.json",
    rotulo: "Setor Portuário – Relações de Trabalho (Lei 12.815/2013)",
  },
  L12850: {
    arquivo: "../../data/lei_l12850.json",
    rotulo: "Organização Criminosa (Lei 12.850/2013)",
  },
  L13058: {
    arquivo: "../../data/lei_l13058.json",
    rotulo: "Guarda Compartilhada (Lei 13.058/2014)",
  },
  L13103: {
    arquivo: "../../data/lei_l13103.json",
    rotulo: "Motorista Profissional (Lei 13.103/2015)",
  },
  L13165: {
    arquivo: "../../data/lei_l13165.json",
    rotulo: "Minirreforma Eleitoral 2015 (Lei 13.165/2015)",
  },
  L13257: {
    arquivo: "../../data/lei_l13257.json",
    rotulo: "Marco Legal da Primeira Infância (Lei 13.257/2016)",
  },
  L13260: {
    arquivo: "../../data/lei_l13260.json",
    rotulo: "Antiterrorismo (Lei 13.260/2016)",
  },
  L13431: {
    arquivo: "../../data/lei_l13431.json",
    rotulo: "Sistema de Garantia – Escuta e Depoimento Especial (Lei 13.431/2017)",
  },
  L13487: {
    arquivo: "../../data/lei_l13487.json",
    rotulo: "Fundo Especial de Financiamento de Campanha (FEFC) (Lei 13.487/2017)",
  },
  L13488: {
    arquivo: "../../data/lei_l13488.json",
    rotulo: "Reforma Eleitoral 2017 (ajustes adicionais) (Lei 13.488/2017)",
  },
  L13869: {
    arquivo: "../../data/lei_l13869.json",
    rotulo: "Abuso de Autoridade (Lei 13.869/2019)",
  },
  L13988: {
    arquivo: "../../data/lei_l13988.json",
    rotulo: "Transação no Contencioso Tributário Federal (Lei 13.988/2020)",
  },
  L14192: {
    arquivo: "../../data/lei_l14192.json",
    rotulo: "Violência Política contra a Mulher (Lei 14.192/2021)",
  },
  L14208: {
    arquivo: "../../data/lei_l14208.json",
    rotulo: "Federações Partidárias (Lei 14.208/2021)",
  },
  L14211: {
    arquivo: "../../data/lei_l14211.json",
    rotulo: "Sobras e Quociente (distribuição de vagas) (Lei 14.211/2021)",
  },
  L14344: {
    arquivo: "../../data/lei_l14344.json",
    rotulo: "Violência Contra Crianças e Adolescentes (Lei 14.344/2022)",
  },
  L14382: {
    arquivo: "../../data/lei_l14382.json",
    rotulo: "Modernização dos Registros Públicos (SERP) (Lei 14.382/2022)",
  },
  L14442: {
    arquivo: "../../data/lei_l14442.json",
    rotulo: "Auxílio‑Alimentação (regras e vedações) (Lei 14.442/2022)",
  },
  L14611: {
    arquivo: "../../data/lei_l14611.json",
    rotulo: "Igualdade Salarial por Gênero (Lei 14.611/2023)",
  },
  L1521: {
    arquivo: "../../data/lei_l1521.json",
    rotulo: "Crimes contra Economia Popular (Lei 1.521/1951)",
  },
  L3207: {
    arquivo: "../../data/lei_l3207.json",
    rotulo: "Vendedores Viajantes ou Pracistas (Lei 3.207/1957)",
  },
  L4090: {
    arquivo: "../../data/lei_l4090.json",
    rotulo: "Gratificação de Natal (13º salário) (Lei 4.090/1962)",
  },
  L4749: {
    arquivo: "../../data/lei_l4749.json",
    rotulo: "Pagamento do 13º salário (prazos e forma) (Lei 4.749/1965)",
  },
  L4950A: {
    arquivo: "../../data/lei_l4950a.json",
    rotulo: "Pisos Profissionais (Eng., Arq., Agr., Vet., Quím.) (Lei 4.950-A/1966)",
  },
  L5478: {
    arquivo: "../../data/lei_l5478.json",
    rotulo: "Alimentos (Lei 5.478/1968)",
  },
  L5584: {
    arquivo: "../../data/lei_l5584.json",
    rotulo: "Normas do Processo do Trabalho (Lei 5.584/1970)",
  },
  L5889: {
    arquivo: "../../data/lei_l5889.json",
    rotulo: "Trabalho Rural (Lei 5.889/1973)",
  },
  L6019: {
    arquivo: "../../data/lei_l6019.json",
    rotulo: "Trabalho Temporário (Lei 6.019/1974)",
  },
  L605: {
    arquivo: "../../data/lei_l605.json",
    rotulo: "Repouso Semanal Remunerado e Feriados (DSR) (Lei 605/1949)",
  },
  L6091: {
    arquivo: "../../data/lei_l6091.json",
    rotulo: "Transporte de Eleitores em Zona Rural (Lei 6.091/1974)",
  },
  L6321: {
    arquivo: "../../data/lei_l6321.json",
    rotulo: "Programa de Alimentação do Trabalhador (PAT) (Lei 6.321/1976)",
  },
  L6515: {
    arquivo: "../../data/lei_l6515.json",
    rotulo: "Lei do Divórcio (Lei 6.515/1977)",
  },
  L6533: {
    arquivo: "../../data/lei_l6533.json",
    rotulo: "Profissão de Artista e de Técnico em Espetáculos (Lei 6.533/1978)",
  },
  L6615: {
    arquivo: "../../data/lei_l6615.json",
    rotulo: "Profissão de Radialista (Lei 6.615/1978)",
  },
  L6858: {
    arquivo: "../../data/lei_l6858.json",
    rotulo: "Pagamento a Dependentes sem Inventário (Lei 6.858/1980)",
  },
  L6996: {
    arquivo: "../../data/lei_l6996.json",
    rotulo: "Apoio Logístico Postal a Alistamento e Eleições (Lei 6.996/1982)",
  },
  L7064: {
    arquivo: "../../data/lei_l7064.json",
    rotulo: "Trabalho no Exterior (brasileiros) (Lei 7.064/1982)",
  },
  L7418: {
    arquivo: "../../data/lei_l7418.json",
    rotulo: "Vale-Transporte (Lei 7.418/1985)",
  },
  L7444: {
    arquivo: "../../data/lei_l7444.json",
    rotulo: "Revisão do Eleitorado (Lei 7.444/1985)",
  },
  L7492: {
    arquivo: "../../data/lei_l7492.json",
    rotulo: "Crimes contra o Sistema Financeiro (Lei 7.492/1986)",
  },
  L7689: {
    arquivo: "../../data/lei_l7689.json",
    rotulo: "CSLL – Contribuição Social sobre o Lucro Líquido (instituidora) (Lei 7.689/1988)",
  },
  L7713: {
    arquivo: "../../data/lei_l7713.json",
    rotulo: "Imposto de Renda da Pessoa Física (IRPF) (Lei 7.713/1988)",
  },
  L7716: {
    arquivo: "../../data/lei_l7716.json",
    rotulo: "Racismo (Lei 7.716/1989)",
  },
  L7783: {
    arquivo: "../../data/lei_l7783.json",
    rotulo: "Direito de Greve (Lei 7.783/1989)",
  },
  L7960: {
    arquivo: "../../data/lei_l7960.json",
    rotulo: "Prisão Temporária (Lei 7.960/1989)",
  },
  L7998: {
    arquivo: "../../data/lei_l7998.json",
    rotulo: "Seguro‑Desemprego, Abono e FAT (Lei 7.998/1990)",
  },
  L8009: {
    arquivo: "../../data/lei_l8009.json",
    rotulo: "Bem de Família (impenhorabilidade do imóvel residencial) (Lei 8.009/1990)",
  },
  L8072: {
    arquivo: "../../data/lei_l8072.json",
    rotulo: "Crimes Hediondos (Lei 8.072/1990)",
  },
  L8137: {
    arquivo: "../../data/lei_l8137.json",
    rotulo: "Crimes contra Ordem Tributária (Lei 8.137/1990)",
  },
  L8212: {
    arquivo: "../../data/lei_l8212.json",
    rotulo: "Plano de Custeio da Seguridade Social (Lei 8.212/1991)",
  },
  L8560: {
    arquivo: "../../data/lei_l8560.json",
    rotulo: "Investigação de Paternidade (filho havido fora do casamento) (Lei 8.560/1992)",
  },
  L8935: {
    arquivo: "../../data/lei_l8935.json",
    rotulo: "Cartórios (Lei 8.935/1994)",
  },
  L8971: {
    arquivo: "../../data/lei_l8971.json",
    rotulo: "Companheiros Alimentos e Sucessão (Lei 8.971/1994)",
  },
  L8989: {
    arquivo: "../../data/lei_l8989.json",
    rotulo: "IPI – Isenção para PcD (automóveis) (Lei 8.989/1995)",
  },
  L9029: {
    arquivo: "../../data/lei_l9029.json",
    rotulo: "Antidiscriminação nas Relações de Trabalho (Lei 9.029/1995)",
  },
  L9096: {
    arquivo: "../../data/lei_l9096.json",
    rotulo: "Lei dos Partidos Políticos (Lei 9.096/1995)",
  },
  L9249: {
    arquivo: "../../data/lei_l9249.json",
    rotulo: "IRPJ/CSLL – Regras centrais (JCP, bases e limites) (Lei 9.249/1995)",
  },
  L9278: {
    arquivo: "../../data/lei_l9278.json",
    rotulo: "União Estável (regime jurídico) (Lei 9.278/1996)",
  },
  L9296: {
    arquivo: "../../data/lei_l9296.json",
    rotulo: "Interceptação Telefônica (Lei 9.296/1996)",
  },
  L9430: {
    arquivo: "../../data/lei_l9430.json",
    rotulo: "Legislação Tributária Federal (IRPJ, compensação etc.) (Lei 9.430/1996)",
  },
  L9455: {
    arquivo: "../../data/lei_l9455.json",
    rotulo: "Tortura (Lei 9.455/1997)",
  },
  L9504: {
    arquivo: "../../data/lei_l9504.json",
    rotulo: "Lei das Eleições (Lei 9.504/1997)",
  },
  L9601: {
    arquivo: "../../data/lei_l9601.json",
    rotulo: "Contrato por Prazo Determinado (via ACT/CCT) (Lei 9.601/1998)",
  },
  L9605: {
    arquivo: "../../data/lei_l9605.json",
    rotulo: "Crimes Ambientais (Lei 9.605/1998)",
  },
  L9613: {
    arquivo: "../../data/lei_l9613.json",
    rotulo: "Lavagem de Dinheiro (Lei 9.613/1998)",
  },
  L9717: {
    arquivo: "../../data/lei_l9717.json",
    rotulo: "Normas Gerais dos RPPS (Lei 9.717/1998)",
  },
  L9796: {
    arquivo: "../../data/lei_l9796.json",
    rotulo: "Compensação Financeira RGPS × RPPS (COMPREV) (Lei 9.796/1999)",
  },
  L9807: {
    arquivo: "../../data/lei_l9807.json",
    rotulo: "Proteção Testemunhas (Lei 9.807/1999)",
  },
  LC105: {
    arquivo: "../../data/lei_lc105.json",
    rotulo: "Quebra Sigilo Bancário (Lei Complementar 105/2001)",
  },
  LC108: {
    arquivo: "../../data/lei_lc108.json",
    rotulo: "Previdência Complementar com Patrocinador Público (Lei Complementar 108/2001)",
  },
  LC109: {
    arquivo: "../../data/lei_lc109.json",
    rotulo: "Previdência Complementar (regras gerais) (Lei Complementar 109/2001)",
  },
  LC116: {
    arquivo: "../../data/lei_lc116.json",
    rotulo: "ISS – Normas Gerais e Lista de Serviços (Lei Complementar 116/2003)",
  },
  LC123: {
    arquivo: "../../data/lei_lc123.json",
    rotulo: "Estatuto Nacional da Microempresa e da Empresa de Pequeno Porte (Lei Complementar 123/2006)",
  },
  LC135: {
    arquivo: "../../data/lei_lc135.json",
    rotulo: "Lei da Ficha Limpa (altera LC 64/1990) (Lei Complementar 135/2010)",
  },
  LC142: {
    arquivo: "../../data/lei_lc142.json",
    rotulo: "Aposentadoria da Pessoa com Deficiência (RGPS) (Lei Complementar 142/2013)",
  },
  LC150: {
    arquivo: "../../data/lei_lc150.json",
    rotulo: "Empregado Doméstico (Lei Complementar 150/2015)",
  },
  LC64: {
    arquivo: "../../data/lei_lc64.json",
    rotulo: "Inelegibilidades (Lei Complementar das Inelegibilidades) (Lei Complementar 64/1990)",
  },
  LC87: {
    arquivo: "../../data/lei_lc87.json",
    rotulo: "ICMS – Normas Gerais (Lei Kandir) (Lei Complementar 87/1996)",
  },
  LCP: {
    arquivo: "../../data/lei_lcp.json",
    rotulo: "Contravenções Penais (Decreto-Lei 3.688/1941)",
  },
  LEF: {
    arquivo: "../../data/lei_lef.json",
    rotulo: "Execução Fiscal (LEF) (Lei 6.830/1980)",
  },
  LMIG: {
    arquivo: "../../data/lei_lmig.json",
    rotulo: "Lei de Migração (Lei 13.445/2017)",
  },
  LOAS: {
    arquivo: "../../data/lei_loas.json",
    rotulo: "Lei Orgânica da Assistência Social (LOAS) (Lei 8.742/1993)",
  },
  LRP: {
    arquivo: "../../data/lei_lrp.json",
    rotulo: "Registros Públicos (Lei 6.015/1973)",
  },
  // [expansao:fim]
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
