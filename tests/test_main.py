"""Testes das funções de saída do main.py. Rodar: python -m unittest discover -s tests -v"""

import unittest

from main import agrupar_por_escada, escadas_em_alerta, resumir_comparacoes, sortear_consultas

LEITURA_NORMAL: dict = {"vibracao": 2.0, "temperatura": 50.0, "corrente": 15.0,
                        "tensao": 380.0, "nivel_oleo": 80.0, "velocidade": 0.50}


def leitura(id_escada: str, data_hora: str, vibracao: float = 2.0) -> dict:
    registro = dict(LEITURA_NORMAL)
    registro.update({"id_escada": id_escada, "estacao": "Luz", "grupo": "crítica",
                     "data_hora": data_hora, "vibracao": vibracao})
    return registro


class TestAgrupar(unittest.TestCase):
    def test_agrupa_e_ordena_por_horario(self):
        leituras = [leitura("ESC-1", "2026-01-01 02:00"), leitura("ESC-1", "2026-01-01 01:00")]
        por_escada = agrupar_por_escada(leituras)
        self.assertEqual([l["data_hora"] for l in por_escada["ESC-1"]],
                         ["2026-01-01 01:00", "2026-01-01 02:00"])


class TestEscadasEmAlerta(unittest.TestCase):
    def test_pega_o_primeiro_alerta(self):
        leituras = [
            leitura("ESC-1", "2026-01-01 00:00"),
            leitura("ESC-1", "2026-01-01 01:00", vibracao=5.0),
            leitura("ESC-1", "2026-01-01 02:00", vibracao=6.0),
        ]
        em_alerta = escadas_em_alerta(agrupar_por_escada(leituras))
        self.assertEqual(em_alerta[0]["primeiro_alerta"], "2026-01-01 01:00")

    def test_escada_normal_fica_de_fora(self):
        em_alerta = escadas_em_alerta(agrupar_por_escada([leitura("ESC-1", "2026-01-01 00:00")]))
        self.assertEqual(em_alerta, [])


class TestSortearConsultas(unittest.TestCase):
    def test_mesma_semente_mesmos_ids(self):
        ids = ["ESC-1", "ESC-2", "ESC-3"]
        self.assertEqual(sortear_consultas(ids, 10, 42), sortear_consultas(ids, 10, 42))

    def test_quantidade_certa(self):
        self.assertEqual(len(sortear_consultas(["ESC-1"], 7, 42)), 7)


class TestResumirComparacoes(unittest.TestCase):
    def test_total_media_e_maximo(self):
        linhas = [
            {"comp_linear_arquivo": 2, "comp_linear_ids": 2, "comp_binaria": 1},
            {"comp_linear_arquivo": 4, "comp_linear_ids": 4, "comp_binaria": 3},
        ]
        resumo = {item["metodo"]: item for item in resumir_comparacoes(linhas)}
        self.assertEqual(resumo["Linear na lista do arquivo"]["total"], 6)
        self.assertEqual(resumo["Linear na lista do arquivo"]["media"], 3.0)
        self.assertEqual(resumo["Binária na lista de IDs"]["maximo"], 3)


if __name__ == "__main__":
    unittest.main()
