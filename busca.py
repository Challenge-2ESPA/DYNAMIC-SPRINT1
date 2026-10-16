"""Busca linear e busca binária, escritas à mão.

Cada comparação de chave conta como 1. Na busca binária, o `==` e o `<`
são contados separadamente, porque são duas comparações por passo.
"""


def busca_linear(lista: list[dict], alvo: str, chave: str) -> tuple[int, int]:
    """Retorna (posição, comparações) do primeiro item cuja chave é igual ao alvo.

    Não exige lista ordenada. Se não achar, a posição é -1.
    """
    comparacoes: int = 0
    for posicao, item in enumerate(lista):
        comparacoes += 1
        if item[chave] == alvo:
            return posicao, comparacoes
    return -1, comparacoes


def busca_binaria(lista: list[dict], alvo: str, chave: str) -> tuple[int, int]:
    """Retorna (posição, comparações) usando divisão ao meio.

    Exige lista ordenada pela chave. Se não achar, a posição é -1.
    """
    comparacoes: int = 0
    inicio: int = 0
    fim: int = len(lista) - 1
    while inicio <= fim:
        meio: int = (inicio + fim) // 2
        valor = lista[meio][chave]

        comparacoes += 1
        if valor == alvo:
            return meio, comparacoes

        comparacoes += 1
        if valor < alvo:
            inicio = meio + 1
        else:
            fim = meio - 1
    return -1, comparacoes


def primeira_leitura_linear(alertas: list[int], limite: int) -> tuple[int, int]:
    """Retorna (índice, comparações) da primeira posição em que o acumulado chega ao limite.

    alertas: 0 ou 1 por leitura, na ordem de horário. Se não chegar, o índice é -1.
    """
    acumulado: int = 0
    comparacoes: int = 0
    for indice, alerta in enumerate(alertas):
        acumulado += alerta
        comparacoes += 1
        if acumulado >= limite:
            return indice, comparacoes
    return -1, comparacoes


def primeira_leitura_binaria(acumulados: list[int], limite: int) -> tuple[int, int]:
    """Retorna (índice, comparações) da primeira posição em que o acumulado chega ao limite.

    acumulados: soma acumulada de alertas. Ela nunca diminui, então a busca binária
    encontra a primeira posição em que o valor atinge o limite.
    """
    inicio: int = 0
    fim: int = len(acumulados) - 1
    resposta: int = -1
    comparacoes: int = 0
    while inicio <= fim:
        meio: int = (inicio + fim) // 2
        comparacoes += 1
        if acumulados[meio] >= limite:
            resposta = meio
            fim = meio - 1
        else:
            inicio = meio + 1
    return resposta, comparacoes


def acumular(alertas: list[int]) -> list[int]:
    """Retorna a soma acumulada dos alertas, em uma única passagem."""
    acumulados: list[int] = []
    total: int = 0
    for alerta in alertas:
        total += alerta
        acumulados.append(total)
    return acumulados


def ordenar_ids(ids: list[str]) -> list[str]:
    """Retorna os IDs ordenados pelo número, para que ESC-2 venha antes de ESC-10."""
    return sorted(ids, key=lambda id_escada: int(id_escada.split("-")[1]))
