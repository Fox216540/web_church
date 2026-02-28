(async () => {
    const grid = document.getElementById("ministries-grid");
    if (!grid) return;

    try {
        const response = await fetch("/api/ministries/");
        if (!response.ok) throw new Error("API error");

        const ministries = await response.json();

        const fragment = document.createDocumentFragment();

        ministries.forEach(m => {
            const card = document.createElement("article");
            card.className = "ministry-card";

            card.innerHTML = `
                <div class="ministry-header">
                    ${
                        m.photo
                            ? `<img src="${m.photo}" alt="${escapeHtml(m.name)}" class="ministry-photo">`
                            : `<div class="ministry-photo placeholder"></div>`
                    }
                    <h3 class="ministry-name">${escapeHtml(m.name)}</h3>
                </div>

                <div class="ministry-body">
                    <p class="ministry-description">${escapeHtml(m.description || "")}</p>
                    <p class="ministry-leader">
                        <span>Руководитель:</span> ${escapeHtml(m.leader || "")}
                    </p>
                </div>

                <div class="ministry-contacts">
                    ${m.phone ? `<a href="tel:${m.phone}" class="contact phone">${m.phone}</a>` : ""}
                    ${m.email ? `<a href="mailto:${m.email}" class="contact email">${m.email}</a>` : ""}
                    ${m.telegram ? `<a href="${m.telegram}" target="_blank" class="contact telegram">Telegram</a>` : ""}
                    ${m.whatsapp ? `<a href="${m.whatsapp}" target="_blank" class="contact whatsapp">WhatsApp</a>` : ""}
                    ${m.instagram ? `<a href="${m.instagram}" target="_blank" class="contact instagram">Instagram</a>` : ""}
                </div>
            `;

            fragment.appendChild(card);
        });

        grid.appendChild(fragment);

    } catch (error) {
        console.error(error);
        grid.innerHTML = "<p>Ошибка загрузки</p>";
    } finally {
    }
})();

/* ============== helpers ============== */

/* защита от XSS */
function escapeHtml(text = "") {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}