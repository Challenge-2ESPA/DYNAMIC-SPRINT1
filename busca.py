#  busca linear e busca binaria.
# Cada comparacao de chave conta como 1 (o == e o < contam separadamente).


def busca_linear(lista, alvo, chave):
    # Percorre a lista do inicio ao fim. Nao exige lista ordenada.
    comparacoes = 0
    for posicao, item in enumerate(lista):
        comparacoes += 1
        if item[chave] == alvo:
            return posicao, comparacoes
    return -1, comparacoes


def busca_binaria(lista, alvo, chave):
    # Exige lista ordenada pela chave. Divide o intervalo ao meio a cada passo.
    comparacoes = 0
    inicio = 0
    fim = len(lista) - 1
    while inicio <= fim:
        meio = (inicio + fim) // 2
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


def primeira_leitura_linear(alertas, limite):
    # alertas: lista de 0 ou 1 por leitura, em ordem de horario.
    # Devolve o indice da primeira leitura em que o acumulado chega ao limite.
    acumulado = 0
    comparacoes = 0
    for indice, alerta in enumerate(alertas):
        acumulado += alerta
        comparacoes += 1
        if acumulado >= limite:
            return indice, comparacoes
    return -1, comparacoes


def primeira_leitura_binaria(acumulados, limite):
    # acumulados: soma acumulada de alertas (nunca diminui), entao a busca binaria
    # acha o primeiro indice em que o valor chega ao limite.
    inicio = 0
    fim = len(acumulados) - 1
    resposta = -1
    comparacoes = 0
    while inicio <= fim:
        meio = (inicio + fim) // 2
        comparacoes += 1
        if acumulados[meio] >= limite:
            resposta = meio
            fim = meio - 1
        else:
            inicio = meio + 1
    return resposta, comparacoes


def acumular(alertas):
    # Soma acumulada dos alertas, em uma passagem.
    acumulados = []
    total = 0
    for alerta in alertas:
        total += alerta
        acumulados.append(total)
    return acumulados


def ordenar_ids(ids):
    # Ordena os IDs pelo numero (ESC-2 vem antes de ESC-10).
    return sorted(ids, key=lambda id_escada: int(id_escada.split("-")[1]))
