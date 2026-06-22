from calendar import monthrange

from django.db.models import Q, Sum
from django.utils import timezone

from . import models


TIPOS_MOVIMENTACAO_VALIDOS = ['entrada', 'saida', 'transferencia']


def obter_periodo_mes_atual():
    hoje = timezone.localdate()
    data_inicio = hoje.replace(day=1)
    data_fim = hoje.replace(day=monthrange(hoje.year, hoje.month)[1])

    return data_inicio, data_fim


def calcular_patrimonio_total(usuario, contas=None):
    if contas is None:
        contas = models.Conta.objects.filter(usuario=usuario)

    return sum(conta.saldo_atual for conta in contas)


def somar_movimentacoes(movimentacoes, tipo):
    return movimentacoes.filter(
        tipo=tipo
    ).aggregate(total=Sum('valor'))['total'] or 0


def filtrar_tipos_movimentacao(tipos_filtro):
    return [
        tipo
        for tipo in tipos_filtro
        if tipo in TIPOS_MOVIMENTACAO_VALIDOS
    ]


def filtrar_categorias_movimentacao(categorias_filtro, categorias):
    categorias_ids_validos = {
        str(categoria_id)
        for categoria_id in categorias.values_list('id', flat=True)
    }

    categorias_validas = [
        categoria_id
        for categoria_id in categorias_filtro
        if categoria_id in categorias_ids_validos
    ]
    incluir_sem_categoria = 'sem_categoria' in categorias_filtro

    categorias_filtradas = categorias_validas + (
        ['sem_categoria'] if incluir_sem_categoria else []
    )

    return categorias_validas, incluir_sem_categoria, categorias_filtradas


def aplicar_filtros_movimentacoes(
    movimentacoes,
    tipos_filtro=None,
    categorias_filtro=None,
    categorias=None
):
    tipos_filtrados = filtrar_tipos_movimentacao(tipos_filtro or [])

    if tipos_filtrados:
        movimentacoes = movimentacoes.filter(tipo__in=tipos_filtrados)

    categorias_filtradas = []

    if categorias is not None:
        (
            categorias_validas,
            incluir_sem_categoria,
            categorias_filtradas
        ) = filtrar_categorias_movimentacao(categorias_filtro or [], categorias)

        if categorias_validas or incluir_sem_categoria:
            filtro_categorias = Q()

            if categorias_validas:
                filtro_categorias |= Q(categoria_id__in=categorias_validas)

            if incluir_sem_categoria:
                filtro_categorias |= Q(categoria__isnull=True)

            movimentacoes = movimentacoes.filter(filtro_categorias)

    return movimentacoes, tipos_filtrados, categorias_filtradas


def calcular_resumo_movimentacoes(movimentacoes):
    total_entradas = somar_movimentacoes(movimentacoes, 'entrada')
    total_saidas = somar_movimentacoes(movimentacoes, 'saida')
    total_transferencias = somar_movimentacoes(movimentacoes, 'transferencia')
    resultado = total_entradas - total_saidas

    return {
        'entradas': total_entradas,
        'saidas': total_saidas,
        'transferencias': total_transferencias,
        'resultado': resultado,
    }


def calcular_resumo_periodo(
    usuario,
    data_inicio,
    data_fim,
    tipos_filtro=None,
    categorias_filtro=None,
    categorias=None
):
    movimentacoes_periodo = models.Movimentacao.objects.filter(
        usuario=usuario,
        data__range=[data_inicio, data_fim]
    )

    movimentacoes_periodo, tipos_filtro, categorias_filtro = (
        aplicar_filtros_movimentacoes(
            movimentacoes_periodo,
            tipos_filtro=tipos_filtro,
            categorias_filtro=categorias_filtro,
            categorias=categorias
        )
    )

    resumo = calcular_resumo_movimentacoes(movimentacoes_periodo)
    resumo['movimentacoes'] = movimentacoes_periodo
    resumo['tipos_filtro'] = tipos_filtro
    resumo['categorias_filtro'] = categorias_filtro

    return resumo


def calcular_resumo_por_conta(usuario, contas, movimentacoes_periodo):
    contas = contas.filter(usuario=usuario)
    movimentacoes_periodo = movimentacoes_periodo.filter(usuario=usuario)
    resumo_por_conta = []

    for conta in contas:
        entradas_conta = movimentacoes_periodo.filter(
            tipo='entrada',
            conta_destino=conta
        ).aggregate(total=Sum('valor'))['total'] or 0

        saidas_conta = movimentacoes_periodo.filter(
            tipo='saida',
            conta_origem=conta
        ).aggregate(total=Sum('valor'))['total'] or 0

        transferencias_recebidas = movimentacoes_periodo.filter(
            tipo='transferencia',
            conta_destino=conta
        ).aggregate(total=Sum('valor'))['total'] or 0

        transferencias_enviadas = movimentacoes_periodo.filter(
            tipo='transferencia',
            conta_origem=conta
        ).aggregate(total=Sum('valor'))['total'] or 0

        resultado_periodo = (
            entradas_conta
            - saidas_conta
            + transferencias_recebidas
            - transferencias_enviadas
        )

        resumo_por_conta.append({
            'conta': conta,
            'entradas': entradas_conta,
            'saidas': saidas_conta,
            'transferencias_recebidas': transferencias_recebidas,
            'transferencias_enviadas': transferencias_enviadas,
            'resultado_periodo': resultado_periodo,
        })

    return resumo_por_conta


def calcular_resumo_conta(
    usuario,
    conta,
    data_inicio,
    data_fim,
    tipos_filtro=None,
    categorias_filtro=None,
    categorias=None
):
    movimentacoes_periodo = models.Movimentacao.objects.filter(
        usuario=usuario,
        data__range=[data_inicio, data_fim]
    ).filter(
        Q(conta_origem=conta) | Q(conta_destino=conta)
    )

    movimentacoes_periodo, tipos_filtro, categorias_filtro = (
        aplicar_filtros_movimentacoes(
            movimentacoes_periodo,
            tipos_filtro=tipos_filtro,
            categorias_filtro=categorias_filtro,
            categorias=categorias
        )
    )

    entradas = movimentacoes_periodo.filter(
        tipo='entrada',
        conta_destino=conta
    ).aggregate(total=Sum('valor'))['total'] or 0

    saidas = movimentacoes_periodo.filter(
        tipo='saida',
        conta_origem=conta
    ).aggregate(total=Sum('valor'))['total'] or 0

    transferencias_recebidas = movimentacoes_periodo.filter(
        tipo='transferencia',
        conta_destino=conta
    ).aggregate(total=Sum('valor'))['total'] or 0

    transferencias_enviadas = movimentacoes_periodo.filter(
        tipo='transferencia',
        conta_origem=conta
    ).aggregate(total=Sum('valor'))['total'] or 0

    resultado_periodo = (
        entradas
        - saidas
        + transferencias_recebidas
        - transferencias_enviadas
    )

    return {
        'entradas': entradas,
        'saidas': saidas,
        'transferencias_recebidas': transferencias_recebidas,
        'transferencias_enviadas': transferencias_enviadas,
        'resultado_periodo': resultado_periodo,
        'movimentacoes': movimentacoes_periodo,
        'tipos_filtro': tipos_filtro,
        'categorias_filtro': categorias_filtro,
    }


def obter_movimentacoes_recentes(usuario, limite=10):
    return models.Movimentacao.objects.filter(usuario=usuario).order_by(
        '-data',
        '-hora',
        '-criada_em'
    )[:limite]
