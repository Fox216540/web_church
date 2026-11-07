const filtersContainer = document.getElementById("filters");
const container = document.getElementById("docsContainer");

let allDocuments = [];

async function loadCategories() {
    const response = await fetch("/api/document-types/");
    if (!response.ok) return;

    const categories = await response.json();

    // Кнопка "Все"
    createFilterButton("Все", "all", true);

    categories.forEach(cat => {
        createFilterButton(cat.name, cat.code);
    });
}

function createFilterButton(name, code, active = false) {
    const btn = document.createElement("button");
    btn.className = "filter-btn";
    if (active) btn.classList.add("active");

    btn.dataset.filter = code;
    btn.textContent = name;

    btn.addEventListener("click", () => {
        document.querySelectorAll(".filter-btn")
            .forEach(b => b.classList.remove("active"));

        btn.classList.add("active");
        renderDocuments(code);
    });

    filtersContainer.appendChild(btn);
}

async function loadDocuments() {
    if (!container) return;

    container.innerHTML = "";

    try {
        const response = await fetch("/api/documents/");
        if (!response.ok) {
            throw new Error("Ошибка загрузки документов");
        }

        allDocuments = await response.json();
        renderDocuments("all");

    } catch (error) {
        console.error("Ошибка:", error);
    }
}

function renderDocuments(filter = "all") {
    container.innerHTML = "";

    const filtered = filter === "all"
        ? allDocuments
        : allDocuments.filter(doc => doc.doc_type === filter);

    filtered.forEach(doc => {
        const card = document.createElement("div");
        card.className = `doc-card ${doc.doc_type}`;

        const title = document.createElement("h3");
        title.textContent = doc.title;

        card.appendChild(title);

        card.addEventListener("click", () => {
            window.location.href = `/doc/${doc.slug}/`;
        });

        container.appendChild(card);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    loadCategories();
    loadDocuments();
});