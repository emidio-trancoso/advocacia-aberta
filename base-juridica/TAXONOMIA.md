# Taxonomia documental e de efeito jurídico

Esta taxonomia separa três perguntas que não devem ser respondidas pelo mesmo rótulo:

1. **o que é o registro** — sua natureza documental;
2. **de onde veio** — sua proveniência;
3. **qual efeito pode produzir** — sua relevância jurídica no estado consultado.

“Fonte oficial” descreve proveniência. Não significa, por si só, que o material seja
texto normativo, precedente ou vinculante. Da mesma forma, um índice criado para busca
não se torna fonte jurídica porque aponta para documentos oficiais.

## Natureza documental

| Rótulo | Uso no repositório | O que não significa |
|---|---|---|
| `TEXTO NORMATIVO` | dispositivo extraído de Constituição, lei ou decreto-lei | confirmação automática de vigência ou aplicabilidade ao caso |
| `ENUNCIADO SUMULAR` | síntese jurisprudencial aprovada por tribunal | vinculação automática; somente a súmula vinculante recebe esse efeito constitucional |
| `PRECEDENTE` | decisão judicial da qual se extrai uma razão determinante | qualquer resumo, ficha ou resultado de busca |
| `REGISTRO DE PRECEDENTE QUALIFICADO` | ficha de tema repetitivo com situação, questão, tese e links | o inteiro teor do acórdão ou tese obrigatória já estabilizada em todo estado possível |
| `ESPELHO DE ACÓRDÃO` | ficha de acórdão selecionado pela Secretaria de Jurisprudência do STJ, com ementa, tese, referências e links | vinculação automática; um acórdão isolado não vincula por si só |
| `COMPILAÇÃO INSTITUCIONAL` | publicação produzida por órgão oficial a partir de julgados, como Jurisprudência em Teses | decisão judicial autônoma ou efeito vinculante próprio |
| `ÍNDICE DERIVADO` | palavras-chave, termos e relações produzidos para recuperação | fonte jurídica ou fundamento autônomo |

## Proveniência

`FONTE OFICIAL` indica que o texto, registro ou compilação foi publicado pelo órgão
competente ou pela instituição que o produziu. Esse rótulo acompanha a URL consultável
e não substitui a natureza documental.

No acervo atual:

- legislação aponta para textos compilados no Planalto;
- súmulas e Jurisprudência em Teses apontam para STF ou STJ;
- temas repetitivos apontam para páginas, consultas e dados oficiais do STJ;
- índices derivados são identificados separadamente e não recebem força jurídica.

## Efeito jurídico

| Rótulo de saída | Regra aplicada |
|---|---|
| `VINCULANTE` | reservado às súmulas vinculantes, nos termos do art. 103-A da Constituição |
| `OBSERVÂNCIA OBRIGATÓRIA QUANDO APLICÁVEL` | tese firmada em recurso repetitivo com estado compatível, nos termos do art. 927, III, do CPC; exige exame do acórdão, da situação atual e do caso |
| `NÃO VINCULANTE POR SI SÓ` | súmula comum ou compilação institucional; os julgados subjacentes podem ter relevância própria |
| `A CONFIRMAR` | texto normativo cuja vigência, redação e aplicabilidade devem ser verificadas na fonte oficial |
| `CANCELADA`, `SUPERADA`, `SUSPENSA`, `INATIVA` ou `ALTERADA` | estado não ativo ou modificado de enunciado sumular; impede que o motor presuma vigência |
| `SEM TESE FIRMADA NESTE SNAPSHOT` | tema cujo registro local não contém tese; não se presume efeito obrigatório |
| `TEMA CANCELADO` | tema cancelado; não se apresenta a tese como vigente |
| `TESE EM POSSÍVEL REVISÃO` | estado que exige conferência da tramitação e dos acórdãos antes do uso |
| `SITUAÇÃO EXIGE CONFERÊNCIA` | há tese no registro, mas o estado não autoriza o motor a presumir estabilidade |

Para texto normativo, o motor não tenta resolver vigência, hierarquia, incidência ou
conflito de normas. Ele apresenta o dispositivo e exige confirmação da redação e da
aplicabilidade no link oficial.

## Aplicação por família

| Família | Natureza | Proveniência | Efeito mostrado |
|---|---|---|---|
| Legislação | `TEXTO NORMATIVO` | `FONTE OFICIAL` — compilação do Planalto | confirmação necessária |
| Súmula vinculante aprovada e vigente | `ENUNCIADO SUMULAR` | `FONTE OFICIAL` — STF | `VINCULANTE` |
| Súmula comum STF/STJ | `ENUNCIADO SUMULAR` | `FONTE OFICIAL` — tribunal | `NÃO VINCULANTE POR SI SÓ` |
| Jurisprudência em Teses | `COMPILAÇÃO INSTITUCIONAL` | `FONTE OFICIAL` — STJ | `NÃO VINCULANTE POR SI SÓ` |
| Informativo STF | `COMPILAÇÃO INSTITUCIONAL` | `FONTE OFICIAL` — STF | `NÃO VINCULANTE POR SI SÓ` |
| Tema repetitivo | `REGISTRO DE PRECEDENTE QUALIFICADO` | `FONTE OFICIAL` — STJ | derivado da situação e da presença de tese |
| Tema de repercussão geral (STF) | `REGISTRO DE PRECEDENTE QUALIFICADO` | `FONTE OFICIAL` — STF | derivado da situação e da presença de tese; observância obrigatória (art. 927, III, do CPC) quando o mérito foi julgado |
| Espelho de acórdão (STJ) | `ESPELHO DE ACÓRDÃO` | `FONTE OFICIAL` — STJ | `NÃO VINCULANTE POR SI SÓ`; confira eventual tese qualificada |
| Keywords e termos | `ÍNDICE DERIVADO` | processo registrado no manifesto | nenhum |

## Referências oficiais e verificação

Taxonomia verificada em 17 de julho de 2026 com base em:

- [Constituição Federal, art. 103-A](https://www.planalto.gov.br/ccivil_03/constituicao/constituicaocompilado.htm);
- [Código de Processo Civil, art. 927, III](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105compilada.htm);
- [STJ — o que é Jurisprudência em Teses](https://centraldeajuda.stj.jus.br/faq/o-que-e-jurisprudencia-em-teses/);
- [STJ — recursos e temas repetitivos](https://www.stj.jus.br/sites/portalp/Processos/Repetitivos-e-IACs/Saiba-mais/Sobre-Recursos-Repetitivos).

Os rótulos ajudam a evitar inferências indevidas, mas não dispensam consulta ao
inteiro teor, atualização da fonte e revisão profissional.
