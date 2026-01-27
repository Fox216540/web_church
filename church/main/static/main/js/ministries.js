document.addEventListener("DOMContentLoaded", async () => {
    const r = await fetch("/api/ministries/");
    const ministries = await r.json();

    const grid = document.getElementById("ministries-grid");
		console.log(ministries);
    ministries.forEach(m => {
    const card = document.createElement("article");
    card.className = "ministry-card";

    card.innerHTML = `
        <div class="ministry-header">
            ${m.photo 
                ? `<img src="${m.photo}" alt="${m.name}" class="ministry-photo">`
                : `<div class="ministry-photo placeholder"></div>`
            }
            <h3 class="ministry-name">${m.name}</h3>
        </div>

        <div class="ministry-body">
            <p class="ministry-description">${m.description}</p>
            <p class="ministry-leader">
                <span>Руководитель:</span> ${m.leader}
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

    grid.appendChild(card);
});
});

