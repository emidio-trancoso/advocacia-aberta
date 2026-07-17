---
name: buscar-fontes
description: Busca súmulas vinculantes/STJ/STF, temas repetitivos e jurisprudência em teses nas fontes primárias curadas do Delfus (busca_delfus CLI) e filtra resultados relevantes por força vinculante.
---

# Busca de Fontes Primárias — busca_delfus

Busca súmulas, jurisprudência em teses e temas repetitivos nas fontes primárias curadas do Delfus e filtra os resultados relevantes para o caso em discussão.

## Instrução

Considere `<consulta>` o tema ou os termos de pesquisa informados pelo usuário. Se não
houver consulta, peça-a antes de continuar. Substitua o marcador pelo texto real nos
comandos abaixo.

### Passo 1 — Executar busca ampla

```bash
bun run ferramentas/pesquisa/busca_delfus/src/cli.ts buscar "<consulta>" 5
```

### Passo 1b — Se necessário, busca focada em legislação

```bash
bun run ferramentas/pesquisa/busca_delfus/src/cli.ts legislacao "<consulta>" todos 3
```

### Passo 2 — Analisar e filtrar

Com base no contexto do caso discutido na conversa, leia cada resultado e selecione apenas os que sustentam alguma das teses relevantes. Descarte os que são de matéria alheia ou não agregam à argumentação.

Prioridade de força vinculante:
1. **Súmulas Vinculantes STF** — obrigatórias (art. 103-A CF)
2. **Temas Repetitivos com tese firmada** — efeito vinculante para casos idênticos (arts. 1.036-1.041 CPC)
3. **Súmulas STJ/STF** — persuasivas (orientação forte)
4. **Jurisprudência em Teses (JT)** — orientativas

### Passo 3 — Apresentar

Para cada resultado selecionado:

```text
📋 [Identificação: Súmula X STJ / JT Edição Y Tese Z / Tema N] | ⚖️ [força: vinculante/persuasiva/orientativa]
STATUS: [ativa/cancelada/pendente]
TESE APOIADA: [qual argumento do caso este resultado sustenta]
ENUNCIADO: "[citação direta mais útil]"
USO: [onde e como usar na peça]
```

Ao final, mostre um quadro resumo com todos os selecionados, a força vinculante de cada um, as teses que apoiam e os respectivos links.

Se nenhum resultado for relevante, sugira variações de consulta ou proponha busca em
tribunal específico com a skill `buscar-tjpr`.
