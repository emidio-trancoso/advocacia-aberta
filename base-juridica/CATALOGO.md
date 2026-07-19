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
| Legislação | 156 | 15.516 registros | 156 diplomas |
| Súmulas | 3 | 1.475 registros | STJ, STF e vinculantes do STF |
| Jurisprudência em Teses | 1 | 3.508 teses | 283 edições do STJ |
| Temas repetitivos | 1 | 1.462 temas | STJ |
| Índices auxiliares | 2 exclusivos + índices embutidos | derivados | palavras-chave e termos de busca |
| Total em JSON | 163 | — | 32.004.582 bytes, cerca de 32 MB |

Os números acima foram contados diretamente nos JSONs. `gerado_em` e `generatedAt`
indicam geração do arquivo, não garantem a data de vigência do conteúdo.

## Legislação

Todos os 15.516 registros legislativos possuem URL individual. Os metadados apontam
para páginas compiladas do Planalto.

| Código | Diploma | Gerado em | Registros | Índice | Situação estrutural |
|---|---|---:|---:|---|---|
| `ADCT` | Ato das Disposições Constitucionais Transitórias | 2026-07-19 | 148 | pré-computado preservado | coerente |
| `CC` | Código Civil — Lei 10.406/2002 | 2026-07-19 | 2.084 | pré-computado preservado | coerente |
| `CDC` | Código de Defesa do Consumidor — Lei 8.078/1990 | 2026-07-19 | 131 | palavras-chave por registro | coerente |
| `CE` | Código Eleitoral — Lei 4.737/1965 | 2026-07-19 | 387 | palavras-chave por registro | coerente |
| `CF` | Constituição Federal de 1988 | 2026-07-19 | 276 | pré-computado preservado | coerente |
| `CLT` | Consolidação das Leis do Trabalho | 2026-07-19 | 1.027 | pré-computado preservado | coerente |
| `CP` | Código Penal — Decreto-Lei 2.848/1940 | 2026-07-19 | 432 | pré-computado preservado | coerente |
| `CPC` | Código de Processo Civil — Lei 13.105/2015 | 2026-07-19 | 1.073 | pré-computado preservado | coerente |
| `CPP` | Código de Processo Penal — Decreto-Lei 3.689/1941 | 2026-07-19 | 843 | pré-computado preservado | coerente |
| `CTB` | Código de Trânsito Brasileiro — Lei 9.503/1997 | 2026-07-19 | 390 | pré-computado preservado | coerente |
| `CTN` | Código Tributário Nacional — Lei 5.172/1966 | 2026-07-19 | 209 | pré-computado preservado | coerente |
| `ECA` | Estatuto da Criança e do Adolescente — Lei 8.069/1990 | 2026-07-19 | 324 | sem índice curado; busca em texto integral | coerente |
| `LBPS` | Lei de Benefícios da Previdência Social — Lei 8.213/1991 | 2026-07-19 | 177 | sem índice curado; busca em texto integral | coerente |
| `LD` | Lei de Drogas — Lei 11.343/2006 | 2026-07-19 | 92 | sem índice curado; busca em texto integral | coerente |
| `LEP` | Lei de Execução Penal — Lei 7.210/1984 | 2026-07-19 | 218 | sem índice curado; busca em texto integral | coerente |
| `LGPD` | Lei Geral de Proteção de Dados Pessoais — Lei 13.709/2018 | 2026-07-19 | 79 | sem índice curado; busca em texto integral | coerente |
| `LINDB` | Lei de Introdução às Normas do Direito Brasileiro — Decreto-Lei 4.657/1942 | 2026-07-19 | 30 | sem índice curado; busca em texto integral | coerente |
| `LLC` | Lei de Licitações e Contratos Administrativos — Lei 14.133/2021 | 2026-07-19 | 196 | sem índice curado; busca em texto integral | coerente |
| `LMP` | Lei Maria da Penha — Lei 11.340/2006 | 2026-07-19 | 57 | sem índice curado; busca em texto integral | coerente |

A tabela acima cobre o núcleo e o piloto (19 diplomas, 8.173 registros); os
demais diplomas da expansão estão resumidos por grupo mais abaixo, e o
inventário completo sai do auditor. O snapshot de 2026-07-19 foi o
primeiro produzido integralmente pelo pipeline reproduzível: o ganho de 196
registros nos 11 diplomas originais vem principalmente de artigos revogados
retidos que o processo legado omitia, além de dispositivos novos como o art.
121-B e o art. 147-C do CP e o art. 699-A do CPC. Os índices invertidos
pré-computados são enriquecimentos legados preservados na transformação; artigos
acrescentados depois deles ficam fora do índice até o `BASE-019` tornar a
geração reproduzível.

A revisão da expansão descobriu defeitos tipográficos nas páginas do Planalto
("Art 4º" sem ponto na Lei 6.001; "Art . 16." com espaço na Lei 6.880) e o
adaptador passou a tolerá-los. A recaptura dos diplomas do núcleo com a regra
corrigida recuperou o art. 1.636 do CC (antes absorvido no art. 1.635) e
reconciliou com a fonte oficial os arts. 554, 555, 571, 572 e 575 da CLT e o
art. 67-B do CTB, que estavam retidos do snapshot legado sem rótulo.

Os diplomas incorporados pela expansão (piloto de 8 leis e fatias do manifesto
[`expansao/normas.json`](expansao/normas.json)) não possuem índice curado: a
busca usa o texto integral dos dispositivos. Particularidades observadas na
fonte e preservadas no snapshot:

- a página da Lei 8.213/1991 consolida os arts. 145 a 147 numa única linha de
  revogação ("Art. 144. a Art. 147. Revogado"), registrada no art. 144; não há
  registros separados para 145–147;
- a página da LGPD apresenta o art. 57 com defeito tipográfico ("Art. 5 7.
  (VETADO)."), e o dispositivo vetado não gera registro próprio;
- os arts. 337-E a 337-P citados na página da Lei 14.133/2021 pertencem ao
  Código Penal (inseridos pelo art. 178 daquela lei) e ficam registrados apenas
  em `CP`; a transformação exclui dispositivos cujo rótulo aponta para outra
  norma.

### Expansão por grupos

A expansão é dirigida pelo manifesto versionado
[`expansao/normas.json`](expansao/normas.json) (253 normas, com sigla, URL
oficial validada e grupo). `gerar_expansao_legislacao.py` materializa cada
grupo (conjunto em `fontes.json`, stubs e entradas geradas do registro do
motor), `revisar_expansao.py` apoia a revisão da captura e a promoção segue o
protocolo comum. O inventário por diploma sai de
`auditar_base_juridica.py --json`.

| Grupo | Diplomas | Registros | Promovido em |
|---|---:|---:|---|
| `estatutos` | 17 | 1.391 | 2026-07-19 |
| `esparsas_trabalhista` | 27 | 540 | 2026-07-19 |
| `codificadas` | 7 | 1.953 | 2026-07-19 |
| `esparsas_penal` | 17 | 508 | 2026-07-19 |
| `esparsas_tributario` | 16 | 803 | 2026-07-19 |
| `esparsas_previdenciario` | 12 | 421 | 2026-07-19 |
| `esparsas_civel_familia` | 18 | 640 | 2026-07-19 |
| `esparsas_eleitoral` | 13 | 379 | 2026-07-19 |
| `esparsas_imobiliario_agrario` | 10 | 614 | 2026-07-19 |

Grupos pendentes de materialização: decretos (1) e as cinco fatias de esparsas
por macro-área restantes (98 normas). O Código Comercial de 1850 foi movido
para o grupo `pendentes_especiais` sem materialização: a página compilada
mistura duas numerações (o corpo do Código, arts. 1 a 913, e o Título Único da
administração da justiça comercial, com arts. 1 a 30 próprios), e a captura por
número único produziria registros ambíguos. Observações das
fatias promovidas: a página oficial confirma o nome atual "Estatuto da Pessoa
Idosa" (Lei 14.423/2022), mantida a sigla `EI`; a linha da planilha rotulada
"Estatuto do Estrangeiro" corresponde à Lei de Migração (`LMIG`); os arts. 4º
e 39 da Lei 6.001, sete artigos da Lei 6.880 e os rótulos de abertura de seis
leis trabalhistas (3.207, 4.950-A, 5.584, 6.321, 6.533 e 6.615) só existem na
fonte com rótulo tipográfico defeituoso ("Art 1º"/"Art . 1º") e passaram a ser
capturados. Nas codificadas, o CBA, o CBT e o CPPM apresentam revogações em
faixa numa linha única da página oficial (ex.: "Art. 77 a 85. Revogado"),
registradas no primeiro número da faixa, e a página do CPM tem árvore HTML com
profundidade ~1.700 por tags nunca fechadas, tolerada pelo parser. Na fatia
tributária, os arts. 42 e 43 da Lei 10.637/2002 aparecem na página apenas como
citação pontilhada de lei alterada, e artigos isolados (DL 1.598 art. 66; Lei
7.713 arts. 28 e 29; Lei 10.637 arts. 39 e 40) são omitidos pela própria página
oficial. Três refinamentos posteriores do adaptador, com testes: o rótulo
com ordinal antes do sufixo ("Art. 1º-A") passou a ser reconhecido — a
recaptura das fatias promovidas separou cerca de 80 dispositivos que estavam
absorvidos no artigo anterior (ex.: arts. 2º-A a 9º-A da Lei 7.998); redações
pontilhadas de normas alteradas ("Art. 155. ....." na Lei 6.515) deixaram de
virar artigos; e artigos vetados da própria lei com rótulo ligado à mensagem
de veto (Lei 11.804) passaram a ser preservados. A página da Lei 13.165
reproduz sem nenhum marcador o texto do art. 59-A da Lei 9.504 (promulgado
após derrubada de veto); o manifesto ganhou o campo de descarte explícito por
número (`descartar_artigos`), e o dispositivo fica registrado apenas na Lei
9.504. O mesmo descarte explícito cobre os arts. 1.358-C a 1.358-U do Código
Civil reproduzidos sem marcador na página da Lei 13.777, e a página da Lei
11.977 omite os arts. 46 a 71, revogados pela Lei 14.620/2023.

### Cobertura real do motor legislativo

| Superfície | Cobertura observada |
|---|---|
| Arquivos disponíveis | 133 diplomas: núcleo (11), piloto (8), estatutos (17), trabalhista (27), codificadas (7), penal (17), tributário (16), previdenciário (12), cível/família (18), eleitoral (13) e imobiliário/agrário (10); a lista completa está no registro do motor e no manifesto da expansão |
| Códigos declarados no TypeScript | exatamente os 156 arquivos disponíveis (expansão gerada entre marcadores) |
| Busca com código específico | aceita os 156 códigos; valor desconhecido produz erro legível |
| Busca `todos` | os 156 códigos do registro central |
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
- a avaliação de recuperação cobre 60 consultas controladas e seis famílias; ela é um
  gate de regressão, não uma estimativa exaustiva para qualquer consulta jurídica.

As métricas e limitações estão em
[`AVALIACAO-RECUPERACAO.md`](AVALIACAO-RECUPERACAO.md), e as correções restantes estão
organizadas no [BACKLOG.md](BACKLOG.md).
