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


def rota_ida_e_volta(linha, estacao):
    # Ida: empilha cada estacao com append (da base ate o destino).
    # Volta: desempilha com pop() (do destino de volta para a base).
    pilha = []
    minutos_ida = 0
    encontrou = False
    for registro in linha:
        pilha.append(registro["estacao"])
        if registro["estacao"] == estacao:
            encontrou = True
            break
        minutos_ida += registro["minutos_ate_proxima"]

    if not encontrou:
        raise ValueError(f"Estação '{estacao}' não existe na linha")

    ida = list(pilha)  # copia a rota de ida antes de desempilhar
    volta = []
    while pilha:
        volta.append(pilha.pop())

    return {
        "ida": ida,
        "volta": volta,
        "minutos_ida": minutos_ida,
        "minutos_ida_volta": minutos_ida * 2,
    }
