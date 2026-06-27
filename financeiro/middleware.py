from django.conf import settings
from django.shortcuts import render
from django.utils.cache import add_never_cache_headers


class NeverCacheAuthenticatedMiddleware:
    caminhos_bloqueados = (
        '/login/',
        '/cadastro/',
        '/logout/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def _obter_url_segura(self, url):
        if not url or url in self.caminhos_bloqueados:
            return '/'

        return url

    def _renderizar_pagina_erro_personalizada(self, request, response):
        if not (
            settings.DEBUG
            and getattr(settings, 'SHOW_CUSTOM_ERROR_PAGES_IN_DEBUG', False)
        ):
            return response

        if response.status_code == 404:
            return render(request, '404.html', status=404)

        if response.status_code == 403:
            return render(request, '403.html', status=403)

        return response

    def __call__(self, request):
        usuario = getattr(request, 'user', None)

        if usuario and usuario.is_authenticated:
            request.url_voltar_segura = self._obter_url_segura(
                request.session.get('ultima_pagina_autenticada_segura')
            )

        response = self.get_response(request)
        response = self._renderizar_pagina_erro_personalizada(
            request,
            response
        )

        if usuario and usuario.is_authenticated:
            add_never_cache_headers(response)

            if (
                request.method == 'GET'
                and response.status_code == 200
                and request.path not in self.caminhos_bloqueados
            ):
                request.session[
                    'ultima_pagina_autenticada_segura'
                ] = request.get_full_path()

        return response
