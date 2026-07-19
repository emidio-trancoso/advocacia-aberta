# BASE-026 — Espelhos de acórdãos do STJ

**Data da verificação:** 2026-07-19
**Fonte oficial:** Portal de Dados Abertos do STJ (CKAN) —
`https://dadosabertos.web.stj.jus.br/` (pacotes `espelhos-de-acordaos-*`).

## Problema

A base tinha os temas repetitivos e a Jurisprudência em Teses do STJ, mas não os
espelhos de acórdãos — as fichas de acórdãos selecionados pela Secretaria de
Jurisprudência por trazerem "novidades quanto a teses jurídicas".

## O que foi feito

- **Coleta reproduzível:** o adaptador `espelhos_stj_ckan_v1` lê o `package_show`
  de cada órgão, enumera os JSONs mensais (`AAAAMMDD.json`) e os baixa; a
  transformação faz o merge incremental por `id` do documento (espelhos
  republicados em meses posteriores sobrescrevem o anterior). A detecção de
  mudança usa o `metadata_modified` do pacote CKAN, como nos temas repetitivos.
- **Escopo — órgãos uniformizadores (decidido com o usuário):** só a Corte
  Especial e as 1ª, 2ª e 3ª Seções, que uniformizam a jurisprudência do STJ. As
  seis Turmas ficaram de fora por volume: os dez órgãos somam ~132 mil acórdãos e
  ~120 MB mesmo sem ementa, contra 11.133 acórdãos e ~33 MB dos uniformizadores.
  A limitação está registrada no `BASE-027`.
- **Campos e findability:** cada acórdão guarda a **ementa** (100% preenchida — o
  conteúdo que sustenta a busca), a tese e o tema quando existirem (588 com tese),
  as referências legislativas e a jurisprudência citada, além de classe, relator,
  órgão, data e os links oficiais. A data de publicação é extraída do formato do
  DJ ("DJE DATA:31/05/2022" → "31/05/2022"). O `termosAuxiliares` foi avaliado e
  descartado (preenchido em 41 de 11.133); o inteiro teor e o histórico pré-2022
  (recursos ZIP) ficam no link oficial.
- **Resiliência de fonte:** o coletor passou a aceitar `application/octet-stream`
  nos JSONs do CKAN (o STJ serve alguns recursos assim), com a estrutura validada
  depois; a transformação ignora, registrando em `_meta.source`, os meses sem
  lançamentos que a fonte publica como JSON malformado (um `}` a mais) — hoje,
  `segunda-secao/20240229.json`.
- **Motor:** módulo `espelhos_stj.ts` com natureza documental própria
  `ESPELHO DE ACÓRDÃO` e efeito `NÃO VINCULANTE POR SI SÓ` (confira eventual tese
  qualificada). Busca por palavra-chave (ementa, tese, tema, classe, referências,
  jurisprudência citada) e por número de registro sobre índice textual em
  memória; ferramenta MCP `buscar_espelho`, subcomando de CLI `espelho` e inclusão
  na busca ampla. Links oficiais: consulta processual por número de registro e
  pesquisa de jurisprudência por código.

## Números observados

- 11.133 acórdãos: Corte Especial 3.337, Primeira Seção 3.986, Segunda Seção
  2.164, Terceira Seção 1.646; 588 com tese registrada.
- Ementa preenchida em 11.127 acórdãos (100%), média ~1.890 caracteres; arquivo
  `espelhos_stj.json` com ~33 MB.
- Codificação limpa (JSON do CKAN em UTF-8; nenhum mojibake — as ocorrências de
  "Ã" são "ÇÃO"/"SÃO"/"NÃO" em caixa alta).

## Testes e validação

- pipeline: `data_publicacao_espelho`, leitura de JSON em lista, transformação
  (campos curados, links, ementa, mês malformado ignorado) e monitor
  (`metadata_modified` mais novo vs igual);
- motor: contagem `TOTAL_ESPELHOS_STJ === 11133` e `TOTAL_ORGAOS_ESPELHOS === 4`,
  descrição MCP da ferramenta e links do formatador;
- avaliação: grupo `espelhos_stj` com três consultas julgadas pelo conteúdo
  (honorários por apreciação equitativa, IRPJ/CSLL sobre juros SELIC na repetição
  de indébito, TUST/TUSD na base do ICMS), precisão@5 0,9333 (limiar 0,70);
  global preservado (precisão 0,8025; recall 0,9907; MRR 1,0);
- bateria completa aprovada: `auditar_base_juridica.py --strict`, unittest,
  `bun run typecheck`, `bun test`, `bun run avaliar`.

## Limitações declaradas

- espelho é ficha de acórdão selecionado: um acórdão isolado não é vinculante por
  si só; confira o inteiro teor no link e a existência de tese qualificada;
- as 6 Turmas e o histórico pré-2022 não foram capturados por escopo (`BASE-027`);
- o sinal de mudança é o `metadata_modified` do CKAN: reenvio de conteúdo idêntico
  ainda contaria como mudança, como nos temas repetitivos.
