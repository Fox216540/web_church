document.addEventListener("DOMContentLoaded", async () => {
    try {
        const r = await fetch("/api/home-groups/");
        const groups = await r.json();

        const container = document.getElementById("home-groups");

        container.innerHTML = groups.map(g => `
            <div class="group-card">
                <img src="${g.photo_of_leader || '/static/img/leader_placeholder.jpg'}" alt="${g.leader}">
                <div class="group-info">
                    <h3>${g.name}</h3>
                    <p>${g.leader}</p>
                    <p class="meta">📍 ${g.location} • 🕒 ${g.meeting_time}</p>
                </div>
            </div>
        `).join("");

    } catch (e) {
        console.error("Home groups API error:", e);
    }
});

