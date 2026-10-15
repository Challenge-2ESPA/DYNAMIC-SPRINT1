# Dataset sintetico dos sensores das escadas rolantes

import csv
import random
from datetime import datetime, timedelta

ESTACOES = ["Luz", "República", "Paulista", "Oscar Freire", "Faria Lima",
            "Pinheiros", "Butantã", "Vila Sônia"]

# Faixas normais de cada sensor (minimo, maximo)
FAIXAS = {
    "vibracao": (1, 4),          # mm/s
    "temperatura": (35, 65),     # °C
    "corrente": (10, 25),        # A
    "tensao": (361, 399),        # V
    "nivel_oleo": (60, 100),     # %
    "velocidade": (0.48, 0.52),  # m/s
}

COLUNAS = ["id_escada", "estacao", "grupo", "data_hora", "vibracao",
           "temperatura", "corrente", "tensao", "nivel_oleo", "velocidade"]


def valor_normal(sensor):
    # Sorteia um valor dentro da faixa normal do sensor
    minimo, maximo = FAIXAS[sensor]
    return random.uniform(minimo, maximo)


def gerar_dataset(n_escadas, n_leituras, semente, caminho_saida="sensores.csv"):
    # Gera n_escadas escadas com n_leituras leituras horarias cada.
    # As escadas ficam embaralhadas dentro de cada hora, como no arquivo final.
    random.seed(semente)

    # 1) Perfil de cada escada: 60% saudavel, 30% desgaste, 10% falha
    qtd_desgaste = int(n_escadas * 0.3)
    qtd_falha = int(n_escadas * 0.1)
    qtd_saudavel = n_escadas - qtd_desgaste - qtd_falha

    perfis = ["saudavel"] * qtd_saudavel + ["desgaste"] * qtd_desgaste + ["falha"] * qtd_falha
    random.shuffle(perfis)

    # 2) Cria a lista de escadas
    escadas = []
    for i in range(n_escadas):
        escada = {
            "id_escada": "ESC-" + str(i + 1),
            "estacao": random.choice(ESTACOES),
            "grupo": random.choice(["crítica", "não crítica"]),
            "perfil": perfis[i],
        }
        escadas.append(escada)

    # 3) Gera as leituras: uma por hora para cada escada
    leituras = []
    inicio = datetime(2026, 1, 1, 0, 0)

    for hora in range(n_leituras):
        data_hora = inicio + timedelta(hours=hora)

        random.shuffle(escadas)  # embaralha a ordem das escadas em cada hora

        for escada in escadas:
            vibracao = valor_normal("vibracao")
            temperatura = valor_normal("temperatura")
            corrente = valor_normal("corrente")
            tensao = valor_normal("tensao")
            nivel_oleo = valor_normal("nivel_oleo")
            velocidade = valor_normal("velocidade")

            if escada["perfil"] == "desgaste":
                # piora aos poucos: quanto mais horas, maior o desgaste
                progresso = hora / n_leituras  # vai de 0 ate 1
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


def mostrar_resumo(leituras, escadas):
    print("===== RESUMO POR SENSOR =====")
    for sensor in FAIXAS:
        valores = [leitura[sensor] for leitura in leituras]
        minimo = min(valores)
        media = sum(valores) / len(valores)
        maximo = max(valores)
        print(f"{sensor:12} | min: {minimo:7.2f} | media: {media:7.2f} | max: {maximo:7.2f}")

    print("\n===== ESCADAS POR PERFIL =====")
    contagem = {"saudavel": 0, "desgaste": 0, "falha": 0}
    for escada in escadas:
        contagem[escada["perfil"]] += 1
    for perfil in contagem:
        print(f"{perfil:10}: {contagem[perfil]} escadas")

    print(f"\nTotal de leituras: {len(leituras)}")


if __name__ == "__main__":
    SEMENTE = 42
    leituras, escadas = gerar_dataset(n_escadas=50, n_leituras=200, semente=SEMENTE)
    mostrar_resumo(leituras, escadas)
    print("\nArquivo sensores.csv salvo!")
