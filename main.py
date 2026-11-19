"""Citizen Assist AI - assistente de orientação ao cidadão (jovens no primeiro emprego)."""

import os

from base_conhecimento import BaseConhecimento
from assistente import Assistente

PASTA = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(PASTA, "data")


def main():
    base = BaseConhecimento(os.path.join(DATA, "base_conhecimento.json"))
    base.carregar()  # lê o JSON e cria os objetos Orientacao

    assistente = Assistente("Citizen Assist AI", base,
                            os.path.join(DATA, "historico.json"),
                            os.path.join(DATA, "atendimentos.csv"))
    try:
        assistente.menu()
    except (KeyboardInterrupt, EOFError):
        print("\n\nAtendimento encerrado.")
        assistente.exportar_csv()


if __name__ == "__main__":
    main()
