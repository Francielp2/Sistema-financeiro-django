(function () {
    var storageKey = 'mazer-theme';
    var toggleDark = document.getElementById('toggle-dark');

    function applyTheme(theme) {
        var oppositeTheme = theme === 'dark' ? 'light' : 'dark';

        document.documentElement.setAttribute('data-theme', theme);
        document.body.classList.remove('theme-' + oppositeTheme);
        document.body.classList.add('theme-' + theme);
        localStorage.setItem(storageKey, theme);

        if (toggleDark) {
            toggleDark.checked = theme === 'dark';
        }
    }

    var currentTheme = localStorage.getItem(storageKey) || 'light';
    applyTheme(currentTheme);

    if (toggleDark) {
        toggleDark.addEventListener('change', function () {
            applyTheme(toggleDark.checked ? 'dark' : 'light');
        });
    }
})();
