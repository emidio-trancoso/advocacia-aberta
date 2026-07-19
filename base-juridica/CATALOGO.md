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
| Legislação | 273 | 22.180 registros | 273 diplomas |
| Súmulas | 3 | 1.475 registros | STJ, STF e vinculantes do STF |
| Jurisprudência em Teses | 1 | 3.508 teses | 283 edições do STJ |
| Temas repetitivos | 1 | 1.462 temas | STJ |
| Temas de repercussão geral | 1 | 1.470 temas | STF |
| Informativo STF | 1 | 11.567 julgados | 1.211 edições do STF |
| Espelhos de acórdãos | 1 | 11.133 acórdãos | Corte Especial e 3 Seções do STJ |
| Índices auxiliares | 275 exclusivos (2 de súmulas, 273 de legislação em `indices/`) + índices embutidos | derivados | palavras-chave e termos de busca |
| Total em JSON | 556 | — | 95.708.033 bytes, cerca de 96 MB |

Os números acima foram contados diretamente nos JSONs. `gerado_em` e `generatedAt`
indicam geração do arquivo, não garantem a data de vigência do conteúdo.

## Legislação

Todos os 22.180 registros legislativos possuem URL individual. Os metadados apontam
para páginas compiladas do Planalto.

| Código | Diploma | Gerado em | Registros | Índice | Situação estrutural |
|---|---|---:|---:|---|---|
| `ADCT` | Ato das Disposições Constitucionais Transitórias | 2026-07-19 | 148 | curado preservado + complemento derivado | coerente |
| `CC` | Código Civil — Lei 10.406/2002 | 2026-07-19 | 2.084 | curado preservado + complemento derivado | coerente |
| `CDC` | Código de Defesa do Consumidor — Lei 8.078/1990 | 2026-07-19 | 131 | derivado (texto integral) | coerente |
| `CE` | Código Eleitoral — Lei 4.737/1965 | 2026-07-19 | 387 | derivado (texto integral) | coerente |
| `CF` | Constituição Federal de 1988 | 2026-07-19 | 276 | curado preservado + complemento derivado | coerente |
| `CLT` | Consolidação das Leis do Trabalho | 2026-07-19 | 1.027 | curado preservado + complemento derivado | coerente |
| `CP` | Código Penal — Decreto-Lei 2.848/1940 | 2026-07-19 | 432 | curado preservado + complemento derivado | coerente |
| `CPC` | Código de Processo Civil — Lei 13.105/2015 | 2026-07-19 | 1.073 | curado preservado + complemento derivado | coerente |
| `CPP` | Código de Processo Penal — Decreto-Lei 3.689/1941 | 2026-07-19 | 849 | curado preservado + complemento derivado | coerente |
| `CTB` | Código de Trânsito Brasileiro — Lei 9.503/1997 | 2026-07-19 | 391 | derivado (texto integral) | coerente |
| `CTN` | Código Tributário Nacional — Lei 5.172/1966 | 2026-07-19 | 209 | curado preservado + complemento derivado | coerente |
| `ECA` | Estatuto da Criança e do Adolescente — Lei 8.069/1990 | 2026-07-19 | 325 | derivado (texto integral) | coerente |
| `LBPS` | Lei de Benefícios da Previdência Social — Lei 8.213/1991 | 2026-07-19 | 177 | derivado (texto integral) | coerente |
| `LD` | Lei de Drogas — Lei 11.343/2006 | 2026-07-19 | 99 | derivado (texto integral) | coerente |
| `LEP` | Lei de Execução Penal — Lei 7.210/1984 | 2026-07-19 | 219 | derivado (texto integral) | coerente |
| `LGPD` | Lei Geral de Proteção de Dados Pessoais — Lei 13.709/2018 | 2026-07-19 | 79 | derivado (texto integral) | coerente |
| `LINDB` | Lei de Introdução às Normas do Direito Brasileiro — Decreto-Lei 4.657/1942 | 2026-07-19 | 30 | derivado (texto integral) | coerente |
| `LLC` | Lei de Licitações e Contratos Administrativos — Lei 14.133/2021 | 2026-07-19 | 196 | derivado (texto integral) | coerente |
| `LMP` | Lei Maria da Penha — Lei 11.340/2006 | 2026-07-19 | 57 | derivado (texto integral) | coerente |

Na coluna "Índice", **curado preservado** é o índice invertido legado
`indexes.keywords`, estrutural para o ranking do núcleo e mantido como artefato
preservado; **complemento derivado** e **derivado (texto integral)** são os
índices reproduzíveis do `BASE-019` em `data/indices/`, que reproduzem a
semântica da busca em texto integral. CDC, CE e CTB também guardam
palavras-chave curadas por registro, preservadas nos dados mas não usadas pelo
motor de busca.

A tabela acima cobre o núcleo e o piloto (19 diplomas, 8.189 registros; as
contagens refletem a recaptura com o rótulo "Art. 1º-A" corrigido); os
demais diplomas da expansão estão resumidos por grupo mais abaixo, e o
inventário completo sai do auditor. O snapshot de 2026-07-19 foi o
primeiro produzido integralmente pelo pipeline reproduzível: o ganho de
registros nos 11 diplomas originais vem principalmente de artigos revogados
retidos que o processo legado omitia, além de dispositivos novos como o art.
121-B e o art. 147-C do CP e o art. 699-A do CPC. Os índices invertidos
curados são enriquecimentos legados preservados na transformação; desde o
`BASE-019`, os dispositivos que eles não cobrem entram no índice derivado
regenerável, e um teste garante a cobertura 1:1 — 314 dispositivos do núcleo
que estavam invisíveis à busca textual (ex.: CLT art. 7º, CPP arts. 3º-A a
3º-F, CP arts. 121-B e 147-C) voltaram a ser recuperáveis.

A revisão da expansão descobriu defeitos tipográficos nas páginas do Planalto
("Art 4º" sem ponto na Lei 6.001; "Art . 16." com espaço na Lei 6.880) e o
adaptador passou a tolerá-los. A recaptura dos diplomas do núcleo com a regra
corrigida recuperou o art. 1.636 do CC (antes absorvido no art. 1.635) e
reconciliou com a fonte oficial os arts. 554, 555, 571, 572 e 575 da CLT e o
art. 67-B do CTB, que estavam retidos do snapshot legado sem rótulo.

Os diplomas incorporados pela expansão (piloto de 8 leis e fatias do manifesto
[`expansao/normas.json`](expansao/normas.json)) não possuem índice curado: a
busca usa o índice derivado do `BASE-019`, que reproduz a semântica do texto
integral dos dispositivos. Particularidades observadas na
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
[`expansao/normas.json`](expansao/normas.json) (254 normas, com sigla, URL
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
| `esparsas_administrativo` | 23 | 1.295 | 2026-07-19 |
| `esparsas_processual_constitucional` | 19 | 501 | 2026-07-19 |
| `esparsas_consumidor_bancario` | 24 | 1.296 | 2026-07-19 |
| `esparsas_empresarial` | 28 | 1.649 | 2026-07-19 |
| `esparsas_regulatorio_outros` | 19 | 1.261 | 2026-07-19 |
| `decretos` | 1 | 23 | 2026-07-19 |
| `codificadas_ccom` | 1 | 448 | 2026-07-19 |
| `empresarial_d2044` | 1 | 57 | 2026-07-19 |
| `consumidor_bancario_l15040` | 1 | 134 | 2026-07-19 |

Todas as 254 normas do manifesto estão materializadas e promovidas; o grupo
`pendentes_especiais` foi esvaziado em 2026-07-19. O Código Comercial de 1850
(`CCOM`), antes retido
porque a página compilada mistura duas numerações (o corpo do Código, arts. 1º
a 913, e o Título Único da administração da justiça comercial, com arts. 1º a
30 próprios), foi capturado com o marcador `fim_antes` ("TÍTULO ÚNICO"), que
encerra a extração no corpo do Código — 448 dispositivos entre os arts. 457 e
913. A página consolida sem rótulo individual os arts. 1º a 456 (Parte
Primeira, revogada pelo CC/2002) e os arts. 731 a 739 (Título IX do comércio
marítimo, revogados pela Lei 7.542/1986); não há registros para essas faixas.
Vigência: subsiste essencialmente a Segunda Parte (comércio marítimo) — a
conferência é por dispositivo, como em todo o acervo. O Decreto 2.044/1908
(letra de câmbio e nota promissória, `D2044`), antes retido porque a URL da
planilha servia o Decreto 2.044/1996 (isenção de vistos) — divergência
flagrada pela conferência de cabeçalho do revisor —, foi capturado da página
oficial localizada em `ccivil_03/decreto/historicos/dpl/dpl2044-1908.htm`
(cabeçalho conferido: "DECRETO Nº 2.044, DE 31 DE DEZEMBRO DE 1908"), com os
57 artigos em sequência completa e a ortografia da época preservada; o
adaptador passou a tolerar as formas "TITULO", "CAPITULO" e "SECÇÃO" sem
acento, com teste. Observações das
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
11.977 omite os arts. 46 a 71, revogados pela Lei 14.620/2023. Na Lei 8.112,
avisos de revogação de artigos consecutivos dividem o mesmo parágrafo na
página (ex.: arts. 88 e 89; 232 a 235) e ficam registrados no primeiro
número do parágrafo. Nos decretos de promulgação de tratados (Convenções de
Haia e de Nova York), o anexo usa "Artigo 1º" e não vira registro próprio: o
texto da convenção fica anexado ao último artigo do decreto, pesquisável pelo
texto integral.

### Cobertura real do motor legislativo

| Superfície | Cobertura observada |
|---|---|
| Arquivos disponíveis | 273 diplomas: núcleo (11), piloto (8), estatutos (17), trabalhista (27), codificadas (7), codificadas_ccom (1), penal (17), tributário (16), previdenciário (12), cível/família (18), eleitoral (13), imobiliário/agrário (10), administrativo (23), processual/constitucional (19), consumidor/bancário (24), consumidor_bancario_l15040 (1), empresarial (28), empresarial_d2044 (1), regulatório/outros (19) e decretos (1); a lista completa está no registro do motor e no manifesto da expansão |
| Códigos declarados no TypeScript | exatamente os 273 arquivos disponíveis (expansão gerada entre marcadores) |
| Busca com código específico | aceita os 273 códigos; valor desconhecido produz erro legível |
| Busca `todos` | os 273 códigos do registro central |
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

### Índices derivados de súmulas e de legislação

| Arquivo | Cobertura | Gerado em | Processo declarado |
|---|---:|---:|---|
| `sumulas_keywords.json` | 676 súmulas STJ | 2026-07-19 | `tokens-significativos-v1` local, regenerado após a atualização das súmulas |
| `sumulas_stf_keywords.json` | 736 súmulas STF | 2026-07-19 | `tokens-significativos-v1` local, regenerado após a atualização das súmulas |
| `indices/lei_*_keywords.json` (273 arquivos) | 16.396 dispositivos fora dos índices curados; a união cobre os 22.180 em relação 1:1 | 2026-07-19 | `tokens-texto-integral-v1` local, regenerado após cada promoção de legislação |

São dados derivados para recuperação, não fontes jurídicas. Desde o `BASE-010`
(súmulas) e o `BASE-019` (legislação), o repositório contém gerador, manifesto,
parâmetros, checksums das fontes e testes de cobertura 1:1. O processo não usa
modelo de linguagem: `modelo` e `prompt` são explicitamente nulos, e os tokens
vêm dos textos publicados. No índice de legislação as stopwords são preservadas
de propósito, para que o ranking reproduza a busca em texto integral do motor.
A reprodução completa está documentada em
[`indices-derivados.json`](indices-derivados.json).

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
na transformação, e a busca de temas não tem fallback textual: os 57 temas 1406 a
1462, acrescentados depois dos índices, hoje só são encontrados pela busca por
número. O `BASE-020` rastreia a correção, no padrão que o `BASE-019` estabeleceu
para a legislação.

## Temas de repercussão geral do STF

| Campo | Valor observado |
|---|---:|
| Arquivo | `temas_rg_stf.json` |
| Gerado em | 2026-07-19 |
| Temas | 1.470 |
| Temas com tese firmada | 1.300 |

O `BASE-021` incorporou os temas de repercussão geral do STF — o par vinculante
dos temas repetitivos do STJ que a base já tinha. O snapshot vem do pipeline
reproduzível a partir da exportação oficial única
(`portal.stf.jus.br/jurisprudenciaRepercussao/exportarDados.asp`), servida como
tabela HTML com o rótulo `application/vnd.ms-excel`; o adaptador corrige, por
célula, o mojibake UTF-8 da fonte ("NÃ£o hÃ¡" → "Não há") sem tocar no texto já
correto. Cada tema guarda a página oficial (`verTeseTema.asp?numTema=N`) e, quando
a fonte oferece, os links de detalhamento do processo, manifestação e acórdão. As
situações observadas foram: Trânsito em Julgado (1.263), Acórdão de Repercussão
Geral publicado (136), Acórdão de mérito publicado (36), Cancelado (21), Mérito
julgado (7), Analisada Preliminar de Repercussão Geral (4) e Em julgamento (3). Ao
contrário da busca de temas do STJ (lacuna `BASE-020`), a busca de RG usa um índice
textual construído em memória a partir do texto publicado, cobrindo todos os 1.470
temas — nenhum tema fica invisível à busca por palavra-chave. A coluna "Assuntos"
da exportação duplica "Descrição" e não traz taxonomia de assuntos; o flag de
suspensão nacional (art. 1.035, §5º, CPC) não existe nas rotas estáticas do STF, só
na base Qlik, e está registrado como limitação no [BACKLOG.md](BACKLOG.md).

## Informativo STF

| Campo | Valor observado |
|---|---:|
| Arquivo | `informativo_stf.json` |
| Gerado em | 2026-07-19 |
| Julgados | 11.567 |
| Edições distintas | 1.211 (numeradas de 1 a 1.222) |
| Julgados com tese registrada | 850 |

O `BASE-025` incorporou o Informativo STF — uma **compilação institucional**, como a
Jurisprudência em Teses, sem vinculação própria. O snapshot vem do pipeline
reproduzível a partir da planilha estruturada oficial (`Dados_InformativosSTF.xlsx`,
9,3 MB), lida por streaming com a biblioteca padrão (XLSX é zip+XML; a planilha usa
strings inline, sem tabela de strings compartilhadas); as datas de julgamento são
convertidas do serial do Excel. Cada julgado guarda o link oficial da edição
(`informativo{N}.htm`, verificado para edições antigas e recentes). A busca usa um
índice textual em memória sobre título, tese, resumo, matéria, ramo e legislação,
cobrindo os 11.567 julgados; a coluna "Matéria" (100% preenchida) sustenta a
recuperação mesmo nos julgados sem resumo ou tese.

**Escopo curado:** foram mantidos os campos curados por julgado (processo, data,
relator, órgão, situação, título, tese, resumo, matéria, ramo, repercussão geral,
Tema RG e legislação). As duas colunas de notícia integral foram omitidas para manter
a base local enxuta — o texto completo de cada julgado fica a um clique no link
oficial da edição. A licença de reprodução declarada pelo STF ("Permite-se a
reprodução desta publicação, no todo ou em parte, sem alteração do conteúdo, desde
que citada a fonte.") está registrada na proveniência do snapshot.

## Espelhos de acórdãos do STJ

| Campo | Valor observado |
|---|---:|
| Arquivo | `espelhos_stj.json` |
| Gerado em | 2026-07-19 |
| Acórdãos | 11.133 |
| Órgãos | Corte Especial e 1ª, 2ª e 3ª Seções |
| Acórdãos com tese registrada | 588 |

O `BASE-026` incorporou os espelhos de acórdãos do STJ — fichas de acórdãos
selecionados pela Secretaria de Jurisprudência por trazerem "novidades quanto a
teses jurídicas". O snapshot vem do pipeline reproduzível a partir do Portal de
Dados Abertos do STJ (CKAN): merge incremental dos JSONs mensais (AAAAMMDD.json)
de cada órgão, por `id` do documento. A detecção de mudança usa o
`metadata_modified` do CKAN, como nos temas repetitivos.

**Escopo — órgãos uniformizadores.** Foram capturados apenas os órgãos que
uniformizam a jurisprudência do STJ (Corte Especial e as três Seções); as seis
Turmas ficaram de fora por volume (os dez órgãos somam ~132 mil acórdãos e ~120
MB sem ementa, contra ~11 mil e ~33 MB dos uniformizadores). Cada acórdão guarda
a **ementa** (o conteúdo que sustenta a busca — 100% preenchida), a tese e o tema
quando existirem, as referências legislativas e a jurisprudência citada, além de
classe, relator, órgão, data e os links oficiais de consulta processual e de
jurisprudência. O inteiro teor e o histórico pré-2022 (recursos ZIP) ficam no
link oficial. A busca usa um índice textual em memória sobre esses campos,
cobrindo os 11.133 acórdãos. Um mês sem lançamentos que a fonte publicou como
JSON malformado (`segunda-secao/20240229.json`) foi ignorado e registrado na
proveniência, sem truncar cobertura em silêncio.

## Rastreabilidade entregue pelo motor

Os dados guardam links oficiais e, desde a conclusão do `BASE-001`, o motor os
preserva na saída formatada:

| Resultado | URL existe no JSON | URL aparece na resposta formatada |
|---|---|---|
| Legislação | sim | sim |
| Súmula STJ/STF/vinculante | sim | sim |
| Jurisprudência em Teses | sim | sim |
| Tema repetitivo | sim | sim; inclui todos os links disponíveis no registro |
| Tema de repercussão geral | sim | sim; inclui todos os links disponíveis no registro |
| Informativo STF | sim | sim; inclui o link oficial da edição |
| Espelho de acórdão | sim | sim; inclui os links de consulta processual e jurisprudência |

Oito testes de regressão cobrem os três ramos de súmulas, Jurisprudência em Teses,
temas repetitivos, temas de repercussão geral, o Informativo STF e os espelhos de
acórdãos. O auditor também verifica estaticamente que os formatadores continuam
usando os campos de URL.

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
- Jurisprudência em Teses e o Informativo STF são compilações institucionais sem
  vinculação por si só;
- temas repetitivos do STJ e temas de repercussão geral do STF são registros de
  precedentes qualificados, e o efeito varia conforme situação e presença de tese;
- espelhos de acórdãos são fichas de acórdãos selecionados pelo STJ; um acórdão
  isolado não é vinculante por si só;
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
- a avaliação de recuperação cobre 74 consultas controladas e seis famílias; ela é um
  gate de regressão, não uma estimativa exaustiva para qualquer consulta jurídica.

As métricas e limitações estão em
[`AVALIACAO-RECUPERACAO.md`](AVALIACAO-RECUPERACAO.md), e as correções restantes estão
organizadas no [BACKLOG.md](BACKLOG.md).
