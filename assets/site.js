(function () {
  var METRIKA_ID = 109393654;
  var COOKIE_NOTICE_KEY = "denis-cookie-notice-v1";

  function renderHeader() {
    var mounts = document.querySelectorAll("[data-site-header]");
    mounts.forEach(function (mount) {
      mount.outerHTML = [
        '<header class="site-header">',
        '  <a class="brand" href="/">',
        '    <span class="mark">D</span>',
        '    <span>Денис Пучков</span>',
        '  </a>',
        '  <nav class="site-nav" aria-label="Навигация">',
        '    <a href="/services/">Услуги</a>',
        '    <a href="/notes/">Полезное</a>',
        '    <a class="site-nav__booking" href="https://dikidi.net/massages" data-goal="online_booking_click">Онлайн-запись</a>',
        '  </nav>',
        '  <button class="mobile-menu-toggle" type="button" aria-label="Открыть меню" aria-expanded="false" aria-controls="mobile-menu">',
        '    <span></span><span></span>',
        '  </button>',
        '  <div class="mobile-menu" id="mobile-menu" aria-hidden="true" inert>',
        '    <div class="mobile-menu__top">',
        '      <a class="brand" href="/">',
        '        <span class="mark">D</span>',
        '        <span>Денис Пучков</span>',
        '      </a>',
        '      <button class="mobile-menu__close" type="button" aria-label="Закрыть меню"><span></span><span></span></button>',
        '    </div>',
        '    <div class="mobile-menu__content">',
        '      <nav class="mobile-menu__nav" aria-label="Мобильная навигация">',
        '        <a href="/">Главная</a>',
        '        <a href="/services/">Услуги</a>',
        '        <a href="/notes/">Полезное</a>',
        '        <a href="/muscles/">База мышц</a>',
        '        <a href="/quizzes/">Тесты</a>',
        '      </nav>',
        '    </div>',
        '    <div class="mobile-menu__bottom">',
        '      <div class="mobile-menu__contact">',
        '        <a class="mobile-menu__phone" href="tel:+79951568066">+7 (995) 156-80-66</a>',
        '        <a class="mobile-menu__address" href="https://yandex.ru/maps/org/159539374930" target="_blank" rel="noopener noreferrer" data-goal="yandex_maps_route_click">Москва, Рублёвское шоссе 34к2</a>',
        '      </div>',
        '      <span class="mobile-menu__social footer-social" aria-label="Соцсети">',
        renderSocialLinks(),
        '      </span>',
        '      <a class="button primary mobile-menu__cta" href="https://dikidi.net/massages" data-goal="online_booking_click">Записаться</a>',
        '    </div>',
        '  </div>',
        '</header>'
      ].join("");
    });
  }

  function initMobileMenu() {
    var toggle = document.querySelector(".mobile-menu-toggle");
    var menu = document.querySelector(".mobile-menu");
    if (!toggle || !menu) return;

    var close = menu.querySelector(".mobile-menu__close");
    var links = menu.querySelectorAll("a");

    menu.setAttribute("inert", "");

    function setOpen(isOpen) {
      document.body.classList.toggle("mobile-menu-open", isOpen);
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
      menu.setAttribute("aria-hidden", isOpen ? "false" : "true");
      if (isOpen) {
        menu.removeAttribute("inert");
      } else {
        menu.setAttribute("inert", "");
      }
    }

    toggle.addEventListener("click", function () { setOpen(true); });
    if (close) close.addEventListener("click", function () { setOpen(false); });
    links.forEach(function (link) {
      link.addEventListener("click", function () { setOpen(false); });
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") setOpen(false);
    });
  }

  var SOCIAL_LINKS = [
      {
        label: "Instagram",
        href: "https://instagram.com/denisyuce",
        path: "M13.0281 2.00073C14.1535 2.00259 14.7238 2.00855 15.2166 2.02322L15.4107 2.02956C15.6349 2.03753 15.8561 2.04753 16.1228 2.06003C17.1869 2.1092 17.9128 2.27753 18.5503 2.52503C19.2094 2.7792 19.7661 3.12253 20.3219 3.67837C20.8769 4.2342 21.2203 4.79253 21.4753 5.45003C21.7219 6.0867 21.8903 6.81337 21.9403 7.87753C21.9522 8.1442 21.9618 8.3654 21.9697 8.58964L21.976 8.78373C21.9906 9.27647 21.9973 9.84686 21.9994 10.9723L22.0002 11.7179C22.0003 11.809 22.0003 11.903 22.0003 12L22.0002 12.2821L21.9996 13.0278C21.9977 14.1532 21.9918 14.7236 21.9771 15.2163L21.9707 15.4104C21.9628 15.6347 21.9528 15.8559 21.9403 16.1225C21.8911 17.1867 21.7219 17.9125 21.4753 18.55C21.2211 19.2092 20.8769 19.7659 20.3219 20.3217C19.7661 20.8767 19.2069 21.22 18.5503 21.475C17.9128 21.7217 17.1869 21.89 16.1228 21.94C15.8561 21.9519 15.6349 21.9616 15.4107 21.9694L15.2166 21.9757C14.7238 21.9904 14.1535 21.997 13.0281 21.9992L12.2824 22C12.1913 22 12.0973 22 12.0003 22L11.7182 22L10.9725 21.9993C9.8471 21.9975 9.27672 21.9915 8.78397 21.9768L8.58989 21.9705C8.36564 21.9625 8.14444 21.9525 7.87778 21.94C6.81361 21.8909 6.08861 21.7217 5.45028 21.475C4.79194 21.2209 4.23444 20.8767 3.67861 20.3217C3.12278 19.7659 2.78028 19.2067 2.52528 18.55C2.27778 17.9125 2.11028 17.1867 2.06028 16.1225C2.0484 15.8559 2.03871 15.6347 2.03086 15.4104L2.02457 15.2163C2.00994 14.7236 2.00327 14.1532 2.00111 13.0278L2.00098 10.9723C2.00284 9.84686 2.00879 9.27647 2.02346 8.78373L2.02981 8.58964C2.03778 8.3654 2.04778 8.1442 2.06028 7.87753C2.10944 6.81253 2.27778 6.08753 2.52528 5.45003C2.77944 4.7917 3.12278 4.2342 3.67861 3.67837C4.23444 3.12253 4.79278 2.78003 5.45028 2.52503C6.08778 2.27753 6.81278 2.11003 7.87778 2.06003C8.14444 2.04816 8.36564 2.03847 8.58989 2.03062L8.78397 2.02433C9.27672 2.00969 9.8471 2.00302 10.9725 2.00086L13.0281 2.00073ZM12.0003 7.00003C9.23738 7.00003 7.00028 9.23956 7.00028 12C7.00028 14.7629 9.23981 17 12.0003 17C14.7632 17 17.0003 14.7605 17.0003 12C17.0003 9.23713 14.7607 7.00003 12.0003 7.00003ZM12.0003 9.00003C13.6572 9.00003 15.0003 10.3427 15.0003 12C15.0003 13.6569 13.6576 15 12.0003 15C10.3434 15 9.00028 13.6574 9.00028 12C9.00028 10.3431 10.3429 9.00003 12.0003 9.00003ZM17.2503 5.50003C16.561 5.50003 16.0003 6.05994 16.0003 6.74918C16.0003 7.43843 16.5602 7.9992 17.2503 7.9992C17.9395 7.9992 18.5003 7.4393 18.5003 6.74918C18.5003 6.05994 17.9386 5.49917 17.2503 5.50003Z"
      },
      {
        label: "Telegram",
        href: "https://t.me/+79951568066",
        path: "M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12ZM12.3584 9.38246C11.3857 9.78702 9.4418 10.6244 6.5266 11.8945C6.05321 12.0827 5.80524 12.2669 5.78266 12.4469C5.74451 12.7513 6.12561 12.8711 6.64458 13.0343C6.71517 13.0565 6.78832 13.0795 6.8633 13.1039C7.37388 13.2698 8.06071 13.464 8.41776 13.4717C8.74164 13.4787 9.10313 13.3452 9.50222 13.0711C12.226 11.2325 13.632 10.3032 13.7203 10.2832C13.7826 10.269 13.8689 10.2513 13.9273 10.3032C13.9858 10.3552 13.98 10.4536 13.9739 10.48C13.9361 10.641 12.4401 12.0318 11.666 12.7515C11.4351 12.9661 11.2101 13.1853 10.9833 13.4039C10.509 13.8611 10.1533 14.204 11.003 14.764C11.8644 15.3317 12.7323 15.8982 13.5724 16.4971C13.9867 16.7925 14.359 17.0579 14.8188 17.0156C15.0861 16.991 15.3621 16.7397 15.5022 15.9903C15.8335 14.2193 16.4847 10.3821 16.6352 8.80083C16.6484 8.6623 16.6318 8.485 16.6185 8.40717C16.6052 8.32934 16.5773 8.21844 16.4762 8.13635C16.3563 8.03913 16.1714 8.01863 16.0887 8.02009C15.7125 8.02672 15.1355 8.22737 12.3584 9.38246Z"
      },
      {
        label: "WhatsApp",
        href: "https://wa.me/79951568066",
        path: "M12.001 2C17.5238 2 22.001 6.47715 22.001 12C22.001 17.5228 17.5238 22 12.001 22C10.1671 22 8.44851 21.5064 6.97086 20.6447L2.00516 22L3.35712 17.0315C2.49494 15.5536 2.00098 13.8345 2.00098 12C2.00098 6.47715 6.47813 2 12.001 2ZM8.59339 7.30019L8.39232 7.30833C8.26293 7.31742 8.13607 7.34902 8.02057 7.40811C7.93392 7.45244 7.85348 7.51651 7.72709 7.63586C7.60774 7.74855 7.53857 7.84697 7.46569 7.94186C7.09599 8.4232 6.89729 9.01405 6.90098 9.62098C6.90299 10.1116 7.03043 10.5884 7.23169 11.0336C7.63982 11.9364 8.31288 12.8908 9.20194 13.7759C9.4155 13.9885 9.62473 14.2034 9.85034 14.402C10.9538 15.3736 12.2688 16.0742 13.6907 16.4482C13.6907 16.4482 14.2507 16.5342 14.2589 16.5347C14.4444 16.5447 14.6296 16.5313 14.8153 16.5218C15.1066 16.5068 15.391 16.428 15.6484 16.2909C15.8139 16.2028 15.8922 16.159 16.0311 16.0714C16.0311 16.0714 16.0737 16.0426 16.1559 15.9814C16.2909 15.8808 16.3743 15.81 16.4866 15.6934C16.5694 15.6074 16.6406 15.5058 16.6956 15.3913C16.7738 15.2281 16.8525 14.9166 16.8838 14.6579C16.9077 14.4603 16.9005 14.3523 16.8979 14.2854C16.8936 14.1778 16.8047 14.0671 16.7073 14.0201L16.1258 13.7587C16.1258 13.7587 15.2563 13.3803 14.7245 13.1377C14.6691 13.1124 14.6085 13.1007 14.5476 13.097C14.4142 13.0888 14.2647 13.1236 14.1696 13.2238C14.1646 13.2218 14.0984 13.279 13.3749 14.1555C13.335 14.2032 13.2415 14.3069 13.0798 14.2972C13.0554 14.2955 13.0311 14.292 13.0074 14.2858C12.9419 14.2685 12.8781 14.2457 12.8157 14.2193C12.692 14.1668 12.6486 14.1469 12.5641 14.1105C11.9868 13.8583 11.457 13.5209 10.9887 13.108C10.8631 12.9974 10.7463 12.8783 10.6259 12.7616C10.2057 12.3543 9.86169 11.9211 9.60577 11.4938C9.5918 11.4705 9.57027 11.4368 9.54708 11.3991C9.50521 11.331 9.45903 11.25 9.44455 11.1944C9.40738 11.0473 9.50599 10.9291 9.50599 10.9291C9.50599 10.9291 9.74939 10.663 9.86248 10.5183C9.97128 10.379 10.0652 10.2428 10.125 10.1457C10.2428 9.95633 10.2801 9.76062 10.2182 9.60963C9.93764 8.92565 9.64818 8.24536 9.34986 7.56894C9.29098 7.43545 9.11585 7.33846 8.95659 7.32007C8.90265 7.31384 8.84875 7.30758 8.79459 7.30402C8.66053 7.29748 8.5262 7.29892 8.39232 7.30833L8.59339 7.30019Z"
      },
      {
        label: "VK",
        href: "https://vk.com/denisyuce",
        path: "M4.26 4.26C3 5.532 3 7.566 3 11.64V12.36C3 16.428 3 18.462 4.26 19.74C5.532 21 7.566 21 11.64 21H12.36C16.428 21 18.462 21 19.74 19.74C21 18.468 21 16.434 21 12.36V11.64C21 7.572 21 5.538 19.74 4.26C18.468 3 16.434 3 12.36 3H11.64C7.572 3 5.538 3 4.26 4.26ZM6.03613 8.47817H8.10013C8.16613 11.9102 9.67813 13.3622 10.8781 13.6622V8.47817H12.8161V11.4362C13.9981 11.3102 15.2461 9.96017 15.6661 8.47217H17.5981C17.4406 9.24243 17.1259 9.97193 16.6737 10.6151C16.2216 11.2582 15.6416 11.8012 14.9701 12.2102C15.7195 12.5831 16.3813 13.1107 16.9118 13.7582C17.4424 14.4056 17.8297 15.1581 18.0481 15.9662H15.9181C15.4621 14.5442 14.3221 13.4402 12.8161 13.2902V15.9662H12.5821H12.5761C8.47213 15.9662 6.13213 13.1582 6.03613 8.47817Z"
      }
    ];


  function renderSocialLinks() {
    return SOCIAL_LINKS.map(function (item) {
      return '    <a href="' + item.href + '" aria-label="' + item.label + '"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="' + item.path + '"></path></svg></a>';
    }).join("");
  }

  function renderFooter() {
    var mounts = document.querySelectorAll("[data-site-footer]");
    var year = new Date().getFullYear();
    var socialHtml = renderSocialLinks();
    var documentLinks = [
      { label: "Противопоказания", href: "/documents/contraindications/" },
      { label: "Политика конфиденциальности", href: "/documents/privacy/" },
      { label: "Правила записи и оказания услуг", href: "/documents/rules/" }
    ];
    var documentsHtml = documentLinks.map(function (item) {
      return '    <a href="' + item.href + '">' + item.label + '</a>';
    }).join("");
    mounts.forEach(function (mount) {
      mount.outerHTML = [
        '<footer>',
        '  <div class="footer-main">',
        '    <div class="footer-brand">',
        '      <a class="brand" href="/">',
        '        <span class="mark">D</span>',
        '        <span>Денис Пучков</span>',
        '      </a>',
        '      <p>Внимательные руки, спокойная голова и массаж, после которого телу легче доверять себе.</p>',
        '    </div>',
        '    <div class="footer-contact">',
        '      <a class="footer-phone" href="tel:+79951568066">+7 (995) 156-80-66</a>',
        '      <span class="footer-social" aria-label="Соцсети">',
        socialHtml,
        '      </span>',
        '    </div>',
        '  </div>',
        '  <div class="footer-bottom">',
        '    <span>© ' + year + ' Денис Пучков</span>',
        '    <nav class="footer-docs" aria-label="Документы">',
        documentsHtml,
        '    </nav>',
        '  </div>',
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
    if (href.indexOf("t.me/+79951568066") !== -1) return "telegram_click";
    if (href.indexOf("wa.me/79951568066") !== -1) return "whatsapp_click";
    if (href.indexOf("vk.com/denisyuce") !== -1) return "vk_click";
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
    var catalog = document.querySelector("[data-muscle-catalog]");
    if (!input || !catalog) return;

    var tabs = Array.prototype.slice.call(catalog.querySelectorAll("[data-muscle-tab]"));
    var panels = Array.prototype.slice.call(catalog.querySelectorAll("[data-muscle-panel]"));
    var empty = document.querySelector("[data-muscle-empty]");
    var activePanel = panels.filter(function (panel) { return !panel.hidden; })[0] || panels[0];

    function normalize(value) {
      return (value || "").toLowerCase().replace(/ё/g, "е").trim();
    }

    function applyFilter() {
      var query = normalize(input.value);
      var panel = activePanel;
      if (!panel) return;

      var cards = Array.prototype.slice.call(panel.querySelectorAll(".muscle-list a"));
      var groups = Array.prototype.slice.call(panel.querySelectorAll("[data-muscle-group]"));
      var visibleCount = 0;

      cards.forEach(function (card) {
        var isVisible = !query || normalize(card.textContent).indexOf(query) !== -1;
        card.hidden = !isVisible;
        if (isVisible) visibleCount += 1;
      });

      groups.forEach(function (group) {
        var visibleLinks = Array.prototype.filter.call(group.querySelectorAll(".muscle-list a"), function (card) {
          return !card.hidden;
        });
        var count = group.querySelector(".muscle-group-head span");
        if (count) count.textContent = String(visibleLinks.length);
        group.hidden = visibleLinks.length === 0;
      });

      if (empty) empty.hidden = visibleCount !== 0;
    }

    function activateMode(mode) {
      tabs.forEach(function (tab) {
        var isActive = tab.getAttribute("data-muscle-tab") === mode;
        tab.classList.toggle("is-active", isActive);
        tab.setAttribute("aria-selected", isActive ? "true" : "false");
      });

      panels.forEach(function (panel) {
        var isActive = panel.getAttribute("data-muscle-panel") === mode;
        panel.hidden = !isActive;
        panel.classList.toggle("is-active", isActive);
        if (isActive) activePanel = panel;
      });

      applyFilter();
    }

    catalog.addEventListener("click", function (event) {
      var tab = event.target.closest && event.target.closest("[data-muscle-tab]");
      if (!tab || !catalog.contains(tab)) return;
      activateMode(tab.getAttribute("data-muscle-tab"));
    });

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
    aside.innerHTML = (document.body.classList.contains("note-lecture-page") ? "" : '<div class="lecture-toc__label">В этой лекции</div>') + '<nav class="lecture-toc__nav"></nav>';

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


  function normalizeVisibleBreadcrumbs() {
    var headings = Array.prototype.slice.call(document.querySelectorAll("h1"));
    var headingText = headings.length ? headings[0].textContent.trim().replace(/\s+/g, " ") : "";
    if (!headingText) return;

    document.querySelectorAll(".breadcrumbs").forEach(function (crumbs) {
      var items = Array.prototype.slice.call(crumbs.children).filter(function (node) {
        return node.matches && (node.matches("a") || node.matches("span"));
      });
      if (!items.length) return;

      var last = items[items.length - 1];
      if (!last.matches("span")) return;

      var lastText = last.textContent.trim().replace(/\s+/g, " ");
      var isCurrentPage = lastText && (
        lastText === headingText ||
        headingText.indexOf(lastText) === 0 ||
        lastText.indexOf(headingText) === 0
      );
      if (!isCurrentPage) return;

      var previous = last.previousElementSibling;
      last.remove();
      if (previous && previous.matches("span") && previous.textContent.trim() === "/") previous.remove();
    });
  }



  var YANDEX_MAPS_API_KEY = "b945c399-6aeb-44f8-9973-bdd99309f45b";

  function loadYandexMapsApi(callback) {
    if (window.ymaps && typeof window.ymaps.ready === "function") {
      callback();
      return;
    }

    var existing = document.getElementById("yandex-maps-api");
    if (existing) {
      existing.addEventListener("load", callback, { once: true });
      return;
    }

    var script = document.createElement("script");
    script.id = "yandex-maps-api";
    script.src = "https://api-maps.yandex.ru/2.1/?apikey=" + encodeURIComponent(YANDEX_MAPS_API_KEY) + "&lang=ru_RU";
    script.async = true;
    script.addEventListener("load", callback, { once: true });
    document.head.appendChild(script);
  }

  function initYandexLocationMap() {
    var container = document.getElementById("yandex-location-map");
    if (!container || container.dataset.mapInitialized === "true") return;
    container.dataset.mapInitialized = "true";
    container.classList.add("is-loading");

    loadYandexMapsApi(function () {
      window.ymaps.ready(function () {
        var coords = [55.749238, 37.419761];
        var map = new window.ymaps.Map(container, {
          center: coords,
          zoom: 13,
          controls: []
        }, {
          suppressMapOpenBlock: true,
          yandexMapDisablePoiInteractivity: true
        });

        map.behaviors.enable(["scrollZoom", "drag", "multiTouch"]);

        var placemark = new window.ymaps.Placemark(coords, {
          hintContent: "Денис Пучков — массаж",
          balloonContent: "Москва, Рублёвское шоссе 34к2, INDI"
        }, {
          preset: "islands#blueDotIcon"
        });

        map.geoObjects.add(placemark);
        container.classList.remove("is-loading");
        container.classList.add("is-ready");
        removeYandexMapPromos(container);
      });
    });
  }

  function initLazyYandexLocationMap() {
    var container = document.getElementById("yandex-location-map");
    if (!container) return;

    if (!("IntersectionObserver" in window)) {
      initYandexLocationMap();
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        observer.disconnect();
        initYandexLocationMap();
      });
    }, { rootMargin: "360px 0px" });

    observer.observe(container);
  }

  function removeYandexMapPromos(container) {
    var hidePromos = function () {
      var nodes = container.querySelectorAll('a, button, [class*="taxi"], [aria-label*="такси" i], [title*="такси" i]');
      nodes.forEach(function (node) {
        var text = (node.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase();
        var className = String(node.className || '').toLowerCase();
        var aria = String(node.getAttribute && (node.getAttribute('aria-label') || '')).toLowerCase();
        var title = String(node.getAttribute && (node.getAttribute('title') || '')).toLowerCase();

        if (
          text.indexOf('доехать на такси') !== -1 ||
          className.indexOf('taxi') !== -1 ||
          aria.indexOf('такси') !== -1 ||
          title.indexOf('такси') !== -1
        ) {
          node.style.setProperty('display', 'none', 'important');
        }
      });
    };

    hidePromos();

    if (window.MutationObserver) {
      var observer = new MutationObserver(hidePromos);
      observer.observe(container, { childList: true, subtree: true });
    }
  }

  function initReviewsCarousel() {
    var viewports = document.querySelectorAll("[data-reviews-viewport]");
    if (!viewports.length) return;

    function formatReviewDate(value) {
      if (!value) return "";

      var normalized = String(value).slice(0, 10);
      var date = new Date(normalized + "T00:00:00Z");
      if (Number.isNaN(date.getTime())) return "";

      try {
        return new Intl.DateTimeFormat("ru-RU", {
          day: "numeric",
          month: "long",
          year: "numeric",
          timeZone: "UTC"
        }).format(date);
      } catch (error) {
        return normalized;
      }
    }

    function createReviewCard(review) {
      var card = document.createElement("article");
      card.className = "review-card";
      card.setAttribute("data-review-api", String(review.source || ""));

      var top = document.createElement("div");
      top.className = "review-top";

      var identity = document.createElement("div");
      var author = document.createElement("h3");
      author.textContent = review.authorName || "Клиент";

      var stars = document.createElement("div");
      var rating = Math.max(0, Math.min(5, parseInt(review.rating, 10) || 0));
      stars.className = "review-stars";
      stars.setAttribute("data-rating", String(rating));
      stars.setAttribute("aria-label", rating + " из 5");

      identity.appendChild(author);
      identity.appendChild(stars);
      top.appendChild(identity);

      var formattedDate = formatReviewDate(review.reviewDate);
      if (formattedDate) {
        var time = document.createElement("time");
        time.dateTime = String(review.reviewDate).slice(0, 10);
        time.textContent = formattedDate;
        top.appendChild(time);
      }

      var text = document.createElement("p");
      text.textContent = review.text || "";

      var source = document.createElement("span");
      source.className = "review-source";
      source.textContent = {
        yandex: "Яндекс",
        avito: "Avito",
        "2gis": "2GIS",
        google: "Google"
      }[review.source] || review.source || "Отзыв";

      card.appendChild(top);
      card.appendChild(text);
      card.appendChild(source);
      return card;
    }

    function prepareReviewCards(root) {
      root.querySelectorAll(".review-card").forEach(function (card) {
        if (card.dataset.reviewPrepared === "true") return;

        var text = card.querySelector("p");
        var source = card.querySelector(".review-source");
        if (!text || !source) return;

        text.classList.add("review-text");

        var footer = document.createElement("div");
        footer.className = "review-footer";
        source.parentNode.insertBefore(footer, source);
        footer.appendChild(source);

        var more = document.createElement("button");
        more.className = "review-more";
        more.type = "button";
        more.textContent = "Читать полностью";
        more.setAttribute("data-review-more", "");
        more.setAttribute("aria-expanded", "false");
        more.hidden = true;
        footer.appendChild(more);

        card.dataset.reviewPrepared = "true";
      });

      root.querySelectorAll(".review-card").forEach(function (card) {
        var text = card.querySelector(".review-text");
        var more = card.querySelector("[data-review-more]");
        if (!text || !more) return;
        if (card.classList.contains("is-expanded")) {
          more.hidden = false;
          return;
        }
        more.hidden = text.scrollHeight <= text.clientHeight + 1;
      });
    }

    function loadRemoteReviews(rail) {
      if (!window.fetch) return Promise.resolve(false);

      return window.fetch("/assets/data/reviews.json", {
        headers: { Accept: "application/json" },
        cache: "no-cache"
      })
        .then(function (response) {
          if (!response.ok) throw new Error("Не удалось загрузить отзывы");
          return response.json();
        })
        .then(function (payload) {
          var reviews = payload && Array.isArray(payload.reviews)
            ? payload.reviews.filter(function (review) {
                return review && review.text && Number(review.rating) >= 4;
              })
            : [];

          if (!reviews.length) return false;

          rail.querySelectorAll("[data-review-api-fallback]").forEach(function (card) {
            card.remove();
          });

          reviews.forEach(function (review) {
            rail.appendChild(createReviewCard(review));
          });

          return true;
        })
        .catch(function () {
          // Если API временно недоступен, посетитель увидит статические отзывы.
          return false;
        });
    }

    function renderStars(root) {
      root.querySelectorAll(".review-stars[data-rating]").forEach(function (stars) {
        var rating = Math.max(0, Math.min(5, parseInt(stars.getAttribute("data-rating"), 10) || 0));
        var html = "";
        for (var i = 1; i <= 5; i += 1) {
          html += '<span class="review-star' + (i > rating ? " is-empty" : "") + '">★</span>';
        }
        stars.innerHTML = html;
        stars.setAttribute("aria-label", rating + " из 5");
      });
    }

    viewports.forEach(function (viewport) {
      var rail = viewport.querySelector("[data-reviews-rail]");
      if (!rail || rail.dataset.carouselReady === "true") return;
      rail.dataset.carouselReady = "loading";

      loadRemoteReviews(rail).then(function () {
        rail.dataset.carouselReady = "true";

        var section = viewport.closest(".reviews-section");
        var prev = section ? section.querySelector("[data-reviews-prev]") : null;
        var next = section ? section.querySelector("[data-reviews-next]") : null;
        var originals = Array.prototype.slice.call(rail.children);
        var originalCount = originals.length;
        if (!originalCount) return;

        renderStars(rail);
        prepareReviewCards(rail);

        var beforeClones = document.createDocumentFragment();
        originals.forEach(function (card) {
          var clone = card.cloneNode(true);
          clone.setAttribute("aria-hidden", "true");
          clone.setAttribute("data-review-clone", "before");
          clone.querySelectorAll("button, a").forEach(function (control) {
            control.tabIndex = -1;
          });
          beforeClones.appendChild(clone);
        });
        rail.insertBefore(beforeClones, rail.firstChild);

        originals.forEach(function (card) {
          var clone = card.cloneNode(true);
          clone.setAttribute("aria-hidden", "true");
          clone.setAttribute("data-review-clone", "after");
          clone.querySelectorAll("button, a").forEach(function (control) {
            control.tabIndex = -1;
          });
          rail.appendChild(clone);
        });

        var slides = Array.prototype.slice.call(rail.children);
        var index = originalCount;
        var scrollEndTimer = null;
        var ignoreScroll = false;

        function updateFade() {
          if (!section) return;
          section.classList.toggle("has-right-fade", originalCount > 1);
        }

        function getOriginalsStart() {
          return slides[originalCount] ? slides[originalCount].offsetLeft : 0;
        }

        function getOriginalsWidth() {
          var firstAfter = slides[originalCount * 2];
          return firstAfter ? firstAfter.offsetLeft - getOriginalsStart() : rail.scrollWidth / 3;
        }

        function normalizeSlideIndex(value) {
          if (value < originalCount) return value + originalCount;
          if (value >= originalCount * 2) return value - originalCount;
          return value;
        }

        function nearestSlideIndex() {
          var current = viewport.scrollLeft;
          var nearest = index;
          var minDistance = Infinity;
          slides.forEach(function (slide, slideIndex) {
            var distance = Math.abs(slide.offsetLeft - current);
            if (distance < minDistance) {
              minDistance = distance;
              nearest = slideIndex;
            }
          });
          return nearest;
        }

        function scrollToOffset(offset, animated) {
          if (viewport.scrollTo) {
            viewport.scrollTo({ left: offset, behavior: animated ? "smooth" : "auto" });
          } else {
            viewport.scrollLeft = offset;
          }
        }

        function jumpToOffset(offset) {
          ignoreScroll = true;
          scrollToOffset(offset, false);
          window.setTimeout(function () { ignoreScroll = false; }, 0);
        }

        function normalizePosition() {
          var originalsStart = getOriginalsStart();
          var originalsWidth = getOriginalsWidth();
          var current = viewport.scrollLeft;

          if (current < originalsStart) {
            current += originalsWidth;
            jumpToOffset(current);
          } else if (current >= originalsStart + originalsWidth) {
            current -= originalsWidth;
            jumpToOffset(current);
          }

          index = normalizeSlideIndex(nearestSlideIndex());
          updateFade();
        }

        function moveTo(nextIndex, animated) {
          index = nextIndex;
          var target = slides[index];
          if (!target) return;
          scrollToOffset(target.offsetLeft, animated);
          updateFade();
          if (!animated) normalizePosition();
        }

        function scheduleNormalize() {
          if (ignoreScroll) return;
          window.clearTimeout(scrollEndTimer);
          scrollEndTimer = window.setTimeout(normalizePosition, 120);
        }

        function goNext() {
          moveTo(index + 1, true);
        }

        function goPrev() {
          moveTo(index - 1, true);
        }

        if (prev) prev.addEventListener("click", goPrev);
        if (next) next.addEventListener("click", goNext);
        viewport.addEventListener("scroll", scheduleNormalize, { passive: true });
        viewport.addEventListener("click", function (event) {
          var more = event.target.closest && event.target.closest("[data-review-more]");
          if (!more || !viewport.contains(more)) return;
          var card = more.closest(".review-card");
          if (!card) return;

          var expanded = !card.classList.contains("is-expanded");
          card.classList.toggle("is-expanded", expanded);
          more.textContent = expanded ? "Свернуть" : "Читать полностью";
          more.setAttribute("aria-expanded", expanded ? "true" : "false");
        });

        window.addEventListener("resize", function () {
          prepareReviewCards(rail);
          moveTo(normalizeSlideIndex(index), false);
        });

        moveTo(index, false);
        window.setTimeout(normalizePosition, 0);
      });
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
      '  <a href="/documents/privacy/">Политика конфиденциальности</a>',
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
  initMobileMenu();
  initMetrika();
  initGoalTracking();
  normalizeVisibleBreadcrumbs();
  initLectureToc();
  initMuscleSearch();
  initReviewsCarousel();
  initCookieNotice();
  initLazyYandexLocationMap();
})();
