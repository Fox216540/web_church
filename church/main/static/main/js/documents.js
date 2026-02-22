async function loadDocuments() {
    const container = document.getElementById("docsContainer");
    if (!container) return;

    container.innerHTML = "";

    try {
        const response = await fetch("/api/documents/");
        if (!response.ok) {
            throw new Error("Ошибка загрузки документов");
        }

        const documents = await response.json();

        documents.forEach(doc => {
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

    } catch (error) {
        console.error("Ошибка:", error);
    }
}

document.addEventListener("DOMContentLoaded", loadDocuments);