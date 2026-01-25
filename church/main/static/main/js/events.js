const formatDate = d => d.split("-").reverse().join(".");

document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("events");
    if (!container) return;

    try {
        const r = await fetch("/api/events/");
        if (!r.ok) throw 0;

        const data = await r.json();
        if (!data.length) {
            container.innerHTML = "<p>Нет событий</p>";
            return;
        }

        container.append(...data.map(renderEvent));
    } catch {
        container.innerHTML = "<p>Ошибка загрузки</p>";
    }
});

function renderEvent(e) {
    const start = formatDate(e.date_start);
    const end = e.date_finish ? ` - ${formatDate(e.date_finish)}` : "";

    const div = document.createElement("div");
    div.className = "events-calendar";
    div.innerHTML = `
        <div class="card event-card">
            <div class="event-date">
                <span class="day">${start}${end}</span>
            </div>
            <div class="event-info">
                <h3>${e.name}</h3>
                <p>${e.description || ""}</p>
            </div>
        </div>
    `;
    return div;
}
