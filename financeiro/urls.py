from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),

    path('contas/', views.listar_contas, name='listar_contas'),
    path('contas/criar/', views.criar_conta, name='criar_conta'),
    path('contas/editar/<int:conta_id>/', views.editar_conta, name='editar_conta'),
    path('contas/excluir/<int:conta_id>/', views.excluir_conta, name='excluir_conta'),
    path('contas/<int:conta_id>/', views.detalhes_conta, name='detalhes_conta'),
]
