from django import forms
from .models import Conta


class ContaForm(forms.ModelForm):
    class Meta:
        model = Conta
        fields = ['nome', 'tipo', 'saldo_inicial', 'descricao', 'ativa']

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
    class Meta:
        model = Conta
        fields = ['nome', 'tipo', 'saldo_inicial', 'descricao', 'ativa']

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
        bloquear_saldo = kwargs.pop('bloquear_saldo', False)
        super().__init__(*args, **kwargs)

        if bloquear_saldo:
            self.fields['saldo_inicial'].disabled = True
            self.fields['saldo_inicial'].help_text = (
                'O saldo inicial não pode ser alterado porque esta conta já possui movimentações.'
            )
