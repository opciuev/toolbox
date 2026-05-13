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
    status: `pending`,
    sections: []
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
}

function buildSidebarForChapter(currentChapterId) {
  buildSidebar(currentChapterId, "");
}

function setupSectionHighlight() {
  const links = Array.from(document.querySelectorAll(".nav-sub a[data-section-id]"));
  const sections = links
    .map((link) => document.getElementById(link.dataset.sectionId))
    .filter(Boolean);
  if (!links.length || !sections.length) return;

  const activate = (sectionId) => {
    links.forEach((link) => {
      const isActive = link.dataset.sectionId === sectionId;
      link.classList.toggle("active", isActive);
      if (isActive) {
        link.scrollIntoView({ block: "nearest" });
      }
    });
  };

  const activateFromHash = () => {
    const id = window.location.hash.replace("#", "");
    if (id) activate(id);
  };

  const activateFromScroll = () => {
    const offset = 96;
    let current = sections[0];
    for (const section of sections) {
      if (section.getBoundingClientRect().top <= offset) {
        current = section;
      } else {
        break;
      }
    }
    activate(current.id);
  };

  links.forEach((link) => {
    link.addEventListener("click", () => {
      const id = link.dataset.sectionId;
      requestAnimationFrame(() => activate(id));
    });
  });

  window.addEventListener("hashchange", activateFromHash);
  window.addEventListener("scroll", activateFromScroll, { passive: true });
  if (window.location.hash) {
    activateFromHash();
  } else {
    activateFromScroll();
  }
}
