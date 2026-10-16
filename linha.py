"""Percurso na linha com pilha.

A linha é uma lista de dicionários, em ordem. A base fica na primeira posição.
A ida empilha as estações com append; a volta desempilha com pop().
"""

import csv


def ler_linha(caminho: str) -> list[dict]:
    """Retorna a linha do CSV (ordem, estação, minutos até a próxima) como lista de dicionários."""
    linha: list[dict] = []
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        for registro in csv.DictReader(arquivo):
            linha.append({
                "estacao": registro["estacao"],
                "minutos_ate_proxima": int(registro["minutos_ate_proxima"]),
            })
    return linha


def tempo_ate(linha: list[dict], estacao: str) -> int:
    """Retorna os minutos da base até a estação, somando os trechos.

    Levanta ValueError se a estação não existir na linha.
    """
    minutos: int = 0
    for registro in linha:
        if registro["estacao"] == estacao:
            return minutos
        minutos += registro["minutos_ate_proxima"]
    raise ValueError(f"Estação '{estacao}' não existe na linha")


def rota_ida_e_volta(linha: list[dict], estacao: str) -> dict:
    """Retorna a rota de ida e de volta da base até a estação e os minutos de cada trecho.

    A ida empilha cada estação. A volta desempilha, começando no destino e terminando na base.
    Levanta ValueError se a estação não existir na linha.
    """
    pilha: list[str] = []
    minutos_ida: int = 0
    encontrou: bool = False
    for registro in linha:
        pilha.append(registro["estacao"])
        if registro["estacao"] == estacao:
            encontrou = True
            break
        minutos_ida += registro["minutos_ate_proxima"]

    if not encontrou:
        raise ValueError(f"Estação '{estacao}' não existe na linha")

    ida: list[str] = list(pilha)  # copia a rota de ida antes de desempilhar
    volta: list[str] = []
    while pilha:
        volta.append(pilha.pop())

    return {
        "ida": ida,
        "volta": volta,
        "minutos_ida": minutos_ida,
        "minutos_ida_volta": minutos_ida * 2,
    }
