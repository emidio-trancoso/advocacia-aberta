# Advocacia Aberta

Este é um espaço de trabalho jurídico para agentes de IA. Ele reúne protocolos
escritos em português, base jurídica estruturada, motores locais e uma convenção para
organizar casos. O público é advogado, não programador: use linguagem direta e
mantenha o foco no trabalho jurídico.

O projeto segue o [Manifesto da Advocacia Aberta](MANIFESTO.md): a alucinação não é a
doença — é o sintoma; a doença é o dado ilegível. Por isso o método é explícito e a fonte
vem antes da afirmação. O método pode ser compartilhado, mas dados de clientes permanecem privados.
Antes de trabalhar com material real, observe [SIGILO-E-DADOS.md](SIGILO-E-DADOS.md).

## Como o agente deve se comportar aqui

- **Anti-alucinação acima de tudo.** Nunca invente fatos, números, datas, citações de
  lei ou jurisprudência. Use apenas o que está nos documentos do caso ou em fontes
  verificadas pelos protocolos `buscar-fontes` e `buscar-tjpr`. Quando não tiver certeza,
  diga que não tem — não preencha com o provável.
- **Toda citação vem com a fonte — e a fonte tem que abrir.** Ao citar lei, súmula,
  tema, tese, acórdão ou doutrina, traga junto a referência verificável: a identificação
  (número, órgão, data) e o link oficial que leva ao próprio documento. Antes de entregar,
  confira que cada link abre de fato o documento citado; link que cai em busca vazia ou em
  página errada conta como ausência de fonte, não como fonte. Sem fonte que abra, não
  afirme como assentado — registre que precisa confirmar.
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
- `analise/` — sínteses geradas pelos protocolos (`SUMARIO.md`, `DIAGNOSTICO.md`)
- `fundamentacao/` — `LEGISLACAO.md`, `JURISPRUDENCIA.md`
- `pecas/` — peças produzidas e versões diagramadas em PDF

Há um modelo vazio em `casos/_modelo-de-caso/`. Para um caso novo, copie-o e renomeie.

## Protocolos disponíveis

| Protocolo | O que faz |
|---|---|
| `criar-protocolo` | Constrói um novo protocolo com o usuário, por entrevista (sem programar) |
| `organizar-caso` | Lê uma pilha de documentos e gera o `SUMARIO.md` do caso |
| `transcrever` | Transcreve áudio/vídeo (reunião, audiência, depoimento) em texto |
| `diagnosticar` | Mapeia forças e fragilidades do caso → `DIAGNOSTICO.md` |
| `buscar-fontes` | Busca súmulas, leis e temas repetitivos (base jurídica local, offline) |
| `buscar-tjpr` | Busca jurisprudência no portal do TJPR |
| `redigir-peca` | Planeja e redige uma peça de qualquer tipo |
| `revisar-peca` | Auditoria adversarial da peça (confere provas e fundamentos) |
| `diagramar-peca` | Gera um PDF diagramado com Legal Design simples |
| `preparar-ambiente` | Instala as ferramentas que algumas skills usam |

Os protocolos também podem ser acionados por um pedido em linguagem natural. Para
invocação explícita, use `/nome` no Claude Code; no Codex, mencione `$nome` ou escolha
o protocolo em `/skills`.

## Fonte canônica e sincronização

- `.agents/skills/` é a fonte canônica, independente de fornecedor.
- `.claude/skills/` é o espelho de compatibilidade com o Claude Code. Não edite esse
  espelho diretamente.
- Depois de criar ou alterar um protocolo, rode
  `bash ferramentas/manutencao/sincronizar-skills.sh`.
- Antes de concluir uma alteração, rode
  `python3 ferramentas/manutencao/verificar_compatibilidade.py`.

## Ferramentas e setup automático

A maioria dos protocolos é markdown puro e roda **sem instalar nada**. Quatro protocolos
usam ferramentas externas: `buscar-fontes` (bun), `buscar-tjpr` (uv + python),
`transcrever` (whisper) e `diagramar-peca` (typst).

**Regra de auto-setup:** se uma dessas ferramentas não estiver instalada e o comando
falhar com "command not found", não desista. Avise o usuário e ofereça executar o
protocolo `preparar-ambiente`, que instala somente o necessário. Instale sob demanda,
nunca tudo de uma vez sem necessidade.

## Base jurídica

- O inventário, a cobertura e as limitações conhecidas estão em
  `base-juridica/CATALOGO.md`; as correções estão em `base-juridica/BACKLOG.md`.
- Um snapshot local ajuda a localizar a fonte, mas não confirma silenciosamente
  vigência ou exatidão na data de uso.
- Antes e depois de alterar os JSONs ou o motor de pesquisa, rode
  `python3 ferramentas/manutencao/auditar_base_juridica.py`.
- Não corrija divergência de conteúdo jurídico apenas para fazer a contagem fechar.
  Confirme a fonte oficial e registre data, mudança e validação.
- Quando a pergunta for **"está atualizado de fato?"**, o monitor semanal não
  responde: ele vê sinal de mudança, não conteúdo. A resposta vem da conferência
  completa (recoleta e comparação de tudo), com roteiro em
  `base-juridica/ATUALIZACAO.md`. Em 29/07/2026 o sinal deu "sem mudança" nas 288
  fontes e a recoleta achou duas teses com o enunciado substituído.
- No site, **"atualizado em"** é a última mudança promovida e **"conferido em"** é a
  última verificação na fonte. Acervo parado há semanas e conferido hoje está em
  dia — a fonte é que não mudou.

## Crédito de contribuição externa

A origem externa de um item é registrada em dois lugares com réguas diferentes, e
**um não alimenta o outro**:

| onde | o que registra | nomeia a pessoa? |
|---|---|---|
| `base-juridica/BACKLOG.md` e `base-juridica/verificacoes/BASE-0NN.md` | a contribuição como **fato** | não — "relatado pela comunidade", "levantado em contribuição externa" |
| `CREDITOS.md` e a página de créditos do site (repo `advocacia-aberta-site`: `src/pages/creditos.astro` e a lista curta em `index.astro`) | a **pessoa** | sim |

Por isso, **fechar um item de origem externa não credita ninguém.** Ao concluir um
item assim, o mesmo trabalho tem de chegar aos três lugares: o backlog, o
`CREDITOS.md` e o site. O `BASE-050` fechou sem isso — relatado em 06/10/2026,
corrigido em 17/10, mergeado em 18/10 citando "contribuição da comunidade — issue
#26", e creditado só em 18/10, depois de alguém perguntar; doze dias em que a
correção estava em produção e a contribuição não aparecia na vitrine.

O que guarda cada parte:

- `ferramentas/manutencao/tests/test_credito_contribuicao.py` recusa item de origem
  externa ausente do `CREDITOS.md` — o irmão, para o crédito, do teste que recusa
  limitação omitida. Ele **não** alcança o site, que é outro repositório: essa parte
  é esta régua.
- Autoria que o repositório não registra (contribuição que chegou fora do GitHub)
  entra em `SEM_AUTORIA_CONHECIDA` no teste, com o motivo, e vira pergunta ao
  mantenedor — não se credita por inferência.

Como creditar: pelo que a contribuição **mudou no acervo**, não pelo elogio — é a
régua já escrita no topo de `creditos.astro`. E **pelo que a pessoa tornou público**:
perfil sem nome é escolha dela, então credita-se o handle (precedente: `@peraivo`,
`@ruanlucas-adv`) e se oferece no próprio canal a troca da forma do crédito. Nomear
quem optou por não se identificar não é do mantenedor.

## Gerenciamento de contexto

`GERENCIAR-CONTEXTO.md` é um protocolo fundamental, aplicável a todos os protocolos. Ele
define delimitação, legibilidade, seleção, memória externa, condições de parada e
registro de cobertura. Os termos estão em `GLOSSARIO.md`.
