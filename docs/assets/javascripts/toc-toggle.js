function initialiseTocAccordion() {
  const toc = document.querySelector(".md-nav--secondary");
  if (!toc || toc.dataset.tocAccordionAttached === "true") return;

  const sections = toc.querySelectorAll(
    ":scope > .md-nav__list > .md-nav__item"
  );

  sections.forEach(function (section) {
    const headingLink = section.querySelector(":scope > .md-nav__link");
    const childNavigation = section.querySelector(":scope > .md-nav");

    if (!headingLink || !childNavigation) return;

    headingLink.setAttribute("aria-expanded", "false");

    headingLink.addEventListener("click", function () {
      sections.forEach(function (otherSection) {
        otherSection.classList.remove("toc-section-expanded");

        const otherHeadingLink = otherSection.querySelector(
          ":scope > .md-nav__link"
        );
        if (otherHeadingLink) {
          otherHeadingLink.setAttribute("aria-expanded", "false");
        }
      });

      section.classList.add("toc-section-expanded");
      headingLink.setAttribute("aria-expanded", "true");
    });
  });

  toc.dataset.tocAccordionAttached = "true";
}

document.addEventListener("DOMContentLoaded", initialiseTocAccordion);

if (typeof document$ !== "undefined") {
  document$.subscribe(initialiseTocAccordion);
}
