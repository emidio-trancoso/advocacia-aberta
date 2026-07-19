# Catálogo da base jurídica

| Campo | Valor |
|---|---|
| Auditoria estrutural | 19 de julho de 2026 (UTC) |
| Local atual dos dados | `ferramentas/pesquisa/vade-mecum/data/` |
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
| Legislação | 11 | 6.999 registros | 11 diplomas |
| Súmulas | 3 | 1.475 registros | STJ, STF e vinculantes do STF |
| Jurisprudência em Teses | 1 | 3.508 teses | 283 edições do STJ |
| Temas repetitivos | 1 | 1.462 temas | STJ |
| Índices auxiliares | 2 exclusivos + índices embutidos | derivados | palavras-chave e termos de busca |
| Total em JSON | 18 | — | 19.676.210 bytes, cerca de 20 MB |

Os números acima foram contados diretamente nos JSONs. `gerado_em` e `generatedAt`
indicam geração do arquivo, não garantem a data de vigência do conteúdo.

## Legislação

Todos os 6.803 registros legislativos possuem URL individual. Os metadados apontam
para páginas compiladas do Planalto.

| Código | Diploma | Gerado em | Registros | Índice | Situação estrutural |
|---|---|---:|---:|---|---|
| `ADCT` | Ato das Disposições Constitucionais Transitórias | 2026-07-19 | 148 | pré-computado preservado | coerente |
| `CC` | Código Civil — Lei 10.406/2002 | 2026-07-19 | 2.083 | pré-computado preservado | coerente |
| `CDC` | Código de Defesa do Consumidor — Lei 8.078/1990 | 2026-07-19 | 131 | palavras-chave por registro | coerente |
| `CE` | Código Eleitoral — Lei 4.737/1965 | 2026-07-19 | 387 | palavras-chave por registro | coerente |
| `CF` | Constituição Federal de 1988 | 2026-07-19 | 276 | pré-computado preservado | coerente |
| `CLT` | Consolidação das Leis do Trabalho | 2026-07-19 | 1.027 | pré-computado preservado | coerente |
| `CP` | Código Penal — Decreto-Lei 2.848/1940 | 2026-07-19 | 432 | pré-computado preservado | coerente |
| `CPC` | Código de Processo Civil — Lei 13.105/2015 | 2026-07-19 | 1.073 | pré-computado preservado | coerente |
| `CPP` | Código de Processo Penal — Decreto-Lei 3.689/1941 | 2026-07-19 | 843 | pré-computado preservado | coerente |
| `CTB` | Código de Trânsito Brasileiro — Lei 9.503/1997 | 2026-07-19 | 390 | pré-computado preservado | coerente |
| `CTN` | Código Tributário Nacional — Lei 5.172/1966 | 2026-07-19 | 209 | pré-computado preservado | coerente |

A soma dos metadados e a contagem real são 6.999. O snapshot de 2026-07-19 foi o
primeiro produzido integralmente pelo pipeline reproduzível: o ganho de 196
registros vem principalmente de artigos revogados retidos que o processo legado
omitia, além de dispositivos novos como o art. 121-B e o art. 147-C do CP e o
art. 699-A do CPC. Os índices invertidos pré-computados são enriquecimentos
legados preservados na transformação; artigos acrescentados depois deles ficam
fora do índice até o `BASE-019` tornar a geração reproduzível.

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
| STJ | 2026-07-19 | 676 | 647 ativas; 29 canceladas | 676 |
| STF não vinculantes | 2026-07-19 | 736 | 724 ativas; 10 canceladas; 1 alterada; 1 superada | 736 |
| STF vinculantes | 2026-07-19 | 63 | 62 aprovadas; 1 cancelada | 63 |

As contagens, os estados e a presença de URLs são coerentes com os metadados. A
auditoria não comparou os enunciados nem os estados atuais com os portais dos
tribunais.

### Índices derivados de súmulas

| Arquivo | Cobertura | Gerado em | Processo declarado |
|---|---:|---:|---|
| `sumulas_keywords.json` | 676 súmulas STJ | 2026-07-19 | `tokens-significativos-v1` local, regenerado após a atualização das súmulas |
| `sumulas_stf_keywords.json` | 736 súmulas STF | 2026-07-19 | `tokens-significativos-v1` local, regenerado após a atualização das súmulas |

São dados derivados para recuperação, não fontes jurídicas. Desde o `BASE-010`, o
repositório contém gerador, manifesto, parâmetros, checksums das fontes e testes de
cobertura 1:1. O processo não usa modelo de linguagem: `modelo` e `prompt` são
explicitamente nulos, e os tokens vêm dos enunciados publicados. A reprodução completa
está documentada em [`indices-derivados.json`](indices-derivados.json).

## Jurisprudência em Teses do STJ

| Campo | Valor observado |
|---|---:|
| Arquivo | `jt_stj.json` |
| Gerado em | 2026-07-19 |
| Edições distintas | 283 |
| Teses | 3.508 |
| Edições retidas sem correspondência na coleta | 147, 153 e 165 |

Os totais por ramo do Direito conferem com os metadados. O `BASE-006` removeu
`JT_179_T19`: a edição oficial possui apenas as teses 1 a 10, e o registro vazio era
um artefato de extração. Na atualização de 2026-07-19, a página oficial das edições
147, 153 e 165 devolveu resultado vazio; suas teses publicadas foram retidas e a
retenção está registrada em `edicoes_retidas_sem_correspondencia`. `JT_020_T13` foi
removida porque a edição 20 oficial passou a listar 12 teses, e enunciados foram
atualizados conforme as revisões do STJ (ex.: a tese 4 da edição 45 substituiu a
referência à Súmula 512, cancelada, pelo Tema 600). Desde `BASE-008`, a descrição do
servidor MCP deriva automaticamente dos dados carregados: 3.508 teses em 283
edições.

## Temas repetitivos do STJ

| Campo | Valor observado |
|---|---:|
| Arquivo | `flash_temas_stj.json` |
| Gerado em | 2026-07-19 |
| Temas | 1.462 |

A ausência de tese firmada em parte dos registros aparece associada principalmente a
temas afetados, cancelados ou ainda em julgamento; ela não foi classificada
automaticamente como erro.

Desde a conclusão do `BASE-007`, `_meta.source` registra o pacote e os recursos
oficiais do Portal de Dados Abertos do STJ e a chave de relacionamento. O snapshot de
2026-07-19 foi produzido pelo pipeline reproduzível a partir dos CSVs oficiais
(`provenanceStatus: reproducible_pipeline`), superando a limitação histórica do
snapshot legado de janeiro, cujos brutos não haviam sido versionados. Os índices
`keywords` e `terms` consumidos pelo motor são enriquecimentos legados preservados
na transformação; temas acrescentados depois deles ficam fora do índice até o
`BASE-019`.

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

Os índices de palavras-chave são regeneráveis por processo local determinístico e
continuam classificados como enriquecimentos de busca, não como fontes jurídicas.

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
- a avaliação de recuperação cobre 24 consultas controladas e seis famílias; ela é um
  gate de regressão, não uma estimativa exaustiva para qualquer consulta jurídica.

As métricas e limitações estão em
[`AVALIACAO-RECUPERACAO.md`](AVALIACAO-RECUPERACAO.md), e as correções restantes estão
organizadas no [BACKLOG.md](BACKLOG.md).
