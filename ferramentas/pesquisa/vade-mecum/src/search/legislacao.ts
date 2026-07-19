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

// Números de artigo podem ser sufixados ("121-A"), então o índice aceita
// strings além de números; o motor normaliza tudo para string no lookup.
type IndiceInvertido = Record<string, ReadonlyArray<number | string>>;

interface CodigoJSON {
  _meta: {
    codigo: string;
    nome: string;
    lei: string;
    url_base: string;
    total_artigos: number;
  };
  artigos: Record<string, Artigo>;
  indexes?: { keywords?: IndiceInvertido };
}

// Índice derivado por diploma (BASE-019): para cada dispositivo fora do
// índice curado, os tokens normalizados do texto publicado, em uma string
// na ordem da primeira ocorrência. Gerado por
// ferramentas/manutencao/gerar_indices_derivados.py (manifesto em
// base-juridica/indices-derivados.json).
interface IndiceGeradoJSON {
  _meta: { codigo: string | null; fonte: { sha256: string } };
  tokens: Record<string, string>;
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
  D10278: {
    arquivo: "../../data/lei_d10278.json",
    rotulo: "Digitalização de Documentos – Requisitos de Integridade (Decreto 10.278/2020)",
  },
  D11034: {
    arquivo: "../../data/lei_d11034.json",
    rotulo: "Serviço de Atendimento ao Consumidor (SAC) (Decreto 11.034/2022)",
  },
  D2181: {
    arquivo: "../../data/lei_d2181.json",
    rotulo: "Sistema Nacional de Defesa do Consumidor e Sanções Administrativas (Decreto 2.181/1997)",
  },
  D3413: {
    arquivo: "../../data/lei_d3413.json",
    rotulo: "Convenção de Haia – Sequestro Internacional de Crianças (promulgação) (Decreto 3.413/2000)",
  },
  D4311: {
    arquivo: "../../data/lei_d4311.json",
    rotulo: "Convenção de Nova York (1958) — sentenças arbitrais — promulgação (Decreto 4.311/2002)",
  },
  D70235: {
    arquivo: "../../data/lei_d70235.json",
    rotulo: "Processo Administrativo Fiscal (PAF) Federal (Decreto 70.235/1972)",
  },
  D7962: {
    arquivo: "../../data/lei_d7962.json",
    rotulo: "Regulamentação da contratação no comércio eletrônico (Decreto 7.962/2013)",
  },
  D8660: {
    arquivo: "../../data/lei_d8660.json",
    rotulo: "Apostila da Haia (1961) — promulgação (Decreto 8.660/2016)",
  },
  D9039: {
    arquivo: "../../data/lei_d9039.json",
    rotulo: "Haia — Obtenção de Provas no Exterior (1970) — promulgação (Decreto 9.039/2017)",
  },
  D9734: {
    arquivo: "../../data/lei_d9734.json",
    rotulo: "Haia — Citação/Intimação no Exterior (1965) — promulgação (Decreto 9.734/2019)",
  },
  D9936: {
    arquivo: "../../data/lei_d9936.json",
    rotulo: "Decreto 9.936/2019 - Regulamenta Base de Dados para Score de Crédito (Decreto 9.936/2019)",
  },
  DL1598: {
    arquivo: "../../data/lei_dl1598.json",
    rotulo: "IRPJ – Normas Gerais (conceitos e apuração) (Decreto-Lei 1.598/1977)",
  },
  DL167: {
    arquivo: "../../data/lei_dl167.json",
    rotulo: "Cédulas de Crédito Rural (Decreto-Lei 167/1967)",
  },
  DL3365: {
    arquivo: "../../data/lei_dl3365.json",
    rotulo: "Desapropriação por utilidade pública (Decreto-Lei 3.365/1941)",
  },
  DL73: {
    arquivo: "../../data/lei_dl73.json",
    rotulo: "Seguros Privados (Decreto-Lei 73/1966)",
  },
  DL911: {
    arquivo: "../../data/lei_dl911.json",
    rotulo: "Busca e Apreensão Fiduciária (veículos) (Decreto-Lei 911/1969)",
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
  L10185: {
    arquivo: "../../data/lei_l10185.json",
    rotulo: "Seguro Saúde (Lei 10.185/2001)",
  },
  L10233: {
    arquivo: "../../data/lei_l10233.json",
    rotulo: "ANTT/ANTAQ — Reestruturação dos Transportes (Lei 10.233/2001)",
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
  L10820: {
    arquivo: "../../data/lei_l10820.json",
    rotulo: "Consignado (Lei 10.820/2003)",
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
  L10931: {
    arquivo: "../../data/lei_l10931.json",
    rotulo: "Cédula de Crédito Bancário (Lei 10.931/2004)",
  },
  L10962: {
    arquivo: "../../data/lei_l10962.json",
    rotulo: "Exibição de Preços de Produtos e Serviços (Lei 10.962/2004)",
  },
  L11076: {
    arquivo: "../../data/lei_l11076.json",
    rotulo: "Títulos do Agronegócio (LCA/CRA e correlatos) (Lei 11.076/2004)",
  },
  L11079: {
    arquivo: "../../data/lei_l11079.json",
    rotulo: "Parcerias Público-Privadas (PPPs) (Lei 11.079/2004)",
  },
  L11107: {
    arquivo: "../../data/lei_l11107.json",
    rotulo: "Consórcios Públicos (Lei 11.107/2005)",
  },
  L11417: {
    arquivo: "../../data/lei_l11417.json",
    rotulo: "Súmula Vinculante (procedimento e efeitos) (Lei 11.417/2006)",
  },
  L11419: {
    arquivo: "../../data/lei_l11419.json",
    rotulo: "Processo Judicial Eletrônico (PJe) e atos eletrônicos (Lei 11.419/2006)",
  },
  L11441: {
    arquivo: "../../data/lei_l11441.json",
    rotulo: "Inventários Extrajudiciais (Lei 11.441/2007)",
  },
  L11445: {
    arquivo: "../../data/lei_l11445.json",
    rotulo: "Saneamento Básico (marco setorial) (Lei 11.445/2007)",
  },
  L11598: {
    arquivo: "../../data/lei_l11598.json",
    rotulo: "REDESIM (registro e legalização) (Lei 11.598/2007)",
  },
  L11638: {
    arquivo: "../../data/lei_l11638.json",
    rotulo: "Alterações Contábeis (S.A. e grandes empresas) (Lei 11.638/2007)",
  },
  L11770: {
    arquivo: "../../data/lei_l11770.json",
    rotulo: "Programa Empresa Cidadã (licenças) (Lei 11.770/2008)",
  },
  L11788: {
    arquivo: "../../data/lei_l11788.json",
    rotulo: "Lei do Estágio (Lei 11.788/2008)",
  },
  L11795: {
    arquivo: "../../data/lei_l11795.json",
    rotulo: "Consórcios (Lei 11.795/2008)",
  },
  L11804: {
    arquivo: "../../data/lei_l11804.json",
    rotulo: "Alimentos Gravídicos (Lei 11.804/2008)",
  },
  L11977: {
    arquivo: "../../data/lei_l11977.json",
    rotulo: "Minha Casa Minha Vida (Lei 11.977/2009)",
  },
  L12010: {
    arquivo: "../../data/lei_l12010.json",
    rotulo: "Adoção (Lei 12.010/2009)",
  },
  L12030: {
    arquivo: "../../data/lei_l12030.json",
    rotulo: "Perícia Oficial de Natureza Criminal (Lei 12.030/2009)",
  },
  L12037: {
    arquivo: "../../data/lei_l12037.json",
    rotulo: "Identificação Criminal (Lei 12.037/2009)",
  },
  L12153: {
    arquivo: "../../data/lei_l12153.json",
    rotulo: "Juizados da Fazenda Pública (Lei 12.153/2009)",
  },
  L12305: {
    arquivo: "../../data/lei_l12305.json",
    rotulo: "Política Nacional de Resíduos Sólidos (PNRS) (Lei 12.305/2010)",
  },
  L12318: {
    arquivo: "../../data/lei_l12318.json",
    rotulo: "Alienação Parental (Lei 12.318/2010)",
  },
  L12414: {
    arquivo: "../../data/lei_l12414.json",
    rotulo: "SPC/SERASA (Lei 12.414/2011)",
  },
  L12506: {
    arquivo: "../../data/lei_l12506.json",
    rotulo: "Aviso Prévio Proporcional (Lei 12.506/2011)",
  },
  L12529: {
    arquivo: "../../data/lei_l12529.json",
    rotulo: "Defesa da Concorrência (CADE) (Lei 12.529/2011)",
  },
  L12618: {
    arquivo: "../../data/lei_l12618.json",
    rotulo: "Funpresp / Regime de Previdência Complementar do Servidor (Lei 12.618/2012)",
  },
  L12741: {
    arquivo: "../../data/lei_l12741.json",
    rotulo: "Transparência de Tributos na Nota Fiscal (Lei 12.741/2012)",
  },
  L12815: {
    arquivo: "../../data/lei_l12815.json",
    rotulo: "Setor Portuário – Relações de Trabalho (Lei 12.815/2013)",
  },
  L12846: {
    arquivo: "../../data/lei_l12846.json",
    rotulo: "Lei Anticorrupção (responsabilização de pessoas jurídicas) (Lei 12.846/2013)",
  },
  L12850: {
    arquivo: "../../data/lei_l12850.json",
    rotulo: "Organização Criminosa (Lei 12.850/2013)",
  },
  L12865: {
    arquivo: "../../data/lei_l12865.json",
    rotulo: "Arranjos e Instituições de Pagamento (Lei 12.865/2013)",
  },
  L13019: {
    arquivo: "../../data/lei_l13019.json",
    rotulo: "Marco Regulatório das OSCs (MROSC) (Lei 13.019/2014)",
  },
  L13058: {
    arquivo: "../../data/lei_l13058.json",
    rotulo: "Guarda Compartilhada (Lei 13.058/2014)",
  },
  L13103: {
    arquivo: "../../data/lei_l13103.json",
    rotulo: "Motorista Profissional (Lei 13.103/2015)",
  },
  L13116: {
    arquivo: "../../data/lei_l13116.json",
    rotulo: "Marco das Antenas (Lei 13.116/2015)",
  },
  L13140: {
    arquivo: "../../data/lei_l13140.json",
    rotulo: "Lei da Mediação (Lei 13.140/2015)",
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
  L13300: {
    arquivo: "../../data/lei_l13300.json",
    rotulo: "Mandado de Injunção (Lei 13.300/2016)",
  },
  L13303: {
    arquivo: "../../data/lei_l13303.json",
    rotulo: "Estatais (Lei 13.303/2016)",
  },
  L13431: {
    arquivo: "../../data/lei_l13431.json",
    rotulo: "Sistema de Garantia – Escuta e Depoimento Especial (Lei 13.431/2017)",
  },
  L13455: {
    arquivo: "../../data/lei_l13455.json",
    rotulo: "Preço Diferenciado por Forma de Pagamento (Lei 13.455/2017)",
  },
  L13460: {
    arquivo: "../../data/lei_l13460.json",
    rotulo: "Direitos do Usuário do Serviço Público (Lei 13.460/2017)",
  },
  L13465: {
    arquivo: "../../data/lei_l13465.json",
    rotulo: "Regularização Fundiária (Lei 13.465/2017)",
  },
  L13487: {
    arquivo: "../../data/lei_l13487.json",
    rotulo: "Fundo Especial de Financiamento de Campanha (FEFC) (Lei 13.487/2017)",
  },
  L13488: {
    arquivo: "../../data/lei_l13488.json",
    rotulo: "Reforma Eleitoral 2017 (ajustes adicionais) (Lei 13.488/2017)",
  },
  L13726: {
    arquivo: "../../data/lei_l13726.json",
    rotulo: "Desburocratização — Atos e Documentos Públicos (Lei 13.726/2018)",
  },
  L13775: {
    arquivo: "../../data/lei_l13775.json",
    rotulo: "Duplicata Escritural (Lei 13.775/2018)",
  },
  L13777: {
    arquivo: "../../data/lei_l13777.json",
    rotulo: "Multipropriedade (Lei 13.777/2018)",
  },
  L13786: {
    arquivo: "../../data/lei_l13786.json",
    rotulo: "Distrato Imobiliário (Lei 13.786/2018)",
  },
  L13848: {
    arquivo: "../../data/lei_l13848.json",
    rotulo: "Agências Reguladoras (Lei 13.848/2019)",
  },
  L13869: {
    arquivo: "../../data/lei_l13869.json",
    rotulo: "Abuso de Autoridade (Lei 13.869/2019)",
  },
  L13874: {
    arquivo: "../../data/lei_l13874.json",
    rotulo: "Declaração de Direitos de Liberdade Econômica (Lei 13.874/2019)",
  },
  L13966: {
    arquivo: "../../data/lei_l13966.json",
    rotulo: "Franquia Empresarial (Lei de Franquias) (Lei 13.966/2019)",
  },
  L13988: {
    arquivo: "../../data/lei_l13988.json",
    rotulo: "Transação no Contencioso Tributário Federal (Lei 13.988/2020)",
  },
  L14026: {
    arquivo: "../../data/lei_l14026.json",
    rotulo: "Novo Marco do Saneamento (Lei 14.026/2020)",
  },
  L14063: {
    arquivo: "../../data/lei_l14063.json",
    rotulo: "Assinaturas Eletrônicas na Administração Pública (Lei 14.063/2020)",
  },
  L14113: {
    arquivo: "../../data/lei_l14113.json",
    rotulo: "FUNDEB (permanente) (Lei 14.113/2020)",
  },
  L14129: {
    arquivo: "../../data/lei_l14129.json",
    rotulo: "Governo Digital e Eficiência Pública (Lei 14.129/2021)",
  },
  L14181: {
    arquivo: "../../data/lei_l14181.json",
    rotulo: "Superendividamento (Lei 14.181/2021)",
  },
  L14192: {
    arquivo: "../../data/lei_l14192.json",
    rotulo: "Violência Política contra a Mulher (Lei 14.192/2021)",
  },
  L14195: {
    arquivo: "../../data/lei_l14195.json",
    rotulo: "Melhoria do Ambiente de Negócios (extinção EIRELI) (Lei 14.195/2021)",
  },
  L14208: {
    arquivo: "../../data/lei_l14208.json",
    rotulo: "Federações Partidárias (Lei 14.208/2021)",
  },
  L14211: {
    arquivo: "../../data/lei_l14211.json",
    rotulo: "Sobras e Quociente (distribuição de vagas) (Lei 14.211/2021)",
  },
  L14286: {
    arquivo: "../../data/lei_l14286.json",
    rotulo: "Marco Legal do Câmbio (Lei 14.286/2021)",
  },
  L14344: {
    arquivo: "../../data/lei_l14344.json",
    rotulo: "Violência Contra Crianças e Adolescentes (Lei 14.344/2022)",
  },
  L14382: {
    arquivo: "../../data/lei_l14382.json",
    rotulo: "Modernização dos Registros Públicos (SERP) (Lei 14.382/2022)",
  },
  L14430: {
    arquivo: "../../data/lei_l14430.json",
    rotulo: "Marco das Securitizadoras e Securitização (Lei 14.430/2022)",
  },
  L14442: {
    arquivo: "../../data/lei_l14442.json",
    rotulo: "Auxílio‑Alimentação (regras e vedações) (Lei 14.442/2022)",
  },
  L14478: {
    arquivo: "../../data/lei_l14478.json",
    rotulo: "Marco dos Criptoativos (Lei 14.478/2022)",
  },
  L14611: {
    arquivo: "../../data/lei_l14611.json",
    rotulo: "Igualdade Salarial por Gênero (Lei 14.611/2023)",
  },
  L14711: {
    arquivo: "../../data/lei_l14711.json",
    rotulo: "Marco Legal das Garantias (Lei 14.711/2023)",
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
  L4320: {
    arquivo: "../../data/lei_l4320.json",
    rotulo: "Normas Gerais de Direito Financeiro (Lei 4.320/1964)",
  },
  L4591: {
    arquivo: "../../data/lei_l4591.json",
    rotulo: "Incorporação Imobiliária (Lei 4.591/1964)",
  },
  L4595: {
    arquivo: "../../data/lei_l4595.json",
    rotulo: "Sistema Financeiro Nacional (Lei 4.595/1964)",
  },
  L4717: {
    arquivo: "../../data/lei_l4717.json",
    rotulo: "Ação Popular (Lei 4.717/1965)",
  },
  L4728: {
    arquivo: "../../data/lei_l4728.json",
    rotulo: "Mercado de Capitais (Lei 4.728/1965)",
  },
  L4749: {
    arquivo: "../../data/lei_l4749.json",
    rotulo: "Pagamento do 13º salário (prazos e forma) (Lei 4.749/1965)",
  },
  L4886: {
    arquivo: "../../data/lei_l4886.json",
    rotulo: "Representação Comercial (Lei 4.886/1965)",
  },
  L4950A: {
    arquivo: "../../data/lei_l4950a.json",
    rotulo: "Pisos Profissionais (Eng., Arq., Agr., Vet., Quím.) (Lei 4.950-A/1966)",
  },
  L5474: {
    arquivo: "../../data/lei_l5474.json",
    rotulo: "Duplicatas (Lei 5.474/1968)",
  },
  L5478: {
    arquivo: "../../data/lei_l5478.json",
    rotulo: "Alimentos (Lei 5.478/1968)",
  },
  L5584: {
    arquivo: "../../data/lei_l5584.json",
    rotulo: "Normas do Processo do Trabalho (Lei 5.584/1970)",
  },
  L5764: {
    arquivo: "../../data/lei_l5764.json",
    rotulo: "Cooperativismo (Lei 5.764/1971)",
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
  L6099: {
    arquivo: "../../data/lei_l6099.json",
    rotulo: "Arrendamento Mercantil (Leasing) (Lei 6.099/1974)",
  },
  L6321: {
    arquivo: "../../data/lei_l6321.json",
    rotulo: "Programa de Alimentação do Trabalhador (PAT) (Lei 6.321/1976)",
  },
  L6360: {
    arquivo: "../../data/lei_l6360.json",
    rotulo: "Vigilância de Medicamentos (Lei 6.360/1976)",
  },
  L6385: {
    arquivo: "../../data/lei_l6385.json",
    rotulo: "Mercado de Valores Mobiliários (CVM) (Lei 6.385/1976)",
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
  L6729: {
    arquivo: "../../data/lei_l6729.json",
    rotulo: "Concessão Comercial de Veículos (Lei 6.729/1979)",
  },
  L6766: {
    arquivo: "../../data/lei_l6766.json",
    rotulo: "Parcelamento Solo (Lei 6.766/1979)",
  },
  L6858: {
    arquivo: "../../data/lei_l6858.json",
    rotulo: "Pagamento a Dependentes sem Inventário (Lei 6.858/1980)",
  },
  L6938: {
    arquivo: "../../data/lei_l6938.json",
    rotulo: "Política Nacional do Meio Ambiente (PNMA) (Lei 6.938/1981)",
  },
  L6996: {
    arquivo: "../../data/lei_l6996.json",
    rotulo: "Apoio Logístico Postal a Alistamento e Eleições (Lei 6.996/1982)",
  },
  L7064: {
    arquivo: "../../data/lei_l7064.json",
    rotulo: "Trabalho no Exterior (brasileiros) (Lei 7.064/1982)",
  },
  L7357: {
    arquivo: "../../data/lei_l7357.json",
    rotulo: "Cheque (Lei 7.357/1985)",
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
  L8038: {
    arquivo: "../../data/lei_l8038.json",
    rotulo: "Procedimentos no STF e STJ (ações originárias/recursos) (Lei 8.038/1990)",
  },
  L8072: {
    arquivo: "../../data/lei_l8072.json",
    rotulo: "Crimes Hediondos (Lei 8.072/1990)",
  },
  L8080: {
    arquivo: "../../data/lei_l8080.json",
    rotulo: "Lei Orgânica da Saúde (SUS) (Lei 8.080/1990)",
  },
  L8112: {
    arquivo: "../../data/lei_l8112.json",
    rotulo: "Regime Jurídico dos Servidores Federais (RJU) (Lei 8.112/1990)",
  },
  L8137: {
    arquivo: "../../data/lei_l8137.json",
    rotulo: "Crimes contra Ordem Tributária (Lei 8.137/1990)",
  },
  L8142: {
    arquivo: "../../data/lei_l8142.json",
    rotulo: "Participação da Comunidade no SUS (Lei 8.142/1990)",
  },
  L8212: {
    arquivo: "../../data/lei_l8212.json",
    rotulo: "Plano de Custeio da Seguridade Social (Lei 8.212/1991)",
  },
  L8245: {
    arquivo: "../../data/lei_l8245.json",
    rotulo: "Inquilinato (Lei 8.245/1991)",
  },
  L8437: {
    arquivo: "../../data/lei_l8437.json",
    rotulo: "Suspensão de Liminar e Sentença (Fazenda Pública) (Lei 8.437/1992)",
  },
  L8560: {
    arquivo: "../../data/lei_l8560.json",
    rotulo: "Investigação de Paternidade (filho havido fora do casamento) (Lei 8.560/1992)",
  },
  L8629: {
    arquivo: "../../data/lei_l8629.json",
    rotulo: "Reforma Agrária (Lei 8.629/1993)",
  },
  L8929: {
    arquivo: "../../data/lei_l8929.json",
    rotulo: "Cédula de Produto Rural (CPR) (Lei 8.929/1994)",
  },
  L8934: {
    arquivo: "../../data/lei_l8934.json",
    rotulo: "Registro Público de Empresas Mercantis (Lei 8.934/1994)",
  },
  L8935: {
    arquivo: "../../data/lei_l8935.json",
    rotulo: "Cartórios (Lei 8.935/1994)",
  },
  L8971: {
    arquivo: "../../data/lei_l8971.json",
    rotulo: "Companheiros Alimentos e Sucessão (Lei 8.971/1994)",
  },
  L8987: {
    arquivo: "../../data/lei_l8987.json",
    rotulo: "Concessões e Permissões de Serviços Públicos (Lei 8.987/1995)",
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
  L9279: {
    arquivo: "../../data/lei_l9279.json",
    rotulo: "Propriedade Industrial (Lei 9.279/1996)",
  },
  L9289: {
    arquivo: "../../data/lei_l9289.json",
    rotulo: "Custas na Justiça Federal (Lei 9.289/1996)",
  },
  L9296: {
    arquivo: "../../data/lei_l9296.json",
    rotulo: "Interceptação Telefônica (Lei 9.296/1996)",
  },
  L9307: {
    arquivo: "../../data/lei_l9307.json",
    rotulo: "Arbitragem (Lei 9.307/1996)",
  },
  L9427: {
    arquivo: "../../data/lei_l9427.json",
    rotulo: "Agência Nacional de Energia Elétrica (ANEEL) (Lei 9.427/1996)",
  },
  L9430: {
    arquivo: "../../data/lei_l9430.json",
    rotulo: "Legislação Tributária Federal (IRPJ, compensação etc.) (Lei 9.430/1996)",
  },
  L9434: {
    arquivo: "../../data/lei_l9434.json",
    rotulo: "Transplantes (Lei 9.434/1997)",
  },
  L9455: {
    arquivo: "../../data/lei_l9455.json",
    rotulo: "Tortura (Lei 9.455/1997)",
  },
  L9478: {
    arquivo: "../../data/lei_l9478.json",
    rotulo: "Petróleo (Lei 9.478/1997)",
  },
  L9492: {
    arquivo: "../../data/lei_l9492.json",
    rotulo: "Protesto de Títulos (Lei 9.492/1997)",
  },
  L9494: {
    arquivo: "../../data/lei_l9494.json",
    rotulo: "Efeitos Processuais contra a Fazenda Pública (Lei 9.494/1997)",
  },
  L9504: {
    arquivo: "../../data/lei_l9504.json",
    rotulo: "Lei das Eleições (Lei 9.504/1997)",
  },
  L9507: {
    arquivo: "../../data/lei_l9507.json",
    rotulo: "Habeas Data (Lei 9.507/1997)",
  },
  L9514: {
    arquivo: "../../data/lei_l9514.json",
    rotulo: "Alienação Fiduciária de Imóveis (SFI) (Lei 9.514/1997)",
  },
  L9537: {
    arquivo: "../../data/lei_l9537.json",
    rotulo: "Segurança do Tráfego Aquaviário (Lei 9.537/1997)",
  },
  L9601: {
    arquivo: "../../data/lei_l9601.json",
    rotulo: "Contrato por Prazo Determinado (via ACT/CCT) (Lei 9.601/1998)",
  },
  L9605: {
    arquivo: "../../data/lei_l9605.json",
    rotulo: "Crimes Ambientais (Lei 9.605/1998)",
  },
  L9609: {
    arquivo: "../../data/lei_l9609.json",
    rotulo: "Propriedade Intelecutal sobre Software (programa de computador) (Lei 9.609/1998)",
  },
  L9610: {
    arquivo: "../../data/lei_l9610.json",
    rotulo: "Direitos Autorais (Lei 9.610/1998)",
  },
  L9613: {
    arquivo: "../../data/lei_l9613.json",
    rotulo: "Lavagem de Dinheiro (Lei 9.613/1998)",
  },
  L9656: {
    arquivo: "../../data/lei_l9656.json",
    rotulo: "Planos e Seguros Privados de Assistência à Saúde (Lei 9.656/1998)",
  },
  L9709: {
    arquivo: "../../data/lei_l9709.json",
    rotulo: "Plebiscito, Referendo e Iniciativa Popular (Lei 9.709/1998)",
  },
  L9717: {
    arquivo: "../../data/lei_l9717.json",
    rotulo: "Normas Gerais dos RPPS (Lei 9.717/1998)",
  },
  L9782: {
    arquivo: "../../data/lei_l9782.json",
    rotulo: "ANVISA — Sistema Nacional de Vigilância Sanitária (Lei 9.782/1999)",
  },
  L9784: {
    arquivo: "../../data/lei_l9784.json",
    rotulo: "Processo Administrativo Federal (PAF) (Lei 9.784/1999)",
  },
  L9787: {
    arquivo: "../../data/lei_l9787.json",
    rotulo: "Genéricos (Lei 9.787/1999)",
  },
  L9790: {
    arquivo: "../../data/lei_l9790.json",
    rotulo: "OSCIPs (Lei 9.790/1999)",
  },
  L9796: {
    arquivo: "../../data/lei_l9796.json",
    rotulo: "Compensação Financeira RGPS × RPPS (COMPREV) (Lei 9.796/1999)",
  },
  L9807: {
    arquivo: "../../data/lei_l9807.json",
    rotulo: "Proteção Testemunhas (Lei 9.807/1999)",
  },
  L9868: {
    arquivo: "../../data/lei_l9868.json",
    rotulo: "ADI e ADC no STF (processo e julgamento) (Lei 9.868/1999)",
  },
  L9882: {
    arquivo: "../../data/lei_l9882.json",
    rotulo: "ADPF no STF (processo e julgamento) (Lei 9.882/1999)",
  },
  L9961: {
    arquivo: "../../data/lei_l9961.json",
    rotulo: "Agência Nacional de Saúde (ANS) (Lei 9.961/2000)",
  },
  L9985: {
    arquivo: "../../data/lei_l9985.json",
    rotulo: "Sistema Nacional de Unidades de Conservação (SNUC) (Lei 9.985/2000)",
  },
  L9986: {
    arquivo: "../../data/lei_l9986.json",
    rotulo: "Gestão de RH das Agências Reguladoras (Lei 9.986/2000)",
  },
  LACP: {
    arquivo: "../../data/lei_lacp.json",
    rotulo: "Ação Civil Pública (ACP) (Lei 7.347/1985)",
  },
  LAI: {
    arquivo: "../../data/lei_lai.json",
    rotulo: "Acesso à Informação (LAI) (Lei 12.527/2011)",
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
  LC182: {
    arquivo: "../../data/lei_lc182.json",
    rotulo: "Marco Legal das Startups (Lei Complementar 182/2021)",
  },
  LC64: {
    arquivo: "../../data/lei_lc64.json",
    rotulo: "Inelegibilidades (Lei Complementar das Inelegibilidades) (Lei Complementar 64/1990)",
  },
  LC80: {
    arquivo: "../../data/lei_lc80.json",
    rotulo: "Organização da Defensoria Pública (LC 80) (Lei Complementar 80/1994)",
  },
  LC87: {
    arquivo: "../../data/lei_lc87.json",
    rotulo: "ICMS – Normas Gerais (Lei Kandir) (Lei Complementar 87/1996)",
  },
  LCP: {
    arquivo: "../../data/lei_lcp.json",
    rotulo: "Contravenções Penais (Decreto-Lei 3.688/1941)",
  },
  LDB: {
    arquivo: "../../data/lei_ldb.json",
    rotulo: "LDB — Lei de Diretrizes e Bases da Educação (Lei 9.394/1996)",
  },
  LEF: {
    arquivo: "../../data/lei_lef.json",
    rotulo: "Execução Fiscal (LEF) (Lei 6.830/1980)",
  },
  LGT: {
    arquivo: "../../data/lei_lgt.json",
    rotulo: "Lei Geral de Telecomunicações (LGT) (Lei 9.472/1997)",
  },
  LIA: {
    arquivo: "../../data/lei_lia.json",
    rotulo: "Improbidade Administrativa (Lei 8.429/1992)",
  },
  LJE: {
    arquivo: "../../data/lei_lje.json",
    rotulo: "Juizados Especiais (Lei 9.099/1995)",
  },
  LMIG: {
    arquivo: "../../data/lei_lmig.json",
    rotulo: "Lei de Migração (Lei 13.445/2017)",
  },
  LMS: {
    arquivo: "../../data/lei_lms.json",
    rotulo: "Mandado de Segurança (Lei 12.016/2009)",
  },
  LOAS: {
    arquivo: "../../data/lei_loas.json",
    rotulo: "Lei Orgânica da Assistência Social (LOAS) (Lei 8.742/1993)",
  },
  LREF: {
    arquivo: "../../data/lei_lref.json",
    rotulo: "Recuperação e Falência (Lei 11.101/2005)",
  },
  LRF: {
    arquivo: "../../data/lei_lrf.json",
    rotulo: "Responsabilidade Fiscal (LRF) (Lei Complementar 101/2000)",
  },
  LRP: {
    arquivo: "../../data/lei_lrp.json",
    rotulo: "Registros Públicos (Lei 6.015/1973)",
  },
  LSA: {
    arquivo: "../../data/lei_lsa.json",
    rotulo: "Lei das S.A. (Lei 6.404/1976)",
  },
  MCI: {
    arquivo: "../../data/lei_mci.json",
    rotulo: "Marco Civil da Internet (Lei 12.965/2014)",
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

const cacheIndices = new Map<CodigoCodigo, IndiceGeradoJSON | null>();

export function carregarIndiceGerado(
  codigo: CodigoCodigo,
): IndiceGeradoJSON | null {
  const memo = cacheIndices.get(codigo);
  if (memo !== undefined) return memo;
  const arquivo = REGISTRO_CODIGOS[codigo].arquivo.replace(
    /^\.\.\/\.\.\/data\/(lei_.+)\.json$/,
    "../../data/indices/$1_keywords.json",
  );
  let indice: IndiceGeradoJSON | null = null;
  try {
    indice = require(arquivo) as IndiceGeradoJSON;
  } catch {
    // Sem índice derivado o diploma cai na busca em texto integral (fallback
    // correto, apenas mais lento); a auditoria e os testes acusam a ausência.
    indice = null;
  }
  cacheIndices.set(codigo, indice);
  return indice;
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
    const curado = data.indexes?.keywords;
    const gerado = carregarIndiceGerado(cod);

    if (curado || gerado) {
      const scores = new Map<string, number>();

      if (curado) {
        // Índice curado preservado: esquema legado de pontuação, estrutural
        // para o ranking do núcleo (não substituir sem passar pela avaliação).
        for (const word of words) {
          (curado[word] ?? []).forEach((numero) => {
            const key = String(numero);
            scores.set(key, (scores.get(key) ?? 0) + 2);
          });
          // Match parcial
          for (const [indexWord, numeros] of Object.entries(curado)) {
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
      }

      if (gerado) {
        // Índice gerado (BASE-019): reproduz a busca em texto integral sobre
        // os tokens dos dispositivos que o índice curado não cobre — uma
        // palavra casa quando aparece dentro da string de tokens (nunca cruza
        // um espaço), conta no máximo uma vez por dispositivo e o piso de 40%
        // é o mesmo do fallback. As entradas seguem a ordem do documento, e a
        // ordenação final estável resolve empates pela posição do artigo,
        // como no texto integral. A escala ×3 equipara uma palavra casada ao
        // caso típico do índice curado (casamento exato +2 somado ao próprio
        // prefixo +1); num diploma sem índice curado o fator é monotônico e
        // não altera o ranking interno.
        const minMatches = Math.max(1, Math.ceil(words.length * 0.4));
        for (const [numero, tokens] of Object.entries(gerado.tokens)) {
          let casadas = 0;
          for (const word of words) {
            if (tokens.includes(word)) casadas += 1;
          }
          if (casadas >= minMatches) {
            scores.set(numero, (scores.get(numero) ?? 0) + casadas * 3);
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
