from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)
from django.contrib.auth.models import User
from .models import Conta, Categoria, Movimentacao


class CadastroUsuarioForm(UserCreationForm):
    # FORMULÁRIO PARA CADASTRO PÚBLICO DE USUÁRIOS COMUNS
    first_name = forms.CharField(
        label='Nome',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome'
        })
    )
    last_name = forms.CharField(
        label='Sobrenome',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu sobrenome'
        })
    )
    email = forms.EmailField(
        label='E-mail',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com'
        })
    )

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome de usuário'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Senha'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme a senha'
        })

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.is_staff = False
        usuario.is_superuser = False

        if commit:
            usuario.save()

        return usuario


class LoginUsuarioForm(AuthenticationForm):
    # FORMULÁRIO DE LOGIN COM ESTILO DO PROJETO
    username = forms.CharField(
        label='Usuário',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome de usuário',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha'
        })
    )


class EditarPerfilForm(forms.ModelForm):
    # FORMULÁRIO PARA EDITAR DADOS PESSOAIS EXIGINDO SENHA ATUAL
    senha_atual = forms.CharField(
        label='Senha atual',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme sua senha atual'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu nome'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu sobrenome'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'seu@email.com'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario')
        super().__init__(*args, **kwargs)

    def clean_senha_atual(self):
        senha_atual = self.cleaned_data['senha_atual']

        if not self.usuario.check_password(senha_atual):
            raise forms.ValidationError('Senha atual incorreta.')

        return senha_atual


class AlterarSenhaForm(PasswordChangeForm):
    # FORMULÁRIO DE ALTERAÇÃO DE SENHA COM VALIDAÇÕES NATIVAS DO DJANGO
    old_password = forms.CharField(
        label='Senha atual',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha atual'
        })
    )
    new_password1 = forms.CharField(
        label='Nova senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nova senha'
        })
    )
    new_password2 = forms.CharField(
        label='Confirmar nova senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a nova senha'
        })
    )


class ContaForm(forms.ModelForm):
    # FORMULÁRIO PARA CRIAR CONTA
    class Meta:
        model = Conta
        fields = ['nome', 'tipo', 'saldo_inicial', 'descricao', 'ativa']

        # CAMPOS COM CLASSES DO BOOTSTRAP
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Conta Principal'
            }),

            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),

            'saldo_inicial': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1000.00'
            }),

            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição opcional da conta'
            }),

            'ativa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class ContaEditarForm(forms.ModelForm):
    # FORMULÁRIO PARA EDITAR CONTA
    class Meta:
        model = Conta
        fields = ['nome', 'tipo', 'saldo_inicial', 'descricao', 'ativa']

        # CAMPOS COM CLASSES DO BOOTSTRAP
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Conta Principal'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'saldo_inicial': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1000.00'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição opcional da conta'
            }),
            'ativa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        # BLOQUEIA SALDO INICIAL QUANDO A CONTA JÁ TEM MOVIMENTAÇÕES
        bloquear_saldo = kwargs.pop('bloquear_saldo', False)
        super().__init__(*args, **kwargs)

        if bloquear_saldo:
            self.fields['saldo_inicial'].disabled = True
            self.fields['saldo_inicial'].help_text = (
                'O saldo inicial não pode ser alterado porque esta conta já possui movimentações.'
            )


class CategoriaForm(forms.ModelForm):
    # FORMULÁRIO PARA CRIAR E EDITAR CATEGORIA
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao', 'ativa']

        # CAMPOS COM CLASSES DO BOOTSTRAP
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Alimentação'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição opcional da categoria'
            }),
            'ativa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class MovimentacaoForm(forms.ModelForm):
    # FORMULÁRIO PARA CRIAR E EDITAR MOVIMENTAÇÃO
    class Meta:
        model = Movimentacao
        fields = [
            'descricao',
            'valor',
            'tipo',
            'categoria',
            'conta_origem',
            'conta_destino',
            'data',
            'hora',
            'observacao'
        ]

        # CAMPOS COM CLASSES DO BOOTSTRAP
        widgets = {
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Salário do mês'
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1500.00'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'conta_origem': forms.Select(attrs={
                'class': 'form-select'
            }),
            'conta_destino': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'hora': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'observacao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observação opcional'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # MOSTRA APENAS CATEGORIAS E CONTAS ATIVAS NOS SELECTS
        self.fields['categoria'].queryset = Categoria.objects.filter(
            ativa=True)
        self.fields['conta_origem'].queryset = Conta.objects.filter(ativa=True)
        self.fields['conta_destino'].queryset = Conta.objects.filter(
            ativa=True)
