(function () {
  const nav = document.querySelector("[data-nav]");
  const toggle = document.querySelector("[data-nav-toggle]");
  if (nav && toggle) {
    toggle.addEventListener("click", function () {
      const open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  const cardRoot = document.querySelector("[data-chronicle-cards]");
  if (cardRoot) {
    const cards = Array.from(cardRoot.querySelectorAll("[data-card]"));
    const search = cardRoot.querySelector("[data-card-search]");
    const chips = Array.from(cardRoot.querySelectorAll("[data-energy-chip]"));
    const live = cardRoot.querySelector("[data-card-count]");
    const empty = cardRoot.querySelector("[data-card-empty]");
    let energy = "all";

    function applyCards() {
      const q = ((search && search.value) || "").trim().toLowerCase();
      let shown = 0;
      cards.forEach(function (el) {
        const hay = (el.getAttribute("data-search") || "").toLowerCase();
        const okQ = !q || hay.includes(q);
        const okE = energy === "all" || el.getAttribute("data-energy") === energy;
        const visible = okQ && okE;
        el.hidden = !visible;
        if (visible) shown += 1;
      });
      chips.forEach(function (chip) {
        chip.setAttribute("aria-pressed", chip.value === energy ? "true" : "false");
      });
      if (live) {
        live.textContent = "当前显示 " + shown + " / " + cards.length + " 张";
      }
      if (empty) empty.hidden = shown !== 0;
    }

    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        energy = chip.value || "all";
        applyCards();
      });
    });
    if (search) {
      search.addEventListener("input", applyCards);
    }
    applyCards();
  }

  const root = document.querySelector("[data-archive]");
  if (!root) return;

  const items = Array.from(root.querySelectorAll("[data-item]"));
  const search = root.querySelector("[data-search]");
  const category = root.querySelector("[data-filter-category]");
  const year = root.querySelector("[data-filter-year]");
  const visibility = root.querySelector("[data-filter-visibility]");
  const language = root.querySelector("[data-filter-language]");
  const demo = root.querySelector("[data-filter-demo]");
  const live = root.querySelector("[data-count]");
  const empty = root.querySelector("[data-empty]");

  function setCategoryFromHash() {
    const key = decodeURIComponent((location.hash || "").replace("#", ""));
    if (!key || !category) return;
    const exists = Array.prototype.some.call(category.options, function (opt) {
      return opt.value === key;
    });
    if (exists) category.value = key;
  }

  function apply() {
    const q = (search && search.value || "").trim().toLowerCase();
    const cat = category && category.value || "all";
    const yr = year && year.value || "all";
    const vis = visibility && visibility.value || "all";
    const lang = language && language.value || "all";
    const hasDemo = demo && demo.value || "all";
    let shown = 0;

    items.forEach(function (el) {
      const hay = (el.getAttribute("data-search") || "").toLowerCase();
      const okQ = !q || hay.includes(q);
      const okCat = cat === "all" || el.getAttribute("data-category") === cat;
      const okYear = yr === "all" || el.getAttribute("data-year") === yr;
      const okVis =
        vis === "all" ||
        (vis === "public" && el.getAttribute("data-private") === "0") ||
        (vis === "private" && el.getAttribute("data-private") === "1");
      const okLang = lang === "all" || el.getAttribute("data-language") === lang;
      const okDemo =
        hasDemo === "all" ||
        (hasDemo === "yes" && el.getAttribute("data-demo") === "1") ||
        (hasDemo === "no" && el.getAttribute("data-demo") === "0");
      const visible = okQ && okCat && okYear && okVis && okLang && okDemo;
      el.hidden = !visible;
      if (visible) shown += 1;
    });

    if (live) {
      live.textContent = "当前显示 " + shown + " / " + items.length + " 条";
    }
    if (empty) empty.hidden = shown !== 0;
  }

  [search, category, year, visibility, language, demo].forEach(function (el) {
    if (!el) return;
    el.addEventListener("input", apply);
    el.addEventListener("change", apply);
  });

  window.addEventListener("hashchange", function () {
    setCategoryFromHash();
    apply();
  });
  setCategoryFromHash();
  apply();
})();
