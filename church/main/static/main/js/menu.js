document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector(".menu-toggle");
    const nav = document.querySelector(".nav-links");

    toggle?.addEventListener("click", () => nav.classList.toggle("active"));

    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener("click", e => {
            e.preventDefault();
            document.querySelector(a.getAttribute("href"))?.scrollIntoView({ behavior: "smooth" });
        });
    });
});
