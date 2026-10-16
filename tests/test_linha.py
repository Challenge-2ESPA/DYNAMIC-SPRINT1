# Testes do percurso na linha. Rodar: python -m unittest discover -s tests -v
import os
import tempfile
import unittest

from linha import ler_linha, rota_ida_e_volta, tempo_ate

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


class TestRotaIdaEVolta(unittest.TestCase):
    def test_ida_com_append_e_volta_com_pop(self):
        rota = rota_ida_e_volta(LINHA, "Paulista")
        self.assertEqual(rota["ida"], ["Luz", "República", "Paulista"])
        self.assertEqual(rota["volta"], ["Paulista", "República", "Luz"])
        self.assertEqual(rota["minutos_ida"], 6)
        self.assertEqual(rota["minutos_ida_volta"], 12)

    def test_base_tem_rota_vazia_de_minutos(self):
        rota = rota_ida_e_volta(LINHA, "Luz")
        self.assertEqual(rota["ida"], ["Luz"])
        self.assertEqual(rota["minutos_ida_volta"], 0)

    def test_estacao_inexistente(self):
        with self.assertRaises(ValueError):
            rota_ida_e_volta(LINHA, "Sé")


if __name__ == "__main__":
    unittest.main()
