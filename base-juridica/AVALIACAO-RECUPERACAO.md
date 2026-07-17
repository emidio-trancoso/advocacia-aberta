# Avaliação da recuperação jurídica

Este protocolo mede a capacidade do **Vade Mecum** de recuperar registros relevantes
para consultas textuais. Ele protege o ranking contra regressões reproduzíveis, mas
não confirma vigência, força jurídica, aplicabilidade ao caso ou completude do acervo.

## Corpus versionado

O arquivo
[`consultas.json`](../ferramentas/pesquisa/vade-mecum/avaliacao/consultas.json)
contém 24 consultas avaliadas em 17 de julho de 2026:

| Família | Consultas |
|---|---:|
| Súmulas STJ | 4 |
| Súmulas STF | 3 |
| Súmulas vinculantes | 3 |
| Jurisprudência em Teses STJ | 4 |
| Temas repetitivos STJ | 3 |
| Legislação | 7 |

Cada caso registra consulta, filtro, justificativa, conjunto de resultados relevantes
e resultados canônicos obrigatórios. Os julgamentos foram feitos sobre o conteúdo do
snapshot local, não gerados pelo próprio algoritmo de busca. IDs obrigatórios impedem
que um resultado central desapareça mesmo quando as métricas agregadas ainda passam.

Os julgamentos representam um conjunto controlado de regressão. Eles não afirmam que
todo resultado relevante possível foi identificado em todo o acervo.

## Métricas

O corte é `k = 5` e as métricas são agregadas sobre as consultas:

- **precisão@5:** acertos divididos pelos resultados efetivamente retornados na janela
  de até cinco itens;
- **recall julgado@5:** resultados relevantes recuperados divididos pelo conjunto
  relevante julgado e versionado;
- **cobertura de casos:** proporção de consultas com ao menos um resultado relevante;
- **cobertura de obrigatórios:** proporção de consultas que preserva todos os seus IDs
  canônicos;
- **MRR:** média do inverso da posição do primeiro resultado relevante.

Há limiares globais e um limiar de precisão para cada família. A separação impede que
o bom desempenho de um conjunto compense silenciosamente uma regressão em outro.

## Linha de base

| Escopo | Precisão@5 | Recall julgado@5 | Cobertura | Obrigatórios | MRR |
|---|---:|---:|---:|---:|---:|
| Global | 0,7944 | 1,0000 | 1,0000 | 1,0000 | 1,0000 |
| Súmulas STJ | 0,6667 | 1,0000 | 1,0000 | 1,0000 | 1,0000 |
| Súmulas STF | 0,5714 | 1,0000 | 1,0000 | 1,0000 | 1,0000 |
| Súmulas vinculantes | 0,6000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 |
| Jurisprudência em Teses | 0,9500 | 1,0000 | 1,0000 | 1,0000 | 1,0000 |
| Temas repetitivos | 0,8667 | 1,0000 | 1,0000 | 1,0000 | 1,0000 |
| Legislação | 0,8571 | 1,0000 | 1,0000 | 1,0000 | 1,0000 |

Os valores são uma linha de base operacional, não uma alegação de precisão geral para
qualquer consulta jurídica.

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
