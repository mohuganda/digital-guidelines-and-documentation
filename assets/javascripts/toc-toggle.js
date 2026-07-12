document.addEventListener("DOMContentLoaded", function () {
  function initialiseTocToggle() {
    const toc = document.querySelector(".md-nav--secondary");
    if (!toc) return;

    const title = toc.querySelector(":scope > .md-nav__title");
    if (!title) return;

    // Avoid attaching the event more than once
    if (title.dataset.tocToggleAttached === "true") return;
    title.dataset.tocToggleAttached = "true";

    // Default collapsed
    toc.classList.remove("toc-expanded");

    title.addEventListener("click", function () {
      toc.classList.toggle("toc-expanded");
    });
  }

  initialiseTocToggle();

  // MkDocs Material uses instant navigation in some setups.
  // This ensures the toggle still works after page navigation.
  document$.subscribe(function () {
    initialiseTocToggle();
  });
});



document.addEventListener("DOMContentLoaded", function () {
  function initialiseTocToggle() {
    const toc = document.querySelector(".md-nav--secondary");
    if (!toc) return;

    const title = toc.querySelector(":scope > .md-nav__title");
    if (!title) return;

    // Avoid attaching the event more than once
    if (title.dataset.tocToggleAttached === "true") return;
    title.dataset.tocToggleAttached = "true";

    // Default collapsed
    toc.classList.remove("toc-expanded");

    title.addEventListener("click", function () {
      toc.classList.toggle("toc-expanded");
    });
  }

  initialiseTocToggle();

  // MkDocs Material uses instant navigation in some setups.
  // This ensures the toggle still works after page navigation.
  document$.subscribe(function () {
    initialiseTocToggle();
  });
});
