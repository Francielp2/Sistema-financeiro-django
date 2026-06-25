from django.urls import path
from . import views
from . import usuarios_views

urlpatterns = [
    # ROTAS DE USUÁRIOS
    path('cadastro/', usuarios_views.cadastro_usuario, name='cadastro'),
    path('login/', usuarios_views.login_usuario, name='login'),
    path('logout/', usuarios_views.logout_usuario, name='logout'),
    path('perfil/', usuarios_views.perfil_usuario, name='perfil'),
    path('perfil/editar/', usuarios_views.editar_perfil, name='editar_perfil'),
    path('perfil/alterar-senha/', usuarios_views.alterar_senha, name='alterar_senha'),
    path('usuarios/', usuarios_views.listar_usuarios, name='listar_usuarios'),

    # ROTAS DA PÁGINA INICIAL
    path('', views.inicio, name='inicio'),

    # ROTAS DE CONTAS
    path('contas/', views.listar_contas, name='listar_contas'),
    path('contas/criar/', views.criar_conta, name='criar_conta'),
    path('contas/editar/<int:conta_id>/', views.editar_conta, name='editar_conta'),
    path('contas/excluir/<int:conta_id>/', views.excluir_conta, name='excluir_conta'),
    path(
        'contas/<int:conta_id>/dashboard/',
        views.dashboard_conta,
        name='dashboard_conta'
    ),
    path('contas/<int:conta_id>/', views.detalhes_conta, name='detalhes_conta'),

    # ROTAS DE CATEGORIAS
    path('categorias/', views.listar_categorias, name='listar_categorias'),
    path('categorias/criar/', views.criar_categoria, name='criar_categoria'),
    path('categorias/<int:categoria_id>/', views.detalhes_categoria, name='detalhes_categoria'),
    path('categorias/editar/<int:categoria_id>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/excluir/<int:categoria_id>/', views.excluir_categoria, name='excluir_categoria'),

    # ROTAS DE MOVIMENTAÇÕES
    path('movimentacoes/', views.listar_movimentacoes, name='listar_movimentacoes'),
    path('movimentacoes/criar/', views.criar_movimentacao, name='criar_movimentacao'),
    path('movimentacoes/<int:movimentacao_id>/', views.detalhes_movimentacao, name='detalhes_movimentacao'),
    path('movimentacoes/editar/<int:movimentacao_id>/', views.editar_movimentacao, name='editar_movimentacao'),
    path('movimentacoes/excluir/<int:movimentacao_id>/', views.excluir_movimentacao, name='excluir_movimentacao'),

    # ROTAS DE RESUMOS FINANCEIROS
    path('resumo/', views.resumo_financeiro, name='resumo_financeiro'),
    path('resumo/conta/<int:conta_id>/', views.resumo_conta, name='resumo_conta'),
    ]
