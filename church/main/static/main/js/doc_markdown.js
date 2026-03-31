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

    // Add hanging indents for multi-level numbered items like 1.2.5.1
    targetNode.querySelectorAll("p, li").forEach((node) => {
        const text = (node.textContent || "").trim();
        const match = text.match(/^(\d+(?:\.\d+)*\.?)\s+/);
        if (!match) return;

        const depth = match[1]
            .split(".")
            .filter(Boolean)
            .length;

        node.classList.add("numbered-item");
        node.style.setProperty("--item-depth", String(depth));
    });
});
