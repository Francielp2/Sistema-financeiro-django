from django import forms
from .models import Conta, Categoria, Movimentacao


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
