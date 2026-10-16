"""Roda as análises do DP e grava os resultados em saidas/.

Uso: python main.py sensores.csv linha.csv saidas

As funções calculam e retornam. Só o bloco principal imprime e grava arquivos.
"""

import csv
import json
import os
import random
import sys
import time

from busca import (acumular, busca_binaria, busca_linear, ordenar_ids,
                   primeira_leitura_binaria, primeira_leitura_linear)
from dados import esta_em_alerta, ler_leituras
from linha import ler_linha, rota_ida_e_volta, tempo_ate
from turno import perder_hora, planejar_turno

SEMENTE_CONSULTAS: int = 42
N_CONSULTAS: int = 1000
LIMITE_ALERTAS: int = 5
HORAS_DO_TURNO: tuple[int, ...] = (4, 6, 8)


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


def sortear_consultas(ids_ordenados: list[str], quantidade: int, semente: int) -> list[str]:
    """Sorteia IDs com semente fixa, para todos os métodos buscarem os mesmos IDs."""
    rnd = random.Random(semente)
    return [rnd.choice(ids_ordenados) for _ in range(quantidade)]


def comparar_buscas_por_id(
    leituras: list[dict],
    lista_ordenada: list[dict],
    consultas: list[str],
) -> list[dict]:
    """Retorna, para cada consulta, as comparações de cada método."""
    linhas: list[dict] = []
    for numero, alvo in enumerate(consultas, start=1):
        _, comp_linear_arquivo = busca_linear(leituras, alvo, "id_escada")
        _, comp_linear_ids = busca_linear(lista_ordenada, alvo, "id")
        _, comp_binaria = busca_binaria(lista_ordenada, alvo, "id")
        linhas.append({
            "consulta": numero,
            "id_escada": alvo,
            "comp_linear_arquivo": comp_linear_arquivo,
            "comp_linear_ids": comp_linear_ids,
            "comp_binaria": comp_binaria,
        })
    return linhas


def resumir_comparacoes(linhas_por_consulta: list[dict]) -> list[dict]:
    """Retorna total, média e máximo de comparações de cada método."""
    metodos = {
        "Linear na lista do arquivo": "comp_linear_arquivo",
        "Linear na lista de IDs": "comp_linear_ids",
        "Binária na lista de IDs": "comp_binaria",
    }
    resumo: list[dict] = []
    for nome, chave in metodos.items():
        valores = [linha[chave] for linha in linhas_por_consulta]
        resumo.append({
            "metodo": nome,
            "total": sum(valores),
            "media": round(sum(valores) / len(valores), 2),
            "maximo": max(valores),
        })
    return resumo


def comparar_primeira_leitura(
    por_escada: dict[str, list[dict]],
    ids_ordenados: list[str],
    limite: int,
) -> list[dict]:
    """Retorna, para cada escada, a primeira leitura com o limite de alertas e as comparações."""
    linhas: list[dict] = []
    for id_escada in ids_ordenados:
        alertas = [1 if esta_em_alerta(l) else 0 for l in por_escada[id_escada]]
        acumulados = acumular(alertas)
        posicao_linear, comp_linear = primeira_leitura_linear(alertas, limite)
        posicao_binaria, comp_binaria = primeira_leitura_binaria(acumulados, limite)
        if posicao_linear != posicao_binaria:
            raise AssertionError(f"As buscas divergem em {id_escada}")
        data_hora = por_escada[id_escada][posicao_linear]["data_hora"] if posicao_linear >= 0 else ""
        linhas.append({
            "id_escada": id_escada,
            "posicao_primeira_leitura": posicao_linear,
            "data_hora": data_hora,
            "comp_linear": comp_linear,
            "comp_binaria": comp_binaria,
        })
    return linhas


def tempos_da_base(linha: list[dict]) -> list[dict]:
    """Retorna, para cada estação, os minutos de ida e de ida e volta a partir da base."""
    tempos: list[dict] = []
    for registro in linha:
        destino = registro["estacao"]
        rota = rota_ida_e_volta(linha, destino)
        tempos.append({
            "estacao": destino,
            "minutos_ida": tempo_ate(linha, destino),
            "minutos_ida_volta": rota["minutos_ida_volta"],
        })
    return tempos


def planos_dos_turnos(linha: list[dict], em_alerta: list[dict]) -> dict[str, dict]:
    """Retorna o plano de cada turno e o plano caso o turno perca 1 hora."""
    base = linha[0]["estacao"]
    planos: dict[str, dict] = {}
    for horas in HORAS_DO_TURNO:
        plano = planejar_turno(base, horas, linha, em_alerta)
        planos[f"{horas}h"] = {
            "plano": plano,
            "se_perder_1_hora": perder_hora(plano),
        }
    return planos


def salvar_csv(caminho: str, linhas: list[dict]) -> None:
    """Grava uma lista de dicionários em CSV, com o cabeçalho das chaves."""
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0].keys()))
        escritor.writeheader()
        escritor.writerows(linhas)


def salvar_json(caminho: str, dados: dict) -> None:
    """Grava um dicionário em JSON, com acentos preservados."""
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def main(caminho_sensores: str, caminho_linha: str, pasta_saida: str) -> None:
    """Roda as análises, imprime o resumo e grava os arquivos de saída."""
    os.makedirs(pasta_saida, exist_ok=True)

    leituras = ler_leituras(caminho_sensores)
    por_escada = agrupar_por_escada(leituras)
    ids_ordenados = ordenar_ids(por_escada.keys())
    lista_ordenada = [{"id": id_escada} for id_escada in ids_ordenados]
    linha = ler_linha(caminho_linha)
    print(f"Leituras: {len(leituras)} | escadas: {len(ids_ordenados)} | estações: {len(linha)}")

    consultas = sortear_consultas(ids_ordenados, N_CONSULTAS, SEMENTE_CONSULTAS)
    por_consulta = comparar_buscas_por_id(leituras, lista_ordenada, consultas)
    resumo = resumir_comparacoes(por_consulta)
    primeira = comparar_primeira_leitura(por_escada, ids_ordenados, LIMITE_ALERTAS)

    print("\nComparações por método")
    for item in resumo:
        print(f"  {item['metodo']:30} total {item['total']:>6} | média {item['media']:>6} | máx {item['maximo']}")
    print(f"\nPrimeira leitura com {LIMITE_ALERTAS} alertas: "
          f"linear {sum(l['comp_linear'] for l in primeira)} | binária {sum(l['comp_binaria'] for l in primeira)}")

    salvar_csv(os.path.join(pasta_saida, "comparacoes_consultas.csv"), por_consulta)
    salvar_csv(os.path.join(pasta_saida, "comparacoes_resumo.csv"), resumo)
    salvar_csv(os.path.join(pasta_saida, "comparacoes_primeira_leitura.csv"), primeira)

    tempos = tempos_da_base(linha)
    print(f"\nPercurso a partir da base {linha[0]['estacao']}")
    for item in tempos:
        print(f"  {item['estacao']:14} ida {item['minutos_ida']:>3} min | ida e volta {item['minutos_ida_volta']:>3} min")
    salvar_csv(os.path.join(pasta_saida, "tempos_base.csv"), tempos)

    em_alerta = escadas_em_alerta(por_escada)
    planos = planos_dos_turnos(linha, em_alerta)
    print(f"\nPlano do turno: escadas em alerta: {len(em_alerta)}")
    for nome, dados in planos.items():
        plano = dados["plano"]
        desfeito = dados["se_perder_1_hora"]
        print(f"  {nome}: {len(plano['agenda'])} na agenda, {len(plano['pendentes'])} pendentes, "
              f"{plano['tempo_usado_min']} de {plano['limite_min']} min | "
              f"perdendo 1 h: {len(desfeito['agenda'])} na agenda")
    salvar_json(os.path.join(pasta_saida, "planos_turno.json"), planos)

    print(f"\nArquivos gravados em: {pasta_saida}")


if __name__ == "__main__":
    caminho_sensores_arg = sys.argv[1] if len(sys.argv) > 1 else "sensores.csv"
    caminho_linha_arg = sys.argv[2] if len(sys.argv) > 2 else "linha.csv"
    pasta_arg = sys.argv[3] if len(sys.argv) > 3 else "saidas"
    inicio = time.perf_counter()
    main(caminho_sensores_arg, caminho_linha_arg, pasta_arg)
    print(f"Tempo total: {time.perf_counter() - inicio:.2f} s")
