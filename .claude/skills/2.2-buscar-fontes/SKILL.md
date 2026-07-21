---
name: buscar-fontes
description: Busca legislação, súmulas, temas repetitivos e Jurisprudência em Teses no Vade Mecum local, preservando fonte, natureza documental, situação e efeito jurídico.
---

# Busca de fontes jurídicas — base local

Busca súmulas, jurisprudência em teses e temas repetitivos na base jurídica local e
filtra os resultados relevantes para o caso em discussão.

## Instrução

Considere `<consulta>` o tema ou os termos de pesquisa informados pelo usuário. Se não
houver consulta, peça-a antes de continuar.

Esta skill busca no mesmo acervo (Vade Mecum) por dois caminhos, conforme o que estiver
disponível. Use o primeiro que existir:

- **Modo ferramentas** — quando as ferramentas de busca do Vade Mecum estiverem
  disponíveis na conversa (servidor MCP conectado): use-as diretamente, sem terminal.
- **Modo terminal** — quando você trabalha sobre o repositório, com Bun disponível: use o
  CLI abaixo, substituindo o marcador pelo texto real.

### Passo 1 — Executar busca ampla

**Modo ferramentas:** para uma varredura ampla da `<consulta>`, chame `buscar_sumula`,
`buscar_tese`, `buscar_tema`, `buscar_tema_rg`, `buscar_informativo` e `buscar_espelho`, e
reúna os resultados.

**Modo terminal:**

```bash
bun run "${PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-.}}/ferramentas/pesquisa/vade-mecum/src/cli.ts" buscar "<consulta>" 5
```

### Passo 1b — Se necessário, busca focada em legislação

**Modo ferramentas:** chame `buscar_legislacao` com a `<consulta>` (e o código, se souber qual).

**Modo terminal:**

```bash
bun run "${PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-.}}/ferramentas/pesquisa/vade-mecum/src/cli.ts" legislacao "<consulta>" todos 3
```

### Passo 2 — Analisar e filtrar

Com base no contexto do caso discutido na conversa, leia cada resultado e selecione apenas os que sustentam alguma das teses relevantes. Descarte os que são de matéria alheia ou não agregam à argumentação.

Classifique cada resultado conforme a taxonomia exibida pelo próprio Vade Mecum:

1. **Súmula vinculante aprovada e vigente** — efeito vinculante nos termos do art.
   103-A da Constituição;
2. **Tema repetitivo com tese publicada e estado compatível** — observância obrigatória
   quando aplicável, nos termos do art. 927, III, do CPC;
3. **Súmula comum** — enunciado sumular não vinculante por si só;
4. **Jurisprudência em Teses** — compilação institucional não vinculante por si só.

Respeite estados cancelado, superado, suspenso, alterado, afetado ou em revisão. Não
promova um resultado a vinculante apenas pela instituição que o publicou.

### Passo 3 — Apresentar

Para cada resultado selecionado:

```text
📋 [Identificação: Súmula X STJ / JT Edição Y Tese Z / Tema N]
NATUREZA: [enunciado sumular / compilação institucional / registro de precedente qualificado]
EFEITO: [rótulo apresentado pelo Vade Mecum]
SITUAÇÃO: [estado informado no registro]
TESE APOIADA: [qual argumento do caso este resultado sustenta]
ENUNCIADO: "[citação direta mais útil]"
USO: [onde e como usar na peça]
```

Ao final, mostre um quadro resumo com todos os selecionados, natureza, efeito, situação,
tese apoiada e respectivos links.

Se nenhum resultado for relevante, sugira variações de consulta ou proponha busca em
tribunal específico com a skill `buscar-tjpr`.
