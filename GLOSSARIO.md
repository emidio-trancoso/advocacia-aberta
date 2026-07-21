# Glossário da Advocacia Aberta

Este glossário traduz os termos técnicos usados no projeto para a linguagem do
trabalho jurídico.

## Advocacia Aberta

É a infraestrutura que torna o trabalho jurídico com IA **eficaz e confiável** pela via
dos dados e do método — não do discurso. Reúne um **acervo** organizado por taxonomia
jurídica e um **método** — protocolos explícitos e gerenciamento de contexto —, para que
a IA execute e o profissional compreenda, sem expor casos ou dados de clientes. Ver o
[Manifesto](MANIFESTO.md).

**Em uma frase:** método aberto, fontes verificáveis, dados protegidos.

## Acervo

É o conjunto curado de fontes jurídicas públicas — legislação, súmulas, temas, teses,
julgados e espelhos de acórdãos — organizado por **taxonomia jurídica** para ser lido por
um agente de IA, com a fonte oficial em cada item. É o "material" da Advocacia Aberta; o
**método** é o "procedimento" que o põe para trabalhar. Ver o
[catálogo da base](base-juridica/CATALOGO.md).

## Protocolo

É um procedimento de trabalho que declara entradas, passos, critérios de qualidade,
saídas, limitações e condições de parada. O protocolo é independente da ferramenta
que o executa.

*Analogia jurídica:* um procedimento interno acompanhado de checklist e critérios de
revisão.

## Skill

É uma forma executável de entregar um protocolo a um agente de IA. Neste repositório,
as skills são escritas em português e adaptadas para Claude Code e Codex.

O **protocolo** é o método; a **skill** é um de seus formatos de execução.

## Agente

É o sistema de IA capaz de seguir instruções e usar ferramentas, como abrir um
arquivo, pesquisar uma base e salvar uma síntese. O agente auxilia a execução; não
assume a responsabilidade profissional pelo resultado.

## Prompt

É o pedido dado ao agente. Um prompt claro delimita objetivo, material disponível,
resultado esperado e restrições.

*Analogia jurídica:* um quesito pericial — sua formulação condiciona a utilidade da
resposta.

## Janela de contexto

É a quantidade finita de informação que o agente consegue considerar na memória de
trabalho de uma conversa. Documentos, instruções e respostas ocupam esse espaço.

*Analogia jurídica:* a mesa de trabalho onde se abrem as peças necessárias para a
tarefa atual.

## Gerenciamento de contexto

É o protocolo para selecionar o dado certo, torná-lo legível, apresentá-lo na medida
adequada e preservar sínteses rastreáveis entre etapas. Veja
[GERENCIAR-CONTEXTO.md](GERENCIAR-CONTEXTO.md).

## Dado legível

É informação que o agente consegue efetivamente ler e relacionar: texto extraível,
estrutura preservada, origem identificada e recorte compatível com a tarefa. Nome de
arquivo, imagem sem OCR ou áudio sem transcrição não equivalem a conteúdo lido.

## Taxonomia jurídica

É o sistema que classifica cada norma ou julgado por **natureza, proveniência e efeito** —
o que separa "dado" de "dado legível por uma IA". Sem taxonomia, a base é um monte de
texto; com ela, o agente sabe o que é vinculante, o que é histórico, o que confirma uma
tese e o que apenas a indica. Ver [base-juridica/TAXONOMIA.md](base-juridica/TAXONOMIA.md).

## Alucinação

É uma resposta que apresenta como verdadeiro algo não sustentado pelos dados ou pelas
fontes. Pode assumir a forma de fato, citação, artigo, precedente, data ou número
inventado.

Na leitura do projeto, a alucinação **não é a doença — é o sintoma; a doença é o dado
ilegível**: quando a fonte não chega organizada ao modelo, ele completa a lacuna com o
provável. Bom contexto e verificação reduzem o risco, mas não o eliminam. Por isso o
projeto exige rastreabilidade, declaração de incerteza e revisão profissional.

## Base jurídica curada

É um conjunto estruturado de fontes jurídicas públicas preparado para pesquisa (é o
**acervo**, no vocabulário de apresentação do projeto). Sua
confiabilidade depende de cobertura, proveniência, data de referência, transformação
documentada e confirmação na fonte oficial correspondente.

## Dado público

É a informação jurídica de fonte oficial e acesso livre — legislação, súmulas,
jurisprudência. A Advocacia Aberta organiza esse dado público para que uma IA o leia e o
mantém aberto: acesso a um bem comum não deveria virar barreira paga.

## Proveniência

É o registro de onde o dado veio, quando foi coletado, como foi transformado e quais
limitações possui. Proveniência permite auditar o caminho entre fonte e resultado.

## Motor

É uma ferramenta que executa uma capacidade específica, como pesquisar súmulas,
consultar jurisprudência, transcrever áudio ou diagramar uma peça. O motor encontra ou
transforma informação; ele não decide sozinho a conclusão jurídica.

## Adaptador

É a camada que apresenta um protocolo a uma plataforma específica. `.agents/skills/`
e `.claude/skills/` são os adaptadores atuais. O conhecimento jurídico não deve ficar
preso exclusivamente a um deles.

## Conector (MCP)

É a ponte que liga o acervo a um assistente de IA (como Claude ou ChatGPT) por um padrão
aberto — o *Model Context Protocol* (MCP). Colando o endereço do conector, o assistente
passa a consultar o acervo e a citar a fonte oficial, sem instalar nada. O acervo é
servido em `https://mcp.advocaciaaberta.org/mcp`.

## Conectar e adotar

São os dois modos de usar a Advocacia Aberta. **Conectar** é plugar o *acervo* ao seu
assistente (por MCP), para ele responder com a fonte oficial. **Adotar** é levar um
*protocolo* (o método) para o assistente — colando-o no chat ou rodando a via plena no
agente local. O acervo você conecta; os protocolos você adota.

## Execução local

É o processamento feito no ambiente controlado pelo usuário, sem enviar o arquivo a
um novo serviço externo. Pode reduzir exposição, mas ainda exige segurança do
dispositivo, controle de acesso e cópias de segurança.

## Copiloto e operação

No uso como **copiloto**, o agente responde a uma demanda pontual. Na **operação**, ele
executa etapas de um protocolo persistente, registra resultados nos arquivos do caso
e permite revisão. A Advocacia Aberta suporta os dois usos, mas trata método e
rastreabilidade como infraestrutura duradoura.
