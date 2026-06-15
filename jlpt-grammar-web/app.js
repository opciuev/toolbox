const state = {
  book: null,
  activeSectionId: null,
  query: "",
  showText: false,
  zoom: 1,
};

const els = {
  nav: document.querySelector("#sectionNav"),
  content: document.querySelector("#content"),
  search: document.querySelector("#searchInput"),
  title: document.querySelector("#readerTitle"),
  kicker: document.querySelector("#readerKicker"),
  pageStat: document.querySelector("#pageStat"),
  matchStat: document.querySelector("#matchStat"),
  childTabs: document.querySelector("#childTabs"),
  textToggle: document.querySelector("#textToggle"),
  zoomIn: document.querySelector("#zoomIn"),
  zoomOut: document.querySelector("#zoomOut"),
  zoomReset: document.querySelector("#zoomReset"),
  zoomValue: document.querySelector("#zoomValue"),
};

const ZOOM_MIN = 0.7;
const ZOOM_MAX = 2.4;
const ZOOM_STEP = 0.15;

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (char) => {
    const entities = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    };
    return entities[char];
  });
}

function highlight(text, query) {
  const safe = escapeHtml(text);
  if (!query.trim()) return safe;
  const escapedQuery = query.trim().replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return safe.replace(new RegExp(escapedQuery, "gi"), (match) => `<mark>${match}</mark>`);
}

function countMatches(text, query) {
  const normalized = query.trim().toLowerCase();
  if (!normalized) return 0;
  let count = 0;
  let index = 0;
  const source = text.toLowerCase();
  while (index <= source.length) {
    const found = source.indexOf(normalized, index);
    if (found === -1) break;
    count += 1;
    index = found + normalized.length;
  }
  return count;
}

function getActiveSection() {
  return state.book.sections.find((section) => section.id === state.activeSectionId) || state.book.sections[0];
}

function pageImagePath(pageNumber) {
  return `./assets/pages/page-${String(pageNumber).padStart(3, "0")}.webp`;
}

function clampZoom(value) {
  return Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, value));
}

function updateZoomControls() {
  const percent = Math.round(state.zoom * 100);
  els.zoomValue.textContent = `${percent}%`;
  els.zoomOut.disabled = state.zoom <= ZOOM_MIN;
  els.zoomIn.disabled = state.zoom >= ZOOM_MAX;
  els.content.style.setProperty("--page-zoom", String(state.zoom));
}

function setZoom(value) {
  state.zoom = clampZoom(Number(value.toFixed(2)));
  updateZoomControls();
}

function sectionMatches(section, query) {
  const normalized = query.trim().toLowerCase();
  if (!normalized) return true;
  const haystack = [
    section.title,
    ...section.children.map((child) => child.title),
    ...section.pages.map((page) => page.text),
  ]
    .join("\n")
    .toLowerCase();
  return haystack.includes(normalized);
}

function pageMatches(page, query) {
  const normalized = query.trim().toLowerCase();
  if (!normalized) return true;
  return page.text.toLowerCase().includes(normalized);
}

function renderNav() {
  const query = state.query.trim();
  const sections = state.book.sections.filter((section) => sectionMatches(section, query));

  els.nav.innerHTML = sections
    .map((section) => {
      const active = section.id === state.activeSectionId ? " active" : "";
      return `
        <button class="nav-button${active}" data-section="${section.id}" type="button">
          <span class="nav-title">${escapeHtml(section.title)}</span>
          <span class="nav-meta">P.${section.pageStart}-${section.pageEnd}</span>
        </button>
      `;
    })
    .join("");

  for (const button of els.nav.querySelectorAll(".nav-button")) {
    button.addEventListener("click", () => {
      state.activeSectionId = button.dataset.section;
      render();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
}

function renderChildTabs(section) {
  els.childTabs.innerHTML = section.children
    .map(
      (child) => `
        <button class="child-tab" type="button" data-page="${child.page}">
          ${escapeHtml(child.title)}
        </button>
      `,
    )
    .join("");

  for (const tab of els.childTabs.querySelectorAll(".child-tab")) {
    tab.addEventListener("click", () => {
      document.querySelector(`#page-${tab.dataset.page}`)?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    });
  }
}

function renderPageText(page, query) {
  if (!state.showText && !query.trim()) return "";
  return `
    <details class="simple-text" ${query.trim() ? "open" : ""}>
      <summary>简体文字辅助</summary>
      <div>${highlight(page.text, query)}</div>
    </details>
  `;
}

function renderContent(section) {
  const query = state.query.trim();
  const pages = section.pages.filter((page) => pageMatches(page, query));
  const matchCount = pages.reduce((sum, page) => sum + countMatches(page.text, query), 0);

  els.title.textContent = section.title;
  els.kicker.textContent = `${state.book.subtitle} / 原版页图 / P.${section.pageStart}-${section.pageEnd}`;
  els.pageStat.textContent = `${pages.length} 页`;
  els.matchStat.textContent = query ? `${matchCount} 处` : `${section.children.length} 小节`;
  els.textToggle.textContent = state.showText ? "隐藏简体文字" : "显示简体文字";
  els.textToggle.classList.toggle("active", state.showText);

  if (!pages.length) {
    els.content.innerHTML = `<div class="empty-state">当前章节没有匹配页</div>`;
    return;
  }

  els.content.innerHTML = pages
    .map(
      (page) => `
        <article class="page-sheet" id="page-${page.page}">
          <header>
            <span>PDF 第 ${page.page} 页</span>
            <span>${escapeHtml(section.title)}</span>
          </header>
          <div class="page-viewport">
            <img
              class="original-page"
              src="${pageImagePath(page.page)}"
              alt="PDF 第 ${page.page} 页原版"
              loading="${page === pages[0] ? "eager" : "lazy"}"
            />
          </div>
          ${renderPageText(page, query)}
        </article>
      `,
    )
    .join("");
}

function ensureVisibleSection() {
  if (!state.query.trim()) return;
  const active = getActiveSection();
  if (sectionMatches(active, state.query)) return;
  const firstMatch = state.book.sections.find((section) => sectionMatches(section, state.query));
  if (firstMatch) state.activeSectionId = firstMatch.id;
}

function render() {
  ensureVisibleSection();
  const section = getActiveSection();
  renderNav();
  renderChildTabs(section);
  renderContent(section);
}

async function init() {
  const response = await fetch("./data/book.json");
  state.book = await response.json();
  state.activeSectionId = state.book.sections.find((section) => section.title.startsWith("UNIT 01"))?.id;

  els.search.addEventListener("input", (event) => {
    state.query = event.target.value;
    render();
  });
  els.textToggle.addEventListener("click", () => {
    state.showText = !state.showText;
    render();
  });
  els.zoomOut.addEventListener("click", () => setZoom(state.zoom - ZOOM_STEP));
  els.zoomIn.addEventListener("click", () => setZoom(state.zoom + ZOOM_STEP));
  els.zoomReset.addEventListener("click", () => setZoom(1));

  render();
  updateZoomControls();
}

init().catch((error) => {
  console.error(error);
  els.content.innerHTML = `<div class="empty-state">数据加载失败</div>`;
});
