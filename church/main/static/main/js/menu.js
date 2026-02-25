document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("menuToggle");
    const nav = document.getElementById("navLinks");

    if (!toggle || !nav) return;

    // открытие / закрытие по бургеру
    toggle.addEventListener("click", () => {
        toggle.classList.toggle("active");
        nav.classList.toggle("active");
    });

    // закрытие после клика по ссылке
    nav.querySelectorAll("a").forEach(link => {
        link.addEventListener("click", () => {
            nav.classList.remove("active");
            toggle.classList.remove("active");
        });
    });
});