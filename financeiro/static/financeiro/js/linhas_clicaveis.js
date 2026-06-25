document.addEventListener('click', function (event) {
    const linha = event.target.closest('tr[data-href]');

    if (
        !linha ||
        event.target.closest('[data-no-row-link]') ||
        event.target.closest('a, button, input, select, textarea, label')
    ) {
        return;
    }

    window.location.assign(linha.dataset.href);
});

document.addEventListener('keydown', function (event) {
    const linha = event.target.closest('tr[data-href]');

    if (
        !linha ||
        event.key !== 'Enter' ||
        event.target.closest('[data-no-row-link]') ||
        event.target.closest('a, button, input, select, textarea, label')
    ) {
        return;
    }

    window.location.assign(linha.dataset.href);
});
