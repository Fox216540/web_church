document.addEventListener("DOMContentLoaded", async () => {
    try {
        const r = await fetch("/api/home-groups/");
        const groups = await r.json();

        const container = document.getElementById("home-groups");

        container.innerHTML = groups.map(g => `
            <div class="group-card">
                <div class="group-image">
                    <img 
                        src="${g.photo_of_leader || '/static/main/img/default-person.png'}" 
                        alt="${g.leader}"
                        onerror="this.src='/static/main/img/default-person.png'"
                    >
                </div>

                <div class="group-info">
                    <h3>${g.leader}</h3>
                    <p class="meta">
                        <span>📍 ${g.location || 'Место уточняется'}</span>
                        <span>🕒 ${g.meeting_time}</span>
                    </p>
                </div>
            </div>
        `).join("");

    } catch (e) {
        console.error("Home groups API error:", e);
    }
});
