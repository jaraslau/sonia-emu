document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('analog-toggle');
    toggle.addEventListener('change', () => {
        const analog = document.querySelectorAll('.analog-trigger');
        const digital = document.querySelectorAll('.button-trigger');
        if (toggle.checked) {
            analog.forEach(el => el.style.display = 'flex');
            digital.forEach(el => el.style.display = 'none');
        } else {
            analog.forEach(el => el.style.display = 'none');
            digital.forEach(el => el.style.display = 'flex');
        }
    });
});
