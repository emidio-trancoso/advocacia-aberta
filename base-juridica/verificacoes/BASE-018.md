# BASE-018 — nomes reais das divisões no adaptador de legislação

| Campo | Valor |
|---|---|
| Verificação | 19 de julho de 2026 (UTC) |
| Escopo | adaptador `planalto_html_v1` (`transformar_legislacao`); qualidade do dado de hierarquia |
| Modelo externo | nenhum |

## Limitação anterior

O adaptador preenchia `title_name`, `chapter_name` e `section_name` com a
própria linha do marcador ("TÍTULO I"), porque o Planalto costuma separar o
rótulo do nome real em parágrafos distintos. O snapshot legado tinha os nomes
reais ("DOS PRINCÍPIOS FUNDAMENTAIS") — os registros retidos preservam essa
forma, como o `BASE-011` documentou.

## Mudança realizada

`nome_da_divisao` resolve o nome em três passos, nesta ordem:

1. o que sobra na própria linha depois do rótulo
   ("CAPÍTULO II - DA COBRANÇA" → "DA COBRANÇA");
2. senão, o parágrafo seguinte, pulando linhas vazias e remissões
   "(Vide ...)", desde que não seja artigo, outro marcador estrutural ou
   parágrafo longo demais para ser um nome (mais de 120 caracteres, olhando
   até três parágrafos adiante);
3. senão, a própria linha do marcador, como antes — nada fica pior.

## Demonstração em páginas reais (offline, brutos já capturados)

| Página | Extração |
|---|---|
| Código Comercial de 1850 | "TÍTULO I" → "DAS EMBARCAÇÕES"; "TÍTULO III" → "DOS CAPITÃES OU MESTRES DE NAVIO" |
| Decreto 2.044/1908 | "TÍTULO I" → "Da letra de cambio"; "CAPÍTULO IV" → "DO AVAL" |
| Lei 15.040/2024 | "CAPÍTULO II" → "DOS SEGUROS DE DANO"; "CAPÍTULO V" → "DA PRESCRIÇÃO" |

## Validação executada

```bash
python3 -m unittest ferramentas.manutencao.tests.test_atualizar_base_juridica
```

O teste novo cobre o nome na mesma linha do marcador, o nome em parágrafo
separado com remissão "(Vide ...)" no meio, a seção com nome em minúsculas e o
fallback quando a página não traz nome. Os testes anteriores do adaptador
(fim_antes, ortografia antiga, retenção de registros) continuam passando.

## Limitações declaradas

- o motor de busca não consome os campos de nome; o item é de qualidade do
  dado, como registrado no critério de aceite;
- os dados publicados só ganham os nomes reais na próxima recaptura de cada
  diploma — a mudança de hierarquia aparecerá no relatório de diferenças da
  promoção correspondente e no resumo do manifesto de snapshots (`BASE-013`);
- divisões acima de título (PARTE, LIVRO) continuam fora do rastreamento do
  adaptador, como antes.
