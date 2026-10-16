# Testes do gerador de dados. Rodar: python -m unittest discover -s tests -v
import os
import tempfile
import unittest

from gerar_dataset import gerar_dataset


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


if __name__ == "__main__":
    unittest.main()
