function renderPdfChapter(config) {
  const container = document.getElementById("pdf-pages");
  if (!container) return;

  const anchorsByPage = new Map();
  Object.entries(config.anchors || {}).forEach(([sectionId, page]) => {
    if (!anchorsByPage.has(page)) anchorsByPage.set(page, []);
    anchorsByPage.get(page).push(sectionId);
  });

  const pages = [];
  for (let page = 1; page <= config.pageCount; page += 1) {
    const anchors = (anchorsByPage.get(page) || [])
      .map((id) => `<span class="section-anchor" id="${id}"></span>`)
      .join("");
    const pageName = String(page).padStart(2, "0");
    pages.push(`${anchors}
      <figure class="book-page">
        <img src="${config.imageDir}/page_${pageName}.jpg" alt="${config.title} 第 ${page} 页" loading="lazy">
      </figure>`);
  }

  container.innerHTML = pages.join("");
}
