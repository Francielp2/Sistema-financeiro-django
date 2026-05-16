from django.shortcuts import render, redirect, get_object_or_404
from .import models
from .forms import ContaForm, ContaEditarForm


def inicio(request):
    return render(request, 'financeiro/inicio.html')


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