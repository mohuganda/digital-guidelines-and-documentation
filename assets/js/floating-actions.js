(function () {
  const STORAGE_KEY = "ucg_bookmarks_v1";

  function getPageKey() {
    // Use pathname as stable key
    return window.location.pathname;
  }

  function getBookmarks() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    } catch (e) {
      return [];
    }
  }

  function setBookmarks(list) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
  }

  function isBookmarked(key) {
    return getBookmarks().some(x => x.key === key);
  }

  function toggleBookmark() {
    const key = getPageKey();
    const title = document.title || key;
    const url = window.location.href;

    const current = getBookmarks();
    const idx = current.findIndex(x => x.key === key);

    if (idx >= 0) {
      current.splice(idx, 1);
      setBookmarks(current);
      return false;
    } else {
      current.unshift({ key, title, url, ts: Date.now() });
      // Keep it tidy
      setBookmarks(current.slice(0, 200));
      return true;
    }
  }

  async function copyLink() {
    const url = window.location.href;
    try {
      await navigator.clipboard.writeText(url);
      toast("Link copied");
    } catch (e) {
      // Fallback
      const temp = document.createElement("input");
      temp.value = url;
      document.body.appendChild(temp);
      temp.select();
      document.execCommand("copy");
      document.body.removeChild(temp);
      toast("Link copied");
    }
  }

  function toast(msg) {
    // Simple toast (doesn't depend on Material internals)
    const el = document.createElement("div");
    el.textContent = msg;
    el.style.position = "fixed";
    el.style.bottom = "18px";
    el.style.right = "18px";
    el.style.background = "rgba(17,17,17,0.92)";
    el.style.color = "#fff";
    el.style.padding = "10px 12px";
    el.style.borderRadius = "10px";
    el.style.zIndex = "99999";
    el.style.fontSize = "13px";
    el.style.boxShadow = "0 10px 26px rgba(0,0,0,0.25)";
    document.body.appendChild(el);

    setTimeout(() => {
      el.style.transition = "opacity 180ms ease";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 200);
    }, 1100);
  }

function shareWhatsApp() {
  const url = window.location.href;
  const titleEl = document.querySelector("h1");
  const title = titleEl ? titleEl.innerText.trim() : document.title;
  const text = encodeURIComponent(`${title}\n${url}`);

  // Try app scheme first
  const appUrl = `whatsapp://send?text=${text}`;
  const webUrl = `https://wa.me/?text=${text}`;

  // Open app link in same tab (best chance to trigger app)
  window.location.href = appUrl;

  // If nothing happens, fallback to web after a short delay
  setTimeout(() => {
    window.open(webUrl, "_blank", "noopener,noreferrer");
  }, 400);
}
  function shareEmail() {
    const subject = encodeURIComponent(document.title || "Uganda Clinical Guidelines 2023");
    const body = encodeURIComponent(`Link:\n${window.location.href}`);
    window.location.href = `mailto:?subject=${subject}&body=${body}`;
  }

  function mount() {
    // Prevent duplicates on Material instant navigation
    if (document.querySelector(".ucg-fab")) return;

    const fab = document.createElement("div");
    fab.className = "ucg-fab";

    const btnBookmark = document.createElement("button");
    btnBookmark.type = "button";
    btnBookmark.setAttribute("data-tip", "Bookmark");
    btnBookmark.innerHTML = `<span class="ucg-ico">⭐</span>`;
    btnBookmark.addEventListener("click", () => {
      const state = toggleBookmark();
      btnBookmark.setAttribute("aria-pressed", state ? "true" : "false");
      toast(state ? "Bookmarked" : "Bookmark removed");
    });

    const btnCopy = document.createElement("button");
    btnCopy.type = "button";
    btnCopy.setAttribute("data-tip", "Copy link");
    btnCopy.innerHTML = `<span class="ucg-ico">🔗</span>`;
    btnCopy.addEventListener("click", copyLink);

    const btnWA = document.createElement("button");
    btnWA.type = "button";
    btnWA.setAttribute("data-tip", "Share WhatsApp");
    btnWA.innerHTML = `<span class="ucg-ico">💬</span>`;
    btnWA.addEventListener("click", shareWhatsApp);

    const btnMail = document.createElement("button");
    btnMail.type = "button";
    btnMail.setAttribute("data-tip", "Share email");
    btnMail.innerHTML = `<span class="ucg-ico">✉️</span>`;
    btnMail.addEventListener("click", shareEmail);

    // initial bookmark state
    btnBookmark.setAttribute("aria-pressed", isBookmarked(getPageKey()) ? "true" : "false");

    fab.appendChild(btnBookmark);
    fab.appendChild(btnCopy);
    fab.appendChild(btnWA);
    fab.appendChild(btnMail);

    document.body.appendChild(fab);
  }

  // Material for MkDocs uses instant navigation (AJAX)
  // This event fires after each page change.
  document.addEventListener("DOMContentLoaded", mount);
  document.addEventListener("DOMContentSwitch", mount);
  document.addEventListener("DOMContentLoaded", () => {
    // fallback for some builds
    setTimeout(mount, 300);
  });

  // MkDocs Material specific hook (safe even if not present)
  if (window.document$) {
    window.document$.subscribe(mount);
  }
})();