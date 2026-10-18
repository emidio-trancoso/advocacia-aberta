# Créditos e proveniência

A Advocacia Aberta distribui o conteúdo **autoral** (protocolos, ferramentas, motores,
documentação e templates) sob a licença [MIT](LICENSE). Materiais de
terceiros e fontes oficiais **preservam a sua situação jurídica, os seus termos de uso e a
sua proveniência**, conforme o [Manifesto](MANIFESTO.md), os [Princípios](PRINCIPIOS.md) (método
aberto e execução local) e a
[Política de sigilo e dados](SIGILO-E-DADOS.md). A licença MIT não relicencia direitos que o
projeto não possui.

## Quem mantém

- **Emidio Trancoso** (OAB/PR 119.075 · Maringá/PR) — autor do projeto: o método, a taxonomia, a
  curadoria do acervo e a decisão sobre o que entra na base.
- **[Apolus.ai](https://apolus.ai)** — mantenedora da infraestrutura desde 30/07/2026: hospeda o
  endpoint público de consulta (`mcp.advocaciaaberta.org/mcp`) e responde pela sua operação e pela
  rotina de atualização, para que o serviço se sustente ao longo do tempo.

A mantenedora banca a máquina, não o método. Seguem como estão o [Manifesto](MANIFESTO.md), os
[Princípios](PRINCIPIOS.md), o domínio `advocaciaaberta.org`, a licença [MIT](LICENSE) e o
repositório público — a iniciativa continua aberta. O acesso ao endpoint permanece **gratuito**; a
autenticação prevista (ainda não implementada) serve para conter abuso, não para cobrar. E quem
preferir não depender de quem hospeda clona o repositório e roda o acervo inteiro na própria
máquina: é o que o Manifesto chama de não haver aprisionamento a fornecedor.

## Fontes jurídicas oficiais

A base jurídica reúne legislação, súmulas, teses, temas e julgados a partir de **fontes
públicas oficiais** (Planalto, STF, STJ e correlatos). Textos legais e decisões judiciais
são de fonte oficial; o trabalho autoral está na **curadoria** — reunião, normalização,
indexação, classificação, preservação de links e conexão com os protocolos.

Proveniência, cobertura, data de coleta e ressalvas de cada conjunto estão registradas em
[`base-juridica/CATALOGO.md`](base-juridica/CATALOGO.md). Constar de fonte pública não
elimina deveres de sigilo, proteção de dados e prudência na reutilização.

## Design do template de parecer

O template [`templates/parecer-trafico-drogas.typ`](templates/parecer-trafico-drogas.typ)
usa um sistema de componentes de **Legal Design** (paleta, badges processuais, blocos de
silogismo, callouts de jurisprudência e lei) **inlinado no próprio arquivo, sem dependência
de import externo**. Esses componentes derivam de um template de legal design
(`template-af.typ`) empregado anteriormente pelo autor em trabalho para **Souza Neto
Advocacia**, e foram reescritos para este repositório.

O **conteúdo jurídico** do parecer é `SINTÉTICO`: relatório, análise e parecer final são
placeholders (`«PREENCHER»`), sem origem em caso real. Os precedentes citados nos blocos de
jurisprudência são **reais e verificados** via Vade Mecum, mantidos como exemplos.

## Ferramentas e formatos de terceiros

O projeto executa com apoio de ferramentas de código aberto de terceiros — entre outras,
[Bun](https://bun.sh), [Typst](https://typst.app), [uv](https://github.com/astral-sh/uv),
[ffmpeg](https://ffmpeg.org) e [whisper](https://github.com/openai/whisper) —, cada uma sob
a sua própria licença. A instalação é feita sob demanda (`preparar-ambiente` / `setup.sh`) e
nenhuma delas é redistribuída dentro deste repositório.

## Contribuições

- **Michelle Flores** — Nexx1 Contabilidade — contadora, especialista na nova arquitetura
  tributária, conectou o acervo ao assistente e testou o MCP em matéria tributária (split payment,
  créditos de IBS e CBS, Súmula Vinculante 13). O retorno veio por escrito, com número de tema, data
  e o passo a passo para reproduzir cada ponto — foi a primeira contribuição externa ao projeto
  (23/07/2026) e abriu os itens `BASE-033` a `BASE-041` do
  [BACKLOG](base-juridica/BACKLOG.md). Do que já entrou: as duas datas dos temas de repercussão
  geral, cada uma com o nome que a fonte lhe dá (julgamento da repercussão geral e fixação da tese);
  a ferramenta `cobertura_da_base`, que mostra a quem consulta pelo MCP a data do snapshot e os
  limites da base; o léxico de equivalências curado, declarado na própria resposta; os 227
  precedentes representativos das 63 súmulas vinculantes, extraídos da página oficial do STF em vez
  de inferidos; e a indexação da LC 214/2025 (IBS, CBS e Imposto Seletivo) junto com as LC 227/2026,
  LC 225/2026 e LC 220/2025 — o acervo passou de 273 para 277 diplomas e de 22.180 para 23.064
  dispositivos. Os itens `BASE-038` a `BASE-041`, ainda abertos, também vieram daí.
- **Rafael Nogueira Reis** ([@rafael-reis-advogados](https://github.com/rafael-reis-advogados))
  — sócio-administrador do Girotto e Reis Advogados (Jandaia do Sul-PR) — achou e corrigiu
  o defeito do `BASE-042` nos temas repetitivos: a consulta por
  número puro devolvia **outro** tema, formatado como acerto e com o carimbo de observância
  obrigatória do art. 927, III, do CPC. O diagnóstico chegou com a causa no dado
  (`terms["981"] = [1056]`, porque o Tema 1056 cita o EREsp 1.121.981/RJ), teste de
  regressão com guarda da premissa e a verificação completa reproduzida sobre cópia limpa
  do repositório. A revisão da contribuição revelou o mesmo mecanismo nas súmulas e na
  legislação, corrigido junto. Verificação em
  [`base-juridica/verificacoes/BASE-042.md`](base-juridica/verificacoes/BASE-042.md).
- **Ruan Lucas** ([@ruanlucas-adv](https://github.com/ruanlucas-adv)) — primeiro pull request
  externo aceito no repositório
  ([#23](https://github.com/emidio-trancoso/advocacia-aberta/pull/23), aberto em 14/08/2026 e
  aceito em 31/08/2026): cobertura de teste para `construir_indice_geo.py`, o único script de
  `ferramentas/manutencao/` que ainda não tinha par de teste. São oito casos sobre a conversão
  de IPv4 em inteiro usada nas faixas do índice de geolocalização — endereço válido, extremos,
  IPv6, entrada vazia e malformada —, todos verificados contra o comportamento real da função
  antes do aceite. Não muda comportamento; protege contra regressão silenciosa o índice que
  alimenta o relatório de acesso ao acervo.
- **[@peraivo](https://github.com/peraivo)** — comunidade — relatou o `BASE-050` na
  [issue #26](https://github.com/emidio-trancoso/advocacia-aberta/issues/26) (06/10/2026): nos
  diplomas cuja página do Planalto exibe a redação anterior **riscada**, os parágrafos e incisos
  revogados entravam no texto do artigo como texto comum, a redação revogada **primeiro** e sob o
  rótulo "FONTE OFICIAL". Quem lesse o art. 26, § 2º, da Lei 9.514 pegava a versão revogada, e a
  busca por palavras casava com o texto antigo (`"quarenta por cento"` só existe no § 1º riscado do
  art. 3º do DL 911). O relato chegou com comando de reprodução, cinco dispositivos conferidos um a
  um na fonte, a medida do alcance com as próprias ressalvas de super e subcontagem, e a causa
  localizada no código — a checagem de riscado era aplicada só ao caput. A observação que decidiu a
  correção é dele: o `<strike>` fica **dentro** do `<p>`, e a função subia apenas pelos ancestrais.
  Apontou também que nenhum teste mencionava texto riscado. Corrigido em 17/10/2026: 3.697
  parágrafos riscados deixaram de entrar nos artigos em 195 dos 277 diplomas, com quatro testes de
  regressão sobre padrões reais. Verificação em
  [`base-juridica/verificacoes/BASE-050.md`](base-juridica/verificacoes/BASE-050.md).
