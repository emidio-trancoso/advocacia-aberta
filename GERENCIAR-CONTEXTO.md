# Protocolo fundamental — gerenciamento de contexto

| Campo | Definição |
|---|---|
| Finalidade | Dar ao agente o material necessário, legível e rastreável para a tarefa atual |
| Aplica-se a | Toda organização, pesquisa, análise, redação ou revisão jurídica |
| Entrada | Documentos, mídias, fontes jurídicas, instruções e objetivo da tarefa |
| Saída | Contexto selecionado, sínteses persistentes e lacunas declaradas |
| Princípio | Dado certo, no formato certo, na medida certa e com origem identificável |

Gerenciar contexto é parte da infraestrutura jurídica, não um truque de prompt. Um
agente pode errar mesmo com bons dados; contexto bem gerido reduz risco, permite
auditoria e torna visível o que foi ou não considerado.

## Regras do protocolo

1. **Defina a tarefa antes de reunir material.** Sem uma pergunta delimitada, não há
   critério para saber o que é relevante.
2. **Torne o dado legível.** Documento que não pôde ser lido não pode sustentar uma
   conclusão.
3. **Selecione o necessário.** Mais contexto não é sempre melhor; excesso pode diluir
   fatos e instruções importantes.
4. **Separe fonte, síntese e conclusão.** Essa distinção permite voltar ao documento
   original e revisar o raciocínio.
5. **Persista o que será reutilizado.** Sínteses devem morar nos arquivos do caso, não
   apenas na conversa.
6. **Declare lacunas e incertezas.** Não complete silenciosamente o que está ausente,
   ilegível, contraditório ou sem fonte.
7. **Minimize dados sensíveis.** A tarefa define o contexto necessário; a simples
   disponibilidade de um dado não autoriza seu uso ou compartilhamento.

## Procedimento

### 1. Delimitar

Antes de ler os documentos, registre:

- qual é o caso ou matéria;
- qual resultado será produzido;
- quais perguntas precisam ser respondidas;
- quais fontes podem sustentar cada tipo de afirmação;
- onde o resultado será salvo.

Não misture casos ou tarefas independentes na mesma análise.

### 2. Inventariar

Liste o material recebido antes de interpretá-lo. Identifique formato, tamanho,
origem aparente e possíveis duplicidades. O inventário não prova o conteúdo: ele
apenas registra o que está disponível.

Para uma pilha de documentos, use `organizar-caso`. Para áudio ou vídeo, use
`transcrever` antes de extrair conclusões.

### 3. Tornar legível

Verifique se PDFs têm texto extraível, se planilhas preservam suas colunas, se anexos
estão acessíveis e se mídias foram transcritas. Quando a leitura falhar:

- identifique o arquivo e o motivo;
- tente uma transformação adequada, como OCR ou transcrição;
- se ainda assim falhar, registre a limitação;
- nunca infira o conteúdo pelo nome do arquivo.

### 4. Selecionar e fatiar

A janela de contexto é a memória de trabalho finita do agente. Em vez de entregar
todos os autos para cada pergunta:

1. faça o inventário;
2. produza uma síntese inicial;
3. selecione os documentos relacionados à tarefa;
4. leia os originais relevantes;
5. volte à fonte sempre que uma afirmação precisar de confirmação.

Síntese ajuda a localizar e conectar fatos; ela não substitui o original para conferir
uma citação, data, valor ou formulação decisiva.

### 5. Organizar por função

Cada matéria deve seguir a estrutura:

```text
casos/<seu-caso>/
├── autos/            # documentos e mídias recebidos
├── analise/          # SUMARIO.md e DIAGNOSTICO.md
├── fundamentacao/    # LEGISLACAO.md e JURISPRUDENCIA.md
└── pecas/            # peças e versões produzidas
```

Essa separação evita confundir prova do caso, conhecimento jurídico localizado,
interpretação do agente e produto final.

### 6. Criar memória externa rastreável

Use arquivos Markdown como memória entre etapas:

- `SUMARIO.md` registra documentos, pessoas, eventos e datas-chave;
- `DIAGNOSTICO.md` registra forças, fragilidades e lacunas;
- `LEGISLACAO.md` e `JURISPRUDENCIA.md` registram fundamentos e fontes verificadas;
- as peças ficam em `pecas/`, sem apagar as análises das quais derivaram.

Uma síntese deve apontar para o documento ou fonte de origem sempre que isso for
necessário para conferência. Correções devem ser feitas no arquivo persistente, não
apenas mencionadas na conversa.

### 7. Limpar a sessão quando mudar de tarefa

Ao trocar de caso ou de objetivo, comece uma conversa nova e indique os arquivos
relevantes. No Claude Code, `/clear` inicia uma sessão limpa; no Codex, use **Nova
conversa**.

`AGENTS.md` guarda as regras permanentes do projeto. `CLAUDE.md` leva as mesmas regras
ao Claude Code. Nenhum desses arquivos deve armazenar fatos de um cliente específico.

### 8. Encerrar com um registro de cobertura

Ao terminar uma etapa relevante, informe:

- o que foi lido;
- o que não pôde ser lido;
- quais fontes foram usadas;
- quais sínteses ou peças foram criadas;
- quais dúvidas continuam abertas;
- qual revisão humana ainda é necessária.

## Condições de parada

O agente deve parar a conclusão e pedir material ou orientação quando:

- faltar documento indispensável;
- a fonte jurídica necessária não puder ser confirmada;
- houver contradição material que não possa ser resolvida pelos autos;
- o arquivo decisivo estiver ilegível;
- a tarefa exigir envio de dados a novo serviço externo sem decisão do usuário;
- fatos de casos diferentes puderem estar misturados.

Parar de concluir não impede organizar o que já foi confirmado e registrar exatamente
o que falta.

## Checklist de saída

- [ ] A tarefa e o resultado esperado estão delimitados.
- [ ] Os documentos considerados foram identificados.
- [ ] Arquivos ilegíveis e lacunas foram declarados.
- [ ] Fontes, sínteses e conclusões estão separadas.
- [ ] Afirmações decisivas podem ser rastreadas à origem.
- [ ] O resultado foi salvo na pasta correta do caso.
- [ ] Apenas os dados necessários foram usados.
- [ ] A necessidade de revisão profissional está explícita.

> **Regra de bolso:** contexto confiável é legível, suficiente, rastreável e mínimo.

Consulte também a [Política de sigilo e dados](SIGILO-E-DADOS.md) e o
[Glossário](GLOSSARIO.md).
