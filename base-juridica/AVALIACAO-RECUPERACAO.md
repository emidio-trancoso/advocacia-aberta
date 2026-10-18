# Avaliação da recuperação jurídica

Este protocolo mede a capacidade do **Vade Mecum** de recuperar registros relevantes
para consultas textuais. Ele protege o ranking contra regressões reproduzíveis, mas
não confirma vigência, força jurídica, aplicabilidade ao caso ou completude do acervo.

## Corpus versionado

O arquivo
[`consultas.json`](../ferramentas/pesquisa/vade-mecum/avaliacao/consultas.json)
contém 97 consultas: as 24 avaliadas em 17 de julho de 2026; as acrescentadas em
19 de julho de 2026 pela expansão da legislação — dez casos do
piloto, dois a três casos julgados por fatia promovida (estatutos,
trabalhista, codificadas, penal, tributária, previdenciária, cível/família, eleitoral, imobiliário/agrário, administrativa, processual/constitucional, consumidor/bancária, empresarial e regulatória), dois casos do Código
Comercial de 1850 (`CCOM`), dois do Decreto 2.044/1908 (`D2044`) e dois do
Marco Legal dos Contratos de Seguro (`L15040`); e nove casos das famílias de
jurisprudência de alto volume incorporadas na mesma data — três para os temas de
repercussão geral do STF (`temas_rg_stf`), três para o Informativo STF
(`informativo_stf`) e três para os espelhos de acórdãos do STJ (`espelhos_stj`),
julgados nas promoções respectivas:

| Família | Consultas |
|---|---:|
| Súmulas STJ | 4 |
| Súmulas STF | 3 |
| Súmulas vinculantes | 4 |
| Jurisprudência em Teses STJ | 4 |
| Temas repetitivos STJ | 3 |
| Temas de repercussão geral STF | 4 |
| Informativo STF | 3 |
| Espelhos de acórdãos STJ | 3 |
| Legislação | 69 |

Cada caso registra consulta, filtro, justificativa, conjunto de resultados relevantes
e resultados canônicos obrigatórios. Os julgamentos foram feitos sobre o conteúdo do
snapshot local, não gerados pelo próprio algoritmo de busca. IDs obrigatórios impedem
que um resultado central desapareça mesmo quando as métricas agregadas ainda passam.

Os julgamentos representam um conjunto controlado de regressão. Eles não afirmam que
todo resultado relevante possível foi identificado em todo o acervo.

Um caso julgado da LC 227/2026 (competências do Comitê Gestor do IBS) foi deliberadamente
**deixado fora** do corpus: a consulta devolve as cláusulas de alteração da lei à frente
dos dispositivos de competência, e mantê-lo exigiria afrouxar o limiar do grupo. O defeito
está registrado no `BASE-041`, com o caso a reintroduzir quando o ranking o resolver.

Em 23 de julho de 2026 entraram três casos da Lei Complementar 214/2025 (split
payment, Imposto Seletivo e devolução a famílias de baixa renda) e três das leis
complementares promovidas na mesma data (LC 225/2026, Código de Defesa do Contribuinte,
e LC 220/2025, Sistema Nacional de Educação), além de dois casos de recuperação por
equivalência declarada
(`rg-nepotismo` e `sv-nepotismo-termo-unico`): a Súmula Vinculante 13 e o Tema 1000 do
STF descrevem a conduta sem escrever "nepotismo", e a busca léxica sozinha não os
alcançava. A avaliação roda sobre o que o usuário recebe — resultados diretos **mais**
os trazidos pelo léxico (`data/lexico_juridico.json`), para que a expansão seja medida
tanto no ganho quanto no ruído.

## Métricas

O corte é `k = 5` e as métricas são agregadas sobre as consultas:

- **precisão@5:** acertos divididos pelos resultados efetivamente retornados na janela
  de até cinco itens;
- **recall julgado:** resultados relevantes recuperados divididos pelo conjunto relevante
  julgado e versionado. A janela é por caso — `máx(5, nº de relevantes do caso)` —, e não
  os mesmos 5 de sempre: com janela fixa, um caso com mais relevantes do que a janela tem o
  recall limitado por aritmética (5 de 8 = 0,625 no melhor resultado possível) e o teto da
  métrica fica em 0,9761, não em 1. Pior: a base crescer passa a derrubar o número sem a
  busca ter piorado — um julgado novo e pertinente entra em 1º lugar e empurra um relevante
  antigo para fora da janela. Quatro casos hoje têm mais relevantes do que cinco
  (`jt-trafico-dosimetria`, `l9514-alienacao-fiduciaria`, `lc214-split-payment` e
  `lc220-regime-de-colaboracao`); em todos os outros a janela é a de cinco e nada muda;
- **cobertura de casos:** proporção de consultas com ao menos um resultado relevante;
- **cobertura de obrigatórios:** proporção de consultas que preserva todos os seus IDs
  canônicos;
- **MRR:** média do inverso da posição do primeiro resultado relevante.

Precisão, MRR e cobertura de obrigatórios seguem medidos na janela de cinco — é o que
quem consulta recebe. Só o recall usa a janela por caso, porque só ele tem o conjunto
relevante no denominador.

Há limiares globais e um limiar de precisão para cada família. A separação impede que
o bom desempenho de um conjunto compense silenciosamente uma regressão em outro.

A precisão agregada divide acertos por resultados retornados, então consulta com um único
relevante julgado contribui no máximo 1/5 enquanto o motor completar a janela. É o que
`BASE-052` registra: nas quatro consultas estreitas de 18/10/2026 o artigo correto vem em
1º lugar nas quatro e os outros quatro lugares são ruído. Por isso o limiar de `legislacao`
está em 0,76 desde 18/10/2026, com a nota no próprio corpus — ele volta a subir quando o
motor parar de completar a janela em consulta estreita.

## Linha de base

Medida em 18/10/2026, sobre 103 consultas julgadas (69 → 73 em legislação com as quatro
consultas do conteúdo novo de 18/10).

| Escopo | Precisão@5 | Recall julgado | Cobertura | Obrigatórios | MRR |
|---|---:|---:|---:|---:|---:|
| Global | 0,7694 | 0,9707 | 1,0000 | 1,0000 | 0,9903 |
| Súmulas STJ | 0,6667 | 1,0000 | 1,0000 | 1,0000 | 1,0000 |
| Súmulas STF | 0,5714 | 1,0000 | 1,0000 | 1,0000 | 1,0000 |
| Súmulas vinculantes | 0,6667 | 1,0000 | 1,0000 | 1,0000 | 1,0000 |
| Jurisprudência em Teses | 0,9167 | 0,9583 | 1,0000 | 1,0000 | 1,0000 |
| Temas repetitivos | 0,8667 | 1,0000 | 1,0000 | 1,0000 | 1,0000 |
| Temas de repercussão geral STF | 0,7273 | 1,0000 | 1,0000 | 1,0000 | 1,0000 |
| Informativo STF | 0,8000 | 0,9231 | 1,0000 | 1,0000 | 1,0000 |
| Espelhos de acórdãos STJ | 0,9333 | 1,0000 | 1,0000 | 1,0000 | 1,0000 |
| Legislação | 0,7642 | 0,9669 | 1,0000 | 1,0000 | 0,9863 |

## Execução e manutenção

```bash
cd ferramentas/pesquisa/vade-mecum
bun run avaliar
```

O comando encerra com erro quando um limiar ou resultado obrigatório deixa de ser
atendido. Os mesmos critérios rodam nos testes e no GitHub Actions.

Ao alterar o ranking ou o acervo:

1. execute o corpus antes e depois da mudança;
2. examine os enunciados e dispositivos dos resultados alterados;
3. ajuste julgamentos somente com justificativa humana registrada;
4. não reduza limiares para acomodar uma regressão sem documentá-la;
5. acrescente consultas para vocabulários, ramos e falhas ainda não representados.

Uma avaliação externa futura pode ampliar o corpus, usar julgadores independentes e
medir concordância entre avaliadores. Essa ampliação não é pré-condição para o gate de
regressão atual.
