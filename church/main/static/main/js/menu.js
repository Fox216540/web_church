document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("menuToggle");
    const nav = document.getElementById("navLinks");

    /* =========================
       БУРГЕР-МЕНЮ
    ========================= */

    if (toggle && nav) {
        // открытие / закрытие по бургеру
        toggle.addEventListener("click", (e) => {
            e.stopPropagation();
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

        // закрытие при клике на свободное место
        document.addEventListener("click", (e) => {
            if (
                nav.classList.contains("active") &&
                !nav.contains(e.target) &&
                !toggle.contains(e.target)
            ) {
                nav.classList.remove("active");
                toggle.classList.remove("active");
            }
        });
    }

    /* =========================
       ПЕРЕХВАТ ЯКОРЕЙ (#...)
       ❗ КЛЮЧЕВОЙ ФИКС "ЕДЕТ"
    ========================= */

    document.addEventListener("click", (e) => {
        const link = e.target.closest('a[href^="#"]');
        if (!link) return;

        const id = link.getAttribute("href").slice(1);
        if (!id) return;

        const target = document.getElementById(id);
        if (!target) return;

        // ❗ отключаем нативный якорный скролл
        e.preventDefault();

        // скроллим всегда одинаково и стабильно
        const section = target.closest("section") || target;
        section.scrollIntoView({ block: "start" });

        // обновляем URL
        history.pushState(null, "", `#${id}`);
    });
});