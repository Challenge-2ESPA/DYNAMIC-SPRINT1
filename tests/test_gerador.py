# Testes do gerador de dados. Rodar: python -m unittest discover -s tests -v
import os
import tempfile
import unittest

from gerar_dataset import COLUNAS, ESTACOES, gerar_dataset
from linha import ler_linha


class TestGerador(unittest.TestCase):
    def test_gera_escadas_e_leituras(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "sensores.csv")
            leituras, escadas = gerar_dataset(30, 200, 42, caminho)
            self.assertEqual(len(escadas), 30)
            self.assertEqual(len(leituras), 30 * 200)
            self.assertTrue(os.path.exists(caminho))

    def test_mesma_semente_mesmo_resultado(self):
        with tempfile.TemporaryDirectory() as pasta:
            a, _ = gerar_dataset(30, 200, 42, os.path.join(pasta, "a.csv"))
            b, _ = gerar_dataset(30, 200, 42, os.path.join(pasta, "b.csv"))
            self.assertEqual(a, b)

    def test_ids_com_tres_digitos_e_colunas(self):
        with tempfile.TemporaryDirectory() as pasta:
            leituras, escadas = gerar_dataset(30, 200, 42, os.path.join(pasta, "s.csv"))
            self.assertEqual(escadas[0]["id_escada"][:4], "ESC-")
            self.assertEqual(len(escadas[0]["id_escada"]), 7)
            self.assertEqual(list(leituras[0].keys()), COLUNAS)

    def test_perfis_60_30_10(self):
        with tempfile.TemporaryDirectory() as pasta:
            _, escadas = gerar_dataset(50, 200, 42, os.path.join(pasta, "s.csv"))
            perfis = [e["perfil"] for e in escadas]
            self.assertEqual((perfis.count("saudavel"), perfis.count("desgaste"),
                              perfis.count("falha")), (30, 15, 5))

    def test_leituras_de_cada_escada_em_ordem_de_horario(self):
        with tempfile.TemporaryDirectory() as pasta:
            leituras, _ = gerar_dataset(30, 200, 42, os.path.join(pasta, "s.csv"))
            horarios = [l["data_hora"] for l in leituras if l["id_escada"] == "ESC-001"]
            self.assertEqual(len(horarios), 200)
            self.assertEqual(horarios, sorted(horarios))

    def test_limites_do_enunciado(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "s.csv")
            with self.assertRaises(ValueError):
                gerar_dataset(29, 200, 42, caminho)
            with self.assertRaises(ValueError):
                gerar_dataset(198, 200, 42, caminho)
            with self.assertRaises(ValueError):
                gerar_dataset(30, 199, 42, caminho)

    def test_estacoes_iguais_as_do_linha_csv(self):
        raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        linha = ler_linha(os.path.join(raiz, "linha.csv"))
        self.assertEqual([r["estacao"] for r in linha], ESTACOES)
        self.assertGreaterEqual(len(linha), 8)


if __name__ == "__main__":
    unittest.main()
