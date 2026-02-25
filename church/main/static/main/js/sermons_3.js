document.addEventListener("DOMContentLoaded", () =>
    loadSermons("3_sermons", "/api/latest_3_sermons/")
);

async function loadSermons(containerId, url) {
    const container = document.getElementById(containerId);
    if (!container) return;

    try {
        const res = await fetch(url);
        if (!res.ok) throw 0;

        const data = await res.json();
        if (!data?.length) {
            container.innerHTML = "<p>Нет проповедей для отображения.</p>";
            return;
        }

        container.append(...data.map(buildCard));
    } catch {
        container.innerHTML = "<p>Произошла ошибка при загрузке данных.</p>";
    }
}

function buildCard({ video_url, title, description, author, scripture }) {
    const videoId = (video_url || "").split("v=")[1]?.split("&")[0] || "";

    const div = document.createElement("div");
    div.className = "sermon-card";
    div.innerHTML = `
        <a href="${video_url}" target="_blank" class="video-thumbnail">
            <img src="https://img.youtube.com/vi/${videoId}/maxresdefault.jpg" alt="${title || ""}">
            <div class="play-overlay"><i class="fab fa-youtube"></i></div>
        </a>
        <div class="sermon-info">
            <h3>${title || ""}</h3>
            <div class="meta">
                ${scripture ? `<p class="scripture-ref">${scripture}</p>` : ""}
                ${description ? `<p class="description">${description}</p>` : ""}
                <div class="pastor">
                    <i class="fas fa-user"></i> ${author || ""}
                </div>
            </div>
        </div>
    `;
    return div;
}