# Base jurídica

Esta pasta documenta o acervo jurídico estruturado da Advocacia Aberta.

Os JSONs permanecem junto ao motor **Vade Mecum**, em
`ferramentas/pesquisa/vade-mecum/data/`. Uma separação futura entre dados e motor só
deve ocorrer com migração explícita dos manifestos e testes.

- [CATALOGO.md](CATALOGO.md) — conteúdo, cobertura, proveniência e ressalvas.
- [BACKLOG.md](BACKLOG.md) — correções priorizadas e critérios de aceite.
- [TAXONOMIA.md](TAXONOMIA.md) — natureza documental, proveniência e efeito jurídico.
- [AVALIACAO-RECUPERACAO.md](AVALIACAO-RECUPERACAO.md) — corpus, métricas e gate de
  regressão da busca.
- [indices-derivados.json](indices-derivados.json) — geração reproduzível dos índices
  auxiliares de busca.
- [ATUALIZACAO.md](ATUALIZACAO.md) — coleta, transformação, validação, comparação e
  promoção controlada de snapshots.
- [fontes.json](fontes.json) — manifesto executável das fontes oficiais e adaptadores.

Para repetir a auditoria estrutural:

```bash
python3 ferramentas/manutencao/auditar_base_juridica.py
```

O relatório mede os arquivos locais. Ele não confirma vigência nem substitui a
consulta à fonte oficial.

Para preparar uma atualização sem alterar a base publicada:

```bash
python3 ferramentas/manutencao/atualizar_base_juridica.py executar \
  --execucao AAAA-MM-DD --conjunto temas_repetitivos_stj
```

Leia o protocolo antes de promover qualquer candidato.
