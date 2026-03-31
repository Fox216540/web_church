document.addEventListener("DOMContentLoaded", () => {
    const sourceNode = document.getElementById("doc-markdown-source");
    const targetNode = document.getElementById("documentContent");

    if (!sourceNode || !targetNode) return;

    let markdown = "";
    try {
        markdown = JSON.parse(sourceNode.textContent || "\"\"");
    } catch (error) {
        markdown = sourceNode.textContent || "";
    }

    const parsedHtml = marked.parse(markdown, {
        breaks: true,
        gfm: true,
    });

    targetNode.innerHTML = DOMPurify.sanitize(parsedHtml);

    // Add hanging indents only for ##### and ###### numbered headings
    targetNode.querySelectorAll("h5, h6").forEach((node) => {
        const text = (node.textContent || "").trim();
        const match = text.match(/^(\d+(?:\.\d+)*\.?)\s+/);
        if (!match) return;

        node.classList.add("numbered-item");
        node.style.setProperty("--tab-multiplier", node.tagName === "H6" ? "2" : "1");
    });
});
