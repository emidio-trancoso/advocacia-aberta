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
| `BASE-010` | Índices de palavras-chave não têm processo reproduzível | Versionar geração, modelo, prompt/parâmetros, relação com a base e teste de cobertura | aberto |

## P2 — robustez e evolução

| ID | Trabalho | Critério de aceite | Estado |
|---|---|---|---|
| `BASE-011` | Criar testes de esquema e integridade | CI valida JSON, campos obrigatórios, contagens, URLs, códigos e referências cruzadas | aberto |
| `BASE-012` | Testar qualidade da recuperação | Conjunto de consultas e resultados esperados mede precisão, cobertura e regressões | aberto |
| `BASE-013` | Versionar snapshots e diferenças | Manifesto por conjunto registra versão, checksum, coleta e resumo das mudanças | aberto |
| `BASE-014` | Neutralizar o nome legado `Delfus` | Prosa pública usa “base jurídica local”; migrar `busca_delfus` para `motores/pesquisa-juridica/` preservando compatibilidade temporária | aberto |
| `BASE-015` | Integrar auditoria estrutural ao fluxo de contribuição | GitHub Actions executa o auditor e apresenta seus achados em toda mudança da base | **concluído em 2026-07-17** |
| `BASE-016` | Endurecer coleta e promoção do pipeline | Allowlist cobre URL inicial e redirecionada; tipo de conteúdo, volume, re-promoção e estados não ativos têm gates e testes | **concluído em 2026-07-17** |

## Itens concluídos

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

## Ordem sugerida de execução

1. `BASE-010`, tornando os índices derivados reproduzíveis.
2. `BASE-011` a `BASE-014`, transformando as garantias em manutenção contínua.

## Regra de encerramento

Um item que altera conteúdo jurídico deve registrar a fonte oficial consultada, a data
da verificação, a mudança realizada e a validação executada. Correções puramente
técnicas ainda devem incluir teste que reproduza a falha anterior.
