const filtersContainer = document.getElementById("filters");
const grid = document.getElementById("contentGrid");
const pagination = document.getElementById("contentPagination");
const imageModal = document.getElementById("imageModal");
const imageModalImg = document.getElementById("imageModalImg");
const imageModalClose = document.getElementById("imageModalClose");

const perPage = 9;
let currentCategory = "all";
let zoom = 1;
let translateX = 0;
let translateY = 0;
const MIN_ZOOM = 1;
const MAX_ZOOM = 4;
let isDragging = false;
let dragStartX = 0;
let dragStartY = 0;
let pinchStartDistance = 0;
let pinchStartZoom = 1;

function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
}

function applyZoomTransform() {
    imageModalImg.style.transform = `translate(${translateX}px, ${translateY}px) scale(${zoom})`;
}

function resetZoomState() {
    zoom = 1;
    translateX = 0;
    translateY = 0;
    isDragging = false;
    pinchStartDistance = 0;
    applyZoomTransform();
}

function getTouchDistance(t1, t2) {
    const dx = t2.clientX - t1.clientX;
    const dy = t2.clientY - t1.clientY;
    return Math.hypot(dx, dy);
}

function openImageModal(src) {
    if (!src) return;

    imageModalImg.src = src;
    resetZoomState();
    imageModal.classList.add("is-open");
    imageModal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
}

function closeImageModal() {
    imageModal.classList.remove("is-open");
    imageModal.setAttribute("aria-hidden", "true");
    imageModalImg.src = "";
    resetZoomState();
    document.body.style.overflow = "";
}

imageModalClose.addEventListener("click", closeImageModal);

imageModal.addEventListener("click", (e) => {
    if (e.target === imageModal) {
        closeImageModal();
    }
});

document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && imageModal.classList.contains("is-open")) {
        closeImageModal();
    }
});

imageModal.addEventListener("wheel", (e) => {
    if (!imageModal.classList.contains("is-open")) return;

    e.preventDefault();
    const delta = e.deltaY < 0 ? 0.2 : -0.2;
    zoom = clamp(zoom + delta, MIN_ZOOM, MAX_ZOOM);

    if (zoom === MIN_ZOOM) {
        translateX = 0;
        translateY = 0;
    }

    applyZoomTransform();
}, { passive: false });

imageModalImg.addEventListener("mousedown", (e) => {
    if (zoom <= 1) return;

    isDragging = true;
    dragStartX = e.clientX - translateX;
    dragStartY = e.clientY - translateY;
});

window.addEventListener("mousemove", (e) => {
    if (!isDragging) return;

    translateX = e.clientX - dragStartX;
    translateY = e.clientY - dragStartY;
    applyZoomTransform();
});

window.addEventListener("mouseup", () => {
    isDragging = false;
});

imageModalImg.addEventListener("touchstart", (e) => {
    if (e.touches.length === 2) {
        pinchStartDistance = getTouchDistance(e.touches[0], e.touches[1]);
        pinchStartZoom = zoom;
        return;
    }

    if (e.touches.length === 1 && zoom > 1) {
        isDragging = true;
        dragStartX = e.touches[0].clientX - translateX;
        dragStartY = e.touches[0].clientY - translateY;
    }
}, { passive: false });

imageModalImg.addEventListener("touchmove", (e) => {
    if (!imageModal.classList.contains("is-open")) return;

    if (e.touches.length === 2) {
        e.preventDefault();
        const distance = getTouchDistance(e.touches[0], e.touches[1]);
        if (!pinchStartDistance) {
            pinchStartDistance = distance;
            pinchStartZoom = zoom;
            return;
        }

        const scaleFactor = distance / pinchStartDistance;
        zoom = clamp(pinchStartZoom * scaleFactor, MIN_ZOOM, MAX_ZOOM);

        if (zoom === MIN_ZOOM) {
            translateX = 0;
            translateY = 0;
        }

        applyZoomTransform();
        return;
    }

    if (e.touches.length === 1 && isDragging && zoom > 1) {
        e.preventDefault();
        translateX = e.touches[0].clientX - dragStartX;
        translateY = e.touches[0].clientY - dragStartY;
        applyZoomTransform();
    }
}, { passive: false });

imageModalImg.addEventListener("touchend", () => {
    isDragging = false;
    pinchStartDistance = 0;
});

async function loadCategories() {
    const response = await fetch("/api/categories/");
    const categories = await response.json();

    createFilterButton("Все", "all", true);
    categories.forEach(cat => createFilterButton(cat.name, cat.slug));
}

function createFilterButton(name, slug, active = false) {
    const btn = document.createElement("button");
    btn.className = "filter-btn";
    if (active) btn.classList.add("active");

    btn.dataset.filter = slug;
    btn.textContent = name;

    btn.addEventListener("click", () => {
        document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        currentCategory = slug;
        loadContent(1);
    });

    filtersContainer.appendChild(btn);
}

async function loadContent(page = 1) {
    let url = `/api/content/?page=${page}`;

    if (currentCategory && currentCategory !== "all") {
        url += `&category=${encodeURIComponent(currentCategory)}`;
    }

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error();

        const data = await response.json();
        const items = Array.isArray(data.items) ? data.items : [];
        const count = Number(data.count || 0);
        const totalPages = Math.ceil(count / perPage);

        renderCards(items);

        if (totalPages <= 1) {
            pagination.style.display = "none";
            pagination.innerHTML = "";
            return;
        }

        pagination.style.display = "flex";
        renderPagination(page, totalPages);
    } catch {
        grid.innerHTML = `<p style="text-align:center;">Ошибка загрузки</p>`;
        pagination.style.display = "none";
        pagination.innerHTML = "";
    }
}

function renderCards(items) {
    grid.innerHTML = "";

    if (!Array.isArray(items) || items.length === 0) {
        grid.innerHTML = `<p style="text-align:center;">Пока нет контента</p>`;
        return;
    }

    items.forEach(item => {
        const card = document.createElement("div");
        card.className = "media-card";

        const categorySlug = item.category_slug || "";
        if (categorySlug) card.dataset.category = categorySlug;

        const photoUrl = item.photo_url;
        card.innerHTML = `
            <img src="${photoUrl}" class="media-image" alt="Фото контента">
            <div class="media-info">${item.drive_date}</div>
        `;

        const img = card.querySelector(".media-image");
        if (img) {
            img.addEventListener("click", () => openImageModal(photoUrl));
        }

        grid.appendChild(card);
    });
}

function renderPagination(page, total) {
    let html = `
        <a data-p="${page - 1}" class="page-item ${page === 1 ? "disabled" : ""}">«</a>
    `;

    for (let i = 1; i <= total; i++) {
        if (i === 1 || i === total || Math.abs(i - page) <= 1) {
            html += `
                <a data-p="${i}" class="page-item ${i === page ? "active" : ""}">${i}</a>
            `;
        } else if (i === 2 || i === total - 1) {
            html += `<span class="page-item ellipsis">…</span>`;
        }
    }

    html += `
        <a data-p="${page + 1}" class="page-item ${page === total ? "disabled" : ""}">»</a>
    `;

    pagination.innerHTML = html;

    pagination.querySelectorAll("a").forEach(a => {
        a.onclick = () => {
            if (!a.classList.contains("disabled")) {
                loadContent(Number(a.dataset.p));
            }
        };
    });
}

loadCategories().then(() => loadContent(1));
