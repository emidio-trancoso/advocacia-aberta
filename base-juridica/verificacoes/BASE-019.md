# BASE-019 — índices de legislação reproduzíveis

| Campo | Valor |
|---|---|
| Verificação | 19 de julho de 2026 (UTC) |
| Escopo | índices de busca dos 270 diplomas legislativos (21.541 dispositivos) |
| Fontes | `data/lei_*.json` (snapshots promovidos do Planalto) |
| Modelo externo | nenhum |
| Algoritmo | `tokens-texto-integral-v1` |

## Limitação do legado

Oito diplomas do núcleo (ADCT, CC, CF, CLT, CP, CPC, CPP, CTN) tinham o índice
invertido `indexes.keywords` — curadoria legada sem processo reproduzível,
preservada pela transformação. Quando esse índice existe, o motor não recorre
ao texto integral: 314 dispositivos fora dele estavam **invisíveis à busca
textual** (CLT: 223, entre eles o art. 7º; CC: 56, o capítulo de seguro
revogado pela Lei 15.040/2024; CPP: 27, incluindo os arts. 3º-A a 3º-F do juiz
das garantias; CTN: 5; CP: 2 — arts. 121-B e 147-C; CPC: 1 — art. 699-A).
CDC, CE e CTB tinham palavras-chave por registro que o motor não usa, e os 259
diplomas restantes não tinham índice nenhum.

## Decisão arbitrada pela avaliação de recuperação

As estratégias foram medidas com o corpus de 74 consultas antes da escolha:

| Estratégia | Precisão global | Precisão legislação | Obrigatórios |
|---|---:|---:|---:|
| Linha de base (antes do BASE-019) | 0,8121 | 0,8295 | 1,0000 |
| Uniforme (descarta o índice curado) | 0,5927 | 0,5528 | 0,8784 |
| Aditiva com a pontuação legada do índice | 0,6236 | 0,5915 | 0,8919 |
| **Adotada: curado intacto + derivado fiel ao texto integral** | **0,8121** | **0,8295** | **1,0000** |

A substituição do índice curado repete a regressão já observada no commit
d4a0b30 e foi descartada. A pontuação legada aplicada a tokens gerados inunda o
top-5 (soma +1 por entrada de prefixo compatível, sem piso mínimo). A
estratégia adotada preserva o índice curado e faz o índice derivado reproduzir
a semântica da busca em texto integral — casamento por subpalavra, no máximo um
ponto-base por palavra por dispositivo, piso de 40% das palavras, empates pela
ordem do documento e stopwords preservadas nos tokens (removê-las alterou
ranking e piso nos casos `cba-responsabilidade-transportador` e
`lc64-inelegibilidades`). Com ela, os 74 casos retornaram exatamente os mesmos
resultados, caso a caso; dentro de um diploma sem índice curado a escala ×3 é
monotônica e não altera o ranking interno.

## Mudança realizada

- `gerar_indices_derivados.py` passou a gerar, por diploma, o arquivo
  `data/indices/lei_*_keywords.json` com os tokens normalizados dos
  dispositivos que o índice curado não cobre (para os 262 sem índice curado,
  todos os dispositivos), na ordem do documento;
- a união índice curado ∪ índice derivado cobre os 21.541 dispositivos em
  relação 1:1, sem sobreposição, garantida por teste em Python e no motor;
- 15.757 dispositivos entraram no índice derivado; os 314 invisíveis do núcleo
  voltaram a ser recuperáveis, com teste de regressão (CPP 3º-B, CP 121-B,
  CLT 7º);
- o manifesto `indices-derivados.json` (schema 2) ganhou a seção `legislacao`
  com algoritmo, parâmetros e datas; modelo e prompt são nulos;
- cada saída registra fonte, SHA-256, contagens e relação de cobertura;
- o motor consome o índice derivado em `carregarIndiceGerado` e o tipo do
  índice aceita números de artigo sufixados ("121-B") como strings;
- o auditor acusa como P0 índice ausente, dessincronizado (SHA-256) ou com
  cobertura quebrada, e o CI roda em modo estrito.

## Validação executada

```bash
python3 ferramentas/manutencao/gerar_indices_derivados.py --verificar
python3 ferramentas/manutencao/auditar_base_juridica.py --strict
python3 -m unittest discover -s ferramentas/manutencao/tests -p 'test_*.py'
python3 ferramentas/manutencao/gerar_expansao_legislacao.py --verificar
python3 ferramentas/manutencao/verificar_compatibilidade.py
cd ferramentas/pesquisa/vade-mecum
bun run typecheck
bun test
bun run avaliar
```

Todos os comandos passaram em 19 de julho de 2026: 54 testes Python, 21 testes
do motor e a avaliação com os limiares globais e por família preservados
(global 0,8121; legislação 0,8295; recall julgado 0,9926; cobertura,
obrigatórios e MRR 1,0000). Nenhum julgamento do corpus foi alterado.

## Limitações declaradas

- o índice curado do núcleo continua sendo um artefato legado preservado, não
  reproduzível; o BASE-019 garante que ele nunca mais esconde dispositivos, e
  qualquer substituição futura precisa ser arbitrada pela avaliação;
- as palavras-chave por registro de CDC, CE e CTB seguem preservadas nos dados
  e não são usadas pelo motor;
- a busca de temas repetitivos tem lacuna análoga (57 temas invisíveis),
  registrada como `BASE-020`.
