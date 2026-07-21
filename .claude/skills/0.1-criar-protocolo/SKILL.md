---
name: criar-protocolo
description: Constrói com você, por entrevista, um protocolo (um arquivo SKILL.md) a partir de uma tarefa que você repete no trabalho — sem programar. Pergunta o que entra, o que sai, o passo a passo e as condições de parada, e entrega o arquivo pronto para usar. Use quando quiser ensinar um procedimento seu para a IA executar sempre igual.
---

# Criar Protocolo — construa o seu primeiro protocolo, sem programar

Esta é a skill que cria outros protocolos. Ela conduz uma **entrevista curta** para
transformar um procedimento que você já faz na cabeça (ou no automático) em um
`SKILL.md` que a IA passa a executar sempre do mesmo jeito.

Um **protocolo** é o seu procedimento escrito em português; a **skill** (`SKILL.md`) é o
formato em que esse protocolo é entregue a um agente de IA. Você não vai programar nada.

A ideia central: **todo trabalho jurídico já é um procedimento.** Você já sabe ler
um processo, montar uma petição, analisar um contrato. Só não escreveu esse caminho
para a IA.

> Todo protocolo responde a três perguntas (a anatomia de qualquer automação):
> **1. O que ENTRA** (os dados que você já tem) → **2. O que SAI** (o resultado que
> você quer) → **3. O PROCEDIMENTO** (o passo a passo que liga um ao outro) — mais as
> **condições de parada**. A entrevista abaixo descobre essas coisas com você.

---

## Instrução

Se o usuário já informou uma ideia de tarefa (ex.: "resumir contratos de locação"),
use-a como ponto de partida. Se não informou, comece perguntando pela tarefa.

**Conduza como uma conversa, não como um formulário.** Faça uma pergunta de cada vez,
em linguagem simples, e use as respostas anteriores para fazer a próxima. Se o usuário
não souber responder algo, ofereça exemplos e siga em frente — o protocolo pode ser
refinado depois.

### Passo 1 — A tarefa (o gatilho)

Pergunte:
- "Qual tarefa você **repete** e gostaria que a IA fizesse por você?"
- "Me dá um exemplo concreto da última vez que você fez isso."

Ouça e devolva em uma frase o que entendeu, para confirmar. Sugira um **nome curto**
em kebab-case para o protocolo (ex.: `resumir-contrato`, `minutar-notificacao`,
`triar-processo-novo`).

### Passo 2 — O que ENTRA (os dados que você TEM)

Pergunte:
- "Quando você vai fazer essa tarefa, **o que você tem em mãos**?" (PDFs dos autos,
  um contrato, um áudio de reunião, um e-mail do cliente, uma planilha…)
- "Onde isso costuma estar?" (uma pasta do caso, um arquivo solto, um texto colado)
- "Tem algum dado que **precisa estar organizado antes**?" Se for áudio, aponte
  o protocolo `transcrever`; se for uma pilha de documentos, aponte o protocolo
  `organizar-caso`.

### Passo 3 — O que SAI (o resultado que você PRECISA)

Pergunte:
- "No fim, **o que você quer receber**?" (um resumo de 1 página, uma minuta de peça,
  uma tabela de prazos, uma lista de riscos…)
- "Em que **formato**?" (um arquivo `.md`, uma resposta na tela, uma peça salva em
  `pecas/`…)
- "Como é um resultado **bom**? E o que tornaria o resultado **ruim**?" (isso vira as
  regras de qualidade do protocolo)

### Passo 4 — O PROCEDIMENTO (o passo a passo)

Peça para a pessoa narrar como ela faz hoje, e transforme em passos numerados:
- "Me conta, **passo a passo**, como você faria isso na mão."
- A cada passo, pergunte o "porquê" quando não for óbvio — o motivo vira instrução
  para a IA não errar.
- Identifique pontos onde a IA **não pode inventar** (números, citações de lei,
  jurisprudência, prazos) e onde ela deve **conferir na fonte** ou **perguntar** em
  vez de chutar.

### Passo 5 — As condições de parada

Pergunte:
- "Em que situações a IA deve **parar e te perguntar**, em vez de seguir?" (falta um
  documento, um prazo não confere, o pedido está ambíguo…)
- "Como saber que a tarefa **terminou bem**?"

Essas respostas viram as condições de parada do protocolo — o que impede a IA de
completar a lacuna com o provável quando falta base.

### Passo 6 — Mostrar o rascunho e confirmar

Antes de salvar, **mostre ao usuário** um resumo do que o protocolo vai fazer
(entra → sai → passos → condições de parada) e pergunte se está certo. Ajuste conforme
o retorno. **Não gere o arquivo antes da confirmação.**

### Passo 7 — Gerar o arquivo do protocolo

Crie o arquivo em `.agents/skills/<nome-escolhido>/SKILL.md` com esta estrutura:

```markdown
---
name: <nome-em-kebab-case>
description: <1 frase clara em português dizendo o que o protocolo faz e QUANDO usá-lo —
  é por aqui que a IA decide acioná-lo sozinha>
---

# <Título amigável>

<1-2 frases explicando o objetivo do protocolo.>

## Instrução

Considere como entrada <o que o usuário informa ao pedir a tarefa, ex.: o caminho da
pasta do caso>. Se a entrada não estiver presente, peça-a antes de continuar.

### Passo 1 — <nome do passo>
<o que fazer, em português>

### Passo 2 — <...>
<...>

## Regras
- <regra de qualidade / o que nunca fazer / quando perguntar em vez de chutar>
- <condição de parada: quando parar e perguntar em vez de seguir>
- Nunca inventar fatos, números, citações de lei ou jurisprudência: usar só o que
  está nos documentos ou em fonte verificada.
```

Regras ao gerar:
- A `description` é a parte mais importante: escreva-a pensando em "quando a IA deve
  usar isto?". É ela que faz o protocolo ser acionado na hora certa.
- Use **caminhos relativos** (`casos/<caso>/...`), nunca caminhos absolutos.
- Linguagem em português, simples. É um procedimento, não código.
- Escreva instruções independentes de fornecedor: use capacidades como "leia o
  arquivo" em vez de nomes de ferramentas exclusivos de um agente.
- Se a tarefa se conecta a outros protocolos do kit, referencie-os pelo nome
  (ex.: "antes, execute o protocolo `organizar-caso`"; "depois, use o protocolo
  `revisar-peca`").

Depois de salvar, rode:

```bash
bash "${CLAUDE_PLUGIN_ROOT:-.}/ferramentas/manutencao/sincronizar-skills.sh"
python3 "${CLAUDE_PLUGIN_ROOT:-.}/ferramentas/manutencao/verificar_compatibilidade.py"
```

### Passo 8 — Explicar como usar

Ao terminar, diga ao usuário:
- "Pronto: criei o protocolo **<nome>**. No Claude Code, use `/<nome>`; no Codex,
  mencione `$<nome>` ou peça a tarefa em linguagem natural."
- Se preferir usar sem clonar o repositório, o mesmo `SKILL.md` pode ser instalado
  como skill autônoma no assistente (por exemplo, em Customize → Skills, no claude.ai).
- Sugira testá-lo agora com um exemplo real.
- Lembre que ele pode ser ajustado quando quiser — é só abrir o arquivo
  `.agents/skills/<nome>/SKILL.md` e editar, ou usar o protocolo `criar-protocolo` de
  novo para refinar.

---

## Dica de ouro (diga ao usuário se ele travar na ideia)

O melhor primeiro protocolo é uma tarefa **chata, repetitiva e bem definida** — não a
mais impressionante. Exemplos que funcionam bem: resumir uma pilha de documentos novos,
montar a linha do tempo de um caso, gerar a minuta de uma notificação padrão, conferir
se uma peça citou todas as provas. Comece pequeno; a IA aprende o seu jeito e você
expande depois.
