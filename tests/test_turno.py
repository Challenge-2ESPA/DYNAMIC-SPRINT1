"""Testes do turno. Rodar: python -m unittest discover -s tests -v"""

import unittest

from turno import (custo_atendimento, formatar_hora, montar_filas, perder_hora,
                   planejar_turno, tempo_de_servico)

LINHA: list[dict] = [
    {"estacao": "Luz", "minutos_ate_proxima": 3},
    {"estacao": "República", "minutos_ate_proxima": 3},
    {"estacao": "Paulista", "minutos_ate_proxima": 2},
    {"estacao": "Pinheiros", "minutos_ate_proxima": 0},
]


def escada(id_escada: str, estacao: str, grupo: str, primeiro: str) -> dict:
    return {"id_escada": id_escada, "estacao": estacao, "grupo": grupo, "primeiro_alerta": primeiro}


class TestTempoDeServico(unittest.TestCase):
    def test_critica_e_normal(self):
        self.assertEqual(tempo_de_servico("crítica"), 60)
        self.assertEqual(tempo_de_servico("não crítica"), 40)


class TestFormatarHora(unittest.TestCase):
    def test_turno_comeca_as_8(self):
        self.assertEqual(formatar_hora(0), "08:00")
        self.assertEqual(formatar_hora(95), "09:35")


class TestMontarFilas(unittest.TestCase):
    def test_separa_por_grupo_na_ordem_do_alerta(self):
        em_alerta = [
            escada("ESC-2", "Paulista", "crítica", "2026-01-01 05:00"),
            escada("ESC-1", "Paulista", "crítica", "2026-01-01 01:00"),
            escada("ESC-3", "Paulista", "não crítica", "2026-01-01 00:00"),
        ]
        critica, normal = montar_filas(em_alerta)
        self.assertEqual([e["id_escada"] for e in critica], ["ESC-1", "ESC-2"])
        self.assertEqual([e["id_escada"] for e in normal], ["ESC-3"])

    def test_listas_vazias(self):
        self.assertEqual(montar_filas([]), ([], []))


class TestCustoAtendimento(unittest.TestCase):
    def test_custo_e_ida_mais_servico_mais_volta(self):
        atendimento = custo_atendimento(LINHA, escada("ESC-1", "Paulista", "crítica", "x"))
        self.assertEqual(atendimento["custo_min"], 12 + 60)

    def test_base_custa_so_o_servico(self):
        atendimento = custo_atendimento(LINHA, escada("ESC-1", "Luz", "não crítica", "x"))
        self.assertEqual(atendimento["custo_min"], 40)


class TestPlanejarTurno(unittest.TestCase):
    def test_critica_entra_antes_da_normal(self):
        em_alerta = [
            escada("ESC-1", "Paulista", "não crítica", "2026-01-01 00:00"),
            escada("ESC-2", "Paulista", "crítica", "2026-01-01 05:00"),
        ]
        plano = planejar_turno("Luz", 4, LINHA, em_alerta)
        self.assertEqual(plano["agenda"][0]["id_escada"], "ESC-2")

    def test_inicio_e_fim_sao_encadeados(self):
        em_alerta = [
            escada("ESC-1", "Paulista", "crítica", "2026-01-01 00:00"),
            escada("ESC-2", "Paulista", "crítica", "2026-01-01 01:00"),
        ]
        plano = planejar_turno("Luz", 8, LINHA, em_alerta)
        self.assertEqual(plano["agenda"][0]["inicio_min"], 0)
        self.assertEqual(plano["agenda"][0]["fim_min"], 72)
        self.assertEqual(plano["agenda"][1]["inicio_min"], 72)

    def test_nao_passa_do_limite_e_o_resto_vai_para_pendentes(self):
        em_alerta = [escada("ESC-%d" % i, "Paulista", "crítica", "2026-01-01 00:00") for i in range(1, 6)]
        plano = planejar_turno("Luz", 4, LINHA, em_alerta)
        self.assertLessEqual(plano["tempo_usado_min"], 240)
        self.assertEqual(len(plano["agenda"]) + len(plano["pendentes"]), 5)

    def test_base_precisa_ser_primeira_estacao(self):
        with self.assertRaises(ValueError):
            planejar_turno("Paulista", 4, LINHA, [])

    def test_sem_escadas_em_alerta(self):
        plano = planejar_turno("Luz", 4, LINHA, [])
        self.assertEqual(plano["agenda"], [])
        self.assertEqual(plano["pendentes"], [])
        self.assertEqual(plano["tempo_usado_min"], 0)

    def test_sem_argumentos_le_os_arquivos_padrao(self):
        # Roda a partir da pasta do projeto, onde estão linha.csv e sensores.csv
        plano = planejar_turno("Luz", 4)
        self.assertEqual(plano["limite_min"], 240)
        self.assertEqual(len(plano["agenda"]) + len(plano["pendentes"]), 20)


class TestPerderHora(unittest.TestCase):
    def test_limite_cai_uma_hora(self):
        em_alerta = [escada("ESC-%d" % i, "Paulista", "crítica", "2026-01-01 00:00") for i in range(1, 5)]
        plano = planejar_turno("Luz", 4, LINHA, em_alerta)
        depois = perder_hora(plano)
        self.assertEqual(depois["limite_min"], 180)
        self.assertEqual(depois["horas"], 3)

    def test_desfaz_com_pop_ate_caber(self):
        em_alerta = [escada("ESC-%d" % i, "Paulista", "crítica", "2026-01-01 00:00") for i in range(1, 5)]
        plano = planejar_turno("Luz", 4, LINHA, em_alerta)  # 3 escadas: 216 min
        depois = perder_hora(plano)  # limite 180: sobra 2 escadas (144 min)
        self.assertEqual(len(depois["agenda"]), 2)
        self.assertEqual(depois["tempo_usado_min"], 144)
        self.assertEqual(depois["agenda"][-1]["id_escada"], "ESC-2")
        self.assertEqual(len(depois["agenda"]) + len(depois["pendentes"]), 4)

    def test_nao_desfaz_quando_ja_cabe(self):
        em_alerta = [escada("ESC-1", "Paulista", "crítica", "2026-01-01 00:00")]
        plano = planejar_turno("Luz", 4, LINHA, em_alerta)
        depois = perder_hora(plano)
        self.assertEqual(len(depois["agenda"]), 1)
        self.assertEqual(depois["pendentes"], [])

    def test_nao_altera_o_plano_original(self):
        em_alerta = [escada("ESC-%d" % i, "Paulista", "crítica", "2026-01-01 00:00") for i in range(1, 5)]
        plano = planejar_turno("Luz", 4, LINHA, em_alerta)
        perder_hora(plano)
        self.assertEqual(len(plano["agenda"]), 3)
        self.assertEqual(plano["limite_min"], 240)

    def test_desfeito_vai_para_pendentes_sem_horario(self):
        em_alerta = [escada("ESC-%d" % i, "Paulista", "crítica", "2026-01-01 00:00") for i in range(1, 5)]
        depois = perder_hora(planejar_turno("Luz", 4, LINHA, em_alerta))
        desfeito = depois["pendentes"][-1]
        self.assertEqual(desfeito["id_escada"], "ESC-3")
        self.assertNotIn("inicio", desfeito)

    def test_agenda_tem_inicio_e_fim_em_horario(self):
        em_alerta = [escada("ESC-1", "Paulista", "crítica", "2026-01-01 00:00")]
        item = planejar_turno("Luz", 4, LINHA, em_alerta)["agenda"][0]
        self.assertEqual((item["inicio"], item["fim"]), ("08:00", "09:12"))


if __name__ == "__main__":
    unittest.main()
