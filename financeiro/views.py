from django.shortcuts import render, redirect, get_object_or_404
from .import models
from .forms import ContaForm, ContaEditarForm, CategoriaForm, MovimentacaoForm

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
    movimentacoes = models.Movimentacao.objects.all()

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

