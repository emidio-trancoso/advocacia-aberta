# Advocacia Aberta

> **Método aberto. Fontes verificáveis. Dados protegidos.**

A Advocacia Aberta é uma infraestrutura de trabalho jurídico legível por pessoas e
executável por agentes de IA. Ela reúne **protocolos**, **bases jurídicas curadas**,
**motores locais** e **adaptadores** para transformar conhecimento profissional em um
método verificável, reutilizável e independente de um único fornecedor.

Não é apenas uma coleção de prompts nem um produto de “advogado automático”. O valor
está na combinação de método explícito, fontes rastreáveis, gerenciamento de contexto
e revisão profissional.

> **Primeira visita?** Abra o [guia de início](COMECE-AQUI.md) e leia o
> [Manifesto](MANIFESTO.md).

## O que já existe no repositório

O projeto nasce de ativos operacionais, não apenas de uma proposta:

| Camada | Ativo atual |
|---|---|
| Base jurídica | 250 conjuntos de legislação, com 20.257 registros de dispositivos |
| Súmulas | 1.475 registros de STJ, STF e súmulas vinculantes |
| Teses | 3.508 registros de Jurisprudência em Teses do STJ, em 283 edições |
| Temas | 1.462 registros de temas repetitivos do STJ |
| Protocolos | 10 skills para organizar, transcrever, diagnosticar, pesquisar, redigir, revisar e diagramar |
| Motores | Vade Mecum para busca jurídica local, busca no TJPR, transcrição e processamento de documentos |
| Adaptadores | Compatibilidade com Claude Code e Codex, sem duplicar a regra jurídica |

Esses números descrevem os arquivos presentes nesta versão. As bases são *snapshots*
de trabalho: não significam, por si sós, vigência, completude ou atualização na data
da consulta. O [catálogo da base](base-juridica/CATALOGO.md) registra proveniência,
cobertura e limitações já identificadas; a confirmação externa e as rotinas de
atualização não dispensam revisão profissional. O
[protocolo de atualização](base-juridica/ATUALIZACAO.md) já permite coletar fontes
oficiais, validar candidatos e comparar mudanças sem sobrescrever a base vigente.

## Como a Advocacia Aberta funciona

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

## Começar em três passos

1. Baixe esta pasta e abra-a no Claude Code ou no Codex.
2. Crie um caso a partir de `casos/_modelo-de-caso/` ou escolha uma tarefa existente.
3. Acione uma skill ou descreva o trabalho em linguagem natural.

Invocação explícita:

| Agente | Exemplo para `organizar-caso` |
|---|---|
| Claude Code | `/organizar-caso casos/meu-caso` |
| Codex | mencione `$organizar-caso` e informe `casos/meu-caso`, ou escolha em `/skills` |

O agente também pode selecionar automaticamente uma skill quando o pedido corresponde
à sua descrição.

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

A maioria dos protocolos roda sem instalação adicional. Se faltar `bun`, `uv`,
`whisper`, `ffmpeg` ou `typst`, use `preparar-ambiente` ou execute `bash setup.sh`.

## Método aberto, casos privados

Protocolos, ferramentas e bases formadas por fontes públicas podem ser compartilhados.
Autos, áudios, dados pessoais, estratégias, comunicações e peças de clientes não.

Cada matéria deve morar em `casos/<numero-ou-nome>/`. O Git ignora os casos reais por
padrão, mas isso é apenas uma barreira contra publicação acidental — não substitui
controle de acesso, armazenamento seguro e julgamento profissional. Leia a
[Política de sigilo e dados](SIGILO-E-DADOS.md) antes de usar material real.

## Documentos fundamentais

- [Manifesto](MANIFESTO.md) — princípios e compromisso público.
- [Arquitetura](ARQUITETURA.md) — ativos, camadas, estado atual e destino estrutural.
- [Catálogo da base jurídica](base-juridica/CATALOGO.md) — inventário, cobertura,
  proveniência e ressalvas do acervo.
- [Backlog da base jurídica](base-juridica/BACKLOG.md) — correções priorizadas e
  critérios de aceite.
- [Atualização da base jurídica](base-juridica/ATUALIZACAO.md) — pipeline seguro e
  reproduzível para preparar novos snapshots, com monitoramento agendado que
  detecta mudanças nas fontes oficiais sem promover nada sozinho.
- [Política de sigilo e dados](SIGILO-E-DADOS.md) — fronteira público–privada.
- [Protocolo de gerenciamento de contexto](GERENCIAR-CONTEXTO.md) — como preparar,
  selecionar e registrar o que o agente lê.
- [Glossário](GLOSSARIO.md) — vocabulário técnico em linguagem jurídica.
- [Guia de início](COMECE-AQUI.md) — primeiro uso em poucos minutos.

## Estrutura atual

```text
.
├── MANIFESTO.md             # princípios
├── ARQUITETURA.md           # mapa atual e arquitetura-alvo
├── SIGILO-E-DADOS.md        # política operacional mínima
├── AGENTS.md                # instruções compartilhadas e lidas pelo Codex
├── CLAUDE.md                # ponte das mesmas instruções para Claude Code
├── .agents/skills/          # fonte canônica dos protocolos executáveis
├── .claude/skills/          # espelho gerado para Claude Code
├── base-juridica/           # catálogo e backlog; dados ainda não foram movidos
├── ferramentas/
│   ├── pesquisa/            # Vade Mecum e demais motores de pesquisa
│   ├── processamento/       # transcrição e tratamento de documentos
│   └── manutencao/          # sincronização e validação
└── casos/                   # espaço privado; inclui um modelo vazio
```

A [arquitetura-alvo](ARQUITETURA.md#arquitetura-alvo) promove protocolos, base
jurídica, motores e adaptadores a componentes próprios. A migração do motor local para
`ferramentas/pesquisa/vade-mecum/` já foi concluída; as demais movimentações continuam
planejadas por etapas.

## Manutenção dos adaptadores

Hoje, `.agents/skills/` é a fonte canônica e `.claude/skills/` é o espelho de
compatibilidade. Depois de alterar uma skill:

```bash
bash ferramentas/manutencao/sincronizar-skills.sh
python3 ferramentas/manutencao/verificar_compatibilidade.py
```

O verificador também roda no GitHub Actions.

## Licença

Salvo indicação em contrário, o código, os protocolos, as ferramentas, os templates
e a documentação autoral deste repositório são disponibilizados sob a licença
[Zero-Clause BSD (0BSD)](LICENSE). Ela permite usar, copiar, modificar e redistribuir
o material para qualquer finalidade, inclusive comercial, sem exigir atribuição.

A licença alcança somente os direitos pertencentes aos autores do projeto. Textos
legais, decisões, bases e outros materiais provenientes de fontes oficiais ou de
terceiros preservam sua situação jurídica, seus termos de uso e sua proveniência. A
0BSD não relicencia direitos que o projeto não possui. Dados e documentos de casos
reais permanecem privados e fora da distribuição pública.

## Estado do projeto

Esta remodelagem estabelece a identidade, os fundamentos e o primeiro catálogo da
Advocacia Aberta sem representar como concluído o que ainda precisa ser construído.
Confirmação jurídica das mudanças, migração estrutural, ampliação dos testes de
confiabilidade e governança de contribuições permanecem como etapas posteriores.
