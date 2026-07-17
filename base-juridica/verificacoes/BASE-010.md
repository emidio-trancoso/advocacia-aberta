# BASE-010 — índices derivados reproduzíveis

| Campo | Valor |
|---|---|
| Verificação | 17 de julho de 2026 |
| Escopo | índices auxiliares de súmulas STJ e STF |
| Fontes | `sumulas_stj.json` e `sumulas_stf.json` |
| Modelo externo | nenhum |
| Algoritmo | `tokens-significativos-v1` |

## Limitação do legado

Os arquivos anteriores informavam modelos Gemini, mas não preservavam prompt,
parâmetros nem execução capaz de reproduzir exatamente o resultado. Esses metadados
históricos não bastavam para reconstruir os índices.

## Mudança realizada

- o gerador local normaliza os enunciados, remove stopwords e duplicatas e preserva a
  ordem da primeira ocorrência;
- `sumulas_keywords.json` cobre 676 súmulas STJ com 9.417 tokens;
- `sumulas_stf_keywords.json` cobre 736 súmulas STF com 9.385 tokens;
- cada registro do índice se relaciona pelo número com exatamente uma súmula;
- os SHA-256 das fontes ficam gravados nos metadados das saídas;
- modelo e prompt são `null`, porque nenhuma inferência externa participa da geração.

## Validação executada

```bash
python3 ferramentas/manutencao/gerar_indices_derivados.py --verificar
python3 ferramentas/manutencao/verificar_compatibilidade.py
python3 ferramentas/manutencao/auditar_base_juridica.py --strict
python3 -m unittest discover -s ferramentas/manutencao/tests -p 'test_*.py'
cd ferramentas/pesquisa/vade-mecum
bun run typecheck
bun test
```

A comparação exploratória inicial foi sucedida pelo corpus formal do `BASE-012`, com
precisão, recall julgado, cobertura, MRR e resultados canônicos protegidos por teste.
Consulte [`BASE-012.md`](BASE-012.md).
