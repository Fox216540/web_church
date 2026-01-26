document.addEventListener("DOMContentLoaded", async () => {
    const r = await fetch("/api/ministries");
    const ministries = await r.json();

    const grid = document.getElementById("ministries-grid");

    ministries.forEach(m => {
        const card = document.createElement("div");
        card.className = "card ministry-card";

        card.innerHTML = `
            <i class="${m.icon} fa-3x"></i>
            <h3>${m.title}</h3>
            ${m.subtitle ? `<p>${m.subtitle}</p>` : ""}
        `;

        grid.appendChild(card);
    });
});

