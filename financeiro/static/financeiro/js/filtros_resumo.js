document.addEventListener('DOMContentLoaded', function () {
    const todos = document.getElementById('tipoTodos');
    const textoTiposSelecionados = document.getElementById('textoTiposSelecionados');
    const categoriaTodas = document.getElementById('categoriaTodas');
    const textoCategoriasSelecionadas = document.getElementById('textoCategoriasSelecionadas');

    const tipos = [
        document.getElementById('tipoEntrada'),
        document.getElementById('tipoSaida'),
        document.getElementById('tipoTransferencia')
    ].filter(Boolean);

    const categorias = Array.from(document.querySelectorAll('.categoria-opcao'));

    function atualizarTextoTipos() {
        if (!textoTiposSelecionados) {
            return;
        }

        const selecionados = tipos
            .filter(function (tipo) {
                return tipo.checked;
            })
            .map(function (tipo) {
                return tipo.dataset.label;
            });

        if (selecionados.length === 0) {
            textoTiposSelecionados.textContent = 'Todos os tipos';
        } else if (selecionados.length === 1) {
            textoTiposSelecionados.textContent = selecionados[0];
        } else {
            textoTiposSelecionados.textContent = 'Tipos selecionados';
        }
    }

    function atualizarTextoCategorias() {
        if (!textoCategoriasSelecionadas) {
            return;
        }

        const selecionadas = categorias
            .filter(function (categoria) {
                return categoria.checked;
            })
            .map(function (categoria) {
                return categoria.dataset.label;
            });

        if (selecionadas.length === 0) {
            textoCategoriasSelecionadas.textContent = 'Todas as categorias';
        } else if (selecionadas.length === 1) {
            textoCategoriasSelecionadas.textContent = selecionadas[0];
        } else {
            textoCategoriasSelecionadas.textContent = 'Categorias selecionadas';
        }
    }

    function atualizarEstadoTodos() {
        if (!todos) {
            return;
        }

        const algumTipoMarcado = tipos.some(function (tipo) {
            return tipo.checked;
        });

        todos.checked = !algumTipoMarcado;
        atualizarTextoTipos();
    }

    function atualizarEstadoCategoriaTodas() {
        if (!categoriaTodas) {
            return;
        }

        const algumaCategoriaMarcada = categorias.some(function (categoria) {
            return categoria.checked;
        });

        categoriaTodas.checked = !algumaCategoriaMarcada;
        atualizarTextoCategorias();
    }

    tipos.forEach(function (tipo) {
        tipo.addEventListener('change', atualizarEstadoTodos);
    });

    categorias.forEach(function (categoria) {
        categoria.addEventListener('change', atualizarEstadoCategoriaTodas);
    });

    if (todos) {
        todos.addEventListener('change', function () {
            if (todos.checked) {
                tipos.forEach(function (tipo) {
                    tipo.checked = false;
                });
            }

            atualizarTextoTipos();
        });
    }

    if (categoriaTodas) {
        categoriaTodas.addEventListener('change', function () {
            if (categoriaTodas.checked) {
                categorias.forEach(function (categoria) {
                    categoria.checked = false;
                });
            }

            atualizarTextoCategorias();
        });
    }

    atualizarEstadoTodos();
    atualizarEstadoCategoriaTodas();
});
