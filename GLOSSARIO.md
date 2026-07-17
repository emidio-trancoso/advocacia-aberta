# Glossário da Advocacia Aberta

Este glossário traduz os termos técnicos usados no projeto para a linguagem do
trabalho jurídico.

## Advocacia Aberta

É a proposta de tornar método, ferramentas e conhecimento jurídico público
estruturado legíveis, verificáveis e aperfeiçoáveis, sem expor casos ou dados de
clientes.

**Em uma frase:** método aberto, fontes verificáveis, dados protegidos.

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

## Alucinação

É uma resposta que apresenta como verdadeiro algo não sustentado pelos dados ou pelas
fontes. Pode assumir a forma de fato, citação, artigo, precedente, data ou número
inventado.

Bom contexto e verificação reduzem o risco, mas não o eliminam. Por isso o projeto
exige rastreabilidade, declaração de incerteza e revisão profissional.

## Base jurídica curada

É um conjunto estruturado de fontes jurídicas públicas preparado para pesquisa. Sua
confiabilidade depende de cobertura, proveniência, data de referência, transformação
documentada e confirmação na fonte primária.

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

## Execução local

É o processamento feito no ambiente controlado pelo usuário, sem enviar o arquivo a
um novo serviço externo. Pode reduzir exposição, mas ainda exige segurança do
dispositivo, controle de acesso e cópias de segurança.

## Copiloto e operação

No uso como **copiloto**, o agente responde a uma demanda pontual. Na **operação**, ele
executa etapas de um protocolo persistente, registra resultados nos arquivos do caso
e permite revisão. A Advocacia Aberta suporta os dois usos, mas trata método e
rastreabilidade como infraestrutura duradoura.
