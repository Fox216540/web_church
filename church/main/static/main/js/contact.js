document.addEventListener("DOMContentLoaded", async () => {

    const r = await fetch("/api/contacts/");
    const data = await r.json();

    const container = document.getElementById("contact-list");
    container.innerHTML = "";

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

        container.appendChild(card);
    });

    if (data.map_embed) {
        document.getElementById("contact-map").src = data.map_embed;
    }
});