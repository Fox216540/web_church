(async () => {
    const container = document.getElementById("events");

    // если блока нет — просто показываем страницу
    if (!container) {
        document.documentElement.style.visibility = "visible";
        return;
    }

    try {
        const response = await fetch("/api/events/");
        if (!response.ok) throw new Error("API error");

        const events = await response.json();

        if (!events.length) {
            container.innerHTML = `
                <div class="no-events">
                    <i class="fa-regular fa-calendar-xmark"></i>
                    <h3>Событий пока нет</h3>
                    <p>Следите за обновлениями и анонсами</p>
                </div>
            `;
        } else {
            const fragment = document.createDocumentFragment();
            events.forEach(event => {
                fragment.appendChild(renderEvent(event));
            });
            container.appendChild(fragment);
        }

    } catch (error) {
        console.error(error);
        container.innerHTML = "<p>Ошибка загрузки</p>";
    } finally {
        // 🔥 показать страницу ПОСЛЕ вставки DOM
        document.documentElement.style.visibility = "visible";

        // 🔥 якорь ТОЛЬКО при ПЕРВОЙ загрузке страницы
        if (!window.__initialAnchorScrollDone && location.hash) {
            window.__initialAnchorScrollDone = true;

            const id = location.hash.slice(1);
            const target = document.getElementById(id);
            if (target) {
                const section = target.closest("section") || target;
                section.scrollIntoView({ block: "start" });
            }
        }
    }
})();

/* ================= helpers ================= */

function renderEvent(event) {
    const dateText = buildDateText(event);

    const card = document.createElement("div");
    card.className = "event-card";

    card.innerHTML = `
        <div class="event-banner ${event.banner ? "" : "no-image"}">
            ${event.banner
                ? `<img src="${event.banner}" alt="${escapeHtml(event.name)}">`
                : ""
            }
        </div>

        <div class="event-content">
            <div class="event-date">${dateText}</div>
            <h3>${escapeHtml(event.name)}</h3>
            <p>${escapeHtml(event.description || "")}</p>
        </div>
    `;

    return card;
}

function buildDateText(event) {
    if (!event.date_start) return "";
    if (event.date_finish) {
        return `${event.date_start} — ${event.date_finish}`;
    }
    return event.date_start;
}

/* защита от XSS */
function escapeHtml(text = "") {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}