# Advocacia Aberta

> **Método aberto. Fontes verificáveis. Dados protegidos.**

Quando um advogado usa IA e ela cita uma jurisprudência que não existe, o problema não é a
ferramenta — é o dado. **A alucinação não é a doença; a doença é o dado ilegível.** A Advocacia
Aberta organiza o dado jurídico e escreve o método, para que a IA trabalhe com fonte e o
profissional entenda o que ela fez. Não é um “advogado automático”: é infraestrutura aberta —
legível por pessoas, executável por Claude Code e Codex, com os casos do cliente sempre privados.

[![Licença MIT](https://img.shields.io/badge/licença-MIT-2563EB)](LICENSE)
[![Agentes: Claude Code + Codex](https://img.shields.io/badge/agentes-Claude%20Code%20%2B%20Codex-111111)](COMECE-AQUI.md)
[![Verificação](https://github.com/emidio-trancoso/advocacia-aberta/actions/workflows/compatibilidade.yml/badge.svg)](.github/workflows/compatibilidade.yml)
[![Manifesto](https://img.shields.io/badge/manifesto-a%20tese-6B7280)](MANIFESTO.md)

🌐 [Read this in English](#in-english)

## O que já existe no repositório

O projeto nasce de ativos operacionais, não apenas de uma proposta:

| Camada | Ativo atual |
|---|---|
| Base jurídica | 273 conjuntos de legislação, com 22.180 registros de dispositivos |
| Súmulas | 1.475 registros de STJ, STF e súmulas vinculantes |
| Teses | 3.508 registros de Jurisprudência em Teses do STJ, em 283 edições |
| Temas | 1.462 temas repetitivos do STJ e 1.470 temas de repercussão geral do STF |
| Informativo | 11.567 julgados resumidos do Informativo STF, em 1.211 edições |
| Espelhos de acórdãos | 11.133 acórdãos dos órgãos uniformizadores do STJ (Corte Especial e Seções — não a totalidade dos acórdãos), com ementa e tese |
| Protocolos | 10 skills para organizar, transcrever, diagnosticar, pesquisar, redigir, revisar e diagramar |
| Motores | Vade Mecum para busca jurídica local, busca no TJPR, transcrição e processamento de documentos |
| Adaptadores | Compatibilidade com Claude Code e Codex, sem duplicar a regra jurídica |

Esses números descrevem os arquivos presentes nesta versão. As bases são *snapshots* de trabalho:
não significam, por si sós, vigência, completude ou atualização na data da consulta. O
[catálogo da base](base-juridica/CATALOGO.md) registra proveniência, cobertura e limitações; o
[protocolo de atualização](base-juridica/ATUALIZACAO.md) coleta fontes oficiais, valida candidatos e
compara mudanças sem sobrescrever a base vigente. Nada disso dispensa revisão profissional.

## Por que existe

Segui um problema até ele mudar minha profissão.

Comecei no Direito e, ainda advogando, mergulhei na inteligência artificial aplicada à advocacia:
fundei e presidi a Comissão de IA da OAB do Paraná, ajudando a desenhar como a profissão deveria
lidar com ela. Mas foi usando IA nos meus próprios casos que bati na parede que nenhuma régua
resolvia — cada conversa resolvia uma tarefa e o contexto morria ali; no caso seguinte, eu explicava
tudo de novo. Em vez de procurar outra ferramenta, escrevi o método e organizei o dado jurídico para
a IA conseguir lê-lo. Isso virou a Advocacia Aberta.

Seguir o problema me levou para fora do Direito: organizar dado jurídico virou organizar dado, ponto.
Hoje transformo dados dispersos — de uma empresa, de um mercado — em ativos de inteligência. A
Advocacia Aberta é a entrega dessa ideia de volta ao meu campo de origem: **dado legível vem antes do
modelo**, no Direito como em qualquer operação.

— *Emidio Trancoso · OAB/PR 119.075 (credencial de origem; sem atuação no foro)*

## Como funciona

```text
Documentos do caso
        ↓
Gerenciamento de contexto
        ↓
Protocolo jurídico → motor ou ferramenta ↔ base jurídica
        ↓
Resultado rastreável
        ↓
Revisão e decisão profissional
```

- **Protocolos** tornam entradas, passos, critérios, saídas e limitações explícitos.
- **Bases jurídicas** dão ao trabalho um acervo estruturado, com fonte e proveniência.
- **Motores** pesquisam ou processam dados sem tomar a decisão jurídica final.
- **Adaptadores** permitem executar o mesmo método em agentes diferentes.
- **Casos** permanecem no espaço privado do profissional.

## Rigor que você pode inspecionar

O método não pede confiança — ele se deixa auditar:

- **Cada mudança no motor de busca passa por um gate de regressão** com 89 consultas julgadas à
  mão (precisão@5, recall e MRR por família de fonte) — veja o
  [protocolo de avaliação](base-juridica/AVALIACAO-RECUPERACAO.md).
- **A base se corrige em público:** cada correção de dado tem um relatório com a fonte consultada,
  a mudança feita e o teste — veja as [verificações](base-juridica/verificacoes/).
- **Um monitoramento agendado vigia as fontes oficiais** e abre uma issue quando detecta mudança —
  sem promover nada sozinho ([workflow](.github/workflows/monitorar-base.yml)).
- **A revisão desconfia de si mesma:** a skill [`revisar-peca`](.agents/skills/4.1-revisar-peca/)
  audita cada citação e classifica os precedentes como Confirmada, Substituível, Forçada ou
  Inexistente.

## Comece pela porta certa

- **Você é da área jurídica** → [Para advogados](PARA-ADVOGADOS.md): o que muda no seu trabalho, um
  caso resolvido de ponta a ponta e um parecer pronto — sem instalar nada.
- **Você constrói com IA** → [Para quem constrói](PARA-DESENVOLVEDORES.md): a base com taxonomia, o
  eval com gate de regressão e a engenharia de contexto por trás.

## Usar em três passos

1. Baixe esta pasta e abra-a no Claude Code ou no Codex.
2. Crie um caso a partir de `casos/_modelo-de-caso/` ou escolha uma tarefa existente.
3. Acione uma skill ou descreva o trabalho em linguagem natural.

Invocação explícita:

| Agente | Exemplo para `organizar-caso` |
|---|---|
| Claude Code | `/organizar-caso casos/meu-caso` |
| Codex | mencione `$organizar-caso` e informe `casos/meu-caso`, ou escolha em `/skills` |

O agente também pode selecionar automaticamente uma skill quando o pedido corresponde à sua
descrição.

**Alternativa — instalar como plugin do Claude Code:**

```bash
/plugin marketplace add emidio-trancoso/advocacia-aberta
/plugin install advocacia-aberta
```

As skills ficam disponíveis com namespace, como `/advocacia-aberta:organizar-caso`.

## Protocolos operacionais disponíveis

| Skill atual | O que faz | Setup |
|---|---|---|
| `criar-skill` | Constrói um novo procedimento com o usuário, por entrevista | — |
| `organizar-caso` | Lê documentos e produz `SUMARIO.md` | — |
| `transcrever` | Converte áudio ou vídeo em texto | 🔧 |
| `diagnosticar` | Mapeia forças e fragilidades em `DIAGNOSTICO.md` | — |
| `buscar-fontes` | Pesquisa a base local de legislação, súmulas, temas e teses | 🔧 |
| `buscar-tjpr` | Pesquisa e lê acórdãos no portal do TJPR | 🔧 |
| `redigir-peca` | Planeja e redige uma peça jurídica | — |
| `revisar-peca` | Audita provas, fontes, argumentos e fragilidades | — |
| `diagramar-peca` | Produz PDF com Legal Design simples | 🔧 |
| `preparar-ambiente` | Instala sob demanda as ferramentas necessárias | — |

Fluxo típico:

```text
organizar-caso → diagnosticar → buscar-fontes (+ buscar-tjpr)
                                    ↓
        redigir-peca → revisar-peca → diagramar-peca
```

A maioria dos protocolos roda sem instalação adicional. Se faltar `bun`, `uv`, `whisper`, `ffmpeg`
ou `typst`, use `preparar-ambiente` ou execute `bash setup.sh`.

## Método aberto, casos privados

Protocolos, ferramentas e bases formadas por fontes públicas podem ser compartilhados. Autos,
áudios, dados pessoais, estratégias, comunicações e peças de clientes não.

Cada matéria deve morar em `casos/<numero-ou-nome>/`. O Git ignora os casos reais por padrão, mas
isso é apenas uma barreira contra publicação acidental — não substitui controle de acesso,
armazenamento seguro e julgamento profissional. Leia a
[Política de sigilo e dados](SIGILO-E-DADOS.md) antes de usar material real.

## Documentos fundamentais

- [Manifesto](MANIFESTO.md) — a tese e o compromisso público.
- [Princípios operacionais](PRINCIPIOS.md) — as regras que tornam o método verificável.
- [Para advogados](PARA-ADVOGADOS.md) e [Para quem constrói](PARA-DESENVOLVEDORES.md) — por onde
  entrar, conforme o seu lado.
- [Arquitetura](ARQUITETURA.md) — ativos, camadas, estado atual e destino estrutural.
- [Catálogo da base jurídica](base-juridica/CATALOGO.md) — inventário, cobertura, proveniência e
  ressalvas do acervo.
- [Avaliação da recuperação](base-juridica/AVALIACAO-RECUPERACAO.md) — o gate de regressão da busca.
- [Atualização da base jurídica](base-juridica/ATUALIZACAO.md) — pipeline seguro e reproduzível para
  novos snapshots, com monitoramento agendado das fontes oficiais.
- [Política de sigilo e dados](SIGILO-E-DADOS.md) — fronteira público–privada.
- [Gerenciamento de contexto](GERENCIAR-CONTEXTO.md) — como preparar, selecionar e registrar o que
  o agente lê.
- [Glossário](GLOSSARIO.md) — vocabulário técnico em linguagem jurídica.
- [Créditos e proveniência](CREDITOS.md) e [Como contribuir](CONTRIBUTING.md).
- [Guia de início](COMECE-AQUI.md) — primeiro uso em poucos minutos.

## Estrutura atual

```text
.
├── MANIFESTO.md             # a tese e o compromisso
├── PRINCIPIOS.md            # princípios operacionais
├── ARQUITETURA.md           # mapa atual e arquitetura-alvo
├── SIGILO-E-DADOS.md        # política operacional mínima
├── AGENTS.md                # instruções compartilhadas e lidas pelo Codex
├── CLAUDE.md                # ponte das mesmas instruções para Claude Code
├── .agents/skills/          # fonte canônica dos protocolos executáveis
├── .claude/skills/          # espelho gerado para Claude Code
├── base-juridica/           # catálogo, taxonomia e governança da base
├── ferramentas/
│   ├── pesquisa/            # Vade Mecum (motor + dados) e busca no TJPR
│   ├── processamento/       # transcrição e tratamento de documentos
│   └── manutencao/          # sincronização e validação
└── casos/                   # espaço privado; inclui um modelo e o exemplo sintético
```

A [arquitetura-alvo](ARQUITETURA.md#arquitetura-alvo) promove protocolos, base jurídica, motores e
adaptadores a componentes próprios; a migração acontece por etapas, preservando histórico e
interfaces.

## Manutenção dos adaptadores

`.agents/skills/` é a fonte canônica. Dela são gerados dois espelhos: `.claude/skills/` (Claude
Code, nível projeto) e `skills/` (lido pelo plugin, via `.claude-plugin/`). Nunca edite um espelho
à mão. Depois de alterar uma skill:

```bash
bash ferramentas/manutencao/sincronizar-skills.sh
```

A sincronização regenera os dois espelhos e roda o verificador de compatibilidade, que também roda
no GitHub Actions.

Ao escrever um comando de skill que chama um motor ou script do kit, prefixe o caminho com
`${CLAUDE_PLUGIN_ROOT:-.}` — por exemplo,
`bun run "${CLAUDE_PLUGIN_ROOT:-.}/ferramentas/pesquisa/vade-mecum/src/cli.ts" …`. Quando o kit roda
como plugin instalado, a variável aponta para a raiz do plugin; dentro do repositório (Claude Code
nível projeto ou Codex) ela fica vazia e o caminho cai para o diretório de trabalho. Assim o mesmo
comando funciona nos dois contextos, sem depender de uma ferramenta de um fornecedor específico.

## Licença

Salvo indicação em contrário, o código, os protocolos, as ferramentas, os templates e a
documentação autoral deste repositório são disponibilizados sob a licença [MIT](LICENSE). Ela permite
usar, copiar, modificar e redistribuir o material para qualquer finalidade, inclusive comercial,
desde que se mantenha o aviso de copyright e a permissão.

A licença alcança somente os direitos pertencentes aos autores do projeto. Textos legais, decisões,
bases e outros materiais provenientes de fontes oficiais ou de terceiros preservam sua situação
jurídica, seus termos de uso e sua proveniência (ver [CREDITOS.md](CREDITOS.md)). A licença MIT não
relicencia direitos que o projeto não possui. Dados e documentos de casos reais permanecem privados
e fora da distribuição pública.

## Estado

A base, os motores e os protocolos já estão em uso. A confirmação de vigência caso a caso, a
ampliação dos testes de confiabilidade e a governança de contribuições seguem em construção — a
abertura existe justamente para que isso melhore pela revisão.

## In English

**Advocacia Aberta** (“Open Advocacy”) is open infrastructure for legal work with AI agents,
focused on Brazilian law. When an AI cites case law that does not exist, the problem is not the
tool — it is the data. **Hallucination is a symptom; illegible data is the disease.** It bundles a
curated legal corpus (statutes, binding precedents, and case-law digests from Brazil's Supreme
Federal Court and Superior Court of Justice — tens of thousands of sourced records), ten executable
protocols (“skills”) for Claude Code and Codex, and local search and processing engines. Every
search change is guarded by a hand-judged regression eval, and a scheduled job watches the official
sources. The method is public; client data stays private. Licensed under [MIT](LICENSE). Start with
the [Manifesto](MANIFESTO.md) and the [getting-started guide](COMECE-AQUI.md).
