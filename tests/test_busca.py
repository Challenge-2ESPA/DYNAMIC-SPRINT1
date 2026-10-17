# Testes das buscas. Rodar: python -m unittest discover -s tests -v
import unittest

from busca import (acumular, busca_binaria, busca_linear, ordenar_ids,
                   primeira_leitura_binaria, primeira_leitura_linear)


class TestBuscaLinear(unittest.TestCase):
    def test_encontra_e_conta(self):
        lista = [{"id": "ESC-1"}, {"id": "ESC-2"}, {"id": "ESC-3"}]
        self.assertEqual(busca_linear(lista, "ESC-2", "id"), (1, 2))

    def test_nao_encontra(self):
        self.assertEqual(busca_linear([{"id": "ESC-1"}], "ESC-9", "id"), (-1, 1))


class TestBuscaBinaria(unittest.TestCase):
    def test_encontra(self):
        lista = [{"id": "ESC-1"}, {"id": "ESC-2"}, {"id": "ESC-3"}, {"id": "ESC-4"}]
        posicao, comparacoes = busca_binaria(lista, "ESC-3", "id")
        self.assertEqual(posicao, 2)
        self.assertLessEqual(comparacoes, 4)

    def test_nao_encontra(self):
        lista = [{"id": "ESC-1"}, {"id": "ESC-3"}]
        self.assertEqual(busca_binaria(lista, "ESC-2", "id")[0], -1)

    def test_acha_todos_os_ids_do_dataset(self):
        ids = ordenar_ids(["ESC-%03d" % i for i in range(197, 0, -1)])
        lista = [{"id": i} for i in ids]
        for posicao, alvo in enumerate(ids):
            self.assertEqual(busca_binaria(lista, alvo, "id")[0], posicao)

    def test_faz_menos_comparacoes_que_linear(self):
        lista = [{"id": "ESC-%d" % i} for i in range(1, 101)]
        _, c_lin = busca_linear(lista, "ESC-100", "id")
        _, c_bin = busca_binaria(lista, "ESC-100", "id")
        self.assertLess(c_bin, c_lin)


class TestOrdenacaoEPrimeiraLeitura(unittest.TestCase):
    def test_ordenar_ids_usa_numero(self):
        self.assertEqual(ordenar_ids(["ESC-10", "ESC-2"]), ["ESC-2", "ESC-10"])

    def test_linear_e_binaria_concordam(self):
        alertas = [0, 1, 0, 0, 1, 1, 0, 1, 1]
        self.assertEqual(primeira_leitura_linear(alertas, 5)[0], 8)
        self.assertEqual(primeira_leitura_binaria(acumular(alertas), 5)[0], 8)

    def test_sem_alertas_suficientes(self):
        alertas = [0, 1, 0]
        self.assertEqual(primeira_leitura_linear(alertas, 5)[0], -1)
        self.assertEqual(primeira_leitura_binaria(acumular(alertas), 5)[0], -1)


if __name__ == "__main__":
    unittest.main()
