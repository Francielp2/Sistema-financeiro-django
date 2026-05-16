from django.contrib import admin
from .models import Conta, Categoria, Movimentacao


@admin.register(Conta)
class ContaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'saldo_inicial',
                    'usuario', 'ativa', 'criada_em')
    list_filter = ('tipo', 'ativa')
    search_fields = ('nome', 'descricao')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'usuario', 'ativa', 'criada_em')
    list_filter = ('ativa',)
    search_fields = ('nome', 'descricao')


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'tipo', 'valor', 'categoria',
                    'conta_origem', 'conta_destino', 'data', 'usuario')
    list_filter = ('tipo', 'data', 'categoria')
    search_fields = ('descricao', 'observacao')
