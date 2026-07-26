(function () {
  "use strict";

  var sidebar = document.querySelector(".sidebar");
  var overlay = document.querySelector(".sidebar-overlay");
  var menuButton = document.querySelector(".menu-button");
  var progress = document.querySelector(".reading-progress");
  var sectionLinks = Array.prototype.slice.call(
    document.querySelectorAll(".section-nav a[href^='#']")
  );

  function closeSidebar() {
    if (!sidebar || !overlay || !menuButton) return;
    sidebar.classList.remove("open");
    overlay.classList.remove("open");
    menuButton.setAttribute("aria-expanded", "false");
  }

  function openSidebar() {
    if (!sidebar || !overlay || !menuButton) return;
    sidebar.classList.add("open");
    overlay.classList.add("open");
    menuButton.setAttribute("aria-expanded", "true");
  }

  if (menuButton) {
    menuButton.addEventListener("click", function () {
      if (sidebar && sidebar.classList.contains("open")) closeSidebar();
      else openSidebar();
    });
  }

  if (overlay) overlay.addEventListener("click", closeSidebar);

  sectionLinks.forEach(function (link) {
    link.addEventListener("click", closeSidebar);
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") closeSidebar();
  });

  function updateProgress() {
    if (!progress) return;
    var scrollable =
      document.documentElement.scrollHeight - window.innerHeight;
    var ratio = scrollable > 0 ? window.scrollY / scrollable : 0;
    progress.style.width = Math.min(100, Math.max(0, ratio * 100)) + "%";
  }

  window.addEventListener("scroll", updateProgress, { passive: true });
  updateProgress();

  if ("IntersectionObserver" in window && sectionLinks.length) {
    var sections = sectionLinks
      .map(function (link) {
        return document.querySelector(link.getAttribute("href"));
      })
      .filter(Boolean);

    var observer = new IntersectionObserver(
      function (entries) {
        var visible = entries
          .filter(function (entry) {
            return entry.isIntersecting;
          })
          .sort(function (a, b) {
            return a.boundingClientRect.top - b.boundingClientRect.top;
          })[0];
        if (!visible) return;
        sectionLinks.forEach(function (link) {
          link.classList.toggle(
            "active",
            link.getAttribute("href") === "#" + visible.target.id
          );
        });
      },
      { rootMargin: "-18% 0px -70% 0px", threshold: 0 }
    );

    sections.forEach(function (section) {
      observer.observe(section);
    });
  }

})();
