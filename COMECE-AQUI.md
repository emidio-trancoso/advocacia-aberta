# Comece aqui 👋

Bem-vindo(a) à **Advocacia Aberta**: métodos jurídicos legíveis, fontes pesquisáveis e
ferramentas executáveis com auxílio de agentes de IA.

Você não precisa programar. Os protocolos são escritos em português e podem ser
lidos, criticados e adaptados. As *skills* são a forma atual de fazer Claude Code e
Codex executarem esses protocolos.

Antes de usar dados reais, guarde uma regra: **o método pode ser aberto; o caso do
cliente permanece privado**. Veja [SIGILO-E-DADOS.md](SIGILO-E-DADOS.md).

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
/criar-skill
```

No Codex:

```text
$criar-skill
```

Você também pode pedir: “Quero criar um protocolo para revisar contratos de locação”.
O agente fará uma entrevista sobre entrada, saída e passo a passo e só salvará a skill
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
