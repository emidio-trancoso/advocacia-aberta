export const NATUREZAS_DOCUMENTAIS = Object.freeze({
  textoNormativo: "TEXTO NORMATIVO",
  enunciadoSumular: "ENUNCIADO SUMULAR",
  compilacaoInstitucional: "COMPILAÇÃO INSTITUCIONAL",
  registroPrecedenteQualificado: "REGISTRO DE PRECEDENTE QUALIFICADO",
  espelhoDeAcordao: "ESPELHO DE ACÓRDÃO",
  indiceDerivado: "ÍNDICE DERIVADO",
});

export const FONTE_OFICIAL = "FONTE OFICIAL";

function normalizarSituacao(situacao: string): string {
  return situacao
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

export function descreverEfeitoSumula(
  vinculante: boolean,
  status: string,
): string {
  const normalizado = normalizarSituacao(status);
  const estadosNaoAtivos: Record<string, string> = {
    cancelada: "CANCELADA — não tratar como enunciado vigente; confira o histórico oficial",
    cancelado: "CANCELADA — não tratar como enunciado vigente; confira o histórico oficial",
    superada: "SUPERADA — não tratar como orientação atual; confira a jurisprudência posterior",
    suspensa: "SUSPENSA — não tratar como aplicável sem conferir a situação atual",
    inativa: "INATIVA — não tratar como orientação atual; confira a situação oficial",
    alterada: "ALTERADA — confira a redação e a situação atuais na fonte oficial",
  };
  const efeitoEstado = estadosNaoAtivos[normalizado];
  if (efeitoEstado) return efeitoEstado;

  return vinculante
    ? "VINCULANTE — alcança Judiciário e Administração Pública nos termos do art. 103-A da CF"
    : "NÃO VINCULANTE POR SI SÓ — enunciado sumular; confira vigência e aplicabilidade";
}

export function descreverEfeitoTema(
  situacao: string,
  teseFirmada?: string,
): string {
  const normalizada = normalizarSituacao(situacao);

  if (normalizada.includes("cancelado")) {
    return "TEMA CANCELADO — não tratar como tese vigente; confira o histórico oficial";
  }

  if (normalizada.includes("possivel revisao")) {
    return "TESE EM POSSÍVEL REVISÃO — confira a situação e os acórdãos antes de aplicar";
  }

  if (!teseFirmada?.trim()) {
    return "SEM TESE FIRMADA NESTE SNAPSHOT — não atribuir efeito obrigatório ao tema";
  }

  const situacoesComTesePublicada = [
    "transito em julgado",
    "acordao publicado",
    "acordao publicado - re pendente",
    "revisado",
  ];
  if (situacoesComTesePublicada.includes(normalizada)) {
    return "OBSERVÂNCIA OBRIGATÓRIA QUANDO APLICÁVEL — tese de recurso repetitivo (art. 927, III, CPC); confira o acórdão e a situação atual";
  }

  return "SITUAÇÃO EXIGE CONFERÊNCIA — há tese no snapshot, mas o estado do tema não autoriza presumir estabilidade";
}

export function descreverEfeitoTemaRG(situacao: string, tese?: string): string {
  const normalizada = normalizarSituacao(situacao);

  if (normalizada.includes("cancelado")) {
    return "TEMA CANCELADO — não tratar como tese vigente; confira o histórico oficial";
  }

  if (!tese?.trim()) {
    return "SEM TESE FIRMADA NESTE SNAPSHOT — não atribuir efeito obrigatório ao tema";
  }

  // Repercussão geral só produz observância obrigatória quando o mérito foi
  // julgado; "Acórdão de Repercussão Geral publicado" e estados preliminares
  // indicam reconhecimento da RG, não necessariamente decisão de mérito.
  const situacoesMeritoDecidido = [
    "transito em julgado",
    "acordao de merito publicado",
    "merito julgado",
  ];
  if (situacoesMeritoDecidido.includes(normalizada)) {
    return "OBSERVÂNCIA OBRIGATÓRIA QUANDO APLICÁVEL — tese de repercussão geral com mérito julgado (art. 927, III, do CPC); confira o acórdão e a situação atual";
  }

  return "SITUAÇÃO EXIGE CONFERÊNCIA — há tese no snapshot, mas o estado do tema não autoriza presumir estabilidade";
}
