document.addEventListener("DOMContentLoaded", () => {

    const DEFAULT_PHOTO = "/static/main/img/default-person.png";
    const PER_PAGE = 6;

    const modal = document.getElementById("modal");
    const modalClose = document.getElementById("modalClose");
    const pagination = document.getElementById("boardPagination");

    const modalImg = document.getElementById("modalImg");
    const modalName = document.getElementById("modalName");
    const modalRole = document.getElementById("modalRole");
    const modalDesc = document.getElementById("modalDesc");

    const modalPhone = document.getElementById("modalPhone");
    const modalEmail = document.getElementById("modalEmail");
    const modalTelegram = document.getElementById("modalTelegram");
    const modalWhatsapp = document.getElementById("modalWhatsapp");

    const teamGrid = document.getElementById("teamGrid");

        function clearContact(node) {
            node.textContent = "";
            node.style.display = "none";
        }

        function setContactLink(node, label, value, href, isExternal = false) {
            if (!value || !href) {
                clearContact(node);
                return;
            }

            const a = document.createElement("a");
            a.href = href;
            a.textContent = `${label}: ${value}`;

            if (isExternal) {
                a.target = "_blank";
                a.rel = "noopener noreferrer";
            }

            node.innerHTML = "";
            node.appendChild(a);
            node.style.display = "";
        }

        function sanitizePhone(phone) {
            return String(phone).replace(/[^\d+]/g, "");
        }

        function buildTelegramHref(value) {
            const v = String(value).trim();
            if (!v) return "";
            if (v.startsWith("http://") || v.startsWith("https://")) return v;
            return `https://t.me/${v.replace(/^@/, "")}`;
        }

        function buildWhatsappHref(value) {
            const v = String(value).trim();
            if (!v) return "";
            if (v.startsWith("http://") || v.startsWith("https://")) return v;
            return `https://wa.me/${v.replace(/[^\d]/g, "")}`;
        }

		function openModal(person) {
		    modal.classList.add("active");

		    const scrollBarWidth = window.innerWidth - document.documentElement.clientWidth;

		    document.body.style.overflow = "hidden";

		    // добавляем компенсацию только если есть скроллбар
		    if (scrollBarWidth > 0) {
		        document.body.style.paddingRight = scrollBarWidth + "px";
		    }

		    modalImg.src = person.photo || DEFAULT_PHOTO;
		    modalImg.onerror = () => modalImg.src = DEFAULT_PHOTO;

		    modalName.textContent = person.name;
		    modalRole.textContent = person.role;
		    modalDesc.textContent = person.short_bio || "";

		    setContactLink(
                modalPhone,
                "Телефон",
                person.phone,
                person.phone ? `tel:${sanitizePhone(person.phone)}` : ""
            );
		    setContactLink(
                modalEmail,
                "Email",
                person.email,
                person.email ? `mailto:${person.email}` : ""
            );
		    setContactLink(
                modalTelegram,
                "Telegram",
                person.telegram,
                buildTelegramHref(person.telegram),
                true
            );
            setContactLink(
                modalWhatsapp,
                "WhatsApp",
                person.whatsapp,
                buildWhatsappHref(person.whatsapp),
                true
            );
		}

		function closeModal() {
		    modal.classList.remove("active");
		    document.body.style.overflow = "";
		    document.body.style.paddingRight = "";
		}

    modalClose.addEventListener("click", closeModal);

    modal.addEventListener("click", (e) => {
        if (e.target === modal) closeModal();
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeModal();
    });

    function renderCards(items) {
        teamGrid.innerHTML = "";

        items.forEach(person => {
            const card = document.createElement("div");
            card.className = "person-card";

            card.innerHTML = `
                <img src="${person.photo || DEFAULT_PHOTO}" 
                     onerror="this.src='${DEFAULT_PHOTO}'">
                <div class="person-info">
                    <h3>${person.name}</h3>
                    <p class="role">${person.role}</p>
                </div>
            `;

            card.addEventListener("click", () => openModal(person));
            teamGrid.appendChild(card);
        });
    }

    function renderPagination(page, totalPages, onPageClick) {
        if (totalPages <= 1) {
            pagination.style.display = "none";
            pagination.innerHTML = "";
            return;
        }

        pagination.style.display = "flex";

        let html = `
            <a
                data-p="${page - 1}"
                class="page-item ${page === 1 ? "disabled" : ""}"
            >«</a>
        `;

        for (let i = 1; i <= totalPages; i++) {
            if (
                i === 1 ||
                i === totalPages ||
                Math.abs(i - page) <= 1
            ) {
                html += `
                    <a
                        data-p="${i}"
                        class="page-item ${i === page ? "active" : ""}"
                    >${i}</a>
                `;
            } else if (i === 2 || i === totalPages - 1) {
                html += `<span class="page-item ellipsis">…</span>`;
            }
        }

        html += `
            <a
                data-p="${page + 1}"
                class="page-item ${page === totalPages ? "disabled" : ""}"
            >»</a>
        `;

        pagination.innerHTML = html;

        pagination.querySelectorAll("a").forEach(a => {
            a.onclick = () => {
                if (!a.classList.contains("disabled")) {
                    onPageClick(Number(a.dataset.p));
                }
            };
        });
    }

    function renderPage(data, page) {
        const totalPages = Math.ceil(data.length / PER_PAGE);
        const start = (page - 1) * PER_PAGE;
        const pageItems = data.slice(start, start + PER_PAGE);

        renderCards(pageItems);
        renderPagination(page, totalPages, (nextPage) => renderPage(data, nextPage));
    }

    fetch("/api/church-board/")
        .then(r => r.json())
        .then(data => {
            if (!Array.isArray(data) || data.length === 0) {
                teamGrid.innerHTML = "<p style='text-align:center;'>Служители пока не добавлены</p>";
                pagination.style.display = "none";
                return;
            }

            renderPage(data, 1);
        })
        .catch(err => {
            console.error("Ошибка загрузки:", err);
            teamGrid.innerHTML = "<p style='text-align:center;'>Ошибка загрузки</p>";
            pagination.style.display = "none";
        });
});
