# Arquitetura da Advocacia Aberta

Este documento explica quais ativos o repositório possui, como eles se relacionam e
qual estrutura o projeto pretende adotar. Ele separa deliberadamente o **estado
atual** da **arquitetura-alvo**: a remodelagem conceitual vem antes da movimentação de
pastas e da atualização das bases.

## A unidade do projeto

A Advocacia Aberta combina três ativos principais:

1. **conhecimento jurídico estruturado** — legislação, súmulas, temas e teses;
2. **método jurídico explícito** — protocolos de contexto e de execução do trabalho;
3. **capacidade operacional** — motores locais de pesquisa e processamento.

Adaptadores permitem que agentes diferentes executem esses ativos, enquanto a pasta
de casos mantém os dados privados fora da camada pública.

```text
Dados do caso
    ↓
Protocolo de contexto
    ↓
Protocolo operacional
    ↓
Motor ou ferramenta ↔ Base jurídica curada
    ↓
Resultado rastreável
    ↓
Revisão profissional
```

## As seis camadas

### 1. Base jurídica curada

É o acervo estruturado consultado pelos motores de pesquisa. O repositório contém hoje
snapshots de legislação, súmulas, temas repetitivos e Jurisprudência em Teses.

O valor dessa camada não está apenas no texto público, mas na reunião, normalização,
indexação, classificação, preservação de links e conexão com os protocolos.

Requisitos desta camada:

- catálogo de cobertura;
- proveniência por conjunto de dados;
- data de coleta e data de referência;
- rotina reproduzível de atualização;
- comparação entre versões;
- validação contra a fonte oficial correspondente;
- indicação clara de limitações.

### 2. Protocolos fundamentais

São regras que governam todos os demais trabalhos:

- gerenciamento de contexto;
- verificação de fontes;
- proteção de sigilo e dados;
- registro de incerteza;
- separação entre documento, síntese e conclusão.

O atual `GERENCIAR-CONTEXTO.md` é o primeiro protocolo fundamental do projeto.

### 3. Protocolos operacionais

Descrevem tarefas jurídicas com entrada, saída, passos, critérios de qualidade e
condições de parada. O acervo atual inclui organização, transcrição, diagnóstico,
pesquisa, redação, revisão e diagramação.

No estado atual, esses protocolos são materializados como Agent Skills. Na arquitetura
alvo, o **protocolo** será a fonte conceitual; a skill será uma forma de distribuição e
execução.

### 4. Motores e ferramentas

Executam busca, transformação ou geração de artefatos. Não são responsáveis pela
conclusão jurídica: fornecem capacidade operacional ao protocolo.

Exemplos atuais:

- motor local de pesquisa jurídica (`busca_delfus`);
- pesquisa de acórdãos do TJPR;
- transcrição local de áudio e vídeo;
- separação de autos extensos;
- diagramação de peças em PDF.

### 5. Adaptadores

Traduzem os protocolos para as superfícies de execução. Hoje o projeto mantém:

- `.agents/skills/` para o padrão Agent Skills e Codex;
- `.claude/skills/` para Claude Code;
- `AGENTS.md` e `CLAUDE.md` para instruções persistentes.

Adaptadores não devem conter conhecimento jurídico exclusivo. Se uma regra existe
somente em um adaptador, ela corre o risco de desaparecer ao trocar de plataforma.

### 6. Espaço privado de casos

`casos/` é o espaço operacional do usuário. Nele ficam autos, transcrições, análises,
fundamentação específica e peças. Essa camada não integra o acervo público e é ignorada
pelo Git por padrão, exceto pelo modelo vazio e sua documentação.

## Inventário atual

| Ativo | Local atual | Papel conceitual |
|---|---|---|
| Catálogo e backlog | `base-juridica/` | Governança inicial da base jurídica |
| Manifesto e pipeline de atualização | `base-juridica/fontes.json` e `ferramentas/manutencao/` | Coleta, transformação, validação e promoção controlada |
| Legislação, súmulas, temas e teses | `ferramentas/pesquisa/busca_delfus/data/` | Base jurídica curada |
| Motor de busca local | `ferramentas/pesquisa/busca_delfus/src/` | Motor jurídico |
| Busca TJPR | `ferramentas/pesquisa/busca-tjpr/` | Motor jurídico externo |
| Transcrição | `ferramentas/processamento/transcrever/` | Motor de processamento |
| Skills canônicas | `.agents/skills/` | Protocolos + adaptador atual |
| Skills Claude | `.claude/skills/` | Espelho de compatibilidade |
| Gestão de contexto | `GERENCIAR-CONTEXTO.md` | Protocolo fundamental |
| Casos | `casos/` | Espaço privado de trabalho |

## Arquitetura-alvo

```text
advocacia-aberta/
├── MANIFESTO.md
├── README.md
├── ARQUITETURA.md
├── SIGILO-E-DADOS.md
│
├── protocolos/
│   ├── fundamentais/
│   │   ├── gerenciar-contexto/
│   │   ├── verificar-fontes/
│   │   ├── proteger-sigilo/
│   │   └── registrar-incerteza/
│   └── operacionais/
│       ├── organizar-caso/
│       ├── transcrever/
│       ├── diagnosticar/
│       ├── pesquisar-fontes/
│       ├── redigir-peca/
│       └── revisar-peca/
│
├── base-juridica/
│   ├── CATALOGO.md
│   ├── legislacao/
│   ├── sumulas/
│   ├── temas-repetitivos/
│   └── jurisprudencia-em-teses/
│
├── motores/
│   ├── pesquisa-juridica/
│   ├── pesquisa-tjpr/
│   ├── transcricao/
│   └── diagramacao/
│
├── adaptadores/
│   ├── agent-skills/
│   ├── claude/
│   └── codex/
│
├── casos/
└── testes/
```

Essa árvore é um destino, não uma descrição falsa do repositório atual. A migração
deve preservar histórico, caminhos funcionais e compatibilidade durante a transição.

## Regras de dependência

Para evitar novo acoplamento:

1. protocolos podem consultar a base por meio de motores;
2. motores não tomam a decisão jurídica final;
3. dados voláteis não ficam copiados dentro dos protocolos;
4. adaptadores não guardam lógica jurídica exclusiva;
5. casos privados nunca alimentam automaticamente a base pública;
6. resultados derivados devem apontar documento ou fonte de origem;
7. ausência de fonte é um estado válido e deve ser registrada.

## Sequência de evolução

### Fase 1 — Identidade e documentação

Manifesto, proposta, arquitetura, vocabulário e fronteira de sigilo.

### Fase 2 — Catálogo do que já existe

Inventariar bases, motores e protocolos sem alterar seu conteúdo. Documentar cobertura,
datas, fontes e lacunas conhecidas.

**Estado:** catálogo estrutural inicial concluído em `base-juridica/CATALOGO.md`; a
validação externa do conteúdo e da vigência permanece pendente.

### Fase 3 — Migração estrutural

Promover protocolos e base jurídica a componentes de primeira classe, mantendo
adaptadores gerados para Claude e Codex.

### Fase 4 — Confiabilidade dos dados

Construir atualização reproduzível, validação, versionamento e testes das bases.

**Estado:** coleta, transformação, validação, comparação e promoção controlada foram
entregues no `BASE-004`. Correções materiais, snapshots publicados e testes de
qualidade continuam no backlog da base.

### Fase 5 — Governança e distribuição

Definir contribuição, revisão, estados de maturidade, casos sintéticos e formas de
instalação.

**Estado:** licença de distribuição definida como Zero-Clause BSD (`0BSD`); os demais
itens de governança e distribuição permanecem em construção.

## Critério de sucesso

A arquitetura estará cumprindo sua função quando for possível trocar o agente de IA,
atualizar o motor de pesquisa ou ampliar a base jurídica sem reescrever o método de
trabalho e sem expor os dados dos casos.
