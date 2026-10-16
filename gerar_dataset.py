"""Gerador do dataset sintético dos sensores das escadas rolantes.

Usa só a biblioteca padrão do Python. Com a mesma semente, o resultado é sempre igual.
As funções calculam e retornam. Só o bloco principal imprime e grava o arquivo final.
"""

import csv
import random
from datetime import datetime, timedelta

ESTACOES: list[str] = ["Luz", "República", "Paulista", "Oscar Freire", "Faria Lima",
                       "Pinheiros", "Butantã", "Vila Sônia"]

# Faixas normais de cada sensor: (mínimo, máximo)
FAIXAS: dict[str, tuple[float, float]] = {
    "vibracao": (1, 4),          # mm/s
    "temperatura": (35, 65),     # °C
    "corrente": (10, 25),        # A
    "tensao": (361, 399),        # V
    "nivel_oleo": (60, 100),     # %
    "velocidade": (0.48, 0.52),  # m/s
}

COLUNAS: list[str] = ["id_escada", "estacao", "grupo", "data_hora", "vibracao",
                      "temperatura", "corrente", "tensao", "nivel_oleo", "velocidade"]


def valor_normal(sensor: str) -> float:
    """Retorna um valor sorteado dentro da faixa normal do sensor."""
    minimo, maximo = FAIXAS[sensor]
    return random.uniform(minimo, maximo)


def gerar_dataset(
    n_escadas: int,
    n_leituras: int,
    semente: int,
    caminho_saida: str = "sensores.csv",
) -> tuple[list[dict], list[dict]]:
    """Gera as leituras e as escadas, grava o CSV e retorna (leituras, escadas).

    Cada escada recebe uma leitura por hora. Em cada hora, a ordem das escadas é
    embaralhada, como acontece num registro real.
    """
    random.seed(semente)

    # 1) Perfil de cada escada: 60% saudável, 30% desgaste, 10% falha
    qtd_desgaste: int = int(n_escadas * 0.3)
    qtd_falha: int = int(n_escadas * 0.1)
    qtd_saudavel: int = n_escadas - qtd_desgaste - qtd_falha

    perfis: list[str] = ["saudavel"] * qtd_saudavel + ["desgaste"] * qtd_desgaste + ["falha"] * qtd_falha
    random.shuffle(perfis)

    # 2) Cria a lista de escadas
    escadas: list[dict] = []
    for i in range(n_escadas):
        escada: dict = {
            "id_escada": "ESC-" + str(i + 1),
            "estacao": random.choice(ESTACOES),
            "grupo": random.choice(["crítica", "não crítica"]),
            "perfil": perfis[i],
        }
        escadas.append(escada)

    # 3) Gera as leituras: uma por hora para cada escada
    leituras: list[dict] = []
    inicio: datetime = datetime(2026, 1, 1, 0, 0)

    for hora in range(n_leituras):
        data_hora: datetime = inicio + timedelta(hours=hora)

        random.shuffle(escadas)  # embaralha a ordem das escadas em cada hora

        for escada in escadas:
            vibracao: float = valor_normal("vibracao")
            temperatura: float = valor_normal("temperatura")
            corrente: float = valor_normal("corrente")
            tensao: float = valor_normal("tensao")
            nivel_oleo: float = valor_normal("nivel_oleo")
            velocidade: float = valor_normal("velocidade")

            if escada["perfil"] == "desgaste":
                # piora aos poucos: quanto mais horas, maior o desgaste
                progresso: float = hora / n_leituras  # vai de 0 até 1
                vibracao = vibracao + 4 * progresso
                temperatura = temperatura + 20 * progresso
                nivel_oleo = nivel_oleo - 30 * progresso

            elif escada["perfil"] == "falha":
                # 5% de chance de um pico isolado
                if random.random() < 0.05:
                    vibracao = random.uniform(7, 10)
                    temperatura = random.uniform(75, 90)

            leituras.append({
                "id_escada": escada["id_escada"],
                "estacao": escada["estacao"],
                "grupo": escada["grupo"],
                "data_hora": data_hora.strftime("%Y-%m-%d %H:%M"),
                "vibracao": round(vibracao, 2),
                "temperatura": round(temperatura, 1),
                "corrente": round(corrente, 2),
                "tensao": round(tensao, 1),
                "nivel_oleo": round(nivel_oleo, 1),
                "velocidade": round(velocidade, 3),
            })

    # 4) Salva o CSV
    with open(caminho_saida, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS)
        escritor.writeheader()
        escritor.writerows(leituras)

    return leituras, escadas


def resumir_dataset(leituras: list[dict], escadas: list[dict]) -> dict:
    """Retorna o mínimo, a média e o máximo de cada sensor, e a contagem de escadas por perfil."""
    sensores: dict[str, dict[str, float]] = {}
    for sensor in FAIXAS:
        valores: list[float] = [leitura[sensor] for leitura in leituras]
        sensores[sensor] = {
            "minimo": min(valores),
            "media": sum(valores) / len(valores),
            "maximo": max(valores),
        }

    perfis: dict[str, int] = {"saudavel": 0, "desgaste": 0, "falha": 0}
    for escada in escadas:
        perfis[escada["perfil"]] += 1

    return {
        "sensores": sensores,
        "perfis": perfis,
        "total_leituras": len(leituras),
    }


if __name__ == "__main__":
    SEMENTE: int = 42
    leituras, escadas = gerar_dataset(n_escadas=50, n_leituras=200, semente=SEMENTE)
    resumo = resumir_dataset(leituras, escadas)

    print("===== RESUMO POR SENSOR =====")
    for sensor, valores in resumo["sensores"].items():
        print(f"{sensor:12} | min: {valores['minimo']:7.2f} | media: {valores['media']:7.2f} | max: {valores['maximo']:7.2f}")

    print("\n===== ESCADAS POR PERFIL =====")
    for perfil, quantidade in resumo["perfis"].items():
        print(f"{perfil:10}: {quantidade} escadas")

    print(f"\nTotal de leituras: {resumo['total_leituras']}")
    print("\nArquivo sensores.csv salvo!")
