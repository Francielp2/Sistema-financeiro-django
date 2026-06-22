from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Conta, Categoria, Movimentacao


admin.site.unregister(User)


@admin.register(User)
class UsuarioAdmin(UserAdmin):
    # EVITA QUE UM SUPERUSUÁRIO REMOVA DE SI MESMO ACESSOS CRÍTICOS
    def save_model(self, request, obj, form, change):
        if change and obj.pk == request.user.pk and request.user.is_superuser:
            usuario_original = User.objects.get(pk=obj.pk)
            obj.is_staff = usuario_original.is_staff
            obj.is_superuser = usuario_original.is_superuser
            obj.is_active = usuario_original.is_active

        super().save_model(request, obj, form, change)


@admin.register(Conta)
class ContaAdmin(admin.ModelAdmin):
    # CONFIGURAÇÃO DA CONTA NO ADMIN
    list_display = ('nome', 'tipo', 'saldo_inicial',
                    'usuario', 'ativa', 'criada_em')
    list_filter = ('tipo', 'ativa')
    search_fields = ('nome', 'descricao')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    # CONFIGURAÇÃO DA CATEGORIA NO ADMIN
    list_display = ('nome', 'usuario', 'ativa', 'criada_em')
    list_filter = ('ativa',)
    search_fields = ('nome', 'descricao')


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    # CONFIGURAÇÃO DA MOVIMENTAÇÃO NO ADMIN
    list_display = ('descricao', 'tipo', 'valor', 'categoria',
                    'conta_origem', 'conta_destino', 'data', 'usuario')
    list_filter = ('tipo', 'data', 'categoria')
    search_fields = ('descricao', 'observacao')
