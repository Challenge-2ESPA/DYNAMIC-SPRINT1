# Testes do percurso na linha. Rodar: python -m unittest test_linha -v
import os
import tempfile
import unittest

from linha import ler_linha, tempo_ate

LINHA = [
    {"estacao": "Luz", "minutos_ate_proxima": 3},
    {"estacao": "República", "minutos_ate_proxima": 3},
    {"estacao": "Paulista", "minutos_ate_proxima": 2},
    {"estacao": "Pinheiros", "minutos_ate_proxima": 0},
]


class TestTempoAte(unittest.TestCase):
    def test_base_e_zero(self):
        self.assertEqual(tempo_ate(LINHA, "Luz"), 0)

    def test_soma_minutos_desde_a_base(self):
        self.assertEqual(tempo_ate(LINHA, "Paulista"), 6)
        self.assertEqual(tempo_ate(LINHA, "Pinheiros"), 8)

    def test_estacao_inexistente(self):
        with self.assertRaises(ValueError):
            tempo_ate(LINHA, "Sé")


class TestLerLinha(unittest.TestCase):
    def test_le_o_csv_na_ordem(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "linha.csv")
            with open(caminho, "w", encoding="utf-8") as arq:
                arq.write("ordem,estacao,minutos_ate_proxima\n1,Luz,3\n2,República,0\n")
            linha = ler_linha(caminho)
            self.assertEqual(linha[0], {"estacao": "Luz", "minutos_ate_proxima": 3})
            self.assertEqual(len(linha), 2)


if __name__ == "__main__":
    unittest.main()
