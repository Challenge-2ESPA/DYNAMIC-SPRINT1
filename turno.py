"""Plano do turno com filas (FIFO) e agenda (pilha).

A fila crítica é atendida antes da normal. Cada escada entra na agenda
se couber no tempo do turno; se não couber, vai para os pendentes.
"""

from dados import carregar_escadas_em_alerta
from linha import ler_linha, rota_ida_e_volta

TEMPO_SERVICO_CRITICA: int = 60  # minutos
TEMPO_SERVICO_NORMAL: int = 40   # minutos
MINUTOS_POR_HORA: int = 60
CAMINHO_LINHA: str = "linha.csv"
CAMINHO_SENSORES: str = "sensores.csv"


def montar_filas(escadas_em_alerta: list[dict]) -> tuple[list[dict], list[dict]]:
    """Retorna (fila_critica, fila_normal), na ordem do primeiro alerta."""
    ordenadas = sorted(
        escadas_em_alerta,
        key=lambda escada: (escada["primeiro_alerta"], escada["id_escada"]),
    )
    fila_critica: list[dict] = []
    fila_normal: list[dict] = []
    for escada in ordenadas:
        if escada["grupo"] == "crítica":
            fila_critica.append(escada)
        else:
            fila_normal.append(escada)
    return fila_critica, fila_normal


def tempo_de_servico(grupo: str) -> int:
    """Retorna o tempo de serviço em minutos: 60 para crítica e 40 para normal."""
    if grupo == "crítica":
        return TEMPO_SERVICO_CRITICA
    return TEMPO_SERVICO_NORMAL


def custo_atendimento(linha: list[dict], escada: dict) -> dict:
    """Retorna a rota e o custo (ida + serviço + volta) de uma escada."""
    servico = tempo_de_servico(escada["grupo"])
    rota = rota_ida_e_volta(linha, escada["estacao"])
    return {
        "id_escada": escada["id_escada"],
        "grupo": escada["grupo"],
        "estacao": escada["estacao"],
        "rota_ida": rota["ida"],
        "rota_volta": rota["volta"],
        "servico_min": servico,
        "custo_min": rota["minutos_ida_volta"] + servico,
    }


def planejar_turno(
    base: str,
    horas: int,
    linha: list[dict] | None = None,
    escadas_em_alerta: list[dict] | None = None,
) -> dict:
    """Retorna o plano do turno: agenda, pendentes e tempo usado.

    base: nome da estação-base, que precisa ser a primeira da linha.
    linha e escadas_em_alerta são opcionais. Se não forem passados, lê os arquivos
    linha.csv e sensores.csv da pasta atual. Quem testa pode passar dados de exemplo.
    """
    if linha is None:
        linha = ler_linha(CAMINHO_LINHA)
    if escadas_em_alerta is None:
        escadas_em_alerta = carregar_escadas_em_alerta(CAMINHO_SENSORES)

    if linha[0]["estacao"] != base:
        raise ValueError("A base precisa ser a primeira estação da linha")

    fila_critica, fila_normal = montar_filas(escadas_em_alerta)
    limite = horas * MINUTOS_POR_HORA
    agenda: list[dict] = []
    pendentes: list[dict] = []
    tempo_usado = 0

    for fila in (fila_critica, fila_normal):
        while fila:
            escada = fila.pop(0)
            atendimento = custo_atendimento(linha, escada)
            custo = atendimento["custo_min"]
            if tempo_usado + custo <= limite:
                atendimento["inicio_min"] = tempo_usado
                atendimento["fim_min"] = tempo_usado + custo
                agenda.append(atendimento)
                tempo_usado += custo
            else:
                pendentes.append(atendimento)

    return {
        "base": base,
        "horas": horas,
        "limite_min": limite,
        "tempo_usado_min": tempo_usado,
        "agenda": agenda,
        "pendentes": pendentes,
    }


def perder_hora(plano: dict) -> dict:
    """Retorna o plano com 1 hora a menos, desfazendo a agenda com pop() até caber.

    As escadas desfeitas vão para o fim dos pendentes. O plano original não é alterado.
    """
    novo_limite = plano["limite_min"] - MINUTOS_POR_HORA
    agenda = list(plano["agenda"])
    pendentes = list(plano["pendentes"])
    tempo_usado = plano["tempo_usado_min"]

    while tempo_usado > novo_limite and agenda:
        desfeito = agenda.pop()
        tempo_usado -= desfeito["custo_min"]
        pendentes.append(desfeito)

    return {
        "base": plano["base"],
        "horas": plano["horas"] - 1,
        "limite_min": novo_limite,
        "tempo_usado_min": tempo_usado,
        "agenda": agenda,
        "pendentes": pendentes,
    }
