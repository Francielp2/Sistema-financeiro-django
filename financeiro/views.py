from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .import models
from . import servicos
from .forms import ContaForm, ContaEditarForm, CategoriaForm, MovimentacaoForm
from datetime import datetime

# PÁGINA INICIAL DO APP FINANCEIRO


@login_required
def inicio(request):
    data_inicio_mes, data_fim_mes = servicos.obter_periodo_mes_atual()
    contas = models.Conta.objects.filter(usuario=request.user).order_by('nome')
    resumo_mes = servicos.calcular_resumo_periodo(
        request.user,
        data_inicio_mes,
        data_fim_mes
    )
    dados_gastos_por_categoria = servicos.obter_gastos_por_categoria(
        request.user,
        data_inicio_mes,
        data_fim_mes
    )
    dados_entradas_por_categoria = servicos.obter_entradas_por_categoria(
        request.user,
        data_inicio_mes,
        data_fim_mes
    )
    dados_patrimonio_por_conta = servicos.obter_patrimonio_por_conta(
        request.user
    )
    dados_entradas_saidas_meses = (
        servicos.obter_entradas_saidas_ultimos_meses(
            request.user,
            quantidade_meses=6
        )
    )

    return render(request, 'financeiro/inicio.html', {
        'patrimonio_total': servicos.calcular_patrimonio_total(
            request.user,
            contas
        ),
        'total_entradas_mes': resumo_mes['entradas'],
        'total_saidas_mes': resumo_mes['saidas'],
        'total_transferencias_mes': resumo_mes['transferencias'],
        'resultado_mes': resumo_mes['resultado'],
        'contas': contas,
        'movimentacoes_recentes': servicos.obter_movimentacoes_recentes(
            request.user,
            5
        ),
        'data_inicio_mes': data_inicio_mes,
        'data_fim_mes': data_fim_mes,
        'dados_gastos_por_categoria': dados_gastos_por_categoria,
        'dados_entradas_por_categoria': dados_entradas_por_categoria,
        'dados_patrimonio_por_conta': dados_patrimonio_por_conta,
        'dados_entradas_saidas_meses': dados_entradas_saidas_meses,
    })

# VIEWS DE CONTAS


@login_required
def listar_contas(request):
    contas = models.Conta.objects.filter(usuario=request.user)

    # FILTROS DA LISTAGEM DE CONTAS
    nome_filtro = request.GET.get('nome', '').strip()
    tipo_filtro = request.GET.get('tipo', '')
    ativa_filtro = request.GET.get('ativa', '')

    if nome_filtro:
        contas = contas.filter(nome__icontains=nome_filtro)

    if tipo_filtro:
        contas = contas.filter(tipo=tipo_filtro)

    if ativa_filtro == 'sim':
        contas = contas.filter(ativa=True)
    elif ativa_filtro == 'nao':
        contas = contas.filter(ativa=False)

    contas = contas.order_by('nome')

    return render(request, 'financeiro/contas/listar_contas.html', {
        'contas': contas,
        'nome_filtro': nome_filtro,
        'tipo_filtro': tipo_filtro,
        'ativa_filtro': ativa_filtro,
        'tipos_conta': models.Conta.TIPO_CONTA_CHOICES,
    })


@login_required
def criar_conta(request):
    if request.method == 'POST':
        form = ContaForm(request.POST)
        if form.is_valid():
            conta = form.save(commit=False)
            conta.usuario = request.user
            conta.save()
            return redirect('listar_contas')
    else:
        form = ContaForm()

    return render(request, 'financeiro/contas/form_conta.html', {'form': form})


@login_required
def editar_conta(request, conta_id):
    conta = get_object_or_404(
        models.Conta,
        id=conta_id,
        usuario=request.user
    )

    # BLOQUEIA ALTERAÇÃO DO SALDO INICIAL QUANDO JÁ EXISTEM MOVIMENTAÇÕES
    possui_movimentacoes = (
        conta.movimentacoes_origem.exists() or
        conta.movimentacoes_destino.exists()
    )

    if request.method == 'POST':
        form = ContaEditarForm(
            request.POST,
            instance=conta,
            bloquear_saldo=possui_movimentacoes
        )

        if form.is_valid():
            form.save()
            return redirect('listar_contas')
    else:
        form = ContaEditarForm(
            instance=conta,
            bloquear_saldo=possui_movimentacoes
        )

    return render(request, 'financeiro/contas/form_conta.html', {'form': form})


@login_required
def excluir_conta(request, conta_id):
    conta = get_object_or_404(
        models.Conta,
        id=conta_id,
        usuario=request.user
    )

    if request.method == 'POST':
        conta.delete()
        return redirect('listar_contas')

    return render(request, 'financeiro/contas/excluir_conta.html', {'conta': conta})


@login_required
def detalhes_conta(request, conta_id):
    conta = get_object_or_404(
        models.Conta,
        id=conta_id,
        usuario=request.user
    )

    return render(request, 'financeiro/contas/detalhes_conta.html', {
        'conta': conta
    })


# VIEWS DE CATEGORIAS

@login_required
def listar_categorias(request):
    categorias = models.Categoria.objects.filter(usuario=request.user)

    # FILTROS DA LISTAGEM DE CATEGORIAS
    nome_filtro = request.GET.get('nome', '').strip()
    ativa_filtro = request.GET.get('ativa', '')

    if nome_filtro:
        categorias = categorias.filter(nome__icontains=nome_filtro)

    if ativa_filtro == 'sim':
        categorias = categorias.filter(ativa=True)
    elif ativa_filtro == 'nao':
        categorias = categorias.filter(ativa=False)

    categorias = categorias.order_by('nome')

    return render(request, 'financeiro/categorias/listar_categorias.html', {
        'categorias': categorias,
        'nome_filtro': nome_filtro,
        'ativa_filtro': ativa_filtro,
    })


@login_required
def criar_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)

        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.usuario = request.user
            categoria.save()
            return redirect('listar_categorias')
    else:
        form = CategoriaForm()

    return render(request, 'financeiro/categorias/form_categoria.html', {
        'form': form
    })


@login_required
def detalhes_categoria(request, categoria_id):
    categoria = get_object_or_404(
        models.Categoria,
        id=categoria_id,
        usuario=request.user
    )

    return render(request, 'financeiro/categorias/detalhes_categoria.html', {
        'categoria': categoria
    })


@login_required
def editar_categoria(request, categoria_id):
    categoria = get_object_or_404(
        models.Categoria,
        id=categoria_id,
        usuario=request.user
    )

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)

        if form.is_valid():
            form.save()
            return redirect('listar_categorias')
    else:
        form = CategoriaForm(instance=categoria)

    return render(request, 'financeiro/categorias/form_categoria.html', {
        'form': form
    })


@login_required
def excluir_categoria(request, categoria_id):
    categoria = get_object_or_404(
        models.Categoria,
        id=categoria_id,
        usuario=request.user
    )

    if request.method == 'POST':
        categoria.delete()
        return redirect('listar_categorias')

    return render(request, 'financeiro/categorias/excluir_categoria.html', {
        'categoria': categoria
    })


# VIEWS DE MOVIMENTAÇÕES

@login_required
def listar_movimentacoes(request):
    movimentacoes = models.Movimentacao.objects.filter(usuario=request.user)

    # FILTROS DA LISTAGEM DE MOVIMENTAÇÕES
    data_inicio_filtro = request.GET.get('data_inicio', '')
    data_fim_filtro = request.GET.get('data_fim', '')
    tipo_filtro = request.GET.get('tipo', '')
    categoria_filtro = request.GET.get('categoria', '')
    conta_origem_filtro = request.GET.get('conta_origem', '')
    conta_destino_filtro = request.GET.get('conta_destino', '')
    descricao_filtro = request.GET.get('descricao', '').strip()

    if data_inicio_filtro:
        try:
            data_inicio = datetime.strptime(
                data_inicio_filtro, '%Y-%m-%d'
            ).date()
            movimentacoes = movimentacoes.filter(data__gte=data_inicio)
        except ValueError:
            data_inicio_filtro = ''

    if data_fim_filtro:
        try:
            data_fim = datetime.strptime(data_fim_filtro, '%Y-%m-%d').date()
            movimentacoes = movimentacoes.filter(data__lte=data_fim)
        except ValueError:
            data_fim_filtro = ''

    tipos_validos = [
        tipo
        for tipo, _ in models.Movimentacao.TIPO_MOVIMENTACAO_CHOICES
    ]

    if tipo_filtro in tipos_validos:
        movimentacoes = movimentacoes.filter(tipo=tipo_filtro)
    else:
        tipo_filtro = ''

    if categoria_filtro == 'sem_categoria':
        movimentacoes = movimentacoes.filter(categoria__isnull=True)
    elif (
        categoria_filtro.isdigit()
        and models.Categoria.objects.filter(
            id=categoria_filtro,
            usuario=request.user
        ).exists()
    ):
        movimentacoes = movimentacoes.filter(categoria_id=categoria_filtro)
    else:
        categoria_filtro = ''

    if (
        conta_origem_filtro.isdigit()
        and models.Conta.objects.filter(
            id=conta_origem_filtro,
            usuario=request.user
        ).exists()
    ):
        movimentacoes = movimentacoes.filter(
            conta_origem_id=conta_origem_filtro)
    else:
        conta_origem_filtro = ''

    if (
        conta_destino_filtro.isdigit()
        and models.Conta.objects.filter(
            id=conta_destino_filtro,
            usuario=request.user
        ).exists()
    ):
        movimentacoes = movimentacoes.filter(
            conta_destino_id=conta_destino_filtro)
    else:
        conta_destino_filtro = ''

    if descricao_filtro:
        movimentacoes = movimentacoes.filter(
            descricao__icontains=descricao_filtro)

    movimentacoes = movimentacoes.order_by(
        '-data',
        '-hora',
        '-criada_em'
    )

    categorias = models.Categoria.objects.filter(
        usuario=request.user,
        ativa=True
    ).order_by('nome')
    contas = models.Conta.objects.filter(usuario=request.user).order_by('nome')

    # DADOS PARA TABELA E CAMPOS DO FORMULÁRIO DE FILTROS
    return render(request, 'financeiro/movimentacoes/listar_movimentacoes.html', {
        'movimentacoes': movimentacoes,
        'categorias': categorias,
        'contas': contas,
        'data_inicio_filtro': data_inicio_filtro,
        'data_fim_filtro': data_fim_filtro,
        'tipo_filtro': tipo_filtro,
        'categoria_filtro': categoria_filtro,
        'conta_origem_filtro': conta_origem_filtro,
        'conta_destino_filtro': conta_destino_filtro,
        'descricao_filtro': descricao_filtro,
        'tipos_movimentacao': models.Movimentacao.TIPO_MOVIMENTACAO_CHOICES,
    })


@login_required
def criar_movimentacao(request):
    possui_conta_ativa = models.Conta.objects.filter(
        usuario=request.user,
        ativa=True
    ).exists()

    if not possui_conta_ativa:
        messages.warning(
            request,
            'Você precisa ter uma conta ativa para cadastrar movimentações.',
            extra_tags='criar-conta'
        )
        return redirect('listar_movimentacoes')

    if request.method == 'POST':
        form = MovimentacaoForm(request.POST, usuario=request.user)

        if form.is_valid():
            movimentacao = form.save(commit=False)
            movimentacao.usuario = request.user
            movimentacao.save()
            return redirect('listar_movimentacoes')
    else:
        form = MovimentacaoForm(usuario=request.user)

    return render(request, 'financeiro/movimentacoes/form_movimentacao.html', {
        'form': form
    })


@login_required
def detalhes_movimentacao(request, movimentacao_id):
    movimentacao = get_object_or_404(
        models.Movimentacao,
        id=movimentacao_id,
        usuario=request.user
    )

    return render(request, 'financeiro/movimentacoes/detalhes_movimentacao.html', {
        'movimentacao': movimentacao
    })


@login_required
def editar_movimentacao(request, movimentacao_id):
    movimentacao = get_object_or_404(
        models.Movimentacao,
        id=movimentacao_id,
        usuario=request.user
    )

    if request.method == 'POST':
        form = MovimentacaoForm(
            request.POST,
            instance=movimentacao,
            usuario=request.user
        )

        if form.is_valid():
            form.save()
            return redirect('listar_movimentacoes')
    else:
        form = MovimentacaoForm(instance=movimentacao, usuario=request.user)

    return render(request, 'financeiro/movimentacoes/form_movimentacao.html', {
        'form': form
    })


@login_required
def excluir_movimentacao(request, movimentacao_id):
    movimentacao = get_object_or_404(
        models.Movimentacao,
        id=movimentacao_id,
        usuario=request.user
    )

    if request.method == 'POST':
        movimentacao.delete()
        return redirect('listar_movimentacoes')

    return render(request, 'financeiro/movimentacoes/excluir_movimentacao.html', {
        'movimentacao': movimentacao
    })


# VIEW DO RESUMO FINANCEIRO GERAL

@login_required
def resumo_financeiro(request):
    # PERÍODO PADRÃO DO RESUMO GERAL
    data_inicio_str = request.GET.get('data_inicio')
    data_fim_str = request.GET.get('data_fim')

    if data_inicio_str and data_fim_str:
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
    else:
        data_inicio, data_fim = servicos.obter_periodo_mes_atual()

    tipos_filtro = request.GET.getlist('tipos')
    categorias_filtro = request.GET.getlist('categorias')
    categorias = models.Categoria.objects.filter(
        usuario=request.user,
        ativa=True
    ).order_by('nome')

    resumo_periodo = servicos.calcular_resumo_periodo(
        request.user,
        data_inicio,
        data_fim,
        tipos_filtro=tipos_filtro,
        categorias_filtro=categorias_filtro,
        categorias=categorias
    )

    contas = models.Conta.objects.filter(usuario=request.user)
    resumo_por_conta = servicos.calcular_resumo_por_conta(
        request.user,
        contas,
        resumo_periodo['movimentacoes']
    )

    # CONTEXTO USADO PELOS CARDS, TABELAS E FILTROS DO RESUMO GERAL
    return render(request, 'financeiro/resumo_financeiro.html', {
        'patrimonio_total': servicos.calcular_patrimonio_total(
            request.user,
            contas
        ),
        'total_entradas_periodo': resumo_periodo['entradas'],
        'total_saidas_periodo': resumo_periodo['saidas'],
        'resultado_periodo': resumo_periodo['resultado'],
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'contas': contas,
        'resumo_por_conta': resumo_por_conta,
        'tipos_filtro': resumo_periodo['tipos_filtro'],
        'total_transferencias_periodo': resumo_periodo['transferencias'],
        'categorias': categorias,
        'categorias_filtro': resumo_periodo['categorias_filtro'],
    })

# VIEW DO RESUMO INDIVIDUAL DA CONTA


@login_required
def resumo_conta(request, conta_id):
    conta = get_object_or_404(
        models.Conta,
        id=conta_id,
        usuario=request.user
    )

    # PERÍODO PADRÃO DO RESUMO DA CONTA
    data_inicio_str = request.GET.get('data_inicio')
    data_fim_str = request.GET.get('data_fim')

    if data_inicio_str and data_fim_str:
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
    else:
        data_inicio, data_fim = servicos.obter_periodo_mes_atual()

    tipos_filtro = request.GET.getlist('tipos')
    categorias_filtro = request.GET.getlist('categorias')
    categorias = models.Categoria.objects.filter(
        usuario=request.user,
        ativa=True
    ).order_by('nome')

    resumo = servicos.calcular_resumo_conta(
        request.user,
        conta,
        data_inicio,
        data_fim,
        tipos_filtro=tipos_filtro,
        categorias_filtro=categorias_filtro,
        categorias=categorias
    )

    # CONTEXTO USADO PELOS CARDS, FILTROS E TABELA DO RESUMO DA CONTA
    return render(request, 'financeiro/contas/resumo_conta.html', {
        'conta': conta,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'entradas': resumo['entradas'],
        'saidas': resumo['saidas'],
        'transferencias_recebidas': resumo['transferencias_recebidas'],
        'transferencias_enviadas': resumo['transferencias_enviadas'],
        'resultado_periodo': resumo['resultado_periodo'],
        'movimentacoes_conta': resumo['movimentacoes'].order_by(
            '-data',
            '-hora',
            '-criada_em'
        ),
        'tipos_filtro': resumo['tipos_filtro'],
        'categorias_filtro': resumo['categorias_filtro'],
        'categorias': categorias,
    })
