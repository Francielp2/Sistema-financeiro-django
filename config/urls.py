from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # ROTA DO ADMIN DO DJANGO
    path('admin/', admin.site.urls),

    # ROTAS DO APP FINANCEIRO
    path('', include('financeiro.urls')),
]

handler403 = 'django.views.defaults.permission_denied'
handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'
