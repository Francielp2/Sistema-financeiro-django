from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),

    path('contas/', views.listar_contas, name='listar_contas'),
    path('contas/criar/', views.criar_conta, name='criar_conta'),
    path('contas/editar/<int:conta_id>/', views.editar_conta, name='editar_conta'),
    path('contas/excluir/<int:conta_id>/', views.excluir_conta, name='excluir_conta'),
    path('contas/<int:conta_id>/', views.detalhes_conta, name='detalhes_conta'),

    path('categorias/', views.listar_categorias, name='listar_categorias'),
    path('categorias/criar/', views.criar_categoria, name='criar_categoria'),
    path('categorias/<int:categoria_id>/', views.detalhes_categoria, name='detalhes_categoria'),
    path('categorias/editar/<int:categoria_id>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/excluir/<int:categoria_id>/', views.excluir_categoria, name='excluir_categoria'),

    path('movimentacoes/', views.listar_movimentacoes, name='listar_movimentacoes'),
    path('movimentacoes/criar/', views.criar_movimentacao, name='criar_movimentacao'),
    path('movimentacoes/<int:movimentacao_id>/', views.detalhes_movimentacao, name='detalhes_movimentacao'),
    path('movimentacoes/editar/<int:movimentacao_id>/', views.editar_movimentacao, name='editar_movimentacao'),
    path('movimentacoes/excluir/<int:movimentacao_id>/', views.excluir_movimentacao, name='excluir_movimentacao'),

    path('resumo/', views.resumo_financeiro, name='resumo_financeiro'),
    ]
