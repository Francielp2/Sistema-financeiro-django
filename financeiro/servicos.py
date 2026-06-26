from calendar import monthrange

from django.db.models import Q, Sum
from django.utils import timezone

from . import models


TIPOS_MOVIMENTACAO_VALIDOS = ['entrada', 'saida', 'transferencia']
MESES_ABREVIADOS = [
    'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez',
]

CATEGORIAS_PADRAO = [
    ('Salário', 'Recebimento recorrente de salário.'),
    ('Alimentação', 'Gastos com alimentação.'),
    ('Transporte', 'Gastos com transporte.'),
    ('Moradia', 'Gastos com moradia.'),
    ('Saúde', 'Gastos com saúde.'),
    ('Educação', 'Gastos com educação.'),
    ('Lazer', 'Gastos com lazer.'),
    ('Outros', 'Outras entradas ou saídas financeiras.'),
]


def criar_categorias_padrao(usuario):
    categorias_criadas = []

    for nome, descricao in CATEGORIAS_PADRAO:
        categoria, criada = models.Categoria.objects.get_or_create(
            usuario=usuario,
            nome=nome,
            defaults={
                'descricao': descricao,
                'ativa': True,
            }
        )

        if criada:
            categorias_criadas.append(categoria)

    return categorias_criadas


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
    movimentacoes_periodo = obter_movimentacoes_conta(
        usuario,
        conta
    ).filter(
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


def obter_movimentacoes_conta(usuario, conta):
    return models.Movimentacao.objects.filter(
        usuario=usuario
    ).filter(
        Q(conta_origem=conta) | Q(conta_destino=conta)
    )


def obter_movimentacoes_recentes(usuario, limite=10, conta=None):
    if conta is None:
        movimentacoes = models.Movimentacao.objects.filter(usuario=usuario)
    else:
        movimentacoes = obter_movimentacoes_conta(usuario, conta)

    return movimentacoes.order_by(
        '-data',
        '-hora',
        '-criada_em'
    )[:limite]


def _obter_movimentacoes_por_categoria(
    usuario,
    tipo,
    data_inicio,
    data_fim,
    conta=None
):
    movimentacoes = models.Movimentacao.objects.filter(
        usuario=usuario,
        tipo=tipo,
        data__range=[data_inicio, data_fim]
    )

    if conta is not None:
        if tipo == 'entrada':
            movimentacoes = movimentacoes.filter(conta_destino=conta)
        elif tipo == 'saida':
            movimentacoes = movimentacoes.filter(conta_origem=conta)

    totais = movimentacoes.values(
        'categoria__nome'
    ).annotate(
        total=Sum('valor')
    ).order_by(
        '-total',
        'categoria__nome'
    )

    return {
        'labels': [
            item['categoria__nome'] or 'Sem categoria'
            for item in totais
        ],
        'valores': [item['total'] for item in totais],
    }


def obter_gastos_por_categoria(usuario, data_inicio, data_fim):
    return _obter_movimentacoes_por_categoria(
        usuario,
        'saida',
        data_inicio,
        data_fim
    )


def obter_entradas_por_categoria(usuario, data_inicio, data_fim):
    return _obter_movimentacoes_por_categoria(
        usuario,
        'entrada',
        data_inicio,
        data_fim
    )


def obter_patrimonio_por_conta(usuario):
    contas = models.Conta.objects.filter(usuario=usuario)
    contas_com_saldo = sorted(
        (
            (conta.nome, conta.saldo_atual)
            for conta in contas
        ),
        key=lambda conta: conta[1],
        reverse=True
    )

    return {
        'labels': [nome for nome, saldo in contas_com_saldo],
        'valores': [saldo for nome, saldo in contas_com_saldo],
    }


def _obter_ultimos_meses(quantidade_meses, hoje):
    meses = []
    indice_mes_atual = hoje.year * 12 + hoje.month - 1

    for meses_anteriores in range(quantidade_meses - 1, -1, -1):
        indice_mes = indice_mes_atual - meses_anteriores
        ano, mes_indice = divmod(indice_mes, 12)
        meses.append(hoje.replace(year=ano, month=mes_indice + 1, day=1))

    return meses


def obter_entradas_saidas_ultimos_meses(
    usuario,
    quantidade_meses=6,
    conta=None
):
    if quantidade_meses <= 0:
        return {
            'labels': [],
            'entradas': [],
            'saidas': [],
        }

    hoje = timezone.localdate()
    meses = _obter_ultimos_meses(quantidade_meses, hoje)
    fim_mes_atual = hoje.replace(
        day=monthrange(hoje.year, hoje.month)[1]
    )
    movimentacoes = models.Movimentacao.objects.filter(
        usuario=usuario,
        data__range=[meses[0], fim_mes_atual]
    )

    if conta is None:
        movimentacoes = movimentacoes.filter(
            tipo__in=['entrada', 'saida']
        )
    else:
        movimentacoes = movimentacoes.filter(
            Q(tipo='entrada', conta_destino=conta)
            | Q(tipo='saida', conta_origem=conta)
        )

    totais = movimentacoes.values(
        'data__year',
        'data__month',
        'tipo'
    ).annotate(
        total=Sum('valor')
    )

    totais_por_mes = {
        (item['data__year'], item['data__month'], item['tipo']): item['total']
        for item in totais
    }

    return {
        'labels': [
            f'{MESES_ABREVIADOS[mes.month - 1]}/{mes.year}'
            for mes in meses
        ],
        'entradas': [
            totais_por_mes.get((mes.year, mes.month, 'entrada'), 0)
            for mes in meses
        ],
        'saidas': [
            totais_por_mes.get((mes.year, mes.month, 'saida'), 0)
            for mes in meses
        ],
    }


def obter_entradas_saidas_conta_ultimos_meses(
    usuario,
    conta,
    quantidade_meses=6
):
    return obter_entradas_saidas_ultimos_meses(
        usuario,
        quantidade_meses=quantidade_meses,
        conta=conta
    )


def calcular_resultado_mensal(dados_entradas_saidas):
    entradas = dados_entradas_saidas.get('entradas', [])
    saidas = dados_entradas_saidas.get('saidas', [])

    return {
        'labels': dados_entradas_saidas.get('labels', []),
        'resultados': [
            entrada - saida
            for entrada, saida in zip(entradas, saidas)
        ],
    }


def obter_gastos_por_categoria_conta(
    usuario,
    conta,
    data_inicio,
    data_fim
):
    return _obter_movimentacoes_por_categoria(
        usuario,
        'saida',
        data_inicio,
        data_fim,
        conta=conta
    )


def obter_transferencias_conta_ultimos_meses(
    usuario,
    conta,
    quantidade_meses=6
):
    if quantidade_meses <= 0:
        return {
            'labels': [],
            'recebidas': [],
            'enviadas': [],
        }

    hoje = timezone.localdate()
    meses = _obter_ultimos_meses(quantidade_meses, hoje)
    fim_mes_atual = hoje.replace(
        day=monthrange(hoje.year, hoje.month)[1]
    )
    transferencias = models.Movimentacao.objects.filter(
        usuario=usuario,
        tipo='transferencia',
        data__range=[meses[0], fim_mes_atual]
    ).filter(
        Q(conta_destino=conta) | Q(conta_origem=conta)
    )
    recebidas = transferencias.filter(
        conta_destino=conta
    ).values(
        'data__year',
        'data__month'
    ).annotate(
        total=Sum('valor')
    )
    enviadas = transferencias.filter(
        conta_origem=conta
    ).values(
        'data__year',
        'data__month'
    ).annotate(
        total=Sum('valor')
    )
    recebidas_por_mes = {
        (item['data__year'], item['data__month']): item['total']
        for item in recebidas
    }
    enviadas_por_mes = {
        (item['data__year'], item['data__month']): item['total']
        for item in enviadas
    }

    return {
        'labels': [
            f'{MESES_ABREVIADOS[mes.month - 1]}/{mes.year}'
            for mes in meses
        ],
        'recebidas': [
            recebidas_por_mes.get((mes.year, mes.month), 0)
            for mes in meses
        ],
        'enviadas': [
            enviadas_por_mes.get((mes.year, mes.month), 0)
            for mes in meses
        ],
    }


def obter_dashboard_geral(usuario):
    data_inicio_mes, data_fim_mes = obter_periodo_mes_atual()
    contas = models.Conta.objects.filter(usuario=usuario).order_by('nome')
    resumo_mes = calcular_resumo_periodo(
        usuario,
        data_inicio_mes,
        data_fim_mes
    )
    dados_entradas_saidas_meses = obter_entradas_saidas_ultimos_meses(
        usuario,
        quantidade_meses=6
    )

    return {
        'patrimonio_total': calcular_patrimonio_total(usuario, contas),
        'total_entradas_mes': resumo_mes['entradas'],
        'total_saidas_mes': resumo_mes['saidas'],
        'total_transferencias_mes': resumo_mes['transferencias'],
        'resultado_mes': resumo_mes['resultado'],
        'contas': contas,
        'movimentacoes_recentes': obter_movimentacoes_recentes(usuario, 5),
        'data_inicio_mes': data_inicio_mes,
        'data_fim_mes': data_fim_mes,
        'dados_gastos_por_categoria': obter_gastos_por_categoria(
            usuario,
            data_inicio_mes,
            data_fim_mes
        ),
        'dados_entradas_por_categoria': obter_entradas_por_categoria(
            usuario,
            data_inicio_mes,
            data_fim_mes
        ),
        'dados_patrimonio_por_conta': obter_patrimonio_por_conta(usuario),
        'dados_entradas_saidas_meses': dados_entradas_saidas_meses,
        'dados_resultado_mensal': calcular_resultado_mensal(
            dados_entradas_saidas_meses
        ),
    }


def obter_dashboard_conta(usuario, conta):
    if conta.usuario_id != usuario.id:
        raise ValueError('A conta não pertence ao usuário informado.')

    data_inicio_mes, data_fim_mes = obter_periodo_mes_atual()
    resumo_mes = calcular_resumo_conta(
        usuario,
        conta,
        data_inicio_mes,
        data_fim_mes
    )

    return {
        'conta': conta,
        'saldo_atual': conta.saldo_atual,
        'saldo_inicial': conta.saldo_inicial,
        'entradas_mes': resumo_mes['entradas'],
        'saidas_mes': resumo_mes['saidas'],
        'transferencias_recebidas_mes': (
            resumo_mes['transferencias_recebidas']
        ),
        'transferencias_enviadas_mes': (
            resumo_mes['transferencias_enviadas']
        ),
        'resultado_mes': resumo_mes['resultado_periodo'],
        'movimentacoes_recentes': obter_movimentacoes_recentes(
            usuario,
            limite=5,
            conta=conta
        ),
        'dados_entradas_saidas_conta_meses': (
            obter_entradas_saidas_conta_ultimos_meses(
                usuario,
                conta,
                quantidade_meses=6
            )
        ),
        'dados_gastos_categoria_conta': obter_gastos_por_categoria_conta(
            usuario,
            conta,
            data_inicio_mes,
            data_fim_mes
        ),
        'dados_transferencias_conta_meses': (
            obter_transferencias_conta_ultimos_meses(
                usuario,
                conta,
                quantidade_meses=6
            )
        ),
    }
