(async () => {
    const container = document.getElementById("contact-list");
    if (!container) return;

    const classifyContact = (item) => {
        const text = `${item.title || ""} ${item.value || ""} ${item.link || ""}`.toLowerCase();

        if (text.includes("telegram") || text.includes("t.me")) return "telegram";
        if (text.includes("instagram") || text.includes("insta")) return "instagram";
        if (text.includes("whatsapp") || text.includes("wa.me") || text.includes("whats")) return "whatsapp";
        if (text.includes("youtube") || text.includes("youtu.be")) return "youtube";
        if (text.includes("facebook") || text.includes("fb.com") || text.includes("fb.me")) return "facebook";
        if (text.includes("email") || text.includes("@") || text.includes("mailto:")) return "email";
        if (text.includes("тел") || text.includes("phone") || text.includes("tel:")) return "phone";
        return "other";
    };

    const socialMeta = {
        telegram: { label: "Telegram", icon: "fab fa-telegram-plane", className: "tg" },
        instagram: { label: "Instagram", icon: "fab fa-instagram", className: "ig" },
        whatsapp: { label: "WhatsApp", icon: "fab fa-whatsapp", className: "wa" },
        youtube: { label: "YouTube", icon: "fab fa-youtube", className: "yt" },
        facebook: { label: "Facebook", icon: "fab fa-facebook-f", className: "fb" },
    };

    const ensureUrl = (link) => {
        if (!link) return null;
        if (link.startsWith("http://") || link.startsWith("https://")) return link;
        if (link.startsWith("mailto:") || link.startsWith("tel:")) return link;
        return `https://${link}`;
    };

    const createMainContact = (item, type) => {
        const card = document.createElement("div");
        card.className = "contact-item card";

        const icon = document.createElement("i");
        icon.className = `fas ${item.icon} fa-2x`;

        const content = document.createElement("div");
        content.className = "contact-item-content";

        const title = document.createElement("h3");
        title.textContent = item.title;

        const valueText = (item.value || "").trim();
        let link = ensureUrl(item.link);
        if (!link && type === "email" && valueText) {
            link = `mailto:${valueText}`;
        }
        if (!link && type === "phone" && valueText) {
            const phoneRaw = valueText.replace(/\s+/g, "");
            link = `tel:${phoneRaw}`;
        }
        let valueEl;
        if (link) {
            valueEl = document.createElement("a");
            valueEl.href = link;
            valueEl.textContent = valueText;
            if (link.startsWith("http")) {
                valueEl.target = "_blank";
                valueEl.rel = "noopener noreferrer";
            }
        } else {
            valueEl = document.createElement("p");
            valueEl.style.whiteSpace = "pre-line";
            valueEl.textContent = valueText;
        }

        content.appendChild(title);
        content.appendChild(valueEl);
        card.appendChild(icon);
        card.appendChild(content);
        return card;
    };

    const createSocialButton = (item, type) => {
        const meta = socialMeta[type];
        if (!meta) return null;

        const link = ensureUrl(item.link || item.value);
        if (!link) return null;

        const a = document.createElement("a");
        a.className = `social-link ${meta.className}`;
        a.href = link;
        a.target = "_blank";
        a.rel = "noopener noreferrer";
        a.setAttribute("aria-label", meta.label);
        a.innerHTML = `<i class="${meta.icon}"></i><span>${meta.label}</span>`;
        return a;
    };

    try {
        const response = await fetch("/api/contacts/");
        if (!response.ok) throw new Error("API error");

        const data = await response.json();
        const contacts = Array.isArray(data.contacts) ? data.contacts : [];

        container.innerHTML = "";
        const fragment = document.createDocumentFragment();
        const socials = [];
        const regularContacts = [];

        contacts.forEach(item => {
            const type = classifyContact(item);
            if (socialMeta[type]) {
                socials.push({ item, type });
                return;
            }
            regularContacts.push(item);
        });

        const renderQueue = regularContacts.map(item => ({
            position: item.id ?? Number.MAX_SAFE_INTEGER,
            node: createMainContact(item, classifyContact(item)),
        }));

        if (socials.length) {
            const socialWrap = document.createElement("div");
            socialWrap.className = "social-links";

            socials
                .sort((a, b) => (a.item.id ?? 0) - (b.item.id ?? 0))
                .forEach(({ item, type }) => {
                    const socialBtn = createSocialButton(item, type);
                    if (socialBtn) socialWrap.appendChild(socialBtn);
                });

            if (socialWrap.children.length) {
                const socialCard = document.createElement("div");
                socialCard.className = "contact-social card";
                const socialTitle = document.createElement("h3");
                socialTitle.textContent = "Мы в соцсетях";
                socialCard.appendChild(socialTitle);
                socialCard.appendChild(socialWrap);

                const socialGroupId = socials
                    .map(({ item }) => item.id)
                    .filter(id => typeof id === "number")
                    .sort((a, b) => a - b)[0] ?? Number.MAX_SAFE_INTEGER;

                renderQueue.push({
                    position: socialGroupId,
                    node: socialCard,
                });
            }
        }

        renderQueue
            .sort((a, b) => a.position - b.position)
            .forEach(({ node }) => fragment.appendChild(node));

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
