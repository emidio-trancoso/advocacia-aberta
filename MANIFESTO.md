# Manifesto da Advocacia Aberta

A inteligência artificial chegou ao Direito antes de o Direito estar pronto para ela. O resultado
apareceu rápido: peças com jurisprudência que nunca existiu, citações fabricadas com aparência de
verdade, e tribunais que já aplicam sanções por isso. Diante disso, o mercado passou a vender mais
ferramentas e o meio jurídico passou a debater efeitos e regulação. Nenhuma das duas reações tocou a
causa.

**A alucinação não é a doença — é o sintoma. A doença é o dado ilegível.** Quando a fonte não chega
organizada ao modelo, ele completa a lacuna com o provável. O problema nunca foi *qual* IA usar; foi
a ausência de um método explícito e de um dado que a máquina — e a pessoa — consigam ler.

A **Advocacia Aberta** responde a isso construindo o que falta, em vez de apenas debatê-lo. Não
abrimos processos, estratégias ou dados de clientes. **Abrimos o acervo e o método.**

## Para que serve

A Advocacia Aberta existe para que o trabalho jurídico com IA seja ao mesmo tempo **eficaz e
confiável** — e sustenta que isso não se decide no discurso, mas nos **dados** e no **método**.

Tornar o procedimento **explícito** e o dado **legível**, para a pessoa e para a máquina, é o que o
projeto entrega. São dois pilares:

- **Acervo — o material.** Não são só dados: são dados organizados por uma **taxonomia jurídica** —
  natureza, proveniência e efeito — que os torna legíveis por um agente de IA, com a fonte oficial
  em cada item.
- **Método — o procedimento.** **Protocolos** transformam operações jurídicas em
  procedimentos-padrão que a IA executa e o profissional audita; e o **gerenciamento de contexto**
  mantém o trabalho vivo entre etapas — o que foi lido, decidido e produzido chega à etapa seguinte,
  em vez de morrer numa janela de conversa.

É a virada que o projeto propõe: sair do **fenômeno jurídico tratado como teoria** e ancorar o
trabalho em **dados**. O mesmo material que ensina a IA a trabalhar mostra ao desenvolvedor como se
organiza o conhecimento jurídico — e mostra ao advogado o que, de fato, é trabalhar com IA.

## A prova é pública

Isto não fica na palavra. Toda mudança no acervo passa por uma régua fixa: **89 consultas reais**,
julgadas uma a uma à mão, medem se a busca ainda devolve o que deveria — e uma mudança que piora
esse resultado é barrada antes de entrar (ver a
[avaliação de recuperação](base-juridica/AVALIACAO-RECUPERACAO.md)). Cada correção fica
[registrada em público](base-juridica/verificacoes/), com a fonte oficial que a motivou. Todo começo
de semana, um [monitor agendado](.github/workflows/monitorar-base.yml) relê Planalto, STF e STJ e
abre uma issue quando uma lei muda ou uma súmula cai — mas quem decide o que entra continua sendo uma
pessoa. São **~52.795 registros**, cada um com link para a fonte oficial. E o método inteiro pode ser
visto rodando num [caso completo](casos/exemplo-trafico-sintetico/) — do primeiro documento à peça
pronta.

E a prova não para em ler. O sistema inteiro é um repositório público: você o clona, roda no seu
próprio agente e confere que faz o que dizemos. O que encontrar de errado, corrige; o que fizer
melhor, devolve. A prova não se pede em confiança — **se refaz**, e melhora a cada mão que passa por
ela.

## Por que aberta

Porque conhecimento jurídico é bem público, e método não precisa ser propriedade de ninguém.

- **Sem aprisionamento — nem a fornecedor, nem a modelo.** A pergunta que domina o meio — "qual é a
  ferramenta de IA?" — mira no que passa. A ferramenta é efêmera, e o próprio modelo de IA também:
  numa corrida em que "a IA do momento" se troca em meses, apostar no modelo é apostar no
  transitório. O que permanece é o **acervo e o método** — que se acumulam, se somam e se
  transformam, mas não se descartam a cada nova geração de tecnologia. Por isso o método é legível e
  executável por qualquer agente: trocar a ferramenta não apaga o que foi construído.
- **Dado público sem pedágio.** Legislação, súmulas e jurisprudência são públicas. Organizá-las para
  que uma IA as leia é trabalho — mas transformar esse acesso em barreira paga é cercar um bem comum.
  A Advocacia Aberta pega o dado público, organiza para ser lido por agentes e **não cobra por isso**.
- **Contra o debate que não entrega.** As questões sobre os efeitos jurídicos da IA —
  responsabilidade, ética, regulação — são pertinentes e precisam ser enfrentadas. Mas debatê-las não
  basta: os dilemas que travam a prática só se resolvem quando alguém constrói, **de forma aberta**, o
  dado legível e o método explícito. Este projeto não substitui esse debate — entrega a
  infraestrutura que faltava a ele.

## O que defendemos

Um trabalho jurídico assistido por IA que se sustenta em compromissos verificáveis, não em promessa:

- **O método é legível.** Para a máquina que o executa e para quem o audita.
- **A prova se refaz, e o bem melhora.** Não pedimos confiança: o sistema é público e reproduzível.
  Quem quiser clona, roda e confere — e o que aprimora, devolve.
- **A fonte vem antes da afirmação.** Cada item do acervo aponta para o original oficial.
- **A incerteza é declarada.** O acervo publica cobertura e limites; o protocolo proíbe inventar fato
  ou citação.
- **A tecnologia é substituível.** Nenhum fornecedor e nenhum modelo é dono do trabalho.
- **O que é público não se cerca.** Lei, súmula e precedente são de todos; organizá-los para uma IA
  ler não os torna propriedade de quem organizou.
- **O caso é do cliente.** Abre-se o método; processo, estratégia e dado sigiloso ficam privados.
- **Quem assina responde.** A decisão é de quem tem OAB.

Esses compromissos, em detalhe operacional, estão em [PRINCIPIOS.md](PRINCIPIOS.md).

Método aberto se constrói junto. Quem se reconhece nisto pode adotar, criticar, melhorar — e assinar.

> **Método aberto. Fontes verificáveis. Dados protegidos.**

Este manifesto define a direção do projeto. O conteúdo autoral da Advocacia Aberta é distribuído sob
a licença [MIT](LICENSE), que permite uso, cópia, modificação e redistribuição para qualquer
finalidade, inclusive comercial, desde que se mantenha o aviso de copyright e a permissão. Materiais
de terceiros preservam sua situação jurídica e sua proveniência (ver [CREDITOS.md](CREDITOS.md)).

## Quem assina

Este manifesto é um compromisso público, não um contrato. Quem se reconhece nestes princípios
pode assiná-lo. A adesão é livre e não cria vínculo, obrigação ou representação entre os
signatários.

- **Emidio Trancoso** — Maringá/PR · autor do projeto · primeiro signatário

> **Quer assinar?** Abra um *pull request* acrescentando seu nome a esta lista, no formato
> `Nome — Cidade/UF · uma linha opcional`. Assinar significa concordar com os princípios acima —
> não é oferta de serviço, publicidade nem captação de clientela.
