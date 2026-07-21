# Para quem constrói

Se você constrói com LLMs, conhece o padrão: o modelo é bom, mas alucina quando falta contexto
recuperável. A Advocacia Aberta é um estudo de caso aberto de como se resolve isso num domínio
difícil — o Direito brasileiro — pela via do dado e do método, não do modelo do momento.

A tese: **dado legível vem antes do modelo.** A ferramenta e o próprio modelo são efêmeros; o que
permanece é o dado organizado e o método explícito. É "AI-last" — a IA é o executor intercambiável
de um harness que continua legível por pessoas.

## O que você encontra

- **Um acervo com taxonomia, não um dump.** 22.180 dispositivos de legislação, além de súmulas, teses
  e jurisprudência do STF/STJ, classificados por natureza, proveniência e efeito
  ([TAXONOMIA](base-juridica/TAXONOMIA.md)) — é o que separa "dado" de "dado legível por um agente".
- **Recuperação com gate de regressão.** Um
  [eval de 89 consultas julgadas à mão](base-juridica/AVALIACAO-RECUPERACAO.md) (precisão@5, recall e
  MRR por família) que quebra o CI ao regredir. Busca jurídica com teste, não no escuro.
- **Dados que se corrigem em público.** Cada correção tem um
  [relatório](base-juridica/verificacoes/) com fonte, mudança e teste; um
  [workflow](.github/workflows/monitorar-base.yml) vigia as fontes oficiais e abre issue quando mudam.
- **Engenharia de contexto explícita.** O [protocolo de contexto](GERENCIAR-CONTEXTO.md) e os
  protocolos mostram como delimitar, tornar legível, persistir e declarar lacunas — o harness, não o
  prompt.

## Como mexer

O motor de busca (`vade-mecum`) é TypeScript/Bun; a base é JSON versionado com schemas. Rode o eval
(`bun run avaliar`), estude a [arquitetura](ARQUITETURA.md), ou instale como
[plugin do Claude Code](README.md#rodar-a-via-plena-local-em-três-passos). Há também um
[adaptador de plugin da OpenAI](.codex-plugin/README.md) (`.codex-plugin/`) que publica um bundle
curado de skills autônomas para o ChatGPT Web/Codex. O método é agnóstico de jurisdição — a lógica
"dado legível + método explícito" se transporta para outro domínio.

Para contribuir: [CONTRIBUTING](CONTRIBUTING.md). Licença [MIT](LICENSE).
