"""Leitura do sensores.csv e regra de alerta.

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
