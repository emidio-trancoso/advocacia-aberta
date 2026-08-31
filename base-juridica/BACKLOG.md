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
| `BASE-028` | Espelhos de acórdãos do STJ com link de fonte que não abre: a jurisprudência usava `@cod=<id do dataset CKAN>`, que não é o código do documento no SCON (cai em busca vazia), e a consulta processual apontava para o domínio legado `ww2.stj.jus.br` | Cada espelho traz link oficial que abre o documento: jurisprudência `@cod` inválida removida; consulta processual migrada para `processo.stj.jus.br?aplicacao=processos.ea` por número de registro, validada no portal. Mesma correção de domínio nos temas repetitivos. Gerador, dados e manifesto de snapshots corrigidos; auditor e 25 testes do motor verdes | **concluído em 2026-07-20** |

| `BASE-046` | O mesmo defeito do `BASE-028`, agora no STF: oito precedentes representativos de súmulas entregavam como inteiro teor um endereço do portal antigo (`www.stf.jus.br/portal/`), desativado — o link responde **404** e o leitor cai na tela de erro do STF em vez do acórdão. Seis dos oito são de repercussão geral (Temas 646, 671, 856, 31, 363 e 33), que é como o defeito chegou reportado. O coletor apenas repassava o `href` que a página da súmula ainda publica, sem conferir se abre | Nenhum link publicado aponta para rota desativada: o coletor descarta o inteiro teor dessas rotas e o precedente fica com a consulta por classe e número, que abre; auditor barra a reintrodução em qualquer JSON da base; teste de regressão reproduz a página com o link morto | **concluído em 2026-08-01** — 8 links corrigidos (7 em `sumulas_stf.json`, 1 em `sumulas_vinculantes.json`); verificação em [`verificacoes/BASE-046.md`](verificacoes/BASE-046.md) |

| `BASE-047` | O portal do STF devolve a **própria tela de erro** — o "404 Desculpe, mas não encontramos o que você está procurando", servido com **status 200** — em parte dos primeiros acessos vindos de outro site; o mesmo endereço abre ao ser recarregado. Diferente do `BASE-046`, o endereço está correto e não há o que trocar no acervo, mas quem consulta conclui que a fonte citada não existe. Do IP da verificação o comportamento não se reproduz (100 requisições, nenhuma falha); balanceamento, cookie de sessão e origem externa foram testados e descartados | Enquanto a fonte se comportar assim, a resposta que traz link de `portal.stf.jus.br` declara o comportamento e diz o que fazer; o aviso acompanha o link, não a família, e sai quando a fonte estabilizar | **mitigado em 2026-08-01** — aviso em temas de repercussão geral e em precedentes com inteiro teor no portal; verificação em [`verificacoes/BASE-047.md`](verificacoes/BASE-047.md) |

| `BASE-048` | A exportação oficial do STF traz os Temas de repercussão geral 1474, 1476 e 1477 ("Em julgamento") com o campo de título **vazio na própria fonte** (conferido no bruto da execução `2026-08-21-completa`), e a validação recusa o conjunto inteiro por campo obrigatório vazio. Com isso a recoleta de 21/08/2026 não pôde promover `temas_rg_stf`: o publicado ficou em 1.470 temas e a fonte está em 1.477 — 7 temas novos (1471–1477) e 10 atualizações de temas existentes (912, 1308, 1370, 1412, 1455, 1460, 1465, 1466, 1469, 1470) represados | Decidir e versionar o tratamento de tema recém-reconhecido ainda sem título na exportação: aceitar com a lacuna declarada na saída, derivar identificação provisória do leading case, ou excluir declaradamente até a fonte preencher. A validação passa a distinguir lacuna da própria fonte de falha de extração, e o conjunto volta a ser promovível sem afrouxar a regra para os demais campos | **aberto em 2026-08-21** · na recoleta de 31/08/2026 a exportação veio com todos os títulos preenchidos: o represamento se desfez e o conjunto foi promovido (1.479 temas, incluindo 1471–1479). O tratamento estrutural para a próxima lacuna da fonte segue pendente |

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
| `BASE-011` | Criar testes de esquema e integridade | CI valida JSON, campos obrigatórios, contagens, URLs, códigos e referências cruzadas | **concluído em 2026-07-19** |
| `BASE-012` | Testar qualidade da recuperação | Conjunto de consultas e resultados esperados mede precisão, cobertura e regressões | **concluído em 2026-07-17** |
| `BASE-013` | Versionar snapshots e diferenças | Manifesto por conjunto registra versão, checksum, coleta e resumo das mudanças | **concluído em 2026-07-19** |
| `BASE-014` | Retirar o identificador legado do motor | Adotar `Vade Mecum`/`vade-mecum` em caminhos, pacote, MCP, setup, skills, CI e documentação, sem alias com o nome anterior | **concluído em 2026-07-17** |
| `BASE-015` | Integrar auditoria estrutural ao fluxo de contribuição | GitHub Actions executa o auditor e apresenta seus achados em toda mudança da base | **concluído em 2026-07-17** |
| `BASE-016` | Endurecer coleta e promoção do pipeline | Allowlist cobre URL inicial e redirecionada; tipo de conteúdo, volume, re-promoção e estados não ativos têm gates e testes | **concluído em 2026-07-17** |
| `BASE-017` | Não existe detecção de mudança nem agendamento; a atualização depende de alguém lembrar | Comando barato responde "a fonte mudou?" por família, sem preparar candidatos; execução agendada publica o resultado; a promoção continua humana | **concluído em 2026-07-18** |
| `BASE-018` | O adaptador de legislação captura `title_name` genérico ("TÍTULO I") onde o snapshot legado tinha o nome real ("DOS PRINCÍPIOS FUNDAMENTAIS") | O adaptador extrai os nomes reais de títulos e capítulos das páginas do Planalto, com teste; o motor não consome o campo hoje, então o item é de qualidade do dado | **concluído em 2026-07-19** |
| `BASE-019` | O índice invertido de legislação (`indexes.keywords`) e os `keywords` por artigo são enriquecimentos legados sem processo reproduzível; a transformação os preserva do arquivo publicado, e artigos novos ficam fora do índice (invisíveis à busca textual quando o índice existe). Os diplomas incorporados pela expansão de julho de 2026 (piloto de 8 leis e fatias do manifesto `expansao/normas.json`) não têm índice curado e usam a busca em texto integral | Gerador determinístico versionado cobre todos os artigos publicados, como o `BASE-010` fez para súmulas; teste garante cobertura 1:1 | **concluído em 2026-07-19** |
| `BASE-020` | A busca de temas repetitivos usa somente os índices legados `keywords` e `terms`, sem fallback textual: os 57 temas 1406 a 1462, incorporados pela atualização de 2026-07-19, só são encontrados pela busca por número (que, até o `BASE-042`, exigia a forma rotulada — `tema 1420` encontrava, `1420` não) | Gerador determinístico cobre todos os temas publicados (como o `BASE-019` fez para a legislação) ou a busca ganha fallback textual; teste garante que nenhum tema publicado fica invisível | aberto |
| `BASE-021` | Falta o par vinculante do STF dos temas repetitivos do STJ — os temas de repercussão geral | Nova família reproduzível (adaptador, monitor, testes) integrada ao motor; busca cobre todos os temas por índice textual em memória, sem a lacuna do `BASE-020` | **concluído em 2026-07-19** |
| `BASE-022` | O flag de suspensão nacional dos temas de repercussão geral (art. 1.035, §5º, do CPC) não existe nas rotas estáticas do STF, só na base Qlik | Capturar quando houver rota estática estável; até lá, registrado como limitação declarada na família de RG | aberto |
| `BASE-023` | Decisões de controle concentrado do STF (ADI/ADC/ADO/ADPF) são Qlik-locked por desenho (Resolução STF 774/2022, export "sempre que possível"); a rota estática só cobre petições iniciais | Reavaliar em ~6 meses se surgir export estático confiável | aberto |
| `BASE-024` | Produtos curados do STJ ainda fora da base — Informativo de Jurisprudência, Pesquisa Pronta e Legislação Aplicada (SCON): as rotas óbvias devolvem 403/shell | Rodada dedicada para achar a rota estável de cada produto | aberto |
| `BASE-025` | Falta o Informativo STF — compilação institucional de julgados resumidos do STF | Nova família reproduzível (adaptador XLSX, monitor, testes) integrada ao motor; busca cobre todos os julgados; licença de reprodução registrada | **concluído em 2026-07-19** |
| `BASE-026` | Faltam os espelhos de acórdãos do STJ — acórdãos selecionados pela Secretaria de Jurisprudência | Nova família reproduzível (adaptador CKAN, merge mensal por id, monitor por `metadata_modified`, testes) integrada ao motor; escopo nos órgãos uniformizadores, com ementa | **concluído em 2026-07-19** |
| `BASE-027` | Os espelhos das 6 Turmas do STJ (~120 mil acórdãos, ~120 MB sem ementa) ficaram fora por volume | Reavaliar captura das Turmas se houver produto de busca dedicado ou compressão; hoje limitação declarada de escopo | aberto |
| `BASE-029` | O sinal de legislação do monitor dava alarme falso: passava a data ISO nua ao `curl --time-cond`, que o curl 8.x descarta em silêncio, emitindo GET incondicional; o Planalto respondia 200 sempre e os ~273 diplomas apareciam como "mudou" toda semana. O erro de coleta virava só "exit status 60/22", sem o motivo real | O monitor decide pela comparação `Last-Modified` × `gerado_em` (mesmo quando o servidor ignora o condicional) e envia a data já em formato HTTP; `executar_curl` preserva o stderr do curl no relatório; testes cobrem os dois casos | **concluído em 2026-07-22** |
| `BASE-030` | O monitor não alcança 4 fontes do STF pelo runner do GitHub Actions: `sumulas_stf`, `sumulas_vinculantes`, `temas_rg_stf` e `informativo_stf` falham com erro SSL de certificado (curl 60) | Diagnosticado: o STF entrega a **cadeia TLS incompleta** (repete o certificado-folha em vez de enviar o intermediário `GlobalSign GCC R6 AlphaSSL CA 2025`), então o cliente não liga a folha à raiz — `openssl verify` falha com `error 20` sem o intermediário e devolve `OK` com ele. Intermediário (certificado público de CA, obtido pela AIA do próprio cert do STF) versionado em `ferramentas/manutencao/certs/` e instalado no armazém de CAs pelo `monitorar-base.yml` — confirmado no CI (`Verify return code: 0 (ok)`). Sem `--insecure`: apenas completa uma cadeia legítima. Corrigir o TLS **revelou um segundo obstáculo por baixo**: o STF também responde `403` a IP de datacenter, tratado no `BASE-031` | **concluído em 2026-07-22** |
| `BASE-031` | Seis famílias ficavam sem verificação — `sumulas_stj`, `jurisprudencia_teses_stj`, `sumulas_stf`, `sumulas_vinculantes`, `temas_rg_stf` e `informativo_stf`: o monitor agendado recebia 403. A hipótese inicial — WAF bloqueando cliente que não fosse navegador — **estava errada** | O bloqueio é **por origem de rede, não por cliente**: o mesmo `curl`, com o mesmo User-Agent do monitor, recebe 403 de IP de datacenter e **200** de rede aceita, com conteúdo íntegro (676 súmulas do STJ, batendo com o snapshot; JT na edição 284; e os 4 endpoints do STF devolvendo de 21 KB a 9,3 MB). Navegador headless é desnecessário. O monitor da nuvem passa a pular essas famílias por `--excluir` (com o relatório **declarando** a exclusão, sem omissão silenciosa) e elas são verificadas por `ferramentas/manutencao/monitorar-fontes-restritas.sh`, agendado numa rede aceita. CKAN confirmado sem dataset das famílias do STJ (dos 21, só `precedentes-qualificados`) | **concluído em 2026-07-22** |
| `BASE-032` | Tratados e convenções anexados a decretos de promulgação usam numeração própria ("Artigo 1", "Artigo 2"), que o adaptador não reconhece como dispositivo — o texto não vira registro em lugar nenhum. Até 2026-07-23 ele aparecia por acidente, colado dentro do último `Art.` do decreto (o art. 2º do Decreto 3.413 carregava o Capítulo 1 da Convenção da Haia sobre sequestro internacional de crianças); a correção do parsing tirou essa contaminação e, com ela, a busca acidental nesse conteúdo | Capturar o anexo como dispositivos próprios, com identificador que não colida com os artigos do decreto promulgador, ou declarar a limitação no catálogo. Enquanto não houver captura, o texto da convenção não é pesquisável na base | aberto |
| `BASE-033` | Os temas de repercussão geral exibiam uma data só, rotulada "Julgamento", que na exportação do STF é a do julgamento da **repercussão geral** — enquanto a data da fixação da tese (`dataTese`) existia no snapshot e não era mostrada. O registro ficava internamente contraditório: efeito jurídico "tese com mérito julgado" ao lado de uma data anterior ao julgamento (Tema 29: 09/02/2008 exibida, tese fixada em 11/12/2014). Achado em teste externo do MCP | Cada evento aparece com o nome que a fonte lhe dá — "Julgamento da repercussão geral" e "Tese fixada em" —, a ausência da data da tese em tema com mérito decidido é declarada, e os temas repetitivos do STJ passam a exibir também a afetação; testes fixam os Temas 29, 66, 1001 e 314 | **concluído em 2026-07-23** |
| `BASE-034` | Quem consulta pelo MCP não via a cobertura da base: nem a data de cada snapshot, nem os diplomas indexados, nem as limitações conhecidas — tudo isso só existia no repositório. Resultado vazio era indistinguível de ausência de norma | Ferramenta `cobertura_da_base` derivada dos metadados publicados (nunca digitada), rodapé de proveniência com a data do snapshot em toda resposta de busca, e `data/limitacoes.json` espelhando os itens abertos do backlog, com teste que recusa omissão | **concluído em 2026-07-23** |
| `BASE-035` | A busca é léxica e perde o registro que descreve o instituto sem nomeá-lo: a consulta "nepotismo" não alcançava o Tema 1000 do STF nem a Súmula Vinculante 13, que descrevem a conduta sem escrever a palavra. Os temas repetitivos do STJ já expandiam sinônimos, mas dentro do índice e sem dizer a quem consulta | Léxico curado e versionado (`data/lexico_juridico.json`) com razão registrada por entrada; a busca direta roda primeiro e mantém a ordem, a expansão vem depois e é declarada na resposta; o corpus de avaliação mede ganho e ruído | **concluído em 2026-07-23** |
| `BASE-036` | As súmulas do STF entravam na base sem os precedentes representativos que o próprio STF publica na página do enunciado — a Súmula Vinculante 13 não trazia a ADC 12 nem os REs que a originaram, e o vínculo oficial com os temas de repercussão geral se perdia | Adaptador extrai a seção oficial de precedentes (processo, relator, órgão, julgamento, publicação, inteiro teor e tema de RG citado) e o motor a exibe; 227 precedentes promovidos nas 63 súmulas vinculantes, 69 com tema de RG vinculado | **concluído em 2026-07-23** |
| `BASE-037` | A Lei Complementar 214/2025 (IBS, CBS e Imposto Seletivo) não estava na base: consultas sobre split payment e créditos de IBS/CBS só encontravam referências indiretas em outras normas, embora a moldura constitucional da EC 132/2023 já constasse da CF do acervo. Achado em teste externo do MCP | Diploma capturado pelo pipeline da expansão, revisado e promovido (580 dispositivos, arts. 1º a 544, sem ausentes), com três casos julgados no corpus de avaliação | **concluído em 2026-07-23** |
| `BASE-038` | Os precedentes representativos só foram capturados para as 63 súmulas vinculantes; as 736 súmulas comuns do STF têm a mesma seção na página oficial e ficaram sem o campo | Rodada dedicada para as súmulas comuns, com o mesmo adaptador e revisão da amostra | aberto |
| `BASE-039` | A recuperação em diplomas longos perde o dispositivo central quando a consulta usa o substantivo e a lei usa o verbo: em LC 214/2025, "apropriação de créditos de IBS e CBS" não devolve o art. 47 ("poderá apropriar créditos"), porque o índice é léxico e não normaliza morfologia | Normalização morfológica (radicalização) no índice, ou outro mecanismo determinístico, medida no corpus de avaliação sem regressão nas consultas existentes | aberto |
| `BASE-040` | A varredura de diplomas faltantes cobriu as leis complementares (quadro oficial do Planalto, 23/07/2026), mas o índice anual de leis ordinárias não tem rota estática conhecida — as tentadas devolvem 404 | Achar a rota de índice por ano (ou fonte equivalente) e repetir o cruzamento com o acervo, apresentando a lista para curadoria antes de capturar | aberto |
| `BASE-041` | Cláusulas de alteração poluem a recuperação em leis recentes: na LC 227/2026, a consulta "comitê gestor competências" devolve os arts. 168, 169 e 174 — que apenas transcrevem alterações à LC 123 e à LC 214 — à frente dos arts. 2º, 11 e 12, que de fato distribuem competências. O caso julgado correspondente foi retirado do corpus de avaliação para não mascarar o defeito com um limiar frouxo | O ranking distingue dispositivo de conteúdo próprio de cláusula de alteração (ou equivalente determinístico); o caso `lc227-comite-gestor` volta ao corpus e passa | aberto |
| `BASE-042` | A consulta por número devolvia o registro **errado**, sem aviso, em três famílias. Nos temas repetitivos o lookup exigia o rótulo (`tema 981`); com o número puro (`981`) — como a CLI e o MCP recebem a consulta — caía no índice de tokens, e `terms["981"] = [1056]` porque o Tema 1056 cita `EREsp 1.121.981/RJ`. Nas súmulas, 22 números de 1 a 900 devolviam outra súmula (`741` → Súmula 199 do STJ, que cita a "Lei n. 5.741/71"). Na legislação, a regex do artigo não era ancorada e capturava número dentro de frase, devolvendo resultado único: "aviso prévio de 30 dias" na CLT devolvia o art. 30, revogado. O falso positivo saía formatado igual ao acerto, nos precedentes qualificados com o carimbo `OBSERVÂNCIA OBRIGATÓRIA QUANDO APLICÁVEL`. Achado nos temas por contribuição externa; extensão às demais famílias na revisão | Regra única nas três famílias: **consulta por número nunca cai no índice textual** — devolve o registro pedido ou vazio, nunca outro. Varredura numérica (temas 1–1500, RG 1–1500, súmulas 1–900) sem nenhum registro alheio no topo; 12 testes de regressão com guarda da premissa em `src/search/temas.test.ts` e `src/search/lookup_numerico.test.ts`; avaliação de recuperação idêntica. Verificação em [`verificacoes/BASE-042.md`](verificacoes/BASE-042.md) | **concluído em 2026-07-30** |
| `BASE-043` | A legislação não tem dimensão temporal: o motor devolve o texto **compilado** — a redação vigente na data da coleta — sem dizer que é uma redação entre várias, qual diploma a deu, nem se o dispositivo foi revogado. O Planalto anota cada mudança dentro do próprio texto já coletado (`(Redação dada pela Lei nº 14.181, de 2021)`), mas a anotação fica como prosa no campo `texto`, invisível à estrutura: artigo de redação originária e artigo revogado saem com a mesma aparência. São 30.247 anotações em 6.844 artigos de 219 diplomas, concentradas nos mais consultados (CLT 2.045, CF 1.191, CP 1.153, CPP 1.060). Levantado em contribuição externa de 2026-07-27 | Índice derivado reproduzível, no padrão do `BASE-019`, classifica as anotações por artigo preservando a **âncora** de cada uma — anotação de inciso nunca é apresentada como alteração do artigo inteiro; a resposta do MCP exibe situação e diplomas alteradores, mantendo o `Efeito jurídico: A CONFIRMAR`; nenhum artigo sem anotação recebe rótulo e em nenhuma hipótese o motor escreve "vigente", que a fonte não afirma. Fora de escopo: o texto das redações anteriores | **concluído em 2026-08-01** — 32.074 eventos em 7.309 artigos dos 277 diplomas (866 revogados, 395 vetados, 33 com vigência encerrada), resíduo de 2 anotações (0,006%) onde a fonte omite a espécie normativa; avaliação de recuperação idêntica à anterior. Verificação em [`verificacoes/BASE-043.md`](verificacoes/BASE-043.md) |
| `BASE-044` | O índice de vigência do `BASE-043` responde **que** o dispositivo mudou, por qual diploma e quando — mas a base não guarda o **texto** das redações anteriores. "Qual era a redação do art. 121 do CP em 2019?" continua sem resposta no acervo, e é a pergunta que decide caso em penal, tributário e contrato antigo. O que existe é o compilado do Planalto na data do snapshot, isto é, uma única redação por dispositivo | Capturar as versões históricas do dispositivo (ou fonte equivalente com texto por período de vigência) e ligá-las aos eventos já indexados, que trazem diploma e ano; enquanto não houver captura, limitação declarada | aberto |
| `BASE-045` | O léxico de equivalências do `BASE-035` não cumpria o critério que ele próprio declarava. Cinco das oito entradas não tinham caso julgado nenhum — foram herdadas da expansão silenciosa dos temas do STJ, com a razão registrada dizendo isso literalmente. Pior, a salvaguarda de concorrência estava invertida (`termos.length >= 3 ? 2 : 1`): a entrada de dois termos dispensava corroboração e bastava casar o mais genérico. Medido no acervo, `pix` devolvia 26 registros por equivalência (transferência de crédito de ICMS, para presídio federal, de pessoa condenada) e `cdi` devolvia 30 (juros compensatórios em desapropriação, imposto de renda sobre juros de mora), nenhum sobre o assunto consultado. O teste que existia só exercitava `nepotismo`, de seis termos, e por isso o buraco atravessou incólume | Concorrência exigida em toda entrada; léxico revisado por evidência, com `casos` apontando os identificadores de `avaliacao/consultas.json` que cada entrada sustenta e teste que recusa entrada sem caso; relações de espécie para gênero e de instituto para instituto declaradas inadmissíveis. Prova mecânica: removida qualquer entrada sobrevivente, a avaliação cai | **concluído em 2026-08-01** — de 8 entradas para 3, com 2 casos julgados novos (99 no total); verificação em [`verificacoes/BASE-045.md`](verificacoes/BASE-045.md) |

## Não capturar (decisão de escopo)

Sondados e deliberadamente fora da base por serem volume bruto sem curadoria ou
dados não jurídicos, não por dificuldade técnica:

- íntegras de decisões do DJ do STJ (CC-BY, mas ~1.200 docs/dia sem ementa/tese —
  caberia num produto de busca dedicado, não no Vade Mecum local);
- pautas futuras de julgamento do STJ (agenda operacional, não acervo);
- bases estatísticas do STF (Acervo, Partes, Recebidos, Baixados).

## Itens concluídos

### `BASE-026` — espelhos de acórdãos do STJ

- nova família `espelhos_stj`: adaptador `espelhos_stj_ckan_v1` percorre os
  pacotes CKAN dos órgãos, baixa os JSONs mensais (AAAAMMDD.json) e faz o merge
  incremental por `id` do documento; monitor por `metadata_modified` de cada
  pacote, como nos temas repetitivos;
- 11.133 acórdãos da Corte Especial e das 1ª, 2ª e 3ª Seções (os órgãos que
  uniformizam a jurisprudência), 588 com tese registrada; escopo decidido com o
  usuário: as 6 Turmas ficaram fora por volume (os dez órgãos somam ~132 mil
  acórdãos e ~120 MB sem ementa), registrado no `BASE-027`;
- campos curados por acórdão — ementa (100% preenchida, o conteúdo que sustenta a
  busca), tese, tema, referências legislativas, jurisprudência citada, classe,
  relator, órgão e data — mais os links oficiais de consulta processual e de
  jurisprudência; o inteiro teor e o histórico pré-2022 (recursos ZIP) ficam no
  link oficial;
- integração no motor: módulo `espelhos_stj.ts` com natureza documental própria
  `ESPELHO DE ACÓRDÃO` e efeito não vinculante por si só, busca por palavra-chave
  e por número de registro sobre índice textual em memória, ferramenta MCP
  `buscar_espelho`, CLI `espelho`, grupo de avaliação com três consultas julgadas
  e auditoria da família;
- resiliência de fonte: o coletor aceita `application/octet-stream` nos JSONs do
  CKAN (o STJ serve alguns assim) e a transformação ignora, registrando na
  proveniência, os meses sem lançamentos que a fonte publica como JSON
  malformado;
- a verificação completa está em
  [`verificacoes/BASE-026.md`](verificacoes/BASE-026.md).

### `BASE-025` — Informativo STF

- nova família `informativo_stf`: adaptador `informativo_stf_xlsx_v1` lê a planilha
  oficial `Dados_InformativosSTF.xlsx` (9,3 MB) por streaming com a biblioteca
  padrão (XLSX é zip+XML; a planilha usa strings inline e colunas numéricas), com
  conversão das datas de julgamento do serial do Excel;
- 11.567 julgados de 1.211 edições (numeradas de 1 a 1.222), 850 com tese
  registrada; escopo curado por julgado (processo, data, relator, órgão, situação,
  título, tese, resumo, matéria, ramo, repercussão geral, Tema RG e legislação),
  com o link oficial da edição e a licença de reprodução do STF registrada na
  proveniência; as colunas de notícia integral foram omitidas para manter a base
  local enxuta;
- integração no motor: módulo `informativo_stf.ts` (natureza compilação
  institucional, efeito não vinculante por si só), busca por edição e por
  palavra-chave sobre índice textual em memória que cobre os 11.567 julgados,
  ferramenta MCP `buscar_informativo`, CLI `informativo`, grupo de avaliação com
  três consultas julgadas e auditoria da família (contagem, link e licença);
- monitor barato por `If-Modified-Since` (o STF responde 304 quando a planilha não
  muda), ciente da pausa no recesso; validação, testes de pipeline (leitura de
  XLSX, conversão de data, transformação, cabeçalho e monitor);
- a verificação completa está em
  [`verificacoes/BASE-025.md`](verificacoes/BASE-025.md).

### `BASE-021` — temas de repercussão geral do STF

- nova família `temas_rg_stf` no pipeline: adaptador `temas_rg_stf_html_v1` lê a
  exportação oficial única (`portal.stf.jus.br/jurisprudenciaRepercussao/exportarDados.asp`,
  tabela HTML com rótulo `application/vnd.ms-excel`), corrige o mojibake UTF-8 por
  célula sem tocar no texto já correto e extrai os 15 campos, com página oficial
  por tema (`verTeseTema.asp?numTema=N`) e os links de detalhamento, manifestação
  e acórdão quando a fonte oferece;
- 1.470 temas, 1.300 com tese firmada; validação, monitor por contagem+situação e
  testes de pipeline (mojibake, transformação, cabeçalho, monitor);
- integração no motor: módulo `temas_rg_stf.ts` com busca por número e por
  palavra-chave sobre índice textual em memória que cobre todos os 1.470 temas —
  evita por desenho a lacuna do `BASE-020`; efeito jurídico `descreverEfeitoTemaRG`
  (observância obrigatória sob art. 927, III, do CPC só com mérito julgado);
  ferramenta MCP `buscar_tema_rg`, CLI `tema-rg`, grupo de avaliação com três
  consultas julgadas e auditoria estrutural da família;
- a verificação completa está em
  [`verificacoes/BASE-021.md`](verificacoes/BASE-021.md).

### `BASE-018` — nomes reais das divisões no adaptador de legislação

- `nome_da_divisao` extrai o nome real de títulos, capítulos e seções: usa o
  que sobra na própria linha do marcador ("CAPÍTULO II - DA COBRANÇA") ou, na
  diagramação mais comum do Planalto, o parágrafo seguinte ("TÍTULO I" seguido
  de "Dos Princípios Fundamentais"), pulando linhas vazias e remissões
  "(Vide ...)"; sem nome identificável, mantém a linha do marcador, como
  antes;
- demonstração offline sobre páginas reais já capturadas: CCOM ("TÍTULO I" →
  "DAS EMBARCAÇÕES"), Decreto 2.044/1908 ("CAPÍTULO IV" → "DO AVAL") e Lei
  15.040/2024 ("CAPÍTULO V" → "DA PRESCRIÇÃO");
- teste cobre nome na mesma linha, nome em parágrafo separado com remissão no
  meio, seção com nome em minúsculas e o fallback sem nome;
- o motor não consome o campo; os nomes reais entram nos dados publicados
  naturalmente nas próximas recapturas de cada diploma, com o diff da
  promoção mostrando a mudança de hierarquia;
- a verificação completa está em
  [`verificacoes/BASE-018.md`](verificacoes/BASE-018.md).

### `BASE-013` — snapshots e diferenças versionados

- o manifesto [`snapshots.json`](snapshots.json) (contrato em
  [`snapshots.schema.json`](snapshots.schema.json)) registra, por arquivo
  publicado das famílias rastreadas (273 diplomas de legislação, três conjuntos
  de súmulas, Jurisprudência em Teses e temas repetitivos), a versão, o
  SHA-256, a data de geração declarada, a contagem de registros e o resumo das
  mudanças promovidas (IDs adicionados, removidos e alterados, com amostra de
  até dez);
- o resumo é computado por `gerar_snapshots.py --escrever` contra o estado
  ainda versionado no Git — por isso o passo entra depois da promoção e antes
  do commit, e a primeira versão de cada arquivo é a linha de base (resumo
  nulo);
- `--verificar` confere SHA-256, contagens e cobertura sem rede, roda no CI em
  passo próprio e acusa promoção que esqueceu o manifesto;
- os índices derivados ficam de fora por já terem manifesto e verificação
  próprios (`BASE-010`/`BASE-019`);
- cinco testes cobrem coerência do manifesto publicado, cobertura, o resumo de
  mudanças, a linha de base e a detecção de SHA divergente;
- a verificação completa está em
  [`verificacoes/BASE-013.md`](verificacoes/BASE-013.md).

### `BASE-011` — testes de esquema e integridade

- `validar_integridade.py` (biblioteca padrão, como o resto do pipeline) valida
  em toda execução do CI: os manifestos versionados (`fontes.json` contra suas
  regras; índices derivados e expansão pelos próprios carregadores), os campos
  obrigatórios de cada registro publicado das quatro famílias, URLs em domínios
  oficiais com HTTPS, coerência chave ↔ campo identificador e o encadeamento
  `prev`/`next` da legislação;
- referências cruzadas: todo ID julgado no corpus de avaliação
  (dispositivos, súmulas, teses e temas) precisa existir na base
  correspondente, e o filtro de cada caso precisa apontar diploma existente —
  um julgamento órfão passa a quebrar o CI;
- registros retidos do snapshot legado são reconhecidos como artefatos
  preservados: a forma antiga de hierarquia (chaves `titulo`/`capitulo`, com
  nomes reais) não é acusada como defeito;
- quatro testes cobrem a base íntegra, a rejeição de URL não oficial e a
  detecção de referência órfã e de hierarquia fora do contrato;
- o GitHub Actions ganhou o passo "Validar esquemas, campos obrigatórios e
  referências cruzadas";
- a verificação completa está em
  [`verificacoes/BASE-011.md`](verificacoes/BASE-011.md).

### `BASE-019` — índices de legislação reproduzíveis

- o gerador local produz, por diploma, um índice derivado determinístico
  (`tokens-texto-integral-v1`) em `data/indices/lei_*_keywords.json`, cobrindo os
  15.757 dispositivos fora dos índices curados; a união com o índice curado
  preservado cobre os 21.541 dispositivos em relação 1:1, garantida por teste em
  Python e no motor;
- 314 dispositivos dos 8 diplomas com índice curado (ex.: CLT art. 7º, CPP arts.
  3º-A a 3º-F do juiz das garantias, CP arts. 121-B e 147-C, CC arts. 757 a 786)
  estavam invisíveis à busca textual e voltaram a ser recuperáveis, com teste de
  regressão;
- as stopwords são preservadas de propósito: o índice reproduz a semântica da
  busca em texto integral do motor (casamento por subpalavra, piso de 40%,
  empate pela ordem do documento), e a avaliação de recuperação retornou
  exatamente os mesmos resultados nos 74 casos (precisão global 0,8121;
  legislação 0,8295; recall, obrigatórios e MRR preservados);
- a substituição do índice curado do núcleo foi medida e reprovada pela
  avaliação (precisão de legislação cairia a 0,5528; a variante aditiva com a
  pontuação legada cairia a 0,5915), repetindo a lição do d4a0b30 — o esquema
  de pontuação curado permanece intacto;
- modelo e prompt são nulos; algoritmo, parâmetros, SHA-256 da fonte, contagens
  e relação de cobertura ficam registrados em cada arquivo derivado e no
  manifesto [`indices-derivados.json`](indices-derivados.json) (schema 2);
- `gerar_indices_derivados.py --verificar` confere igualdade byte a byte e o
  auditor acusa como P0 índice ausente, desatualizado ou com cobertura quebrada;
- a verificação completa está em
  [`verificacoes/BASE-019.md`](verificacoes/BASE-019.md).

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

1. `BASE-020`, cobrindo os temas repetitivos invisíveis à busca textual (1406 a
   1462), no padrão que o `BASE-019` estabeleceu para a legislação.

## Regra de encerramento

Um item que altera conteúdo jurídico deve registrar a fonte oficial consultada, a data
da verificação, a mudança realizada e a validação executada. Correções puramente
técnicas ainda devem incluir teste que reproduza a falha anterior.
