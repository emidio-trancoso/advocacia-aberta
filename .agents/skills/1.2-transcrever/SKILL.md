---
name: transcrever
description: Transcreve áudio ou vídeo de qualquer origem (reunião com cliente, audiência, depoimento, sustentação oral, áudio de WhatsApp, gravação de consulta) usando whisper.cpp local, gerando legenda .srt e transcrição .md com timestamps; opcionalmente rotula os interlocutores e extrai as falas mais relevantes quando há referência de contexto.
---

# Transcrever — Áudio e Vídeo em Texto

Esta skill transforma uma gravação em texto. Serve para **qualquer** gravação:
reunião com cliente, audiência, depoimento, sustentação oral, áudio de WhatsApp,
gravação de consulta ou ligação. O resultado é uma legenda (`.srt`) e uma
transcrição (`.md`) limpa, com a hora de cada fala entre colchetes (`[HH:MM:SS]`)
e um marcador `[?]` no lugar do nome de quem fala.

A transcrição roda **100% no seu computador** (offline). Nenhum áudio sai da sua
máquina — bom para sigilo profissional.

> **Aviso honesto de tempo:** transcrever 1 hora de áudio leva cerca de **15 a 25
> minutos** de processamento. É normal. O computador fica trabalhando esse tempo.

Ao final, há um passo **opcional** que identifica quem é cada pessoa nas falas e
separa os trechos mais importantes — útil quando você tem o contexto da gravação
(uma ata, uma pauta, uma lista de presentes, ou simplesmente sabe quem participou).

## Instrução

Considere `<arquivo-de-midia>` o caminho relativo do áudio ou vídeo informado pelo
usuário. Exemplos:

- `casos/Silva-vs-Maria/autos/audiencia.webm`
- `casos/reuniao-cliente-joao/reuniao.m4a`
- `casos/Silva-vs-Maria/autos/audio-whatsapp.ogg`

Se o caminho não tiver sido informado, detecte o arquivo aberto no editor quando
essa informação estiver disponível; caso contrário, pergunte ao usuário.

Os caminhos abaixo são todos relativos à raiz do projeto aberta no agente. Substitua
`<arquivo-de-midia>` pelo caminho real, sempre entre aspas.

---

### Passo 1 — Verificar o ambiente

Antes de transcrever, confira se as ferramentas necessárias e o modelo de
reconhecimento de voz estão instalados:

```bash
which whisper-cli ffmpeg
ls ~/.whisper-models/ggml-medium-q5_0.bin 2>/dev/null
```

Se **qualquer** uma dessas linhas não encontrar o que procura (saída vazia ou
mensagem de "não encontrado"), o ambiente ainda não está pronto. Nesse caso,
**oriente o usuário a executar a skill `preparar-ambiente`**, que instala tudo
automaticamente (as ferramentas e o modelo de voz). Não tente instalar nada aqui;
apenas aponte para essa skill e pare.

Se tudo foi encontrado, siga para o Passo 2.

---

### Passo 2 — Transcrever

Execute o comando de transcrição com o caminho do arquivo de mídia:

```bash
python3 "${CLAUDE_PLUGIN_ROOT:-.}/ferramentas/processamento/transcrever/transcrever.py" "<arquivo-de-midia>"
```

O que o programa faz, por baixo dos panos:

- Extrai o áudio do arquivo (mesmo de um vídeo) e o prepara para leitura.
- Divide o áudio em blocos de 10 minutos.
- Transcreve cada bloco em português, usando o modelo de voz local.
- Vai salvando a legenda `.srt` a cada bloco concluído (salvamento incremental).
- Monta a transcrição `.md` ao final.

> Lembre o usuário do tempo: ~15 a 25 minutos por hora de áudio. É hora de tomar
> um café.

Se o processo for interrompido no meio (computador desligou, você cancelou),
**basta rodar o mesmo comando de novo**: os blocos já transcritos não são
refeitos, e a transcrição continua de onde parou.

---

### Passo 3 — Conferir as saídas

Os dois arquivos nascem ao lado do arquivo de mídia original, com o mesmo nome:

- `<nome-do-arquivo>.srt` — legenda com a hora exata de cada trecho.
- `<nome-do-arquivo>.md` — transcrição em texto, pronta para leitura, no formato:

```markdown
- **[00:02:15]** `[?]` Boa tarde a todos, vamos dar início à reunião...
- **[00:02:31]** `[?]` Doutor, eu queria entender melhor o prazo...
```

Cada linha traz a hora da fala (`[HH:MM:SS]`) e o marcador `[?]`, que é um espaço
reservado para o nome ou papel de quem está falando. Abra o `.md` e confirme que
o texto está coerente com o áudio.

> **Anti-alucinação:** a transcrição deve ser **fiel ao áudio**. Nunca complete,
> corrija ou invente falas que não foram ditas. Se um trecho ficou inaudível ou
> incompreensível, deixe como está (o programa pode marcar `[inaudível]`).

Pronto. Se você só precisava do texto da gravação, pode parar aqui. O Passo 4 é
opcional.

---

### Passo 4 (OPCIONAL) — Identificar quem fala e destacar o que importa

Este passo só vale a pena quando você **tem contexto** sobre a gravação: sabe quem
são as pessoas, tem uma ata, uma pauta, uma lista de presentes ou a ordem em que
as pessoas falaram. Com esse contexto, dá para trocar cada `[?]` pelo papel real
de quem fala e separar as falas mais relevantes.

Se você não tem esse contexto, pode ignorar este passo.

#### 4a — Reunir a referência de contexto

Junte qualquer material que diga quem participou e em que ordem. Pode ser:

- Uma **ata** (de audiência, de reunião, de assembleia).
- Uma **pauta** ou roteiro do encontro.
- Uma **lista de presentes** ou de testemunhas.
- O `analise/SUMARIO.md` do caso (quem é cliente, parte contrária, advogados).
- Ou simplesmente o que o usuário souber de cabeça sobre quem estava lá.

Extraia dessa referência um **elenco** simples: quem participou e, se houver, a
ordem em que cada pessoa falou. Em audiência, por exemplo, a ordem da ata é a
chave mestra: o juiz abre, depois falam advogados, depois as partes, depois as
testemunhas na ordem listada.

#### 4b — Trocar cada `[?]` pelo papel real

Leia a transcrição e, para cada fala, deduza quem está falando comparando o
conteúdo com a referência de contexto e com pistas da própria fala. Algumas pistas
úteis (adapte ao tipo de gravação):

| Pista na fala | Provável interlocutor |
|---|---|
| "Declaro aberta", "defiro/indefiro", "dou por encerrada" | Juiz (em audiência) |
| "Excelência", "MM. Juiz", "nobre magistrado" | Advogado se dirigindo ao juízo |
| "Pergunto se o senhor...", "o senhor confirma que..." | Quem está conduzindo a pergunta |
| Respostas longas, em 1ª pessoa, narrando um fato | Depoente / pessoa sendo ouvida |
| "Vamos ao próximo ponto da pauta" | Quem conduz a reunião |
| Mudança brusca de tema + nova pessoa | Transição — use a ordem do elenco |

Substitua o `[?]` por um rótulo claro. Use o que fizer sentido para o tipo de
gravação, por exemplo:

- Audiência: `[Juiz]`, `[Adv. Cliente]`, `[Adv. Parte Contrária]`,
  `[Testemunha – Nome]`, `[Parte Autora – Nome]`, `[Perito]`, `[MP]`.
- Reunião com cliente: `[Advogado]`, `[Cliente – Nome]`, `[Sócio]`.
- Sustentação oral: `[Advogado]`, `[Relator]`, `[Procurador]`.

Faça a substituição direto no arquivo `.md`. Exemplo:

```diff
- **[00:02:15]** `[?]` Boa tarde a todos, vamos dar início à reunião...
+ **[00:02:15]** `[Advogado]` Boa tarde a todos, vamos dar início à reunião...
```

Se um trecho ficar **ambíguo** (você não tem certeza de quem fala), **mantenha o
`[?]`** e deixe uma nota ao lado em vez de chutar:

```markdown
- **[00:14:02]** `[?]` ...e foi exatamente isso que combinamos. <!-- AMBÍGUO: Cliente ou Sócio? -->
```

> Continue fiel ao áudio: rotular é só dizer **quem** falou, nunca mudar **o que**
> foi dito.

#### 4c — Extrair as falas mais relevantes

Crie (ou complemente) um resumo das falas que importam juridicamente, usando o
timestamp como "endereço" da prova — assim qualquer pessoa consegue voltar ao
trecho exato da gravação. Sugestão de local: `analise/PROVA_ORAL.md` do caso (ou
outro arquivo de análise que faça sentido). Não sobrescreva o que já existe;
acrescente uma nova seção.

Organize por pessoa e por relevância:

```markdown
## Gravação de DD/MM/AAAA — [tipo: reunião / audiência / depoimento]

**Fonte:** `caminho/do/arquivo-original` · transcrição em `caminho/da/transcricao.md`

### [Pessoa – Nome / papel]
**Favorável**
- **[00:12:34]** Confirmou que o serviço foi concluído em fevereiro/2024.
  → sustenta a tese de cumprimento do contrato.

**A neutralizar / desfavorável**
- **[00:25:10]** Disse que não foi avisada do prazo.
  → risco; possível contraponto: documento que comprova o aviso.

**Contradições**
- **[00:31:48]** Afirmou "A", mas o documento X diz o contrário.
```

O que **selecionar:** fatos controvertidos confirmados ou negados; datas, valores,
nomes e locais relevantes; admissões (algo dito contra o próprio interesse de quem
fala); contradições com documentos; declarações sobre intenção ou conhecimento.

O que **descartar:** cumprimentos, "ahn...", pedidos de repetição, ruído de fala.

> **Anti-alucinação:** todo ponto extraído deve ter respaldo direto no áudio. Se
> você não ouviu, não escreva.

---

### Passo 5 — Confirmar ao usuário

Ao terminar, informe de forma objetiva:

- A duração total do áudio transcrito (em minutos).
- O caminho dos arquivos gerados (`.srt` e `.md`).
- Se o Passo 4 foi feito: quantos interlocutores foram identificados, quantos
  trechos ficaram como `[?]` ambíguos (liste os timestamps) e o caminho do
  resumo de falas relevantes.
- Próximos passos sugeridos, conforme o caso: rotular os `[?]` (se ainda não
  feito), usar a skill `diagnosticar` para revisar a tese à luz do que foi dito,
  ou usar a skill `redigir-peca` para empregar os trechos como prova.
