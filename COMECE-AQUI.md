# Comece aqui 👋

Bem-vindo(a) à **Advocacia Aberta**: método jurídico aberto para que o trabalho com IA
seja eficaz e confiável — pela via dos dados e do método, não do discurso. Aqui o método é
legível, as fontes são pesquisáveis e as ferramentas são executáveis por agentes de IA.

Você não precisa programar. Os protocolos são escritos em português e podem ser
lidos, criticados e adaptados. As *skills* (arquivos `SKILL.md`) são o formato em que
esses protocolos chegam ao Claude Code e ao Codex.

Antes de usar dados reais, guarde uma regra: **o método pode ser aberto; o caso do
cliente permanece privado**. Veja [SIGILO-E-DADOS.md](SIGILO-E-DADOS.md).

## O caminho mais rápido: conectar (sem instalar nada)

Se você só quer que o seu assistente responda com a lei e a jurisprudência certas,
**conecte o acervo** — não precisa clonar nada. No Claude (Pro/Max) ou no ChatGPT (plano
pago), adicione um conector personalizado (MCP) com este endereço:

```text
https://mcp.advocaciaaberta.org/mcp
```

Pronto: pergunte em português e ele consulta o acervo, com a fonte oficial. O **método**
(os protocolos abaixo) você **adota** à parte. Para rodar o método inteiro — inclusive
transcrição, TJPR e diagramação —, siga os três passos.

## Três passos

### 1. Abra esta pasta em um agente compatível

- **Claude Code:** abra a pasta e digite `/skills` para conferir as skills.
- **Codex (GPT/OpenAI):** abra a pasta e digite `/skills` ou mencione uma skill com
  `$nome`.

As instruções e os adaptadores acompanham o repositório; não é preciso cadastrá-los um
a um.

### 2. Escolha o primeiro uso

Para experimentar sem dados de cliente, construa um procedimento seu.

No Claude Code:

```text
/criar-protocolo
```

No Codex:

```text
$criar-protocolo
```

Você também pode pedir: “Quero criar um protocolo para revisar contratos de locação”.
O agente fará uma entrevista sobre entrada, saída e passo a passo e só salvará o protocolo
depois da sua confirmação.

Para iniciar um caso real, copie `casos/_modelo-de-caso/`, renomeie a pasta e coloque
os documentos em `autos/`. Depois, use `organizar-caso`. Não use um caso real como
exemplo público.

### 3. Instale ferramentas somente quando precisar

Pesquisa local, busca no TJPR, transcrição e diagramação usam programas auxiliares. Se
uma dessas tarefas acusar ferramenta ausente, execute:

- Claude Code: `/preparar-ambiente`
- Codex: `$preparar-ambiente`

A instalação é feita sob demanda. No macOS, também é possível dar dois cliques em
`setup.command`.

## O que você encontrará

- **Base jurídica local** — legislação, súmulas, temas repetitivos e teses, em
  snapshots que precisam ser confirmados na fonte antes do uso profissional.
- **Protocolos executáveis** — organização, diagnóstico, pesquisa, redação, revisão,
  transcrição e diagramação.
- **Motores** — busca jurídica, consulta ao TJPR e processamento local.
- **Espaço de casos** — estrutura previsível para documentos, sínteses, fundamentos e
  peças.

Para entender a ideia inteira, siga por
[MANIFESTO.md](MANIFESTO.md) → [ARQUITETURA.md](ARQUITETURA.md) →
[GERENCIAR-CONTEXTO.md](GERENCIAR-CONTEXTO.md).

O agente pode mudar. O método continua legível, as fontes continuam verificáveis e a
responsabilidade continua profissional.
