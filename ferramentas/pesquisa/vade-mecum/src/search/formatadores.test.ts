import { describe, expect, test } from "bun:test";

import { buscarTeses, formatTese } from "./jt.js";
import { buscarArtigo, formatArtigo } from "./legislacao.js";
import { buscarSumulas, formatSumula, type Tribunal } from "./sumulas.js";
import {
  descreverEfeitoSumula,
  descreverEfeitoTema,
  descreverEfeitoTemaRG,
  FONTE_OFICIAL,
  NATUREZAS_DOCUMENTAIS,
} from "./taxonomia.js";
import { buscarTemas, formatTema } from "./temas.js";
import { buscarTemasRG, formatTemaRG } from "./temas_rg_stf.js";
import { buscarInformativos, formatInformativo } from "./informativo_stf.js";
import { buscarEspelhos, formatEspelho } from "./espelhos_stj.js";

describe("rastreabilidade dos formatadores", () => {
  test("inclui a fonte oficial da legislação", () => {
    const artigo = buscarArtigo("CF", "1");
    expect(artigo).toBeDefined();
    expect(artigo!.url).toBeTruthy();
    expect(formatArtigo("CF", artigo!)).toContain(artigo!.url);
  });

  for (const tribunal of ["STJ", "STF", "vinculante"] as const satisfies readonly Tribunal[]) {
    test(`inclui a fonte oficial da súmula ${tribunal}`, () => {
      const resultado = buscarSumulas("1", tribunal, 1)[0];
      expect(resultado).toBeDefined();

      const url = resultado.sumula.url;
      expect(url).toBeTruthy();
      expect(formatSumula(resultado)).toContain(url!);
    });
  }

  test("inclui a fonte oficial da Jurisprudência em Teses", () => {
    const tese = buscarTeses("edição 1", 1)[0];
    expect(tese).toBeDefined();
    expect(tese.url).toBeTruthy();
    expect(formatTese(tese)).toContain(tese.url);
  });

  test("inclui todos os links oficiais disponíveis do tema repetitivo", () => {
    const tema = buscarTemas("tema 1", 1)[0];
    expect(tema).toBeDefined();

    const links = Object.values(tema.links).filter(
      (url): url is string => Boolean(url),
    );
    expect(links.length).toBeGreaterThan(0);

    const formatado = formatTema(tema);
    for (const url of links) expect(formatado).toContain(url);
  });

  test("inclui todos os links oficiais disponíveis do tema de repercussão geral", () => {
    const tema = buscarTemasRG("tema 69", 1)[0];
    expect(tema).toBeDefined();

    const links = Object.values(tema.links).filter(
      (url): url is string => Boolean(url),
    );
    expect(links.length).toBeGreaterThan(0);

    const formatado = formatTemaRG(tema);
    for (const url of links) expect(formatado).toContain(url);
    expect(formatado).toContain(FONTE_OFICIAL);
    expect(formatado).toContain(
      NATUREZAS_DOCUMENTAIS.registroPrecedenteQualificado,
    );
  });

  test("inclui o link oficial da edição do Informativo STF", () => {
    const item = buscarInformativos("informativo 1222", 1)[0];
    expect(item).toBeDefined();
    expect(item.links.edicao).toBeTruthy();

    const formatado = formatInformativo(item);
    expect(formatado).toContain(item.links.edicao!);
    expect(formatado).toContain(FONTE_OFICIAL);
    expect(formatado).toContain(NATUREZAS_DOCUMENTAIS.compilacaoInstitucional);
    expect(formatado).toContain("NÃO VINCULANTE POR SI SÓ");
  });

  test("inclui os links oficiais disponíveis do espelho de acórdão", () => {
    const item = buscarEspelhos("honorários apreciação equitativa", 1)[0];
    expect(item).toBeDefined();

    const links = Object.values(item.links).filter(
      (url): url is string => Boolean(url),
    );
    expect(links.length).toBeGreaterThan(0);

    const formatado = formatEspelho(item);
    for (const url of links) expect(formatado).toContain(url);
    expect(formatado).toContain(FONTE_OFICIAL);
    expect(formatado).toContain(NATUREZAS_DOCUMENTAIS.espelhoDeAcordao);
    expect(formatado).toContain("NÃO VINCULANTE POR SI SÓ");
  });
});

describe("taxonomia documental e de efeito jurídico", () => {
  test("separa texto normativo, enunciado sumular e compilação institucional", () => {
    const artigo = buscarArtigo("CF", "1");
    const sumula = buscarSumulas("1", "STJ", 1)[0];
    const tese = buscarTeses("edição 1", 1)[0];

    expect(formatArtigo("CF", artigo!)).toContain(
      NATUREZAS_DOCUMENTAIS.textoNormativo,
    );
    expect(formatSumula(sumula)).toContain(
      NATUREZAS_DOCUMENTAIS.enunciadoSumular,
    );
    expect(formatTese(tese)).toContain(
      NATUREZAS_DOCUMENTAIS.compilacaoInstitucional,
    );
  });

  test("identifica proveniência oficial sem chamá-la de fonte primária", () => {
    const saidas = [
      formatArtigo("CF", buscarArtigo("CF", "1")!),
      formatSumula(buscarSumulas("1", "STF", 1)[0]),
      formatTese(buscarTeses("edição 1", 1)[0]),
      formatTema(buscarTemas("tema 1", 1)[0]),
    ];

    for (const saida of saidas) {
      expect(saida).toContain(FONTE_OFICIAL);
      expect(saida).not.toContain("FONTE PRIMÁRIA");
      expect(saida).not.toContain("**Força:**");
    }
  });

  test("classifica o efeito do tema conforme estado e presença de tese", () => {
    expect(descreverEfeitoTema("Cancelado", "tese anterior")).toStartWith(
      "TEMA CANCELADO",
    );
    expect(
      descreverEfeitoTema("Afetado - Possível Revisão de Tese", "tese anterior"),
    ).toStartWith("TESE EM POSSÍVEL REVISÃO");
    expect(descreverEfeitoTema("Afetado")).toStartWith(
      "SEM TESE FIRMADA NESTE SNAPSHOT",
    );
    expect(descreverEfeitoTema("Trânsito em Julgado", "tese firmada")).toStartWith(
      "OBSERVÂNCIA OBRIGATÓRIA QUANDO APLICÁVEL",
    );
    expect(descreverEfeitoTema("Sobrestado", "tese anterior")).toStartWith(
      "SITUAÇÃO EXIGE CONFERÊNCIA",
    );
  });

  test("classifica o efeito do tema de repercussão geral conforme estado e tese", () => {
    expect(descreverEfeitoTemaRG("Cancelado", "tese anterior")).toStartWith(
      "TEMA CANCELADO",
    );
    expect(descreverEfeitoTemaRG("Trânsito em Julgado")).toStartWith(
      "SEM TESE FIRMADA NESTE SNAPSHOT",
    );
    expect(
      descreverEfeitoTemaRG("Trânsito em Julgado", "tese firmada"),
    ).toStartWith("OBSERVÂNCIA OBRIGATÓRIA QUANDO APLICÁVEL");
    expect(
      descreverEfeitoTemaRG("Acórdão de mérito publicado", "tese firmada"),
    ).toStartWith("OBSERVÂNCIA OBRIGATÓRIA QUANDO APLICÁVEL");
    expect(
      descreverEfeitoTemaRG("Acórdão de Repercussão Geral publicado", "tese firmada"),
    ).toStartWith("SITUAÇÃO EXIGE CONFERÊNCIA");
    expect(descreverEfeitoTemaRG("Em julgamento", "tese firmada")).toStartWith(
      "SITUAÇÃO EXIGE CONFERÊNCIA",
    );
  });

  test("não atribui efeito vigente a súmula com estado não ativo", () => {
    expect(descreverEfeitoSumula(true, "aprovada")).toStartWith("VINCULANTE");
    expect(descreverEfeitoSumula(true, "cancelada")).toStartWith("CANCELADA");
    expect(descreverEfeitoSumula(false, "ativa")).toStartWith(
      "NÃO VINCULANTE POR SI SÓ",
    );
    expect(descreverEfeitoSumula(false, "superada")).toStartWith("SUPERADA");
    expect(descreverEfeitoSumula(false, "alterada")).toStartWith("ALTERADA");
  });

  test("tema cancelado sem tese não é descrito como pendente", () => {
    const cancelado = formatTema(buscarTemas("tema 56", 1)[0]);
    expect(cancelado).toContain("TEMA CANCELADO");
    expect(cancelado).toContain("não registrada neste snapshot");
    expect(cancelado).not.toContain("Pendente de julgamento");
  });
});
