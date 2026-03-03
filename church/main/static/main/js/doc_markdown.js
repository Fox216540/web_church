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
});
