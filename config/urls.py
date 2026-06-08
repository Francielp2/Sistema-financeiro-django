from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # ROTA DO ADMIN DO DJANGO
    path('admin/', admin.site.urls),

    # ROTAS DO APP FINANCEIRO
    path('', include('financeiro.urls')),
]
