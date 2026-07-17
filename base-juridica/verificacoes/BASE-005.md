# BASE-005 — contagem e art. 326-C do CTB

| Campo | Registro |
|---|---|
| Verificado em | 17 de julho de 2026 |
| Escopo | contagem do Código de Trânsito Brasileiro e art. 326-C |
| Problema | o metadado informava 390 artigos, mas a coleção continha 389 |
| Decisão | incluir o art. 326-C vigente e preservar o total de 390 no metadado |

## Fontes oficiais conferidas

- [texto compilado do Código de Trânsito Brasileiro no Planalto](https://www.planalto.gov.br/ccivil_03/leis/l9503compilado.htm);
- [Lei nº 15.452, de 30 de junho de 2026](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2026/lei/l15452.htm).

A Lei nº 15.452/2026 acrescentou o art. 326-C ao CTB para reconhecer o terceiro
domingo de novembro como o Dia Mundial em Memória das Vítimas do Trânsito. Seu art.
2º determinou vigência na data da publicação, ocorrida em 1º de julho de 2026. O texto
compilado do CTB já apresenta o novo dispositivo.

## Distinção temporal

O snapshot foi gerado em 30 de janeiro de 2026 com 389 registros, embora seu metadado
já informasse 390. O art. 326-C somente foi criado meses depois. Não é possível
reconstruir, com os artefatos versionados, a causa histórica daquele erro de contagem;
por isso, a correção não afirma que o artigo existia em janeiro.

Em 17 de julho, o coletor recebeu HTTP 200 para o texto compilado, cuja resposta
informava última modificação em 1º de julho. O adaptador `planalto_html_v1` reconheceu
o art. 326-C e produziu 390 registros.

## Alteração e validação

- o art. 326-C foi incluído com texto e URL do Planalto;
- os vínculos de navegação passaram a ser `326-B → 326-C → 327`;
- o total real passou de 389 para 390 e agora coincide com `total_artigos`;
- a soma legislativa do repositório passou de 6.802 para 6.803 registros;
- o novo artigo ficou sem palavras-chave derivadas, pendentes do processo reproduzível
  previsto no `BASE-010`;
- um teste de regressão confere presença, texto, contagem e navegação;
- a auditoria estrutural deixou de emitir `CONTAGEM_LEGISLACAO`.

Esta foi uma correção pontual. O candidato integral de julho continha outras mudanças
textuais, que não foram promovidas sem revisão individual.
