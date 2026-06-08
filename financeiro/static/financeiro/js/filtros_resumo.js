document.addEventListener('DOMContentLoaded', function () {
    // ELEMENTOS DOS FILTROS DE TIPO
    const todos = document.getElementById('tipoTodos');
    const textoTiposSelecionados = document.getElementById('textoTiposSelecionados');

    // ELEMENTOS DOS FILTROS DE CATEGORIA
    const categoriaTodas = document.getElementById('categoriaTodas');
    const textoCategoriasSelecionadas = document.getElementById('textoCategoriasSelecionadas');

    // CHECKBOXES ESPECÍFICOS DE TIPO
    const tipos = [
        document.getElementById('tipoEntrada'),
        document.getElementById('tipoSaida'),
        document.getElementById('tipoTransferencia')
    ].filter(Boolean);

    // CHECKBOXES ESPECÍFICOS DE CATEGORIA
    const categorias = Array.from(document.querySelectorAll('.categoria-opcao'));

    function atualizarTextoTipos() {
        // ATUALIZA O TEXTO DO DROPDOWN DE TIPOS
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
        // ATUALIZA O TEXTO DO DROPDOWN DE CATEGORIAS
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
        // MARCA "TODOS" QUANDO NENHUM TIPO ESPECÍFICO ESTÁ MARCADO
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
        // MARCA "TODAS" QUANDO NENHUMA CATEGORIA ESPECÍFICA ESTÁ MARCADA
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
        // REAGE À MUDANÇA DOS TIPOS
        tipo.addEventListener('change', atualizarEstadoTodos);
    });

    categorias.forEach(function (categoria) {
        // REAGE À MUDANÇA DAS CATEGORIAS
        categoria.addEventListener('change', atualizarEstadoCategoriaTodas);
    });

    if (todos) {
        todos.addEventListener('change', function () {
            // LIMPA TIPOS ESPECÍFICOS AO MARCAR "TODOS"
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
            // LIMPA CATEGORIAS ESPECÍFICAS AO MARCAR "TODAS"
            if (categoriaTodas.checked) {
                categorias.forEach(function (categoria) {
                    categoria.checked = false;
                });
            }

            atualizarTextoCategorias();
        });
    }

    // ESTADO INICIAL DOS DROPDOWNS
    atualizarEstadoTodos();
    atualizarEstadoCategoriaTodas();
});
