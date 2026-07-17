# Política de sigilo e dados

Esta política define a fronteira entre o que a **Advocacia Aberta** pretende
compartilhar e o que deve permanecer no ambiente privado de cada profissional ou
organização.

> **Regra central:** abrimos o método, nunca o caso do cliente.

## A fronteira público–privada

| Pode integrar a camada pública | Deve permanecer na camada privada |
|---|---|
| Protocolos e critérios de qualidade | Autos e documentos de clientes |
| Código dos motores e ferramentas | Dados pessoais e dados pessoais sensíveis |
| Bases formadas por fontes jurídicas públicas, com proveniência | Áudios, vídeos e transcrições reais |
| Modelos vazios e exemplos sintéticos | Estratégias, pareceres e análises de casos reais |
| Testes sem dados identificáveis | Credenciais, segredos e comunicações profissionais |
| Documentação de arquitetura e governança | Peças que permitam identificar o cliente ou a causa |

O fato de uma decisão judicial ou um dado constar de fonte pública não elimina
automaticamente deveres de sigilo, proteção de dados, minimização ou prudência na sua
reutilização em outro contexto.

## Regras para o espaço de casos

1. Cada caso deve permanecer em `casos/<numero-ou-nome>/`.
2. Os arquivos reais de `casos/` são ignorados pelo Git por padrão. Essa proteção
   reduz erros acidentais, mas **não é mecanismo suficiente de segurança**.
3. Documentos de clientes não devem ser copiados para `.agents/`, `.claude/`,
   `ferramentas/`, documentação, exemplos ou testes.
4. Um caso real nunca deve alimentar automaticamente a base jurídica pública.
5. Arquivos temporários, exportações e versões diagramadas merecem o mesmo cuidado
   que os documentos originais.
6. O responsável pelo ambiente deve adotar controle de acesso, cópia de segurança,
   criptografia e descarte compatíveis com seu risco e suas obrigações.

## Regras para agentes e ferramentas

Ao trabalhar neste repositório, o agente deve:

- ler apenas o material necessário para a tarefa atual;
- preferir processamento local quando isso for possível e adequado;
- não enviar arquivos a um novo serviço externo sem informar destino, finalidade e
  risco e obter autorização do usuário;
- não expor conteúdo sensível em logs, exemplos, mensagens de erro ou comandos;
- declarar arquivos que não conseguiu ler, em vez de inferir seu conteúdo;
- registrar resultados derivados dentro da pasta privada do caso;
- apontar as fontes utilizadas sem reproduzir dados pessoais desnecessários.

O uso de um agente hospedado já depende dos termos e controles da plataforma escolhida.
Esta política não presume que todo processamento seja local; ela exige que novas
transferências de dados não sejam silenciosas.

## Minimização de contexto

Dar contexto suficiente não significa fornecer todos os dados disponíveis. Antes de
incluir um documento, pergunte:

1. ele é necessário para a finalidade desta etapa?
2. uma síntese rastreável seria suficiente?
3. há dados que podem ser ocultados sem prejudicar o trabalho?
4. o destino e a retenção desse conteúdo são conhecidos?

O procedimento completo está em
[GERENCIAR-CONTEXTO.md](GERENCIAR-CONTEXTO.md).

## Exemplos e demonstrações

Exemplos públicos devem ser sintéticos ou passar por anonimização efetiva. Apenas
trocar nomes pode não ser suficiente: datas, valores, localidades, números processuais
e combinações de fatos também podem permitir reidentificação.

Todo exemplo deve indicar claramente uma destas condições:

- `SINTÉTICO` — criado para demonstração, sem origem em caso real;
- `FONTE PÚBLICA` — extraído de fonte identificada, com finalidade e recorte descritos;
- `ANONIMIZADO` — submetido a revisão específica de risco de reidentificação.

## Se houver exposição indevida

Ao suspeitar de exposição:

1. interrompa a publicação, sincronização ou compartilhamento;
2. preserve o mínimo de evidência necessário para entender o ocorrido;
3. identifique quais dados, pessoas, destinos e credenciais foram afetados;
4. revogue credenciais expostas e restrinja acessos;
5. procure o responsável jurídico e de segurança para avaliar contenção, comunicação
   e demais obrigações aplicáveis;
6. corrija o processo que permitiu o incidente.

Reescrever o histórico do Git pode reduzir a exposição futura, mas não apaga cópias já
clonadas, armazenadas em cache ou enviadas a terceiros.

## Alcance desta política

Este documento é uma regra operacional mínima do projeto. Ele não substitui análise
profissional sobre sigilo, proteção de dados, segurança da informação, contrato com
fornecedores ou deveres aplicáveis a cada organização e caso concreto.
