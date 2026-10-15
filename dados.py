# Leitura do CSV de sensores e regra de alerta.

import csv

from gerar_dataset import FAIXAS


def ler_leituras(caminho):
    # Le o sensores.csv. Os valores numericos usam ponto decimal.
    leituras = []
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            leitura = {
                "id_escada": linha["id_escada"],
                "estacao": linha["estacao"],
                "grupo": linha["grupo"],
                "data_hora": linha["data_hora"],
            }
            for sensor in FAIXAS:
                leitura[sensor] = float(linha[sensor])
            leituras.append(leitura)
    return leituras


def esta_em_alerta(leitura):
    # Alerta: algum sensor sai da faixa normal
    for sensor, (minimo, maximo) in FAIXAS.items():
        if not (minimo <= leitura[sensor] <= maximo):
            return True
    return False
