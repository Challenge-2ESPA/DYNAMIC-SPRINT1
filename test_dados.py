# Testes da regra de alerta. Rodar: python -m unittest test_dados -v
import unittest

from dados import esta_em_alerta


def leitura_normal():
    return {"vibracao": 2.0, "temperatura": 50.0, "corrente": 15.0,
            "tensao": 380.0, "nivel_oleo": 80.0, "velocidade": 0.50}


class TestAlerta(unittest.TestCase):
    def test_leitura_normal_nao_alerta(self):
        self.assertFalse(esta_em_alerta(leitura_normal()))

    def test_sensor_fora_da_faixa_alerta(self):
        leitura = leitura_normal()
        leitura["vibracao"] = 5.0
        self.assertTrue(esta_em_alerta(leitura))

    def test_limite_da_faixa_nao_alerta(self):
        leitura = leitura_normal()
        leitura["tensao"] = 399.0
        self.assertFalse(esta_em_alerta(leitura))


if __name__ == "__main__":
    unittest.main()
