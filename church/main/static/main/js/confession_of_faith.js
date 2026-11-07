document.addEventListener("DOMContentLoaded", () => {
    const close = item => {
        item.classList.remove("active");
        item.querySelector(".icon").textContent = "▼";
        item.querySelectorAll(".confession-item").forEach(close);
    };

    document.querySelectorAll(".confession-item > .confession-header").forEach(h => {
        h.onclick = e => {
            const item = h.parentElement;
            const root = item.closest(".confession-content");

            root?.querySelectorAll(":scope > .confession-item").forEach(i => i !== item && close(i));

            const open = !item.classList.contains("active");
            close(item);
            if (open) {
                item.classList.add("active");
                h.querySelector(".icon").textContent = "▲";
            }

            e.stopPropagation();
        };
    });

    document.querySelectorAll(".confession-item").forEach(i => close(i));
});
