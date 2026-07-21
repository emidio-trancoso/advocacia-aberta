# Adaptador de plugin OpenAI/Codex

Este diretório torna a Advocacia Aberta instalável como **plugin da OpenAI** (Work Mode
no ChatGPT Web e no Codex). Ele coexiste com `.claude-plugin/` — um não substitui o outro.

## O que este plugin publica (v0.3)

Um **bundle curado de 5 skills** que cobrem o fluxo completo no ChatGPT Web hospedado,
operando sobre documentos **anexados na conversa**:

- `organizar-caso` → `SUMARIO.md`
- `diagnosticar` → `DIAGNOSTICO.md`
- `buscar-fontes` → pesquisa no acervo jurídico (via **MCP**, ver abaixo)
- `redigir-peca` → a peça
- `revisar-peca` → o relatório de revisão

A `buscar-fontes` (e, por dependerem dela, `redigir`/`revisar`) usa o servidor **MCP** do
Vade Mecum quando conectado; no repositório, cai no CLI do Bun. As skills puramente locais —
`buscar-tjpr` (scraping), `transcrever` (whisper), `diagramar-peca` (typst) — **não** entram
neste bundle; seguem disponíveis para quem usa o Codex/desktop sobre o repositório completo.

## Layout

```text
.codex-plugin/
├── plugin.json     # manifesto (metadados + bloco interface)
├── skills/         # BUNDLE CURADO — gerado, nunca editado à mão
└── README.md
```

- `skills/` é **gerado** a partir da fonte canônica `.agents/skills/` por
  `ferramentas/manutencao/sincronizar-skills.sh` (só as skills da whitelist) e validado
  por `ferramentas/manutencao/verificar_compatibilidade.py` como subconjunto byte-idêntico.
  Não edite `skills/` diretamente: edite `.agents/skills/` e rode o sincronizador.
- O campo `"skills": "./skills/"` do manifesto assume resolução **relativa ao diretório do
  manifesto** (`.codex-plugin/`). **A confirmar** com o `@plugin-creator`/marketplace local
  antes da submissão: se a resolução for relativa à raiz do plugin (raiz do repo), trocar
  para `"./.codex-plugin/skills/"`. Não deixar `"./skills/"` apontar para o `skills/` da
  raiz — aquele é o espelho completo de 10 skills, usado pelo `.claude-plugin/`.

## Caminhos portáveis

Scripts empacotados devem referenciar a raiz do plugin por variável de ambiente, na ordem:
`${PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-.}}` — `PLUGIN_ROOT`/`PLUGIN_DATA` são as do Codex;
`CLAUDE_PLUGIN_ROOT`/`CLAUDE_PLUGIN_DATA` são aliases legados que o Codex também exporta.

## Conectar o MCP jurídico (v0.3)

O servidor MCP (Vade Mecum) é um só, consumido pelos dois agentes a partir da URL pública
`https://mcp.advocaciaaberta.org/mcp`:

- **Claude** — não precisa de arquivo no plugin: adicione um **connector remoto** por URL em
  claude.ai (Settings → Connectors), ou no Claude Code via `.mcp.json`/`claude mcp add`
  apontando para a URL (transporte HTTP).
- **Codex/OpenAI** — o binding do MCP remoto ao plugin (`.codex-plugin/.mcp.json` e/ou
  `.app.json`, referenciados no manifesto por `mcpServers`/`apps`) deve ser **gerado pelo
  `@plugin-creator`**: a doc pública só especifica MCP local (`command`/`args`), não o formato
  do MCP remoto, então não fixamos esses arquivos à mão. Na submissão, o MCP remoto é
  registrado como app com a URL + verificação de domínio em `/.well-known/openai-apps-challenge`.

## Teste privado (sem submeter nada) — app desktop / Codex

Plugins não publicados são **desktop-only**: só dá para instalá-los no app desktop do
ChatGPT (Work Mode) ou no Codex, não no ChatGPT Web hospedado.

Fluxo recomendado:

1. No Work Mode/Codex, use o `@plugin-creator` para validar o manifesto e **gerar o
   entry do marketplace local** — ele é a fonte de verdade do esquema atual.
2. Reinicie o app desktop; em **Plugins**, escolha o marketplace no seletor e instale o
   plugin. Ele é instalado em `~/.codex/plugins/cache/$MARKETPLACE/$PLUGIN/local/`.
3. Invoque as skills: `@organizar-caso` / `@diagnosticar` (Work Mode) ou `$organizar-caso`
   (Codex CLI), anexando PDFs sintéticos.
4. Confirme que o `SUMARIO.md`/`DIAGNOSTICO.md` são entregues como arquivos e que nenhuma
   afirmação sem fonte é inventada.

Sobre `.agents/plugins/marketplace.json`: o esquema real usa `source` como objeto
(`{"source": "local", "path": "./..."}`), `policy` e `interface`. O `source.path` de uma
fonte `local` precisa ficar **dentro da raiz do marketplace** — como o plugin mora na raiz
do repositório, o arquivo aqui é um ponto de partida; **confirme/regenere com o
`@plugin-creator`** (ou use uma fonte `git-subdir` apontando para o repo).

## Pendências antes da submissão pública (não são código)

O manifesto ainda **não** declara os itens abaixo de propósito — referenciar URL ou asset
que não abre viola o princípio "a fonte tem que abrir". Preencher e adicionar ao `interface`
antes de submeter:

- `privacyPolicyURL` e `termsOfServiceURL` — páginas https públicas (ex.: GitHub Pages).
- `composerIcon`, `logo`, `logoDark`, `screenshots` — assets PNG de marca.
- Confirmar o valor de `category` contra a lista aceita no portal.
- Identidade verificada na OpenAI Platform + permissão `Apps Management: Write`.
- 5 casos de teste positivos + 3 negativos e os países de disponibilidade.

Referências oficiais: [Build plugins](https://learn.chatgpt.com/docs/build-plugins) ·
[plugin.json spec](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/plugin-creator/references/plugin-json-spec.md) ·
[Submit plugins](https://learn.chatgpt.com/docs/submit-plugins).
