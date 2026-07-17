# BASE-009 — taxonomia documental e de efeito jurídico

| Campo | Valor |
|---|---|
| Verificação | 17 de julho de 2026 |
| Escopo | rótulos do motor, descrições MCP e documentação da base |
| Dados jurídicos alterados | nenhum JSON do acervo |
| Decisão | separar natureza documental, proveniência e efeito jurídico |

## Evidência oficial consultada

- a [Constituição Federal, art. 103-A](https://www.planalto.gov.br/ccivil_03/constituicao/constituicaocompilado.htm)
  reserva efeito vinculante à súmula vinculante nas condições constitucionais;
- o [Código de Processo Civil, art. 927, III](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105compilada.htm)
  trata da observância dos acórdãos em recursos extraordinário e especial repetitivos;
- o [STJ descreve Jurisprudência em Teses](https://centraldeajuda.stj.jus.br/faq/o-que-e-jurisprudencia-em-teses/)
  como publicação que reúne teses e os julgados que as sustentam;
- o [STJ apresenta os temas repetitivos](https://www.stj.jus.br/sites/portalp/Processos/Repetitivos-e-IACs/Saiba-mais/Sobre-Recursos-Repetitivos)
  dentro de sua gestão de precedentes qualificados.

## Mudança realizada

- “fonte primária” foi removida das superfícies de execução;
- fonte oficial passou a indicar somente proveniência;
- legislação, súmulas, Jurisprudência em Teses e temas repetitivos receberam naturezas
  documentais distintas;
- “persuasiva” e “orientativa” deixaram de funcionar como rótulos genéricos de força;
- estados não ativos de súmulas impedem que o motor presuma vigência;
- a saída de temas distingue tese publicada, ausência de tese, cancelamento, possível
  revisão e estados que exigem conferência;
- índices derivados foram explicitamente separados das fontes jurídicas.

## Validação executada

```bash
python3 ferramentas/manutencao/verificar_compatibilidade.py
python3 ferramentas/manutencao/auditar_base_juridica.py --strict
python3 -m unittest discover -s ferramentas/manutencao/tests -p 'test_*.py'
cd ferramentas/pesquisa/busca_delfus
bun run typecheck
bun test
```

O auditor não encontrou inconsistências, os 20 testes Python e os 16 testes Bun
passaram, e a tipagem TypeScript foi validada. O auditor agora também bloqueia a
reintrodução dos rótulos ambíguos nas superfícies públicas do motor.
