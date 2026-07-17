---
name: preparar-ambiente
description: Instala sob demanda as ferramentas externas usadas para transcrição, pesquisa jurídica e diagramação em PDF; use quando uma skill avisar que falta whisper, ffmpeg, bun, uv ou typst.
---

# Preparar ambiente

A maioria das skills deste kit é texto puro e funciona sem instalar nada. Apenas quatro
skills dependem de programas externos. Esta skill instala esses programas **sob demanda**,
ou seja, só o que for realmente necessário para o que você quer fazer:

- **`transcrever`** (transcrever áudio/vídeo de audiência) precisa do `whisper-cli`, do
  `ffmpeg` e de um modelo de inteligência artificial de voz (um arquivo de cerca de 539 MB).
- **`buscar-fontes`** (busca de súmulas e jurisprudência no Delfus) precisa do programa `bun`.
- **`buscar-tjpr`** (busca de acórdãos no portal do TJPR) precisa do programa `uv` com
  Python 3.12. Na primeira busca, ele baixa cerca de 400 MB de um navegador automatizado.
- **`diagramar-peca`** (geração do PDF final) precisa do programa `typst`.

Use esta skill quando uma das skills acima avisar que está faltando uma ferramenta, ou
quando você já souber que vai usar esses recursos e quiser deixar tudo pronto.

## Procedimento

### Passo 1 — Descobrir o que instalar

Pergunte ao usuário (ou deduza do que ele já pediu) qual recurso ele quer habilitar:

- **transcrição** de áudio/vídeo de audiência,
- **busca de fontes** (Delfus),
- **busca no TJPR**,
- **diagramação em PDF**, ou
- **tudo** de uma vez.

Instale apenas o necessário. Não instale ferramentas que não serão usadas (setup preguiçoso).

### Passo 2 — Detectar o sistema e ver o que já existe

Descubra qual é o sistema operacional do usuário: **macOS**, **Linux** ou **Windows**.

Antes de instalar qualquer coisa, verifique o que já está instalado para não repetir trabalho:

```bash
which bun uv whisper-cli ffmpeg typst
```

No macOS, verifique também se o Homebrew existe:

```bash
which brew
```

Só instale o que estiver faltando.

### Passo 3 — Instalar o que faltar

Antes de rodar cada comando, **explique ao usuário em uma frase o que ele faz** e
**avise sobre downloads grandes ou demora**. Use exatamente os comandos abaixo.

#### bun (para `buscar-fontes`)

Instalar o programa:

```bash
curl -fsSL https://bun.sh/install | bash
```

Instalar as dependências da ferramenta (use o caminho relativo e volte para a raiz depois):

```bash
cd ferramentas/pesquisa/busca_delfus && bun install
```

Testar se funcionou:

```bash
bun run ferramentas/pesquisa/busca_delfus/src/cli.ts buscar "dano moral" 3
```

#### uv (para `buscar-tjpr`)

Instalar o programa:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Preparar a ferramenta:

```bash
uv sync --project ferramentas/pesquisa/busca-tjpr
```

**Avise o usuário:** a primeira busca no TJPR baixa cerca de 400 MB de um navegador
automatizado (Chromium) e pode levar cerca de 1 minuto. Isso acontece só na primeira vez.

#### typst (para `diagramar-peca`)

No macOS com Homebrew:

```bash
brew install typst
```

Em Linux ou Windows, use o instalador indicado em https://github.com/typst/typst.

#### whisper (para `transcrever` — de forma simples, só no macOS)

Instalar os programas:

```bash
brew install whisper-cpp ffmpeg
```

Baixar o modelo de voz:

```bash
mkdir -p ~/.whisper-models && curl -L -o ~/.whisper-models/ggml-medium-q5_0.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium-q5_0.bin
```

**Avise o usuário:** o modelo tem cerca de 539 MB e o download pode levar alguns minutos.

## O que funciona em cada sistema

- **macOS:** tudo funciona de forma suave. Usa o Homebrew para instalar whisper e typst.
  Se o usuário não tiver o Homebrew, oriente a instalar primeiro seguindo as instruções
  de https://brew.sh.
- **Linux:** `bun`, `uv` e `typst` funcionam normalmente. Para a transcrição, o usuário precisa
  instalar o whisper.cpp e o ffmpeg pelo gerenciador de pacotes da própria distribuição
  (por exemplo, `apt`).
- **Windows:** para este kit, prefira o WSL ao usar `bun` e `uv`. O `typst` possui
  instaladores próprios. A transcrição com whisper é mais complicada no Windows — nesse
  caso, apresente a instalação manual do whisper.cpp ou, somente com autorização e após
  alertar sobre sigilo, uma alternativa de transcrição online.

Observação importante sobre sigilo: todas essas ferramentas rodam **localmente** no
computador do usuário, o que é bom para a confidencialidade dos dados do cliente. A
internet é usada apenas para instalar e baixar os programas — não para enviar os dados
do caso.

---

Depois do setup concluído, volte à skill que precisava da ferramenta e continue o
trabalho normalmente.
