# Protocolo de atualização da base jurídica

Este protocolo reconstrói candidatos a snapshot a partir de fontes oficiais, registra
a coleta e mostra as diferenças antes de qualquer alteração na base publicada.

Ele reduz risco operacional; não substitui a revisão jurídica da vigência, do
conteúdo e das consequências de cada mudança.

## Garantia central

`coletar`, `transformar`, `validar`, `comparar` e `executar` escrevem somente em
`.atualizacao-base-juridica/<execucao>/`, ignorado pelo Git. Nenhum desses comandos
altera os JSONs consumidos pelo motor.

A publicação exige `promover --confirmar PROMOVER`. Antes de copiar o candidato, o
comando repete a validação, gera o relatório de diferenças e preserva os arquivos
anteriores em `backup/` dentro da execução. A mesma execução não pode ser promovida
duas vezes, evitando a sobrescrita desse backup.

Se o relatório contiver qualquer remoção, a promoção ainda é recusada. Depois da
conferência individual dos IDs, uma remoção intencional exige também
`--aceitar-remocoes`.

Uma alteração que supere o limiar versionado em `politica_promocao` — atualmente 25%
da coleção anterior e pelo menos 20 registros — também é recusada. Depois da revisão
do relatório, sua promoção exige adicionalmente `--aceitar-mudanca-volumosa`.

## Dependências

- Python 3.11 ou posterior;
- `curl` com suporte a HTTPS;
- acesso à internet para a etapa de coleta.

O pipeline usa somente a biblioteca padrão do Python. Não envia dados de casos nem
consulta serviços de IA.

## Fontes e transformações

O manifesto versionado está em [fontes.json](fontes.json), validado pelo contrato
[fontes.schema.json](fontes.schema.json).

| Conjunto | Origem oficial | Coleta | Transformação |
|---|---|---|---|
| Legislação | páginas compiladas do Planalto | um HTML por diploma | separa dispositivos, normaliza números como `1.072`, preserva hierarquia, retém registros antigos não reencontrados para revisão e deixa de fora a redação anterior que a fonte exibe **riscada** quando o caput está em vigor — inclusive quando o `<strike>` abre dentro do próprio `<p>`, padrão das páginas não compiladas (`BASE-050`); artigo inteiro riscado (revogado, sem substituto) segue retido com os seus parágrafos |
| Súmulas STJ | catálogo de Súmulas Anotadas do STJ | catálogo completo em HTML | extrai número, enunciado, estado, ramo, tema, órgão, data e URL oficial |
| Súmulas STF | aplicação das Súmulas no STF | catálogo e uma página de detalhe por verbete | junta estado do catálogo, enunciado/data do detalhe e classificação já curada quando existente |
| Súmulas vinculantes | aplicação das Súmulas Vinculantes no STF | catálogo e uma página de detalhe por verbete | mesma transformação do STF, com metadados de vinculância separados |
| Jurisprudência em Teses | páginas de cada edição no STJ | índice e edições de `1` até a mais recente observada | extrai edição, título, data, enunciados, julgados e links para o PDF oficial |
| Temas repetitivos | Portal de Dados Abertos do STJ | metadados CKAN, `Temas.csv` e `Processos.csv` | relaciona os CSVs por `sequencialPrecedente` e produz questões, teses, processo representativo e links |
| Temas de repercussão geral | exportação do Portal da Repercussão Geral do STF | uma tabela HTML única (rótulo `application/vnd.ms-excel`) | corrige mojibake por célula, extrai os 15 campos, monta a página oficial por tema e os links de detalhamento, manifestação e acórdão; tema que a fonte traz **sem título** (recém-reconhecido, "Em julgamento") fica fora da coleção e é declarado em `_meta.excluidosPorLacunaDaFonte`, com o link oficial — a lacuna é da fonte, não do candidato (`BASE-048`) |
| Informativo STF | planilha estruturada `Dados_InformativosSTF.xlsx` | um XLSX único (zip+XML, strings inline) lido por streaming | converte datas do serial do Excel, extrai os campos curados por julgado e monta o link oficial da edição; omite as colunas de notícia integral |
| Espelhos de acórdãos | Portal de Dados Abertos do STJ (CKAN), órgãos uniformizadores | JSONs mensais por órgão (metadados CKAN + `AAAAMMDD.json`) | merge incremental por `id`, campos curados por acórdão (ementa, tese, tema, referências) + links; ignora e registra meses malformados |

Os índices `sumulas_keywords.json` e `sumulas_stf_keywords.json` (súmulas,
`BASE-010`) e os 270 arquivos `indices/lei_*_keywords.json` (legislação,
`BASE-019`) são enriquecimentos derivados, não fontes jurídicas. Eles são
produzidos localmente a partir dos textos publicados, sem modelo ou prompt
externo. No índice de legislação, cada diploma tem um arquivo com os tokens dos
dispositivos que o índice curado preservado (`indexes.keywords`) não cobre; a
união dos dois cobre todos os dispositivos em relação 1:1, e as stopwords são
preservadas para que o ranking reproduza a busca em texto integral do motor.
Algoritmos, parâmetros, fontes, relação 1:1 e data estão em
[`indices-derivados.json`](indices-derivados.json).

Para conferir que os arquivos publicados correspondem exatamente ao processo
versionado:

```bash
python3 ferramentas/manutencao/gerar_indices_derivados.py --verificar
```

Depois de revisar uma atualização das súmulas **ou promover qualquer mudança de
legislação**, regenere os índices com:

```bash
python3 ferramentas/manutencao/gerar_indices_derivados.py --escrever
```

Cada saída registra o SHA-256 da fonte, o total de registros, a versão do gerador e os
parâmetros. Alterar o algoritmo exige nova versão no manifesto e revisão das diferenças
antes da promoção. O auditor estrutural acusa como P0 um índice de legislação
ausente ou dessincronizado do diploma (comparação de SHA-256), então o CI
bloqueia promoções que esqueçam a regeneração — artigos novos nunca mais ficam
invisíveis à busca.

## Expansão da legislação

Diplomas novos entram pela expansão dirigida pelo manifesto
[`expansao/normas.json`](expansao/normas.json), em fatias por grupo:

```bash
python3 ferramentas/manutencao/gerar_expansao_legislacao.py --listar
python3 ferramentas/manutencao/gerar_expansao_legislacao.py --materializar <grupo>
python3 ferramentas/manutencao/atualizar_base_juridica.py executar \
  --execucao <data>-<grupo> --conjunto legislacao_<grupo>
python3 ferramentas/manutencao/revisar_expansao.py \
  --execucao <data>-<grupo> --conjunto legislacao_<grupo>
python3 ferramentas/manutencao/atualizar_base_juridica.py promover \
  --execucao <data>-<grupo> --conjunto legislacao_<grupo> --confirmar PROMOVER
```

Materializar cria o conjunto em `fontes.json`, stubs vazios em `data/` e as
entradas geradas do registro do motor; como o diploma novo parte de coleção
vazia, o diff da execução mostra somente adições e o gate volumétrico exige
`--aceitar-mudanca-volumosa` depois da revisão. O relatório de revisão confere
contagens, sequência de numeração, cabeçalho oficial contra o manifesto e os
dispositivos excluídos por pertencerem a outra norma.
`gerar_expansao_legislacao.py --verificar` confere a sincronia
(manifesto ↔ `fontes.json` ↔ registro do motor ↔ `data/`) e roda nos testes.
Depois da promoção de cada fatia, regenere os índices derivados
(`gerar_indices_derivados.py --escrever`), atualize os fixtures de cobertura,
acrescente consultas julgadas à avaliação e registre a fatia no catálogo.

## Monitoramento de mudanças

O subcomando `monitorar` responde, sem preparar candidatos nem tocar nos dados
publicados, à pergunta "alguma fonte mudou desde o snapshot promovido?":

```bash
python3 ferramentas/manutencao/atualizar_base_juridica.py monitorar
python3 ferramentas/manutencao/atualizar_base_juridica.py monitorar --conjunto legislacao --json
```

Sinal utilizado por família:

| Família | Sinal | Custo |
|---|---|---|
| Legislação | GET condicional (`If-Modified-Since` com o `gerado_em` do snapshot); quando o Planalto honra o cabeçalho responde 304, e quando o ignora (responde 200) o monitor compara o `Last-Modified` devolvido com o `gerado_em` e só sinaliza se a fonte for mais nova | ~zero a 1 página por diploma |
| Súmulas STJ | contagem de súmulas no catálogo oficial vs snapshot | download de 1 página |
| Súmulas STF e vinculantes | contagem por estado (ativas, canceladas etc.) no catálogo vs snapshot | download de 1 página |
| Jurisprudência em Teses | edição mais recente do índice vs snapshot | download de 1 página |
| Temas repetitivos | `last_modified` dos recursos na API CKAN do STJ vs `generatedAt` do snapshot | 1 JSON pequeno |
| Temas de repercussão geral | contagem total e por situação na exportação oficial do STF vs snapshot (os temas omitidos por título vazio contam no snapshot); sinaliza também quando um tema omitido ganha título na fonte | download de 1 arquivo |
| Informativo STF | GET condicional (`If-Modified-Since` com o `Last-Modified` do snapshot); o STF responde 304 quando a planilha não mudou | ~zero quando não há mudança |
| Espelhos de acórdãos | `metadata_modified` do pacote CKAN de cada órgão vs snapshot | metadados de 4 pacotes |

Limitações declaradas do sinal:

- ele indica que **vale preparar um candidato**; a confirmação material vem do
  relatório de diferenças da execução completa;
- `Last-Modified` do Planalto pode mudar por republicação sem alteração
  normativa (observado em republicação em massa de 23/04/2026); como muitas
  páginas do Planalto ignoram o `If-Modified-Since` e respondem 200, o monitor
  não trata todo 200 como mudança — só sinaliza quando o `Last-Modified`
  devolvido é posterior ao snapshot;
- mudanças de estado de súmulas STJ sem alteração de contagem, revisões de
  edições antigas da Jurisprudência em Teses e alterações de enunciado no STF
  não são captadas pelos sinais baratos;
- reenvio de conteúdo idêntico no CKAN do STJ conta como mudança (os hashes dos
  recursos não são publicados pelo portal);
- alteração de tese de tema de repercussão geral sem mudança de contagem ou de
  situação não é captada pelo sinal do STF; o Informativo STF pausa no recesso
  (jan/jul), então uma semana sem nova edição não é erro do monitor;
- falha de uma fonte não interrompe o monitor: aparece como `erro` no relatório.

O GitHub Actions `monitorar-base.yml` executa o monitor semanalmente e abre ou
atualiza uma issue quando há sinais de mudança ou erros. Nenhuma etapa
automatizada promove dados: a preparação, a revisão e a promoção continuam
seguindo este protocolo.

### Registro de conferência (`verificacoes.json`)

`snapshots.json` responde "quando isto mudou por último?". Falta a outra
pergunta: **"quando isto foi conferido por último?"**. Sem ela, uma família
conferida hoje e estável desde junho parece abandonada desde junho — o dado
está certo, a leitura engana. O registro versionado
[`verificacoes.json`](verificacoes.json) responde isso, por conjunto:

```bash
# sinal barato (o que o monitor semanal faz)
python3 ferramentas/manutencao/atualizar_base_juridica.py monitorar --registrar

# conferência forte, a partir do relatório de diferenças de uma recoleta
python3 ferramentas/manutencao/atualizar_base_juridica.py comparar \
  --execucao <execucao> --conjunto todos --registrar
```

Três decisões que o registro precisa respeitar:

- **`metodo` separa as duas forças.** `sinal` é o monitor barato e **não vê
  alteração de enunciado**; `recoleta` compara o conteúdo inteiro contra a fonte.
  `recoletado_em` guarda a última conferência forte e nunca é sobrescrito por um
  sinal — um sinal de hoje não apaga o fato de que a recoleta foi ontem.
- **Merge por conjunto, nunca substituição.** O monitor da nuvem pula as seis
  famílias que exigem rede aceita; elas são conferidas de outro ponto. Reescrever
  o arquivo inteiro faria a última execução apagar a conferência da outra.
- **Erro não é conferência.** Se a fonte não respondeu (403, timeout), a data
  anterior permanece e o erro é registrado à parte, em `ultimo_erro_em`. Afirmar
  frescor sobre o que ninguém verificou seria o mesmo vício que o projeto combate.

Por que a distinção não é teórica: em **29/07/2026** o sinal barato deu
"sem mudança" em todas as 288 fontes, e a recoleta completa encontrou **duas teses
da Jurisprudência em Teses com o enunciado substituído** — uma delas com o sentido
invertido (`JT_087_T09`, revista sob o rito do art. 1.036 do CPC, Tema 1353) — mais
51 súmulas do STF sem os precedentes. Quando a pergunta é "está atualizado de
fato?", a resposta vem da recoleta, não do sinal.

### Fontes que exigem rede aceita (STF e SCON do STJ)

Os portais do STF e o SCON do STJ recusam requisição vinda de **IP de datacenter**:
o monitor agendado recebe `403` em seis famílias — `sumulas_stj`,
`jurisprudencia_teses_stj`, `sumulas_stf`, `sumulas_vinculantes`, `temas_rg_stf` e
`informativo_stf`. Não é bloqueio a "robô": o mesmo `curl`, com o mesmo
User-Agent, responde `200` de uma rede aceita e devolve o conteúdo íntegro.
Navegador headless não resolve nem é necessário — o que muda é a origem da
requisição, não o cliente.

No caso do STF havia **dois** obstáculos empilhados: a cadeia TLS incompleta
(resolvida pelo intermediário versionado em `ferramentas/manutencao/certs/`) e,
por baixo dela, o mesmo `403` por origem. Corrigir o certificado era necessário e
revelou o segundo.

Por isso o monitor da nuvem **pula** essas famílias, e o relatório **declara** a
exclusão (nada some em silêncio):

```bash
python3 ferramentas/manutencao/atualizar_base_juridica.py monitorar \
  --excluir sumulas_stj,jurisprudencia_teses_stj,sumulas_stf,sumulas_vinculantes,temas_rg_stf,informativo_stf
```

Elas são verificadas de uma máquina em rede aceita, com a mesma disciplina (sinal
barato, sem preparar candidato, sem tocar em dado publicado). Quando há sinal, o
script abre ou comenta uma issue:

```bash
bash ferramentas/manutencao/monitorar-fontes-restritas.sh
```

Para rodar semanalmente no macOS, crie um agente em
`~/Library/LaunchAgents/org.advocaciaaberta.monitorar-stj.plist` apontando
`ProgramArguments` para esse script, com `StartCalendarInterval` no dia e hora
desejados e `PATH` incluindo os diretórios de `python3` e `gh` (o `launchd` roda
com ambiente mínimo). Depois:

```bash
launchctl load ~/Library/LaunchAgents/org.advocaciaaberta.monitorar-stj.plist
launchctl list | grep monitorar-stj
```

Se a máquina estiver desligada no horário, o `launchd` executa na volta. Em Linux,
o equivalente é um *timer* do systemd ou uma entrada de `cron`.

## Execução recomendada

Use uma identificação legível, normalmente a data da coleta:

```bash
python3 ferramentas/manutencao/atualizar_base_juridica.py executar \
  --execucao 2026-07-17 \
  --conjunto temas_repetitivos_stj
```

Para processar todas as famílias primárias:

```bash
python3 ferramentas/manutencao/atualizar_base_juridica.py executar \
  --execucao 2026-07-17 \
  --conjunto todos
```

Também é possível interromper e conferir cada etapa:

```bash
python3 ferramentas/manutencao/atualizar_base_juridica.py coletar \
  --execucao 2026-07-17 --conjunto sumulas_stj
python3 ferramentas/manutencao/atualizar_base_juridica.py transformar \
  --execucao 2026-07-17 --conjunto sumulas_stj
python3 ferramentas/manutencao/atualizar_base_juridica.py validar \
  --execucao 2026-07-17 --conjunto sumulas_stj
python3 ferramentas/manutencao/atualizar_base_juridica.py comparar \
  --execucao 2026-07-17 --conjunto sumulas_stj
```

Conjuntos separados por vírgula podem compartilhar a mesma execução. `listar` mostra
os identificadores aceitos.

## Conferência completa: "está atualizado de fato?"

O monitor semanal responde "alguma fonte deu sinal de mudança?". Ele **não**
responde "o que está publicado confere com a fonte oficial hoje?" — e as duas
perguntas não têm a mesma resposta. Em 29/07/2026 o sinal deu "sem mudança" nas
288 fontes e a recoleta encontrou duas teses com o enunciado substituído, uma
delas com o sentido invertido.

Quando fazer: antes de confiar na base para trabalho de peso, depois de um
período longo sem promoções, ou sempre que a pergunta for essa. Não precisa ser
frequente — o sinal semanal cobre o dia a dia.

Custo real medido em 29/07/2026: **1.569 downloads, 181 MB, cerca de 12 minutos**
de coleta e 281 MB na área de trabalho (que é descartável e não versionada).

### O roteiro, em ordem

```bash
# 1. Recoleta tudo e compara com o publicado. NÃO altera nada publicado.
#    Rode da sua máquina: seis famílias do STF e do SCON recusam IP de datacenter.
python3 ferramentas/manutencao/atualizar_base_juridica.py executar \
  --execucao $(date +%F)-completa --conjunto todos

# 2. Leia o resumo. Linhas "+0 -0 ~0" são fontes idênticas à oficial.
cat .atualizacao-base-juridica/$(date +%F)-completa/relatorios/diferencas.md
```

**Se todas as linhas forem `+0 -0 ~0`**, a base está atualizada de fato. Registre a
conferência e pare — não promova nada:

```bash
python3 ferramentas/manutencao/atualizar_base_juridica.py comparar \
  --execucao $(date +%F)-completa --conjunto todos --registrar
```

Promover conjunto sem diferença de conteúdo só troca carimbo de data, cria versão
nova no manifesto e polui o histórico. Não faça.

**Se houver diferença**, leia o que mudou antes de decidir — é aqui que entra o
julgamento jurídico, e nenhuma automação substitui isso. Siga
[Revisão antes de promover](#revisão-antes-de-promover), promova **somente os
conjuntos que mudaram** e complete a sequência obrigatória:

```bash
python3 ferramentas/manutencao/atualizar_base_juridica.py promover \
  --execucao $(date +%F)-completa --conjunto <só os que mudaram> --confirmar PROMOVER

python3 ferramentas/manutencao/gerar_indices_derivados.py --escrever
python3 ferramentas/manutencao/gerar_snapshots.py --escrever
python3 ferramentas/manutencao/auditar_base_juridica.py --strict
python3 -m unittest discover -s ferramentas/manutencao/tests -p 'test_*.py'
(cd ferramentas/pesquisa/vade-mecum && bun run typecheck && bun test)

# registra a conferência forte, agora sobre a base já corrigida
python3 ferramentas/manutencao/atualizar_base_juridica.py comparar \
  --execucao $(date +%F)-completa --conjunto todos --registrar
```

Depois é só commit e PR. O CI recusa promoção sem manifesto atualizado ou com
índice dessincronizado, então esqueceu um passo, ele avisa.

### O que acontece sozinho depois do merge

Nada mais precisa ser feito à mão:

| Quando | O quê |
|---|---|
| até 10 min | a VM puxa a `main` e reinicia o MCP com os dados novos |
| todo dia, 12h | o site reextrai o acervo e republica (só se os dados mudaram) |
| até 15 min depois | a VM serve o site novo |

### Como ler o que aparece no site

Os dois carimbos de cada acervo respondem coisas diferentes, e é proposital:
**"atualizado em"** é a última mudança promovida; **"conferido em"** é a última
verificação contra a fonte oficial. Um acervo parado há semanas e conferido hoje
está em dia — a fonte é que não mudou.

## Artefatos da execução

```text
.atualizacao-base-juridica/<execucao>/
├── bruto/                 # respostas oficiais e cabeçalhos HTTP
├── candidatos/            # JSONs normalizados ainda não publicados
├── relatorios/
│   ├── validacao.json     # erros estruturais e de rastreabilidade
│   ├── diferencas.json    # IDs adicionados, removidos e alterados
│   └── diferencas.md      # resumo legível da comparação
├── backup/                # criado somente pela promoção
├── execucao.json          # URL, horário, bytes, ETag, Last-Modified e SHA-256
└── promocao.json          # recibo dos arquivos efetivamente promovidos
```

## Revisão antes de promover

1. Confira a URL inicial e a URL efetiva registradas no recibo. O coletor aceita
   somente HTTPS nos domínios oficiais permitidos e rejeita redirecionamento externo.
2. Leia `validacao.json`; qualquer erro bloqueia a promoção.
3. Leia `diferencas.md` e examine no JSON os IDs adicionados, removidos e alterados.
4. Em legislação, revise `registros_retidos_sem_correspondencia`: o pipeline preserva
   esses dispositivos em vez de presumir que desapareceram da ordem jurídica.
5. Em súmulas e precedentes, confira especialmente cancelamentos, revisões e mudanças
   de situação.
6. Registre no commit a fonte consultada, a data e a justificativa jurídica.
7. Só então promova o conjunto aprovado:

```bash
python3 ferramentas/manutencao/atualizar_base_juridica.py promover \
  --execucao 2026-07-17 \
  --conjunto temas_repetitivos_stj \
  --confirmar PROMOVER
```

Se e somente se as remoções do relatório tiverem sido confirmadas na fonte, acrescente
`--aceitar-remocoes` ao comando.

Se o gate volumétrico for acionado, examine os IDs alterados e acrescente
`--aceitar-mudanca-volumosa` somente depois de confirmar que a mudança em massa é
intencional.

Depois da promoção — e **antes do commit correspondente** — regenere os
índices derivados (obrigatório para súmulas e legislação; a auditoria acusa
índice dessincronizado), atualize o manifesto de versões dos snapshots (o
resumo das mudanças é computado contra o estado ainda versionado no Git) e
execute a auditoria e os testes do motor:

```bash
python3 ferramentas/manutencao/gerar_indices_derivados.py --escrever
python3 ferramentas/manutencao/gerar_snapshots.py --escrever
python3 ferramentas/manutencao/auditar_base_juridica.py --strict
python3 -m unittest discover -s ferramentas/manutencao/tests -p 'test_*.py'
cd ferramentas/pesquisa/vade-mecum
bun run typecheck
bun test
```

O manifesto [`snapshots.json`](snapshots.json) (contrato em
[`snapshots.schema.json`](snapshots.schema.json)) registra, por arquivo
publicado, a versão, o SHA-256, a data de geração, a contagem de registros e o
resumo das mudanças promovidas (quantos IDs foram adicionados, removidos e
alterados, com amostra). `gerar_snapshots.py --verificar` roda no CI e acusa
promoção sem o manifesto atualizado.

## Política de falha

- URL inicial ou redirecionada fora da allowlist, tipo de conteúdo incompatível,
  download vazio, erro HTTP, catálogo sem registros ou adaptador desconhecido encerra
  a execução;
- JSON inválido, contagem divergente, campo obrigatório vazio, caminho absoluto ou
  URL fora dos domínios oficiais falha na validação;
- a auditoria estrutural roda em modo estrito no CI e bloqueia regressões detectáveis;
- falha de validação bloqueia a promoção;
- qualquer remoção bloqueia a promoção até receber autorização adicional explícita;
- mudança acima de 25% da coleção e de 20 registros exige autorização adicional;
- uma execução já promovida não pode sobrescrever seu backup;
- artefatos brutos não são versionados por padrão; seus checksums e cabeçalhos ficam
  no recibo local da execução.
