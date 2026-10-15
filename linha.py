# Percurso na linha. A linha e uma lista de dicionarios, em ordem.
# A base fica na primeira posicao.

import csv


def ler_linha(caminho):
    # Le o linha.csv (colunas: ordem, estacao, minutos_ate_proxima).
    linha = []
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        for registro in csv.DictReader(arquivo):
            linha.append({
                "estacao": registro["estacao"],
                "minutos_ate_proxima": int(registro["minutos_ate_proxima"]),
            })
    return linha


def tempo_ate(linha, estacao):
    # Busca linear pela estacao e soma os minutos desde a base.
    minutos = 0
    for registro in linha:
        if registro["estacao"] == estacao:
            return minutos
        minutos += registro["minutos_ate_proxima"]
    raise ValueError(f"Estação '{estacao}' não existe na linha")
