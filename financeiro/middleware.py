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

    def __call__(self, request):
        if request.user.is_authenticated:
            request.url_voltar_segura = self._obter_url_segura(
                request.session.get('ultima_pagina_autenticada_segura')
            )

        response = self.get_response(request)

        if request.user.is_authenticated:
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
