# Catálogo da base jurídica

| Campo | Valor |
|---|---|
| Auditoria estrutural | 17 de julho de 2026 |
| Local atual dos dados | `ferramentas/pesquisa/busca_delfus/data/` |
| Escopo | inventário, metadados, cobertura do motor e rastreabilidade interna |

Este catálogo descreve o que o repositório contém. Ele **não confirma externamente**
a vigência, a completude ou a correspondência de cada registro com a fonte oficial na
data de uso.

## Como repetir a auditoria

```bash
python3 ferramentas/manutencao/auditar_base_juridica.py
```

Para obter os dados estruturados:

```bash
python3 ferramentas/manutencao/auditar_base_juridica.py --json
```

## Visão geral

| Acervo | Arquivos principais | Quantidade observada | Tamanho ou cobertura |
|---|---:|---:|---|
| Legislação | 11 | 6.803 registros | 11 diplomas |
| Súmulas | 3 | 1.475 registros | STJ, STF e vinculantes do STF |
| Jurisprudência em Teses | 1 | 3.371 teses | 269 edições do STJ |
| Temas repetitivos | 1 | 1.405 temas | STJ |
| Índices auxiliares | 2 exclusivos + índices embutidos | derivados | palavras-chave e termos de busca |
| Total em JSON | 18 | — | 20.720.739 bytes, cerca de 20 MB |

Os números acima foram contados diretamente nos JSONs. `gerado_em` e `generatedAt`
indicam geração do arquivo, não garantem a data de vigência do conteúdo.

## Legislação

Todos os 6.803 registros legislativos possuem URL individual. Os metadados apontam
para páginas compiladas do Planalto.

| Código | Diploma | Gerado em | Registros | Índice | Situação estrutural |
|---|---|---:|---:|---|---|
| `ADCT` | Ato das Disposições Constitucionais Transitórias | 2026-01-20 | 148 | pré-computado | coerente |
| `CC` | Código Civil — Lei 10.406/2002 | 2026-01-21 | 2.028 | pré-computado | coerente |
| `CDC` | Código de Defesa do Consumidor — Lei 8.078/1990 | 2026-01-30 | 131 | palavras-chave por registro | coerente |
| `CE` | Código Eleitoral — Lei 4.737/1965 | 2026-01-30 | 382 | palavras-chave por registro | coerente |
| `CF` | Constituição Federal de 1988 | 2026-01-20 | 276 | pré-computado | coerente |
| `CLT` | Consolidação das Leis do Trabalho | 2026-01-21 | 920 | pré-computado | coerente; 804 registros têm palavras-chave próprias |
| `CP` | Código Penal — Decreto-Lei 2.848/1940 | 2026-01-20 | 430 | pré-computado | coerente |
| `CPC` | Código de Processo Civil — Lei 13.105/2015 | 2026-01-20 | 1.072 | pré-computado | coerente |
| `CPP` | Código de Processo Penal — Decreto-Lei 3.689/1941 | 2026-01-20 | 822 | pré-computado | coerente |
| `CTB` | Código de Trânsito Brasileiro — Lei 9.503/1997 | 2026-01-30; correção pontual em 2026-07-17 | 390 | 389 com palavras-chave; art. 326-C sem índice derivado | coerente |
| `CTN` | Código Tributário Nacional — Lei 5.172/1966 | 2026-01-30 | 204 | pré-computado | coerente |

A soma dos metadados e a contagem real são 6.803. O `BASE-005` incluiu pontualmente o
art. 326-C do CTB, acrescentado pela Lei nº 15.452/2026. O restante do candidato
integral de julho não foi promovido sem revisão das diferenças.

### Cobertura real do motor legislativo

| Superfície | Cobertura observada |
|---|---|
| Arquivos disponíveis | `ADCT`, `CC`, `CDC`, `CE`, `CF`, `CLT`, `CP`, `CPC`, `CPP`, `CTB`, `CTN` |
| Códigos declarados no TypeScript | exatamente os 11 arquivos disponíveis |
| Busca com código específico | aceita os 11 códigos; valor desconhecido produz erro legível |
| Busca `todos` | os 11 códigos do registro central |
| Esquema MCP e sua documentação | gerados a partir do mesmo registro central |

Desde a conclusão de `BASE-002` e `BASE-003`:

- todo diploma presente é automaticamente incluído na busca `todos` e no enum MCP;
- `EI` não é anunciado nem carregado enquanto não houver base correspondente;
- adicionar um diploma exige uma única entrada no registro, além do JSON auditado.

## Súmulas

| Conjunto | Gerado em | Registros | Estado dos registros | URLs oficiais |
|---|---:|---:|---|---:|
| STJ | 2025-12-17 | 676 | 649 ativas; 27 canceladas | 676 |
| STF não vinculantes | 2026-01-13 | 736 | 724 ativas; 10 canceladas; 1 alterada; 1 superada | 736 |
| STF vinculantes | 2026-01-14 | 63 | 62 aprovadas; 1 cancelada | 63 |

As contagens, os estados e a presença de URLs são coerentes com os metadados. A
auditoria não comparou os enunciados nem os estados atuais com os portais dos
tribunais.

### Índices derivados de súmulas

| Arquivo | Cobertura | Gerado em | Proveniência declarada |
|---|---:|---:|---|
| `sumulas_keywords.json` | 676 súmulas STJ | 2025-12-09 | `gemini-2.0-flash-lite-001` |
| `sumulas_stf_keywords.json` | 736 súmulas STF | 2026-01-13 | `gemini-2.0-flash-lite` |

São dados derivados para recuperação, não fontes jurídicas. O repositório não contém
o procedimento completo, o prompt, os parâmetros ou os testes usados para reproduzir
esses índices. O índice do STJ também é anterior em oito dias ao JSON consolidado de
súmulas do STJ.

## Jurisprudência em Teses do STJ

| Campo | Valor observado |
|---|---:|
| Arquivo | `jt_stj.json` |
| Gerado em | 2026-02-17 |
| Edições distintas | 269 |
| Teses | 3.371 |
| Teses com URL do STJ | 3.371 |
| Teses marcadas como rito especial | 154 |

Os totais por ramo do Direito conferem com os metadados. O `BASE-006` removeu
`JT_179_T19`: a edição oficial possui apenas as teses 1 a 10, e o registro vazio era
um artefato de extração. Desde `BASE-008`, a descrição do servidor MCP deriva
automaticamente dos dados carregados: 3.371 teses em 269 edições.

## Temas repetitivos do STJ

| Campo | Valor observado |
|---|---:|
| Arquivo | `flash_temas_stj.json` |
| Gerado em | 2026-01-07 |
| Temas | 1.405 |
| Temas com questão submetida | 1.405 |
| Temas com página oficial do STJ | 1.405 |
| Temas sem tese firmada preenchida | 331 |

A ausência de tese em 331 registros aparece associada principalmente a temas afetados,
cancelados ou ainda em julgamento; ela não foi classificada automaticamente como erro.

Desde a conclusão do `BASE-007`, `_meta.source` registra o pacote e os recursos
oficiais do Portal de Dados Abertos do STJ, a chave de relacionamento e o adaptador de
reprodução futura. O metadado também preserva a limitação histórica: os artefatos
brutos usados no snapshot de janeiro não foram versionados. Os 1.405 registros não
foram alterados nessa correção.

## Rastreabilidade entregue pelo motor

Os dados guardam links oficiais e, desde a conclusão do `BASE-001`, o motor os
preserva na saída formatada:

| Resultado | URL existe no JSON | URL aparece na resposta formatada |
|---|---|---|
| Legislação | sim | sim |
| Súmula STJ/STF/vinculante | sim | sim |
| Jurisprudência em Teses | sim | sim |
| Tema repetitivo | sim | sim; inclui todos os links disponíveis no registro |

Cinco testes de regressão cobrem os três ramos de súmulas, Jurisprudência em Teses e
temas repetitivos. O auditor também verifica estaticamente que os formatadores
continuam usando os campos de URL.

## Atualização e reprodutibilidade

Desde `BASE-004`, o repositório contém um pipeline para coletar fontes oficiais,
transformar as quatro famílias primárias, validar candidatos, comparar snapshots e
promover somente o conjunto revisado. O manifesto está em
[`fontes.json`](fontes.json) e o procedimento completo em
[`ATUALIZACAO.md`](ATUALIZACAO.md).

O fluxo registra na execução ou exige registrar na revisão de promoção, por conjunto:

- URL ou endpoint de origem;
- instante da coleta e data de referência do conteúdo;
- artefato bruto ou checksum quando for permitido preservá-lo;
- transformação aplicada;
- versão do esquema;
- diferenças em relação à versão anterior;
- validações executadas;
- responsável pela revisão.

Os índices de palavras-chave produzidos por modelo de linguagem continuam fora da
reprodução automática até a conclusão do `BASE-010`. Eles são enriquecimentos de
busca, não fontes jurídicas.

## Taxonomia documental e efeito jurídico

Desde a conclusão do `BASE-009`, a saída do motor separa natureza documental,
proveniência e efeito jurídico. O vocabulário e as regras estão documentados em
[`TAXONOMIA.md`](TAXONOMIA.md).

- legislação é apresentada como texto normativo oriundo de compilação oficial;
- súmulas são enunciados sumulares, com efeito vinculante reservado às vinculantes
  aprovadas e vigentes;
- Jurisprudência em Teses é compilação institucional sem vinculação por si só;
- temas são registros de precedentes qualificados, e o efeito varia conforme situação
  e presença de tese;
- palavras-chave e termos são índices derivados, sem força jurídica.

## Resultado da auditoria

### Pontos fortes confirmados

- acervo local expressivo e estruturado;
- contagens coerentes na maior parte dos conjuntos;
- URLs oficiais presentes em todos os registros das quatro famílias;
- estados de súmulas preservados;
- índices de busca já disponíveis;
- links oficiais preservados nas respostas formatadas;
- motor funcional para consultas locais sem enviar a base a serviço externo.

### Limitações conhecidas

- a confirmação externa desta rodada foi pontual; não houve revisão integral de
  vigência e conteúdo de todos os conjuntos;
- o pipeline prepara candidatos reproduzíveis, mas a confirmação de vigência e a
  aprovação das diferenças continuam sendo revisão humana obrigatória;
- os brutos que deram origem ao snapshot legado de temas não foram preservados, embora
  a referência pública e o processo futuro já estejam documentados;
- os rótulos reduzem inferências indevidas, mas não substituem o exame do inteiro teor,
  da vigência, da situação atual e da aplicabilidade ao caso;
- não há avaliação documentada de precisão e cobertura das buscas por palavras-chave.

As correções estão organizadas no [BACKLOG.md](BACKLOG.md).
