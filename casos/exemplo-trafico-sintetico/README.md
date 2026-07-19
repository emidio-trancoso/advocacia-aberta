# Caso-exemplo — `SINTÉTICO`

> **Tudo aqui é fictício.** Nomes, número de processo, comarca, datas e fatos foram inventados para
> demonstração. Nenhum dado real de cliente. É o único caso versionado no repositório — todos os
> demais em `casos/` são privados e ignorados pelo Git.

Este caso mostra o método da Advocacia Aberta **de ponta a ponta**, para quem quer ver o trabalho
sem instalar nada. Ele percorre o fluxo completo:

```text
organizar-caso  →  diagnosticar  →  buscar-fontes  →  redigir-peca  ( →  revisar-peca  →  diagramar-peca )
```

## O caso (fictício)

João da Silva Exemplo, 24 anos, primário, é preso em flagrante trazendo consigo duas drogas em
pequena quantidade. O Ministério Público o denuncia por tráfico (art. 33, *caput*, da Lei
11.343/2006) e sustenta o afastamento da causa de diminuição do tráfico privilegiado (§ 4º) apenas
pela variedade e quantidade. A defesa demonstra que a natureza e a quantidade, isoladamente, não
afastam o privilégio, e pede o reconhecimento da minorante na fração máxima.

## O que ver em cada pasta

| Pasta | Arquivo | Produzido pela skill |
|---|---|---|
| `autos/` | auto de prisão, denúncia, interrogatório e provas | (material bruto de entrada) |
| `analise/` | `SUMARIO.md`, `DIAGNOSTICO.md` | `organizar-caso`, `diagnosticar` |
| `fundamentacao/` | `LEGISLACAO.md`, `JURISPRUDENCIA.md` | `buscar-fontes` |
| `pecas/` | `alegacoes-finais-memoriais.md` | `redigir-peca` |

Toda fonte jurídica citada foi recuperada da base local do repositório (Vade Mecum) e aponta para a
origem oficial. Onde a íntegra depende de conferência, o texto diz isso — em vez de completar a
lacuna com o provável.
