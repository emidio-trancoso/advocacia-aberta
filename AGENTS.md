# Advocacia Aberta

Este é um espaço de trabalho jurídico para agentes de IA. Ele reúne protocolos
escritos em português, base jurídica estruturada, motores locais e uma convenção para
organizar casos. O público é advogado, não programador: use linguagem direta e
mantenha o foco no trabalho jurídico.

O projeto segue o [Manifesto da Advocacia Aberta](MANIFESTO.md): o método pode ser
compartilhado, mas dados de clientes permanecem privados. Antes de trabalhar com
material real, observe [SIGILO-E-DADOS.md](SIGILO-E-DADOS.md).

## Como o agente deve se comportar aqui

- **Anti-alucinação acima de tudo.** Nunca invente fatos, números, datas, citações de
  lei ou jurisprudência. Use apenas o que está nos documentos do caso ou em fontes
  verificadas pelas skills `buscar-fontes` e `buscar-tjpr`. Quando não tiver certeza,
  diga que não tem — não preencha com o provável.
- **Trabalhe sobre os arquivos do caso**, não só na conversa. Salve as sínteses em
  arquivos `.md` conforme a convenção abaixo.
- **Gerencie o contexto como parte do método.** Delimite a tarefa, registre o que foi
  lido, separe fonte de síntese e conclusão e declare arquivos ilegíveis ou lacunas.
  Siga `GERENCIAR-CONTEXTO.md`.
- **Minimize e proteja dados.** Leia apenas o necessário, não copie dados reais para
  documentação ou testes e não os envie a um novo serviço externo sem informar o
  usuário e obter autorização.
- **Português correto e acessível.** Explique o que vai fazer antes de fazer.
- **Independência de fornecedor.** Nas instruções compartilhadas, descreva capacidades
  (por exemplo, "leia o arquivo" ou "abra a página") em vez de nomes de ferramentas
  exclusivos de Claude Code, Codex ou outro agente.

## Convenção de casos

Cada processo ou matéria mora em `casos/<numero-ou-nome>/`:

- `autos/` — documentos e mídias do caso (o que entra)
- `analise/` — sínteses geradas pelas skills (`SUMARIO.md`, `DIAGNOSTICO.md`)
- `fundamentacao/` — `LEGISLACAO.md`, `JURISPRUDENCIA.md`
- `pecas/` — peças produzidas e versões diagramadas em PDF

Há um modelo vazio em `casos/_modelo-de-caso/`. Para um caso novo, copie-o e renomeie.

## Skills disponíveis

| Skill | O que faz |
|---|---|
| `criar-skill` | Constrói uma nova skill com o usuário, por entrevista (sem programar) |
| `organizar-caso` | Lê uma pilha de documentos e gera o `SUMARIO.md` do caso |
| `transcrever` | Transcreve áudio/vídeo (reunião, audiência, depoimento) em texto |
| `diagnosticar` | Mapeia forças e fragilidades do caso → `DIAGNOSTICO.md` |
| `buscar-fontes` | Busca súmulas, leis e temas repetitivos (base Delfus, offline) |
| `buscar-tjpr` | Busca jurisprudência no portal do TJPR |
| `redigir-peca` | Planeja e redige uma peça de qualquer tipo |
| `revisar-peca` | Auditoria adversarial da peça (confere provas e fundamentos) |
| `diagramar-peca` | Gera um PDF diagramado com Legal Design simples |
| `preparar-ambiente` | Instala as ferramentas que algumas skills usam |

As skills também podem ser acionadas por um pedido em linguagem natural. Para
invocação explícita, use `/nome` no Claude Code; no Codex, mencione `$nome` ou escolha
a skill em `/skills`.

## Fonte canônica e sincronização

- `.agents/skills/` é a fonte canônica, independente de fornecedor.
- `.claude/skills/` é o espelho de compatibilidade com o Claude Code. Não edite esse
  espelho diretamente.
- Depois de criar ou alterar uma skill, rode
  `bash ferramentas/manutencao/sincronizar-skills.sh`.
- Antes de concluir uma alteração, rode
  `python3 ferramentas/manutencao/verificar_compatibilidade.py`.

## Ferramentas e setup automático

A maioria das skills é markdown puro e roda **sem instalar nada**. Quatro skills usam
ferramentas externas: `buscar-fontes` (bun), `buscar-tjpr` (uv + python),
`transcrever` (whisper) e `diagramar-peca` (typst).

**Regra de auto-setup:** se uma dessas ferramentas não estiver instalada e o comando
falhar com "command not found", não desista. Avise o usuário e ofereça executar a
skill `preparar-ambiente`, que instala somente o necessário. Instale sob demanda,
nunca tudo de uma vez sem necessidade.

## Gerenciamento de contexto

`GERENCIAR-CONTEXTO.md` é um protocolo fundamental, aplicável a todas as skills. Ele
define delimitação, legibilidade, seleção, memória externa, condições de parada e
registro de cobertura. Os termos estão em `GLOSSARIO.md`.
