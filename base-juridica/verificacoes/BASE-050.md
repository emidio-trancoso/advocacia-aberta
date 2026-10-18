# BASE-050 — Redação anterior riscada na fonte entrava no artigo sem marca

**Data da verificação:** 2026-10-17
**Famílias:** `legislacao`
**Origem:** contribuição da comunidade — issue #26 (06/10/2026), com reprodução,
cinco exemplos conferidos na página do Planalto e a causa provável apontada no
código.
**Severidade:** alta — a redação revogada saía **antes** da vigente, sob o rótulo
"FONTE OFICIAL", e a busca por palavras casava com o texto antigo.

## Sintoma

```text
legislacao "26" L9514
   → § 2º O contrato definirá o prazo de carência após o qual será expedida a intimação.
     § 2º O contrato poderá estabelecer o prazo de carência, após o qual será
     expedida a intimação. (Redação dada pela Lei nº 14.711, de 2023)
```

Dois "§ 2º" no mesmo artigo. Na página oficial o primeiro está dentro de
`<strike>` (redação anterior); o segundo, não. O bloco "Alterações anotadas na
fonte" dizia que o § 2º mudou, mas nada dizia qual das duas redações exibidas era
a vigente. O mesmo acontecia no art. 27 da Lei 9.514, no art. 3º, III, da Lei
8.009, no art. 3º, § 1º, do DL 911 e no art. 15 do Estatuto da OAB.

## Causa

A checagem de riscado (`tem_ancestral_riscado`) subia pelos **ancestrais** do
parágrafo, e era aplicada **só ao caput**. Duas lacunas:

1. Nas páginas não compiladas do Planalto (195 dos 277 diplomas), a marca não é
   ancestral: o `<strike>` abre **dentro** do `<p>`, depois da âncora —
   `<p><font><a name="art26§2"></a><strike>§ 2º ...</strike></font></p>`. Para a
   checagem por ancestrais, esse parágrafo não estava riscado.
2. Os parágrafos seguintes ao caput eram anexados ao texto do artigo sem checagem
   alguma. Mesmo o padrão que a checagem via (`<p style="line-through">`) passava
   quando estava num parágrafo, e não no caput.

## O que foi medido

Nas quatro páginas citadas na issue, baixadas da fonte em 17/10/2026 e lidas com o
mesmo analisador do pipeline, por parágrafo:

| Página | sem marca | inteiramente riscado, marca dentro do `<p>` | parcialmente riscado |
|---|---|---|---|
| Lei 9.514 | 197 | 63 | 61 |
| Lei 8.009 | 27 | 4 | 1 |
| DL 911 | 101 | 8 | 1 |
| Lei 8.906 (EOAB) | 542 | 32 | 5 |

Nenhuma das quatro páginas tem `<strike>` aberto num `<p>` e fechado em outro, então
o analisador não precisou reconstruir marca entre parágrafos. Os "parcialmente
riscados" são, em todos os casos conferidos, texto riscado seguido de uma anotação
fora da marca — "(Revogado pela Lei nº 14.430, de 2022)", "(Vide ADIN 1.127-8)",
"Vigência encerrada" —, isto é, dispositivo revogado ou suspenso **com** a
informação da fonte ao lado.

Aplicando a transformação corrigida a essas quatro páginas, contra o publicado:

| Diploma | artigos | artigos alterados | artigos com rótulo de parágrafo repetido: antes → depois |
|---|---|---|---|
| Lei 9.514 | 53 | 16 | 11 → 1 |
| Lei 8.009 | 8 | 1 | 1 → 0 |
| DL 911 | 16 | 4 | 4 → 2 |
| EOAB | 96 | 14 | 9 → 2 |

Os cinco rótulos repetidos que sobram foram conferidos um a um e são legítimos:
incisos de parágrafos diferentes do mesmo artigo (art. 8º-B e 8º-C do DL 911,
arts. 7º e 34 do EOAB) e, no art. 22 da Lei 9.514, o inciso IV da MP 700/2015
com "Vigência encerrada" anotado fora da marca, ao lado do inciso IV da Lei
11.481/2007.

## Alcance na recoleta completa de 17–18/10/2026

Com a transformação corrigida, a recoleta dos 277 diplomas contra o publicado
mostrou **119 diplomas com artigos alterados, 618 artigos ao todo** (os sinais do
monitor semanal apontavam 23 diplomas; o restante é efeito da correção). Cada
parágrafo que saiu de um artigo foi conferido no HTML bruto da própria execução:

| Parágrafos que saíram de artigos | quantidade |
|---|---:|
| riscados na fonte (redação anterior, com a vigente ao lado) | 3.697 |
| substituídos por versão nova com o mesmo rótulo (mudança real da fonte) | 31 |
| nem riscados nem substituídos — lidos um a um | 15 |

Os 15 lidos um a um: 2 são mudança real da fonte (CDC art. 57 e CF art. 7º
renumeraram o parágrafo único para § 1º) e 13 são parágrafos da redação **antiga**
que ficavam pendurados num caput riscado e saem com ele enquanto a vigente entra —
Lei 11.445 art. 8º-A (texto da MP 844/2018 dá lugar ao da Lei 14.026/2020), Lei
9.656 art. 27, Lei 10.233 art. 63, Lei 9.478 art. 68-C, Lei 6.615 art. 27, DL 1.598
art. 25 e Lei 9.249 art. 9º. Nenhuma regressão.

Dois diplomas acionaram o gate volumétrico, só por remoção de riscados conferida:
DL 167 (22 artigos de 84) e DL 1.598 (22 de 71). Promovidos com
`--aceitar-mudanca-volumosa` depois dessa conferência.

Efeito colateral esperado no índice de vigência (`BASE-043`): as anotações que
viviam dentro dos parágrafos riscados ("(Incluído pela Medida Provisória nº 844,
de 2018)" etc.) saem com eles — o índice cai de 32.342 para 31.824 anotações,
enquanto o número de dispositivos anotados sobe de 7.359 para 7.381 com as
redações novas da recoleta.

## Correção

- `paragrafo_riscado(no)`: um parágrafo conta como riscado quando um ancestral
  está riscado **ou** quando todo o texto visível dele está dentro de uma marca
  de riscado (`<s>`, `<strike>`, `<del>` ou `text-decoration: line-through`).
  Parágrafo parcialmente riscado não conta.
- A checagem passa a valer para o caput (decide se a ocorrência está ativa e se
  a regra do rótulo em link se aplica) **e** para cada parágrafo anexado ao
  artigo: sob caput em vigor, parágrafo riscado fica de fora.
- Artigo inteiro riscado (revogado, sem redação nova) continua retido com os seus
  parágrafos riscados, como antes — tirar só o caput deixaria o artigo pela
  metade.
- A regra de substituição entre ocorrências do mesmo artigo não mudou: a vigente
  substitui a riscada; sem marca, só com "(Redação dada ...)" e sem encolher o
  artigo.

## Decisão: excluir, não marcar

A issue sugeriu excluir o trecho riscado **ou** mantê-lo com marcação. A base
já declara (`BASE-044`) que guarda **uma única redação por dispositivo** — a
compilada na data do snapshot — e que o texto das redações anteriores está fora
do acervo. Manter o riscado com marca criaria uma segunda forma de redação
anterior, só para os diplomas em que o Planalto risca em vez de omitir, e o
`BASE-044` continuaria falso. Excluir devolve a base ao que ela promete; a
dimensão temporal (que mudou, por qual diploma e quando) continua no índice de
vigência (`BASE-043`), que lê as anotações da redação vigente.

## Validação executada

- Quatro testes de regressão em `tests/test_monitorar.py`, com os padrões reais:
  art. 26 da Lei 9.514 (caput e § 2º riscados dentro do `<p>`, vigente ao lado);
  art. 3º, III, da Lei 8.009 (caput intacto, inciso riscado e substituído); art.
  7º revogado da Lei 9.514 (tudo riscado, sem substituto: retido inteiro); art.
  7º, I, do EOAB (riscado com "(Vide ADIN)" fora da marca: preservado).
- Os 55 testes anteriores do mesmo arquivo continuam passando — em especial os
  que protegem o art. 24 do EOAB, o "Art. 5 7." da LGPD e o art. 37 do Estatuto
  da Terra.
- Recoleta completa de 17/10/2026 e relatório de diferenças, lidos antes da
  promoção (abaixo).

## Limites desta verificação

- A medição por "rótulo repetido" é indício, não contagem exata: superestima em
  leis que alteram outras leis e não olha o caput.
- Dispositivo revogado continua com o texto antigo no artigo quando a anotação
  "(Revogado ...)" está fora da marca de riscado — é o mesmo tratamento de antes,
  agora declarado.
- Em página compilada (`...compilado.htm`) o Planalto costuma omitir a redação
  anterior em vez de riscá-la; o problema não foi observado ali, e nada muda.
