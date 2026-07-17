# casos/ — onde mora cada caso

Cada processo ou matéria que você trabalha vira **uma pasta aqui dentro**.

## Como começar um caso novo

1. Copie a pasta `_modelo-de-caso/` e renomeie para o número do processo ou um nome
   curto — ex.: `0001234-56.2025.8.16.0000` ou `cliente-acme-rescisao`.
2. Jogue os documentos do caso dentro de `autos/` (PDFs, áudios, e-mails, contratos…).
3. Use as skills. Um bom começo é executar `organizar-caso` para
   `casos/<sua-pasta>` e gerar o resumo.

## A estrutura de cada caso

- `autos/` — os documentos e mídias do caso (o material bruto, o que **entra**).
- `analise/` — sínteses geradas pelas skills: `SUMARIO.md`, `DIAGNOSTICO.md`.
- `fundamentacao/` — `LEGISLACAO.md` e `JURISPRUDENCIA.md` (as fontes que sustentam as teses).
- `pecas/` — as peças que você produz e as versões diagramadas em PDF.

## Fluxo sugerido

```text
organizar-caso  →  diagnosticar  →  buscar-fontes (+ buscar-tjpr)
                                          ↓
            redigir-peca  →  revisar-peca  →  diagramar-peca
```

> O Git ignora os casos reais por padrão, mas isso não garante que todo agente ou
> ferramenta processe dados apenas localmente. Antes de usar material de cliente,
> conheça o destino do processamento e siga a
> [Política de sigilo e dados](../SIGILO-E-DADOS.md).
