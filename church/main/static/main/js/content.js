const filtersContainer = document.getElementById("filters");
const grid = document.getElementById("contentGrid");

async function loadCategories() {
    const response = await fetch("/api/categories/");
    const categories = await response.json();

    // Кнопка "Все"
    createFilterButton("Все", "all", true);

    categories.forEach(cat => {
        createFilterButton(cat.name, cat.slug);
    });
}

function createFilterButton(name, slug, active = false) {
    const btn = document.createElement("button");
    btn.className = "filter-btn";
    if (active) btn.classList.add("active");

    btn.dataset.filter = slug;
    btn.textContent = name;

    btn.addEventListener("click", () => {
        document.querySelectorAll(".filter-btn")
            .forEach(b => b.classList.remove("active"));

        btn.classList.add("active");
        loadContent(slug);
    });

    filtersContainer.appendChild(btn);
}

async function loadContent(category = null) {
    let url = "/api/content/";

    if (category && category !== "all") {
        url += `?category=${category}`;
    }

    const response = await fetch(url);
    const data = await response.json();

    renderCards(data.results || data);
}

function renderCards(items) {
    grid.innerHTML = "";

    items.forEach(item => {
        const card = document.createElement("div");
        card.className = "media-card";

        if (item.category.slug === "video") {
            card.innerHTML = `
                <video controls>
                    <source src="${item.url}" type="video/mp4">
                </video>
                <div class="media-info">${item.drive_date}</div>
            `;
        } else {
            card.innerHTML = `
                <img src="${item.url}">
                <div class="media-info">${item.drive_date}</div>
            `;
        }

        grid.appendChild(card);
    });
}

loadCategories();
loadContent();