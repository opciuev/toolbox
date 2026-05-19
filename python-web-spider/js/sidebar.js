const chapters = [
  {
    id: `ch01`,
    title: `第1章 爬虫基础`,
    file: `ch01.html`,
    label: `第1章`,
    status: `completed`,
    sections: [`1.1 HTTP 基本原理`, `1.2 Web 网页基础`, `1.3 爬虫的基本原理`, `1.4 Session 和 Cookie`, `1.5 代理的基本原理`, `1.6 多线程和多进程的基本原理`]
  },
  {
    id: `ch02`,
    title: `第2章 基本库的使用`,
    file: `ch02.html`,
    label: `第2章`,
    status: `completed`,
    sections: [`2.1 urllib 的使用`, `2.2 requests 的使用`, `2.3 正则表达式`, `2.4 httpx 的使用`, `2.5 基础爬虫案例实战`]
  },
  {
    id: `ch03`,
    title: `第3章 网页数据的解析提取`,
    file: `ch03.html`,
    label: `第3章`,
    status: `pending`,
    sections: []
  },
  {
    id: `ch04`,
    title: `第4章 数据的存储`,
    file: `ch04.html`,
    label: `第4章`,
    status: `pending`,
    sections: []
  },
  {
    id: `ch05`,
    title: `第5章 Ajax数据爬取`,
    file: `ch05.html`,
    label: `第5章`,
    status: `pending`,
    sections: []
  },
  {
    id: `ch06`,
    title: `第6章 异步爬虫`,
    file: `ch06.html`,
    label: `第6章`,
    status: `pending`,
    sections: []
  },
  {
    id: `ch07`,
    title: `第7章 JavaScript动态渲染页面爬取`,
    file: `ch07.html`,
    label: `第7章`,
    status: `pending`,
    sections: []
  },
  {
    id: `ch08`,
    title: `第8章 验证码的识别`,
    file: `ch08.html`,
    label: `第8章`,
    status: `pending`,
    sections: []
  },
  {
    id: `ch09`,
    title: `第9章 代理的使用`,
    file: `ch09.html`,
    label: `第9章`,
    status: `pending`,
    sections: []
  },
  {
    id: `ch10`,
    title: `第10章 模拟登录`,
    file: `ch10.html`,
    label: `第10章`,
    status: `pending`,
    sections: []
  },
  {
    id: `ch11`,
    title: `第11章 JavaScript逆向爬虫`,
    file: `ch11.html`,
    label: `第11章`,
    status: `pending`,
    sections: []
  },
  {
    id: `ch12`,
    title: `第12章 APP数据的爬取`,
    file: `ch12.html`,
    label: `第12章`,
    status: `pending`,
    sections: []
  },
  {
    id: `ch13`,
    title: `第13章 Android逆向`,
    file: `ch13.html`,
    label: `第13章`,
    status: `pending`,
    sections: []
  },
  {
    id: `ch14`,
    title: `第14章 页面智能解析`,
    file: `ch14.html`,
    label: `第14章`,
    status: `pending`,
    sections: []
  },
  {
    id: `ch15`,
    title: `第15章 Scrapy框架的使用`,
    file: `ch15.html`,
    label: `第15章`,
    status: `pending`,
    sections: []
  },
  {
    id: `ch16`,
    title: `第16章 分布式爬虫`,
    file: `ch16.html`,
    label: `第16章`,
    status: `pending`,
    sections: []
  },
  {
    id: `ch17`,
    title: `第17章 爬虫的管理和部署`,
    file: `ch17.html`,
    label: `第17章`,
    status: `pending`,
    sections: []
  },
  {
    id: `appendix-a`,
    title: `附录 爬虫与法律`,
    file: `appendix-a.html`,
    label: `附录`,
    status: `pending`,
    sections: []
  }
];

const readyChapters = new Set(chapters.filter((chapter) => chapter.status === "completed").map((chapter) => chapter.id));

function toggleSidebar() {
  document.querySelector(".sidebar")?.classList.toggle("open");
  document.querySelector(".overlay")?.classList.toggle("show");
}

function toggleNav(element) {
  element.classList.toggle("active");
  const sub = element.parentElement.querySelector(".nav-sub");
  if (sub) sub.classList.toggle("show");
}

function buildSidebar(currentChapterId, basePath = "chapters/") {
  const nav = document.getElementById("sidebar-nav");
  if (!nav) return;
  nav.innerHTML = chapters.map((chapter) => {
    const isCurrent = chapter.id === currentChapterId;
    const isReady = readyChapters.has(chapter.id);
    const titleClass = ["nav-group-title", isCurrent ? "current active" : ""].join(" ").trim();
    const subClass = ["nav-sub", isCurrent ? "show" : ""].join(" ").trim();
    const href = `${basePath}${chapter.file}`;
    const sections = isReady ? chapter.sections.map((section, index) => {
      const target = isCurrent ? `#section-${index}` : `${href}#section-${index}`;
      return `<li><a href="${target}" data-section-id="section-${index}">${section}</a></li>`;
    }).join("") : "";
    const statusLabel = chapter.status === "completed" ? "完成" : "未完成";
    return `<div class="nav-group">
      <div class="${titleClass}" onclick="toggleNav(this)">
        <span class="nav-title-text">${chapter.title} <span class="nav-status ${chapter.status}">${statusLabel}</span></span>
        <span class="arrow">&#9654;</span>
      </div>
      ${sections ? `<ul class="${subClass}">${sections}</ul>` : ""}
    </div>`;
  }).join("");
  setupSectionHighlight();
  setupCodeCopyButtons();
  setupBackToTopButton();
  setupSiteSearch();
}

function buildSidebarForChapter(currentChapterId) {
  buildSidebar(currentChapterId, "");
}

function scrollToHashTarget() {
  const query = new URLSearchParams(window.location.search).get("q") || "";
  const target = query ? findSearchHitTarget(query) : getHashElement();
  if (!target) return;

  const scroll = () => target.scrollIntoView({ block: "start" });
  document.querySelectorAll(".search-hit").forEach((el) => el.classList.remove("search-hit"));
  if (query) target.classList.add("search-hit");
  window.requestAnimationFrame(scroll);
  window.setTimeout(scroll, 120);
  window.setTimeout(scroll, 420);
}

function getHashElement() {
  if (!window.location.hash) return null;
  const targetId = decodeURIComponent(window.location.hash.slice(1));
  return document.getElementById(targetId);
}

function getSearchScope() {
  const hashTarget = getHashElement();
  if (!hashTarget) return document.querySelector(".main-content") || document.body;

  const nodes = [];
  let node = hashTarget;
  while (node) {
    nodes.push(node);
    node = node.nextElementSibling;
    if (node && node.classList.contains("section-heading")) break;
  }

  return nodes;
}

function getSearchableBlocks(scope) {
  const selector = [
    ".section-heading",
    ".subsection-heading",
    ".content-text",
    ".note-box",
    ".content-table",
    ".code-block",
    ".result-block",
    ".inline-figure",
    ".table-caption",
  ].join(", ");

  const nodes = Array.isArray(scope)
    ? scope.flatMap((node) => [
        ...(node.matches && node.matches(selector) ? [node] : []),
        ...Array.from(node.querySelectorAll(selector)),
      ])
    : Array.from(scope.querySelectorAll(selector));

  return nodes.filter((node, index, array) => (
    node.textContent &&
    node.textContent.trim() &&
    array.indexOf(node) === index
  ));
}

function findSearchHitTarget(query) {
  const needle = normalizeSearchText(query);
  if (!needle) return getHashElement();

  const scopedBlocks = getSearchableBlocks(getSearchScope());
  const scopedHit = scopedBlocks.find((node) => normalizeSearchText(node.textContent || "").includes(needle));
  if (scopedHit) return scopedHit;

  const pageBlocks = getSearchableBlocks(document.querySelector(".main-content") || document.body);
  return pageBlocks.find((node) => normalizeSearchText(node.textContent || "").includes(needle)) || getHashElement();
}

function setupSectionHighlight() {
  const links = Array.from(document.querySelectorAll(".nav-sub a[data-section-id]"))
    .filter((link) => (link.getAttribute("href") || "").startsWith("#"));
  const sectionLinks = links
    .map((link) => ({ link, section: document.getElementById(link.dataset.sectionId) }))
    .filter((item) => item.section);
  if (!links.length || !sectionLinks.length) return;

  let activeSectionId = "";
  let ticking = false;

  const getScrollTop = () => (
    window.scrollY ||
    document.documentElement.scrollTop ||
    document.body.scrollTop ||
    0
  );

  const getCurrentSectionId = () => {
    const marker = getScrollTop() + 120;
    let current = sectionLinks[0].section.id;
    for (const item of sectionLinks) {
      if (item.section.offsetTop <= marker) {
        current = item.section.id;
      } else {
        break;
      }
    }

    const doc = document.documentElement;
    const bottomGap = doc.scrollHeight - (getScrollTop() + window.innerHeight);
    if (bottomGap <= 4) {
      current = sectionLinks[sectionLinks.length - 1].section.id;
    }
    return current;
  };

  const keepActiveLinkVisible = (link) => {
    const sidebar = document.querySelector(".sidebar");
    if (!sidebar) return;
    const linkRect = link.getBoundingClientRect();
    const sidebarRect = sidebar.getBoundingClientRect();
    if (linkRect.top < sidebarRect.top + 16 || linkRect.bottom > sidebarRect.bottom - 16) {
      link.scrollIntoView({ block: "nearest" });
    }
  };

  const activate = (sectionId, scrollNav = false) => {
    if (!sectionId || sectionId === activeSectionId) return;
    activeSectionId = sectionId;
    links.forEach((link) => {
      const isActive = link.dataset.sectionId === sectionId;
      link.classList.toggle("active", isActive);
      if (isActive && scrollNav) {
        keepActiveLinkVisible(link);
      }
    });
  };

  const updateFromScroll = () => {
    activate(getCurrentSectionId(), true);
  };

  const scheduleUpdate = () => {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(() => {
      ticking = false;
      updateFromScroll();
    });
  };

  const activateFromHash = () => {
    const id = window.location.hash.replace("#", "");
    if (id && sectionLinks.some((item) => item.section.id === id)) {
      activate(id, true);
    } else {
      updateFromScroll();
    }
  };

  links.forEach((link) => {
    link.addEventListener("click", () => {
      const id = link.dataset.sectionId;
      requestAnimationFrame(() => activate(id));
    });
  });

  window.addEventListener("hashchange", activateFromHash);
  window.addEventListener("scroll", scheduleUpdate, { passive: true });
  document.addEventListener("scroll", scheduleUpdate, { passive: true });
  window.addEventListener("resize", scheduleUpdate);
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(scheduleUpdate, {
      rootMargin: "-20% 0px -70% 0px",
      threshold: [0, 1]
    });
    sectionLinks.forEach((item) => observer.observe(item.section));
  }
  if (window.location.hash) {
    activateFromHash();
    scrollToHashTarget();
  } else {
    updateFromScroll();
  }
  window.setTimeout(updateFromScroll, 120);
  window.setInterval(updateFromScroll, 250);
}

function getCodeBlockCopyText(block) {
  const clone = block.cloneNode(true);
  clone.querySelectorAll(".code-copy-button, .line-num").forEach((el) => el.remove());
  return clone.textContent.replace(/^\n+|\s+$/g, "");
}

async function copyTextToClipboard(text) {
  if (navigator.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(text);
    return;
  }

  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.left = "-9999px";
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  textarea.remove();
}

function setupCodeCopyButtons() {
  document.querySelectorAll(".code-block, .result-block").forEach((block) => {
    if (block.querySelector(".code-copy-button")) return;

    const button = document.createElement("button");
    button.type = "button";
    button.className = "code-copy-button";
    button.textContent = "复制";
    button.setAttribute("aria-label", "复制代码");
    button.addEventListener("click", async () => {
      try {
        await copyTextToClipboard(getCodeBlockCopyText(block));
        button.textContent = "已复制";
        button.classList.add("copied");
        window.setTimeout(() => {
          button.textContent = "复制";
          button.classList.remove("copied");
        }, 1400);
      } catch (err) {
        button.textContent = "复制失败";
        window.setTimeout(() => {
          button.textContent = "复制";
        }, 1400);
      }
    });

    block.appendChild(button);
  });
}

function getSearchLinkPrefix() {
  return window.location.pathname.includes("/chapters/") ? "" : "chapters/";
}

function getChapterFetchPrefix() {
  return window.location.pathname.includes("/chapters/") ? "" : "chapters/";
}

function normalizeSearchText(text) {
  return text.toLowerCase().replace(/\s+/g, " ").trim();
}

function escapeSearchHtml(text) {
  return text.replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[char]));
}

function makeSearchSnippet(text, query) {
  const haystack = text.toLowerCase();
  const needle = query.toLowerCase();
  const index = haystack.indexOf(needle);

  if (index < 0) {
    return text.slice(0, 110) + (text.length > 110 ? "..." : "");
  }

  const start = Math.max(0, index - 42);
  const end = Math.min(text.length, index + query.length + 68);
  const prefix = start > 0 ? "..." : "";
  const suffix = end < text.length ? "..." : "";
  return prefix + text.slice(start, end) + suffix;
}

function extractSearchText(doc) {
  const main = doc.querySelector(".main-content") || doc.body;
  const clone = main.cloneNode(true);
  clone.querySelectorAll("script, style, .chapter-nav, .code-copy-button, .back-to-top").forEach((el) => el.remove());
  return clone.textContent.replace(/\s+/g, " ").trim();
}

function extractSectionTexts(doc) {
  const headings = Array.from(doc.querySelectorAll(".section-heading[id]"));
  return headings.map((heading) => {
    const title = (heading.textContent || "").replace(/\s+/g, " ").trim();
    let text = title;
    let node = heading.nextElementSibling;
    while (node && !node.classList.contains("section-heading")) {
      text += " " + (node.textContent || "");
      node = node.nextElementSibling;
    }
    return {
      id: heading.id,
      title,
      text: text.replace(/\s+/g, " ").trim(),
    };
  });
}

function makeFallbackSearchEntry(chapter) {
  const text = [chapter.title, ...(chapter.sections || [])].join(" ");
  return {
    id: chapter.id,
    title: chapter.title,
    file: chapter.file,
    sections: chapter.sections || [],
    sectionTexts: (chapter.sections || []).map((section, index) => ({ id: `section-${index}`, title: section, text: section })),
    text,
    normalized: normalizeSearchText(text),
  };
}

async function buildSearchIndex() {
  const parser = new DOMParser();
  const pathPrefix = getChapterFetchPrefix();
  const completedChapters = chapters.filter((chapter) => readyChapters.has(chapter.id));
  const entries = await Promise.all(completedChapters.map(async (chapter) => {
    try {
      const response = await fetch(pathPrefix + chapter.file);
      if (!response.ok) return makeFallbackSearchEntry(chapter);

      const markup = await response.text();
      const doc = parser.parseFromString(markup, "text/html");
      const text = extractSearchText(doc);
      const sectionTexts = extractSectionTexts(doc);

      return {
        id: chapter.id,
        title: chapter.title,
        file: chapter.file,
        sections: chapter.sections || [],
        sectionTexts,
        text,
        normalized: normalizeSearchText([chapter.title, (chapter.sections || []).join(" "), text].join(" ")),
      };
    } catch (err) {
      return makeFallbackSearchEntry(chapter);
    }
  }));

  return entries;
}

function renderSearchResults(container, entries, query) {
  const normalizedQuery = normalizeSearchText(query);

  if (!normalizedQuery) {
    container.innerHTML = "";
    container.classList.remove("show");
    return [];
  }

  const terms = normalizedQuery.split(" ").filter(Boolean);
  const matches = entries
    .flatMap((entry) => {
      const sectionTexts = (entry.sectionTexts && entry.sectionTexts.length)
        ? entry.sectionTexts
        : [{ id: "", title: "", text: entry.text || "" }];
      return sectionTexts.map((section) => {
        const chapterTitle = normalizeSearchText(entry.title || "");
        const sectionTitle = normalizeSearchText(section.title || "");
        const sectionText = normalizeSearchText(section.text || "");
        const score = terms.reduce((total, term) => {
          let next = total;
          if (sectionTitle.includes(term)) next += 40;
          if (chapterTitle.includes(term)) next += 12;
          if (sectionText.includes(term)) next += 4;
          return next;
        }, 0);
        return { entry, section, score };
      });
    })
    .filter((item) => item.score > 0)
    .sort((a, b) => (
      b.score - a.score ||
      a.entry.id.localeCompare(b.entry.id) ||
      (a.section.id || "").localeCompare(b.section.id || "")
    ))
    .slice(0, 12);

  if (!matches.length) {
    container.innerHTML = '<div class="site-search-empty">没有找到相关内容</div>';
    container.classList.add("show");
    return [];
  }

  const linkPrefix = getSearchLinkPrefix();
  container.innerHTML = matches.map(({ entry, section }, index) => {
    const searchParam = `?q=${encodeURIComponent(query)}`;
    const anchor = section.id ? `#${section.id}` : "";
    const href = `${linkPrefix}${entry.file}${searchParam}${anchor}`;
    const snippet = makeSearchSnippet(section.text || entry.text || "", query);
    const title = section.title ? `${entry.title} · ${section.title}` : entry.title;

    return `
      <a class="site-search-result" href="${href}" data-result-index="${index}">
        <strong>${escapeSearchHtml(title || "")}</strong>
        <span>${escapeSearchHtml(snippet)}</span>
      </a>
    `;
  }).join("");
  container.classList.add("show");
  return matches;
}

function setupSiteSearch() {
  const headerRight = document.querySelector(".header-right");
  if (!headerRight || headerRight.querySelector(".site-search")) return;

  const wrapper = document.createElement("div");
  wrapper.className = "site-search";
  wrapper.innerHTML = `
    <div class="site-search-bar">
      <input class="site-search-input" type="search" placeholder="搜索知识点..." aria-label="搜索 Python 爬虫教程内容" autocomplete="off">
      <button class="site-search-clear" type="button" aria-label="清空搜索" title="清空搜索">&times;</button>
    </div>
    <div class="site-search-results" role="listbox"></div>
  `;
  headerRight.prepend(wrapper);

  const input = wrapper.querySelector(".site-search-input");
  const clearButton = wrapper.querySelector(".site-search-clear");
  const results = wrapper.querySelector(".site-search-results");
  let searchIndexPromise = null;
  let debounceTimer = null;

  const ensureSearchIndex = () => {
    searchIndexPromise ||= buildSearchIndex();
    return searchIndexPromise;
  };

  const warmSearchIndex = () => {
    if ("requestIdleCallback" in window) {
      window.requestIdleCallback(() => ensureSearchIndex(), { timeout: 2000 });
      return;
    }
    window.setTimeout(() => ensureSearchIndex(), 600);
  };

  const updateClearButton = () => {
    const hasQuery = Boolean(input.value.trim());
    clearButton.disabled = !hasQuery;
    clearButton.classList.toggle("show", hasQuery);
  };

  const resetSearch = () => {
    input.value = "";
    renderSearchResults(results, [], "");
    updateClearButton();
  };

  input.addEventListener("input", () => {
    updateClearButton();
    window.clearTimeout(debounceTimer);
    debounceTimer = window.setTimeout(async () => {
      const query = input.value.trim();
      if (!query) {
        resetSearch();
        return;
      }

      results.innerHTML = '<div class="site-search-empty">正在检索...</div>';
      results.classList.add("show");

      const index = await ensureSearchIndex();
      renderSearchResults(results, index, query);
    }, 160);
  });

  input.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      resetSearch();
      input.blur();
    } else if (event.key === "Enter") {
      const active = results.querySelector(".site-search-result.active") || results.querySelector(".site-search-result");
      if (active) {
        event.preventDefault();
        active.click();
      }
    }
  });

  clearButton.addEventListener("click", () => {
    resetSearch();
    input.focus();
  });

  document.addEventListener("click", (event) => {
    if (!wrapper.contains(event.target)) {
      results.classList.remove("show");
    }
  });

  results.addEventListener("click", (event) => {
    const link = event.target.closest(".site-search-result");
    if (!link) return;
    results.classList.remove("show");
    if (link.hash && link.pathname === window.location.pathname) {
      window.setTimeout(scrollToHashTarget, 0);
    }
  });

  updateClearButton();
  warmSearchIndex();
}

function setupBackToTopButton() {
  if (document.querySelector(".back-to-top")) return;

  const button = document.createElement("button");
  button.type = "button";
  button.className = "back-to-top";
  button.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M12 19V5"></path>
    <path d="M5 12l7-7 7 7"></path>
  </svg>`;
  button.setAttribute("aria-label", "回到顶部");
  button.setAttribute("title", "回到顶部");

  const update = () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
    button.classList.toggle("show", scrollTop > 320);
  };

  button.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  window.addEventListener("scroll", update, { passive: true });
  document.addEventListener("scroll", update, { passive: true });
  window.addEventListener("resize", update);
  document.body.appendChild(button);
  update();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    setupBackToTopButton();
    setupSiteSearch();
    scrollToHashTarget();
  }, { once: true });
} else {
  setupBackToTopButton();
  setupSiteSearch();
  scrollToHashTarget();
}
