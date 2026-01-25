const formatDate = d => d.split("-").reverse().join(".");

document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("sermons_all");
    const pagination = document.querySelector(".pagination");
    const perPage = 6;

    async function load(page) {
        try {
            const r = await fetch(`/api/sermons/?page=${page}`);
            if (!r.ok) throw 0;

            const { items, count } = await r.json();
            render(items);
            renderPagination(page, Math.ceil(count / perPage));
        } catch {
            container.innerHTML = "<p>Ошибка загрузки</p>";
        }
    }

    function render(items) {
        container.innerHTML = "";
        items.forEach(s => {
            const id = s.video_url?.split("v=")[1]?.split("&")[0] || "";
            container.innerHTML += `
                <div class="full-sermon-card">
                    <iframe class="sermon-video" src="https://www.youtube.com/embed/${id}" allowfullscreen></iframe>
                    <div class="sermon-meta">
                        <div class="sermon-date">${formatDate(s.date)}</div>
                        <h3>${s.title}</h3>
                        <p class="scripture-ref">${s.description}</p>
                        <p class="preacher">${s.autor}</p>
                    </div>
                </div>
            `;
        });
    }

    function renderPagination(page, total) {
        let html = `
            <a data-p="${page - 1}" class="${page === 1 ? "disabled" : ""}">«</a>
        `;

        for (let i = 1; i <= total; i++) {
            if (i === 1 || i === total || Math.abs(i - page) <= 1) {
                html += `<a data-p="${i}" class="${i === page ? "active" : ""}">${i}</a>`;
            } else if (i === 2 || i === total - 1) {
                html += `<span class="ellipsis">...</span>`;
            }
        }

        html += `
            <a data-p="${page + 1}" class="${page === total ? "disabled" : ""}">»</a>
        `;

        pagination.innerHTML = html;

        pagination.querySelectorAll("a").forEach(a => {
            a.onclick = () => {
                if (!a.classList.contains("disabled")) {
                    load(+a.dataset.p);
                }
            };
        });
    }

    load(1);
});
