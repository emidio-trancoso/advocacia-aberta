# BASE-012 — qualidade da recuperação

| Campo | Valor |
|---|---|
| Verificação | 17 de julho de 2026 |
| Escopo | busca textual local do Vade Mecum |
| Corte | cinco primeiros resultados |
| Corpus | 24 consultas em seis famílias |
| Julgamento | relevância e resultados canônicos registrados manualmente |

## Mudança realizada

- foi versionado um corpus com consulta, filtro, justificativa, IDs relevantes e IDs
  obrigatórios para cada caso;
- a execução usa as funções públicas reais de busca, sem duplicar o algoritmo;
- precisão, recall julgado, cobertura, cobertura dos obrigatórios e MRR são calculados
  globalmente;
- cada família possui limiar próprio de precisão;
- o comando `bun run avaliar` falha abaixo dos limiares;
- testes validam esquema, diversidade, métricas e presença dos resultados canônicos;
- a avaliação passou a rodar no GitHub Actions.

## Resultado observado

Na linha de base, a precisão global no top 5 é `0,7944`. Recall julgado, cobertura de
casos, cobertura dos obrigatórios e MRR são `1,0000`. A menor precisão por família é
`0,5714` nas súmulas STF e permanece acima do limiar específico de `0,55`.

O resultado mede apenas o corpus versionado no snapshot local. Não confirma
completude, vigência ou acerto jurídico fora dessas consultas.

## Validação executada

```bash
cd ferramentas/pesquisa/vade-mecum
bun run typecheck
bun test
bun run avaliar

cd ../../..
python3 ferramentas/manutencao/gerar_indices_derivados.py --verificar
python3 ferramentas/manutencao/verificar_compatibilidade.py
python3 ferramentas/manutencao/auditar_base_juridica.py --strict
python3 -m unittest discover -s ferramentas/manutencao/tests -p 'test_*.py'
```

O protocolo e suas limitações estão em
[`AVALIACAO-RECUPERACAO.md`](../AVALIACAO-RECUPERACAO.md).
