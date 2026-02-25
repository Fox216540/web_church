document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("sermons_all");
    container.classList.add("sermon-grid");

    const pagination = document.querySelector(".pagination");
    const perPage = 6;

    async function load(page) {
        try {
            const r = await fetch(`/api/sermons/?page=${page}`);
            if (!r.ok) throw new Error();

            const { items, count } = await r.json();
            const totalPages = Math.ceil(count / perPage);

            if (count === 0) {
                container.innerHTML = `
                    <p style="text-align:center;">
                        Проповедей пока нет
                    </p>
                `;
                pagination.style.display = "none";
                return;
            }

            render(items);

            if (totalPages <= 1) {
                pagination.style.display = "none";
                return;
            }

            pagination.style.display = "flex";
            renderPagination(page, totalPages);

        } catch {
            container.innerHTML = `
                <p style="text-align:center;">
                    Ошибка загрузки
                </p>
            `;
            pagination.style.display = "none";
        }
    }

    function render(items) {
        container.innerHTML = "";

        items.forEach(s => {
            const id =
                s.video_url?.split("v=")[1]?.split("&")[0] || "";

            container.innerHTML += `
                <div class="sermon-card">
                    <iframe
                        class="sermon-video"
                        src="https://www.youtube.com/embed/${id}"
                        allowfullscreen
                    ></iframe>

                    <div class="sermon-meta">
                        <div class="sermon-date">
                            ${s.date}
                        </div>

                        <h3>${s.title || ""}</h3>

                        ${s.scripture ? `
                            <p class="scripture-ref">
                                ${s.scripture}
                            </p>
                        ` : ""}

                        ${s.description ? `
                            <p class="description">
                                ${s.description}
                            </p>
                        ` : ""}

                        <p class="preacher">
                            ${s.author || ""}
                        </p>
                    </div>
                </div>
            `;
        });
    }

    function renderPagination(page, total) {
        let html = `
            <a
                data-p="${page - 1}"
                class="page-item ${page === 1 ? "disabled" : ""}"
            >«</a>
        `;

        for (let i = 1; i <= total; i++) {
            if (
                i === 1 ||
                i === total ||
                Math.abs(i - page) <= 1
            ) {
                html += `
                    <a
                        data-p="${i}"
                        class="page-item ${i === page ? "active" : ""}"
                    >${i}</a>
                `;
            } else if (i === 2 || i === total - 1) {
                html += `<span class="page-item ellipsis">…</span>`;
            }
        }

        html += `
            <a
                data-p="${page + 1}"
                class="page-item ${page === total ? "disabled" : ""}"
            >»</a>
        `;

        pagination.innerHTML = html;

        pagination.querySelectorAll("a").forEach(a => {
            a.onclick = () => {
                if (!a.classList.contains("disabled")) {
                    load(Number(a.dataset.p));
                }
            };
        });
    }

    load(1);
});