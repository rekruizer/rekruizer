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
  initCookieNotice();
})();
