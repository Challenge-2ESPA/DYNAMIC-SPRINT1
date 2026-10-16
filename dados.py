"""Leitura do sensores.csv, regra de alerta e escadas em alerta.

Uma leitura está em alerta quando pelo menos um sensor sai da faixa normal
definida em gerar_dataset.FAIXAS.
"""

import csv

from gerar_dataset import FAIXAS


def ler_leituras(caminho: str) -> list[dict]:
    """Retorna as leituras do CSV como dicionários, com os sensores convertidos para float."""
    leituras: list[dict] = []
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            leitura: dict = {
                "id_escada": linha["id_escada"],
                "estacao": linha["estacao"],
                "grupo": linha["grupo"],
                "data_hora": linha["data_hora"],
            }
            for sensor in FAIXAS:
                leitura[sensor] = float(linha[sensor])
            leituras.append(leitura)
    return leituras


def esta_em_alerta(leitura: dict) -> bool:
    """Retorna True se algum sensor estiver fora da faixa normal. O limite conta como normal."""
    for sensor, (minimo, maximo) in FAIXAS.items():
        if not (minimo <= leitura[sensor] <= maximo):
            return True
    return False


def agrupar_por_escada(leituras: list[dict]) -> dict[str, list[dict]]:
    """Retorna as leituras de cada escada, em ordem de horário."""
    por_escada: dict[str, list[dict]] = {}
    for leitura in leituras:
        por_escada.setdefault(leitura["id_escada"], []).append(leitura)
    for leituras_da_escada in por_escada.values():
        leituras_da_escada.sort(key=lambda leitura: leitura["data_hora"])
    return por_escada


def escadas_em_alerta(por_escada: dict[str, list[dict]]) -> list[dict]:
    """Retorna as escadas com algum alerta, com a estação, o grupo e a data do primeiro alerta."""
    encontradas: list[dict] = []
    for id_escada, leituras_da_escada in por_escada.items():
        primeiro = next((l for l in leituras_da_escada if esta_em_alerta(l)), None)
        if primeiro is not None:
            encontradas.append({
                "id_escada": id_escada,
                "estacao": primeiro["estacao"],
                "grupo": primeiro["grupo"],
                "primeiro_alerta": primeiro["data_hora"],
            })
    return encontradas


def carregar_escadas_em_alerta(caminho: str) -> list[dict]:
    """Lê o CSV de sensores e retorna as escadas com algum alerta."""
    return escadas_em_alerta(agrupar_por_escada(ler_leituras(caminho)))
