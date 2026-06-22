from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from .forms import (
    AlterarSenhaForm,
    CadastroUsuarioForm,
    EditarPerfilForm,
    LoginUsuarioForm,
)


def usuario_e_administrador(usuario):
    return usuario.is_authenticated and (
        usuario.is_staff or usuario.is_superuser
    )


def cadastro_usuario(request):
    if request.user.is_authenticated:
        return redirect('inicio')

    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Cadastro realizado com sucesso. Faça login para continuar.'
            )
            return redirect('login')
    else:
        form = CadastroUsuarioForm()

    return render(request, 'financeiro/usuarios/cadastro.html', {
        'form': form
    })


def login_usuario(request):
    if request.user.is_authenticated:
        return redirect('inicio')

    if request.method == 'POST':
        form = LoginUsuarioForm(request, data=request.POST)

        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Login realizado com sucesso.')
            return redirect('inicio')
    else:
        form = LoginUsuarioForm()

    return render(request, 'financeiro/usuarios/login.html', {
        'form': form
    })


@login_required
def logout_usuario(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Logout realizado com sucesso.')
        return redirect('login')

    return redirect('inicio')


@login_required
def perfil_usuario(request):
    return render(request, 'financeiro/usuarios/perfil.html')


@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = EditarPerfilForm(
            request.POST,
            instance=request.user,
            usuario=request.user
        )

        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso.')
            return redirect('perfil')
    else:
        form = EditarPerfilForm(instance=request.user, usuario=request.user)

    return render(request, 'financeiro/usuarios/editar_perfil.html', {
        'form': form
    })


@login_required
def alterar_senha(request):
    if request.method == 'POST':
        form = AlterarSenhaForm(request.user, request.POST)

        if form.is_valid():
            usuario = form.save()
            update_session_auth_hash(request, usuario)
            messages.success(request, 'Senha alterada com sucesso.')
            return redirect('perfil')
    else:
        form = AlterarSenhaForm(request.user)

    return render(request, 'financeiro/usuarios/alterar_senha.html', {
        'form': form
    })


@login_required
@user_passes_test(usuario_e_administrador, login_url='inicio')
def listar_usuarios(request):
    usuarios = User.objects.all().order_by('username')

    return render(request, 'financeiro/usuarios/listar_usuarios.html', {
        'usuarios': usuarios
    })
