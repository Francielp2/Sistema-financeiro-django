from django.shortcuts import render, redirect, get_object_or_404
from .import models
from .forms import ContaForm, ContaEditarForm, CategoriaForm, MovimentacaoForm
from django.db.models import Sum, Q
from datetime import datetime
from calendar import monthrange
from django.utils import timezone

# Função para a página inicial do aplicativo financeiro


def inicio(request):
    return render(request, 'financeiro/inicio.html')

# Funções para contas


def listar_contas(request):
    contas = models.Conta.objects.all()
    return render(request, 'financeiro/contas/listar_contas.html', {'contas': contas})


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


def editar_conta(request, conta_id):
    conta = get_object_or_404(models.Conta, id=conta_id)

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


def excluir_conta(request, conta_id):
    conta = get_object_or_404(models.Conta, id=conta_id)

    if request.method == 'POST':
        conta.delete()
        return redirect('listar_contas')

    return render(request, 'financeiro/contas/excluir_conta.html', {'conta': conta})


def detalhes_conta(request, conta_id):
    conta = get_object_or_404(models.Conta, id=conta_id)

    return render(request, 'financeiro/contas/detalhes_conta.html', {
        'conta': conta
    })


# Funções para categorias

def listar_categorias(request):
    categorias = models.Categoria.objects.all()
    return render(request, 'financeiro/categorias/listar_categorias.html', {
        'categorias': categorias
    })


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


def detalhes_categoria(request, categoria_id):
    categoria = get_object_or_404(models.Categoria, id=categoria_id)

    return render(request, 'financeiro/categorias/detalhes_categoria.html', {
        'categoria': categoria
    })


def editar_categoria(request, categoria_id):
    categoria = get_object_or_404(models.Categoria, id=categoria_id)

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


def excluir_categoria(request, categoria_id):
    categoria = get_object_or_404(models.Categoria, id=categoria_id)

    if request.method == 'POST':
        categoria.delete()
        return redirect('listar_categorias')

    return render(request, 'financeiro/categorias/excluir_categoria.html', {
        'categoria': categoria
    })


# Funções par movimentações

def listar_movimentacoes(request):
    movimentacoes = models.Movimentacao.objects.all().order_by(
        '-data',
        '-hora',
        '-criada_em'
    )

    return render(request, 'financeiro/movimentacoes/listar_movimentacoes.html', {
        'movimentacoes': movimentacoes
    })


def criar_movimentacao(request):
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST)

        if form.is_valid():
            movimentacao = form.save(commit=False)
            movimentacao.usuario = request.user
            movimentacao.save()
            return redirect('listar_movimentacoes')
    else:
        form = MovimentacaoForm()

    return render(request, 'financeiro/movimentacoes/form_movimentacao.html', {
        'form': form
    })


def detalhes_movimentacao(request, movimentacao_id):
    movimentacao = get_object_or_404(models.Movimentacao, id=movimentacao_id)

    return render(request, 'financeiro/movimentacoes/detalhes_movimentacao.html', {
        'movimentacao': movimentacao
    })


def editar_movimentacao(request, movimentacao_id):
    movimentacao = get_object_or_404(models.Movimentacao, id=movimentacao_id)

    if request.method == 'POST':
        form = MovimentacaoForm(request.POST, instance=movimentacao)

        if form.is_valid():
            form.save()
            return redirect('listar_movimentacoes')
    else:
        form = MovimentacaoForm(instance=movimentacao)

    return render(request, 'financeiro/movimentacoes/form_movimentacao.html', {
        'form': form
    })


def excluir_movimentacao(request, movimentacao_id):
    movimentacao = get_object_or_404(models.Movimentacao, id=movimentacao_id)

    if request.method == 'POST':
        movimentacao.delete()
        return redirect('listar_movimentacoes')

    return render(request, 'financeiro/movimentacoes/excluir_movimentacao.html', {
        'movimentacao': movimentacao
    })


# Função para resumo financeiro geral

def resumo_financeiro(request):
    hoje = timezone.localdate()

    data_inicio_str = request.GET.get('data_inicio')
    data_fim_str = request.GET.get('data_fim')

    if data_inicio_str and data_fim_str:
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
    else:
        primeiro_dia = hoje.replace(day=1)
        ultimo_dia = hoje.replace(day=monthrange(hoje.year, hoje.month)[1])

        data_inicio = primeiro_dia
        data_fim = ultimo_dia

    movimentacoes_periodo = models.Movimentacao.objects.filter(
        data__range=[data_inicio, data_fim]
    )

    total_entradas_periodo = movimentacoes_periodo.filter(
        tipo='entrada'
    ).aggregate(total=Sum('valor'))['total'] or 0

    total_saidas_periodo = movimentacoes_periodo.filter(
        tipo='saida'
    ).aggregate(total=Sum('valor'))['total'] or 0

    resultado_periodo = total_entradas_periodo - total_saidas_periodo

    contas = models.Conta.objects.all()

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

        resultado_periodo_conta = (
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
            'resultado_periodo': resultado_periodo_conta,
        })

    patrimonio_total = sum(conta.saldo_atual for conta in contas)

    return render(request, 'financeiro/resumo_financeiro.html', {
        'patrimonio_total': patrimonio_total,
        'total_entradas_periodo': total_entradas_periodo,
        'total_saidas_periodo': total_saidas_periodo,
        'resultado_periodo': resultado_periodo,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'contas': contas,
        'resumo_por_conta': resumo_por_conta,
    })

# Função para resumo financeiro por conta

def resumo_conta(request, conta_id):
    conta = get_object_or_404(models.Conta, id=conta_id)

    hoje = timezone.localdate()

    data_inicio_str = request.GET.get('data_inicio')
    data_fim_str = request.GET.get('data_fim')

    if data_inicio_str and data_fim_str:
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
    else:
        data_inicio = hoje.replace(day=1)
        data_fim = hoje.replace(day=monthrange(hoje.year, hoje.month)[1])

    movimentacoes_periodo = models.Movimentacao.objects.filter(
        data__range=[data_inicio, data_fim]
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

    movimentacoes_conta = models.Movimentacao.objects.filter(
        Q(conta_origem=conta) | Q(conta_destino=conta)
    ).order_by('-data', '-hora', '-criada_em')

    return render(request, 'financeiro/contas/resumo_conta.html', {
        'conta': conta,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'entradas': entradas,
        'saidas': saidas,
        'transferencias_recebidas': transferencias_recebidas,
        'transferencias_enviadas': transferencias_enviadas,
        'resultado_periodo': resultado_periodo,
        'movimentacoes_conta': movimentacoes_conta,
    })
