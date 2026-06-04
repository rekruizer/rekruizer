(function () {
  var METRIKA_ID = 109393654;
  var COOKIE_NOTICE_KEY = "denis-cookie-notice-v1";

  function renderHeader() {
    var mounts = document.querySelectorAll("[data-site-header]");
    mounts.forEach(function (mount) {
      mount.outerHTML = [
        '<header>',
        '  <a class="brand" href="/">',
        '    <span class="mark">D</span>',
        '    <span>Денис Пучков</span>',
        '  </a>',
        '  <nav aria-label="Навигация">',
        '    <a href="/services/">Услуги</a>',
        '    <a href="/notes/">Полезное</a>',
        '    <a href="https://dikidi.net/massages" data-goal="online_booking_click">Онлайн-запись</a>',
        '  </nav>',
        '</header>'
      ].join("");
    });
  }

  function renderFooter() {
    var mounts = document.querySelectorAll("[data-site-footer]");
    var year = new Date().getFullYear();
    mounts.forEach(function (mount) {
      mount.outerHTML = [
        '<footer>',
        '  <span>© ' + year + ' Денис Пучков</span>',
        '  <span class="footer-links">',
        '    <a href="/privacy/">Политика конфиденциальности</a>',
        '    <span>denisyuce.com</span>',
        '  </span>',
        '</footer>'
      ].join("");
    });
  }

  function initMetrika() {
    if (window.ym && window.ym.__denisMetrikaLoaded) return;

    (function (m, e, t, r, i, k, a) {
      m[i] = m[i] || function () { (m[i].a = m[i].a || []).push(arguments); };
      m[i].l = 1 * new Date();
      for (var j = 0; j < document.scripts.length; j++) {
        if (document.scripts[j].src === r) return;
      }
      k = e.createElement(t);
      a = e.getElementsByTagName(t)[0];
      k.async = 1;
      k.src = r;
      a.parentNode.insertBefore(k, a);
    })(window, document, "script", "https://mc.yandex.ru/metrika/tag.js?id=" + METRIKA_ID, "ym");

    window.ym.__denisMetrikaLoaded = true;
    window.ym(METRIKA_ID, "init", {
      ssr: true,
      clickmap: true,
      referrer: document.referrer,
      url: location.href,
      accurateTrackBounce: true,
      trackLinks: true
    });
  }

  function reachGoal(goalName) {
    if (!goalName || typeof window.ym !== "function") return;
    window.ym(METRIKA_ID, "reachGoal", goalName);
  }

  function detectGoal(link) {
    var explicit = link.getAttribute("data-goal");
    if (explicit) return explicit;

    var href = link.getAttribute("href") || "";
    if (href.indexOf("dikidi.net") !== -1) return "online_booking_click";
    if (href.indexOf("t.me/massage_yuce") !== -1) return "telegram_click";
    if (href.indexOf("wa.me/79951568066") !== -1) return "whatsapp_click";
    if (href.indexOf("vk.com/massage_yuce") !== -1) return "vk_click";
    if (href.indexOf("instagram.com/denisyuce") !== -1) return "instagram_click";
    if (href === "/notes/massage-income-calculator/" || href.indexOf("/notes/massage-income-calculator/") === 0) return "calculator_open";
    if (href === "/quizzes/" || href.indexOf("/quizzes/") === 0) return "quiz_open";
    if (href === "/muscles/" || href.indexOf("/muscles/") === 0) return "muscles_open";

    return "";
  }

  function initGoalTracking() {
    document.addEventListener("click", function (event) {
      var link = event.target.closest && event.target.closest("a[href]");
      if (link) {
        reachGoal(detectGoal(link));
        return;
      }

      var serviceRow = event.target.closest && event.target.closest(".price-line[data-service-url]");
      if (serviceRow) {
        window.location.href = serviceRow.getAttribute("data-service-url");
      }
    });
  }



  function initMuscleSearch() {
    var input = document.querySelector("[data-muscle-search]");
    var directory = document.querySelector(".muscle-directory");
    if (!input || !directory) return;

    var cards = Array.prototype.slice.call(directory.querySelectorAll(".muscle-list a"));
    var letters = Array.prototype.slice.call(directory.querySelectorAll(".muscle-letter"));
    var empty = document.querySelector("[data-muscle-empty]");

    function normalize(value) {
      return (value || "").toLowerCase().replace(/ё/g, "е").trim();
    }

    function applyFilter() {
      var query = normalize(input.value);
      var visibleCount = 0;

      cards.forEach(function (card) {
        var isVisible = !query || normalize(card.textContent).indexOf(query) !== -1;
        card.hidden = !isVisible;
        if (isVisible) visibleCount += 1;
      });

      letters.forEach(function (letter) {
        var hasVisible = Array.prototype.some.call(letter.querySelectorAll(".muscle-list a"), function (card) {
          return !card.hidden;
        });
        letter.hidden = !hasVisible;
      });

      if (empty) empty.hidden = visibleCount !== 0;
    }

    input.addEventListener("input", applyFilter);
    applyFilter();
  }

  function initLectureToc() {
    if (!document.body.classList.contains("muscle-page")) return;

    var article = document.querySelector(".muscle-article");
    if (!article) return;

    var sourceToc = article.querySelector("#tocmenu");
    var tocLinks = [];

    if (sourceToc) {
      tocLinks = Array.prototype.slice.call(sourceToc.querySelectorAll("a[href^='#']"))
        .map(function (link) {
          return {
            href: link.getAttribute("href"),
            text: (link.textContent || "").trim()
          };
        })
        .filter(function (item) {
          if (!item.href || item.href === "#nachalo" || !item.text) return false;
          try { return !!document.getElementById(decodeURIComponent(item.href.slice(1))); }
          catch (e) { return !!document.getElementById(item.href.slice(1)); }
        });

      var tocWrap = sourceToc.closest("div");
      if (tocWrap && article.contains(tocWrap)) {
        tocWrap.remove();
      } else {
        sourceToc.remove();
      }
    }

    if (!tocLinks.length) {
      tocLinks = Array.prototype.slice.call(article.querySelectorAll("h2[id], h3[id]"))
        .map(function (heading) {
          return {
            href: "#" + heading.id,
            text: (heading.textContent || "").trim()
          };
        })
        .filter(function (item) { return item.text; });
    }

    var shell = document.createElement("div");
    shell.className = "lecture-shell";
    article.parentNode.insertBefore(shell, article);
    shell.appendChild(article);

    if (!tocLinks.length) return;

    var aside = document.createElement("aside");
    aside.className = "lecture-toc";
    aside.setAttribute("aria-label", "Содержание лекции");
    aside.innerHTML = [
      '<div class="lecture-toc__label">В этой лекции</div>',
      '<nav class="lecture-toc__nav"></nav>'
    ].join("");

    var nav = aside.querySelector("nav");
    tocLinks.forEach(function (item) {
      var a = document.createElement("a");
      a.href = item.href;
      a.textContent = item.text;
      nav.appendChild(a);
    });

    shell.appendChild(aside);

    var tocAnchors = Array.prototype.slice.call(nav.querySelectorAll("a"));
    var headings = tocAnchors
      .map(function (link) {
        try { return document.getElementById(decodeURIComponent(link.hash.slice(1))); }
        catch (e) { return document.getElementById(link.hash.slice(1)); }
      })
      .filter(Boolean);

    function setActive(id) {
      tocAnchors.forEach(function (link) {
        link.classList.toggle("is-active", link.hash === "#" + id);
      });
    }

    if (headings.length) setActive(headings[0].id);

    var observer = new IntersectionObserver(function (entries) {
      var visible = entries
        .filter(function (entry) { return entry.isIntersecting; })
        .sort(function (a, b) { return a.boundingClientRect.top - b.boundingClientRect.top; });

      if (visible[0]) setActive(visible[0].target.id);
    }, {
      rootMargin: "-18% 0px -68% 0px",
      threshold: [0, 1]
    });

    headings.forEach(function (heading) { observer.observe(heading); });
  }

  function initCookieNotice() {
    try {
      if (localStorage.getItem(COOKIE_NOTICE_KEY) === "accepted") return;
    } catch (e) {}

    var banner = document.createElement("div");
    banner.className = "cookie-notice";
    banner.setAttribute("role", "status");
    banner.innerHTML = [
      '<div class="cookie-notice__text">',
      '  Мы используем Яндекс Метрику и cookies, чтобы понимать, как работает сайт и какие материалы полезны.',
      '  <a href="/privacy/">Политика конфиденциальности</a>',
      '</div>',
      '<button class="cookie-notice__button" type="button">Понятно</button>'
    ].join("");

    banner.querySelector("button").addEventListener("click", function () {
      try { localStorage.setItem(COOKIE_NOTICE_KEY, "accepted"); } catch (e) {}
      banner.classList.add("is-hidden");
      window.setTimeout(function () { banner.remove(); }, 220);
    });

    document.body.appendChild(banner);
  }

  renderHeader();
  renderFooter();
  initMetrika();
  initGoalTracking();
  initLectureToc();
  initMuscleSearch();
  initCookieNotice();
})();
