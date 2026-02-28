(async () => {
    const container = document.getElementById("contact-list");
    if (!container) return;

    try {
        const response = await fetch("/api/contacts/");
        if (!response.ok) throw new Error("API error");

        const data = await response.json();

        container.innerHTML = "";
        const fragment = document.createDocumentFragment();

        data.contacts.forEach(item => {
            const card = document.createElement("div");
            card.className = "contact-item card";

            const icon = document.createElement("i");
            icon.className = `fas ${item.icon} fa-2x`;

            const content = document.createElement("div");

            const title = document.createElement("h3");
            title.textContent = item.title;

            let value;
            if (item.link) {
                value = document.createElement("a");
                value.href = item.link;
                value.textContent = item.value;
            } else {
                value = document.createElement("p");
                value.style.whiteSpace = "pre-line";
                value.textContent = item.value;
            }

            content.appendChild(title);
            content.appendChild(value);

            card.appendChild(icon);
            card.appendChild(content);

            fragment.appendChild(card);
        });

        container.appendChild(fragment);

        const map = document.getElementById("contact-map");

        if (map && data.map_embed) {
            // ⚠️ ЖДЁМ ЗАГРУЗКИ iframe
            await new Promise(resolve => {
                map.onload = resolve;
                map.src = data.map_embed;
            });
        }

    } catch (error) {
        console.error(error);
        container.innerHTML = "<p>Ошибка загрузки контактов.</p>";
    } finally {
    }
})();