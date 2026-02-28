(async () => {
    const containerId = "3_sermons";
    const url = "/api/latest_3_sermons/";
    const container = document.getElementById(containerId);

    if (!container) return;

    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error("API error");

        const data = await res.json();

        if (!data?.length) {
            container.innerHTML = "<p>Нет проповедей для отображения.</p>";
            return;
        }

        const fragment = document.createDocumentFragment();
        data.forEach(item => fragment.appendChild(buildCard(item)));
        container.appendChild(fragment);

    } catch (error) {
        console.error(error);
        container.innerHTML = "<p>Произошла ошибка при загрузке данных.</p>";
    } finally {
    }
})();

/* ================= helpers ================= */

function buildCard({ video_url, title, description, author, scripture }) {
    const videoId =
        (video_url || "").split("v=")[1]?.split("&")[0] || "";

    const div = document.createElement("div");
    div.className = "sermon-card";

    div.innerHTML = `
        <a href="${video_url || "#"}" target="_blank" class="video-thumbnail">
            <img
                src="https://img.youtube.com/vi/${videoId}/maxresdefault.jpg"
                alt="${escapeHtml(title || "")}"
            >
            <div class="play-overlay">
                <i class="fab fa-youtube"></i>
            </div>
        </a>

        <div class="sermon-info">
            <h3>${escapeHtml(title || "")}</h3>
            <div class="meta">
                ${scripture ? `<p class="scripture-ref">${escapeHtml(scripture)}</p>` : ""}
                ${description ? `<p class="description">${escapeHtml(description)}</p>` : ""}
                <div class="pastor">
                    <i class="fas fa-user"></i> ${escapeHtml(author || "")}
                </div>
            </div>
        </div>
    `;

    return div;
}

/* защита от XSS */
function escapeHtml(text = "") {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}