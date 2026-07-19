# Backlog de confiabilidade da base jurídica

Este backlog transforma os achados do [catálogo](CATALOGO.md) em trabalho verificável.
Nenhum item deve ser encerrado apenas porque a saída “parece correta”.

## Prioridades

- **P0 — confiança operacional:** afeta cobertura, execução ou possibilidade de
  conferir a fonte.
- **P1 — integridade e proveniência:** afeta coerência, atualização ou compreensão do
  dado.
- **P2 — robustez e evolução:** melhora testes, arquitetura e qualidade de busca.

## P0 — confiança operacional

| ID | Problema | Critério de aceite | Estado |
|---|---|---|---|
| `BASE-001` | Formatadores omitem URLs de súmulas, teses e temas | Toda resposta dessas famílias exibe ao menos um link oficial existente no registro | **concluído em 2026-07-17** |
| `BASE-002` | Busca legislativa `todos` cobre somente 6 dos 11 diplomas disponíveis | Lista única de códigos alimenta carregamento, `todos`, CLI, MCP e documentação; teste cobre os 11 | **concluído em 2026-07-17** |
| `BASE-003` | `EI` é declarado, mas `lei_ei.json` não existe | Adicionar conjunto verificado ou remover o código de todas as superfícies; consulta nunca termina em erro de módulo | **concluído em 2026-07-17** |
| `BASE-004` | Não existe pipeline reproduzível de atualização | Cada família possui coletor, transformação documentada, validação, versão e instrução de execução | **concluído em 2026-07-17** |

## P1 — integridade e proveniência

| ID | Problema | Critério de aceite | Estado |
|---|---|---|---|
| `BASE-005` | CTB informa 390 registros no metadado, mas contém 389 | Conferir na fonte e corrigir o registro ausente ou o metadado, com justificativa registrada | **concluído em 2026-07-17** |
| `BASE-006` | `JT_179_T19` tem enunciado vazio | Conferir a edição oficial; restaurar o enunciado ou documentar por que o registro não representa uma tese | **concluído em 2026-07-17** |
| `BASE-007` | Metadados de temas expõem caminhos locais de `Downloads` | Substituir por origem pública, data, método e identificador reproduzível, sem caminho pessoal | **concluído em 2026-07-17** |
| `BASE-008` | Descrição MCP declara 792 edições, mas existem 269 | Gerar descrição a partir do metadado ou corrigir o valor; teste impede nova divergência | **concluído em 2026-07-17** |
| `BASE-009` | “Fonte primária” e força jurídica não seguem taxonomia documentada | Definir e revisar rótulos para texto normativo, fonte oficial, compilação institucional, precedente e índice derivado | **concluído em 2026-07-17** |
| `BASE-010` | Índices de palavras-chave não têm processo reproduzível | Versionar geração, modelo, prompt/parâmetros, relação com a base e teste de cobertura | **concluído em 2026-07-17** |

## P2 — robustez e evolução

| ID | Trabalho | Critério de aceite | Estado |
|---|---|---|---|
| `BASE-011` | Criar testes de esquema e integridade | CI valida JSON, campos obrigatórios, contagens, URLs, códigos e referências cruzadas | aberto |
| `BASE-012` | Testar qualidade da recuperação | Conjunto de consultas e resultados esperados mede precisão, cobertura e regressões | **concluído em 2026-07-17** |
| `BASE-013` | Versionar snapshots e diferenças | Manifesto por conjunto registra versão, checksum, coleta e resumo das mudanças | aberto |
| `BASE-014` | Retirar o identificador legado do motor | Adotar `Vade Mecum`/`vade-mecum` em caminhos, pacote, MCP, setup, skills, CI e documentação, sem alias com o nome anterior | **concluído em 2026-07-17** |
| `BASE-015` | Integrar auditoria estrutural ao fluxo de contribuição | GitHub Actions executa o auditor e apresenta seus achados em toda mudança da base | **concluído em 2026-07-17** |
| `BASE-016` | Endurecer coleta e promoção do pipeline | Allowlist cobre URL inicial e redirecionada; tipo de conteúdo, volume, re-promoção e estados não ativos têm gates e testes | **concluído em 2026-07-17** |
| `BASE-017` | Não existe detecção de mudança nem agendamento; a atualização depende de alguém lembrar | Comando barato responde "a fonte mudou?" por família, sem preparar candidatos; execução agendada publica o resultado; a promoção continua humana | **concluído em 2026-07-18** |
| `BASE-018` | O adaptador de legislação captura `title_name` genérico ("TÍTULO I") onde o snapshot legado tinha o nome real ("DOS PRINCÍPIOS FUNDAMENTAIS") | O adaptador extrai os nomes reais de títulos e capítulos das páginas do Planalto, com teste; o motor não consome o campo hoje, então o item é de qualidade do dado | aberto |
| `BASE-019` | O índice invertido de legislação (`indexes.keywords`) e os `keywords` por artigo são enriquecimentos legados sem processo reproduzível; a transformação os preserva do arquivo publicado, e artigos novos ficam fora do índice (invisíveis à busca textual quando o índice existe) | Gerador determinístico versionado cobre todos os artigos publicados, como o `BASE-010` fez para súmulas; teste garante cobertura 1:1 | aberto |

## Itens concluídos

### `BASE-017` — monitoramento de mudanças nas fontes

- o subcomando `monitorar` verifica as seis famílias sem preparar candidatos e
  sem tocar nos dados publicados;
- legislação usa GET condicional (`If-Modified-Since` com o `gerado_em` do
  snapshot; o Planalto responde 304 quando nada mudou), súmulas comparam
  contagens por estado nos catálogos oficiais, Jurisprudência em Teses compara a
  edição mais recente do índice e temas repetitivos usam o `last_modified` da
  API CKAN do STJ;
- as URLs do Planalto no manifesto passaram a usar o caminho minúsculo
  canônico, eliminando o redirecionamento 301 que impedia a resposta 304;
- falha de uma fonte aparece como `erro` no relatório sem interromper o
  monitor; a saída `--json` alimenta automação;
- o GitHub Actions `monitorar-base.yml` roda o monitor semanalmente e abre ou
  atualiza uma issue quando há sinal de mudança ou erro; nenhuma etapa
  automatizada promove dados;
- oito testes cobrem os sinais por família, o tratamento de erro e a CLI;
- as limitações de cada sinal estão declaradas em
  [`ATUALIZACAO.md`](ATUALIZACAO.md);
- a verificação completa está em
  [`verificacoes/BASE-017.md`](verificacoes/BASE-017.md).

### `BASE-001` — links oficiais na saída

- súmulas STJ, STF e vinculantes exibem a URL oficial do registro;
- Jurisprudência em Teses exibe o link do PDF oficial do STJ;
- temas repetitivos exibem página do tema, consulta jurisprudencial e consulta
  processual quando disponíveis;
- cinco testes executam os formatadores reais;
- tipagem estrita e testes rodam no GitHub Actions;
- o auditor deixou de emitir `URL_OMITIDA_NA_SAIDA`.

### `BASE-015` — auditoria no fluxo de contribuição

- o GitHub Actions executa `auditar_base_juridica.py` em `push` e `pull_request`;
- o modo `--strict` faz qualquer achado bloquear a validação do projeto;
- os achados também ficam visíveis no log da execução.

### `BASE-002`, `BASE-003` e `BASE-008` — promessa e execução alinhadas

- um registro único alimenta carregamento, busca `todos`, enum e descrição MCP;
- os 11 diplomas existentes participam da busca global;
- `EI` foi removido das superfícies públicas e recebe erro legível se solicitado;
- quantidades de súmulas, teses, edições, temas e legislação são derivadas dos JSONs;
- quatro testes de cobertura protegem códigos, carregamento e contagens;
- um teste de integração consulta o servidor MCP e confere enum e descrição públicos;
- o auditor deixou de emitir `ARQUIVO_DECLARADO_AUSENTE`, `COBERTURA_TODOS` e
  `DESCRICAO_MCP`.

### `BASE-004` — pipeline reproduzível de atualização

- manifesto versionado identifica fontes, destinos, adaptadores e versão do pipeline;
- coletores cobrem Planalto, catálogos STJ/STF, Jurisprudência em Teses e os CSVs de
  dados abertos de precedentes qualificados;
- adaptadores determinísticos produzem candidatos para as quatro famílias primárias;
- cada download registra URL, horário, cabeçalhos, bytes e SHA-256;
- validação confere esquema, campos, contagens, caminhos locais e domínios oficiais;
- comparação lista IDs adicionados, removidos e alterados antes da publicação;
- promoção exige confirmação literal, autorização adicional para remoções, repete as
  travas e cria backup;
- dezoito testes do pipeline rodam no GitHub Actions;
- índices derivados permanecem corretamente separados no `BASE-010`.

### `BASE-016` — endurecimento da coleta e promoção

- URLs iniciais e efetivas precisam usar HTTPS e pertencer à allowlist oficial;
- tipo de conteúdo incompatível encerra a coleta antes de publicar o arquivo;
- mudança acima de 25% e de 20 registros exige aceite adicional explícito;
- a mesma execução não pode ser promovida duas vezes e sobrescrever o backup;
- estados não ativos das súmulas STJ não são reduzidos automaticamente a “ativa”;
- testes cobrem redirecionamento externo, conteúdo inesperado, volume e re-promoção.

### `BASE-007` — proveniência pública dos temas repetitivos

- caminhos absolutos de `Downloads` foram removidos dos metadados publicados;
- pacote, recursos, URLs e chave de relacionamento do Portal de Dados Abertos do STJ
  foram registrados;
- o metadado declara que os artefatos brutos do snapshot legado não foram versionados,
  sem atribuir ao arquivo histórico uma reprodução que não ocorreu;
- o checksum canônico confirma que os 1.405 temas não foram alterados;
- a verificação completa está em [`verificacoes/BASE-007.md`](verificacoes/BASE-007.md).

### `BASE-006` — registro espúrio na edição 179

- a página e o PDF oficiais apresentam somente as teses 1 a 10;
- `JT_179_T19`, vazio e sem destino de fragmento textual, foi removido;
- o total foi corrigido para 3.371 teses, preservadas as 269 edições;
- um teste de regressão fixa os dez identificadores oficiais da edição;
- a verificação completa está em [`verificacoes/BASE-006.md`](verificacoes/BASE-006.md).

### `BASE-005` — contagem e art. 326-C do CTB

- o texto compilado atual e a Lei nº 15.452/2026 confirmam o art. 326-C;
- o dispositivo foi incluído com URL oficial e navegação entre artigos;
- a base passou a conter os 390 registros já informados no metadado;
- a atualização foi pontual; as demais diferenças do candidato integral não foram
  promovidas sem revisão;
- a verificação completa está em [`verificacoes/BASE-005.md`](verificacoes/BASE-005.md).

### `BASE-009` — taxonomia documental e de efeito jurídico

- natureza documental, proveniência e efeito jurídico passaram a ser dimensões
  independentes;
- “fonte oficial” deixou de ser sinônimo de fonte primária ou de força vinculante;
- legislação, enunciados sumulares, compilações institucionais, registros de
  precedentes qualificados e índices derivados receberam definições explícitas;
- temas repetitivos agora distinguem tese publicada, ausência de tese, cancelamento,
  possível revisão e estados que exigem conferência;
- descrições MCP e formatadores deixaram de usar “persuasiva” e “orientativa” como
  classificações genéricas;
- testes e auditoria estrita impedem o retorno dos rótulos ambíguos;
- a taxonomia completa está em [`TAXONOMIA.md`](TAXONOMIA.md), e a verificação está
  em [`verificacoes/BASE-009.md`](verificacoes/BASE-009.md).

### `BASE-010` — índices derivados reproduzíveis

- os índices legados gerados por modelo foram substituídos por tokens derivados
  deterministicamente dos enunciados publicados;
- modelo e prompt são explicitamente nulos; algoritmo, parâmetros e stopwords são
  versionados;
- cada saída registra fonte, SHA-256, data, contagem e relação 1:1;
- um comando verifica igualdade byte a byte e outro regenera os arquivos;
- testes cobrem manifesto, reprodução e os 1.412 vínculos entre súmulas e índices;
- o processo está em [`indices-derivados.json`](indices-derivados.json), e a
  verificação em [`verificacoes/BASE-010.md`](verificacoes/BASE-010.md).

### `BASE-014` — motor Vade Mecum

- o motor passou a se chamar **Vade Mecum**, com identificador técnico `vade-mecum`;
- dados e código foram movidos para `ferramentas/pesquisa/vade-mecum/`;
- pacote, servidor MCP, setup, CI, skills, pipeline, auditor, templates e documentação
  apontam para o novo caminho;
- a CLI passou a usar a taxonomia da base jurídica em vez do rótulo genérico “fontes
  primárias”;
- a migração não mantém alias com o identificador anterior;
- teste de regressão varre caminhos e textos e impede a reintrodução do nome legado;
- a verificação completa está em
  [`verificacoes/BASE-014.md`](verificacoes/BASE-014.md).

### `BASE-012` — qualidade da recuperação

- 24 consultas representam súmulas STJ, STF e vinculantes, Jurisprudência em Teses,
  temas repetitivos e sete diplomas legislativos;
- relevância, justificativa e resultados canônicos são julgamentos versionados, não
  expectativas geradas pelo próprio ranking;
- precisão, recall julgado, cobertura, obrigatórios e MRR possuem limiares executáveis;
- a precisão global observada no top 5 é 0,7944, com recall julgado, coberturas e MRR
  em 1,0000;
- cada família tem limiar próprio e toda consulta preserva ao menos um ID obrigatório;
- testes e GitHub Actions bloqueiam regressões;
- o protocolo está em
  [`AVALIACAO-RECUPERACAO.md`](AVALIACAO-RECUPERACAO.md), e a verificação em
  [`verificacoes/BASE-012.md`](verificacoes/BASE-012.md).

## Ordem sugerida de execução

1. `BASE-011`, ampliando validações de esquema e integridade.
2. `BASE-013`, versionando snapshots e diferenças.
3. `BASE-019`, tornando reproduzíveis os índices de busca da legislação (artigos
   novos hoje ficam fora do índice preservado).
4. `BASE-018`, recuperando os nomes reais de títulos e capítulos no adaptador de
   legislação.

## Regra de encerramento

Um item que altera conteúdo jurídico deve registrar a fonte oficial consultada, a data
da verificação, a mudança realizada e a validação executada. Correções puramente
técnicas ainda devem incluir teste que reproduza a falha anterior.
