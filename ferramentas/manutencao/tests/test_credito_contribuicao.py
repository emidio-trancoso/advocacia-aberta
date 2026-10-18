"""Contribuição externa fechada tem de aparecer em CREDITOS.md.

O projeto registra a origem externa de um item em dois lugares com réguas
diferentes, e um não alimenta o outro:

- `base-juridica/BACKLOG.md` e `base-juridica/verificacoes/BASE-0NN.md` registram
  a contribuição como **fato**, muitas vezes sem nomear quem contribuiu
  ("relatado pela comunidade", "levantado em contribuição externa");
- `CREDITOS.md` e a página de créditos do site (repo `advocacia-aberta-site`)
  são onde a pessoa é **creditada**.

Sem checagem, um item podia fechar com correção em produção e a contribuição
sumir da vitrine. Aconteceu com o `BASE-050`: relatado em 06/10/2026, corrigido
em 17/10, mergeado em 18/10 citando "contribuição da comunidade — issue #26", e
só creditado em 18/10 depois de alguém perguntar. Doze dias.

Este teste é o irmão, para o crédito, do `cobertura.test.ts` ("o relatório
mostra cada limitação que afeta cobertura"): recusa a omissão silenciosa.

O que ele NÃO alcança: a página de créditos do site vive noutro repositório.
A régua de cascatear para lá está escrita em `AGENTS.md`.
"""

from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
BACKLOG = ROOT / "base-juridica" / "BACKLOG.md"
CREDITOS = ROOT / "CREDITOS.md"

# O vocabulário realmente usado no backlog para marcar origem externa. Ele é
# inconsistente de propósito — as entradas foram escritas em datas diferentes —,
# então o teste aceita as formas existentes em vez de exigir uma só. Forma nova
# entra aqui.
VOCABULARIO_ORIGEM_EXTERNA = re.compile(
    r"contribui[çc][ãa]o externa"
    r"|contribui[çc][ãa]o da comunidade"
    r"|relatado pela comunidade"
    r"|relato externo"
    r"|teste externo",
    re.IGNORECASE,
)

# Itens de origem externa cuja autoria o repositório não registra, e que por isso
# não podem ser creditados sem perguntar ao mantenedor. Pendência declarada, não
# dispensa: sair desta lista é creditar ou confirmar que não há quem creditar.
SEM_AUTORIA_CONHECIDA = {
    # "Levantado em contribuição externa de 2026-07-27" (BACKLOG) e "A lacuna veio
    # de contribuição externa em 2026-07-27" (verificacoes/BASE-043.md). A leitura
    # contribuída foi que os campos da legislação eram todos estruturais e nenhum
    # temporal, enquanto a jurisprudência já trazia data e situação — e foi dela
    # que nasceu o índice de vigência inteiro.
    #
    # Procurado em 18/10/2026, sem achar o nome: o commit que abriu o item
    # (6d348cc, que só repete "contribuição externa de 27/07/2026"), o backlog, a
    # verificação, as issues e os PRs do repositório (não houve nenhuma atividade
    # no GitHub em 27/07) e as comunicações dos repos orion e hermes na janela de
    # 25 a 29/07. A contribuição chegou por canal privado, como a primeira.
    #
    # Pendente de confirmação do mantenedor — não se credita por inferência, e as
    # datas vizinhas (23/07 e 30/07) são de outras duas pessoas, o que torna o
    # palpite pior que a lacuna.
    "BASE-043",
}


def _itens_de_origem_externa() -> dict[str, str]:
    """BASE-0NN -> a linha do backlog, para os itens marcados como externos."""
    itens: dict[str, str] = {}
    for linha in BACKLOG.read_text(encoding="utf-8").splitlines():
        achado = re.match(r"\| `(BASE-\d+)`", linha)
        if achado and VOCABULARIO_ORIGEM_EXTERNA.search(linha):
            itens[achado.group(1)] = linha
    return itens


def _itens_creditados() -> set[str]:
    """Os BASE-0NN citados em CREDITOS.md, com as faixas expandidas.

    O crédito da primeira contribuição externa cobre uma faixa inteira
    ("abriu os itens `BASE-033` a `BASE-041`"), então procurar o identificador
    literal daria falso negativo em sete itens.
    """
    texto = re.sub(r"\s+", " ", CREDITOS.read_text(encoding="utf-8"))
    creditados = set(re.findall(r"BASE-\d+", texto))
    for inicio, fim in re.findall(r"BASE-(\d+)`?\s*a\s*`?BASE-(\d+)", texto):
        creditados |= {f"BASE-{n:03d}" for n in range(int(inicio), int(fim) + 1)}
    return creditados


class CreditoContribuicaoTest(unittest.TestCase):
    def test_todo_item_de_origem_externa_esta_creditado(self) -> None:
        creditados = _itens_creditados()
        sem_credito = sorted(
            identificador
            for identificador in _itens_de_origem_externa()
            if identificador not in creditados
            and identificador not in SEM_AUTORIA_CONHECIDA
        )
        self.assertEqual(
            sem_credito,
            [],
            "itens de origem externa ausentes de CREDITOS.md: "
            f"{', '.join(sem_credito)}. Credite a contribuição (e cascateie para a "
            "página de créditos do site, noutro repositório) ou, se a autoria não "
            "constar do repositório, declare o item em SEM_AUTORIA_CONHECIDA com o "
            "motivo.",
        )

    def test_o_backlog_tem_itens_de_origem_externa(self) -> None:
        """Guarda da premissa: se o vocabulário mudar, o teste acima passa vazio.

        Sem isto, renomear "contribuição externa" para outra forma faria o teste
        deixar de checar qualquer coisa — e passar.
        """
        self.assertGreaterEqual(len(_itens_de_origem_externa()), 5)

    def test_pendencia_declarada_continua_sendo_de_origem_externa(self) -> None:
        """A lista de exceção não sobrevive ao item que ela dispensa.

        Se o BASE-043 for creditado (ou deixar de ser externo), a entrada em
        SEM_AUTORIA_CONHECIDA vira ruído e este teste manda removê-la.
        """
        externos = _itens_de_origem_externa()
        creditados = _itens_creditados()
        for identificador in sorted(SEM_AUTORIA_CONHECIDA):
            self.assertIn(
                identificador,
                externos,
                f"{identificador} está em SEM_AUTORIA_CONHECIDA mas o backlog não o "
                "marca como de origem externa — remova a entrada.",
            )
            self.assertNotIn(
                identificador,
                creditados,
                f"{identificador} já está creditado em CREDITOS.md — remova a "
                "entrada de SEM_AUTORIA_CONHECIDA.",
            )


if __name__ == "__main__":
    unittest.main()
