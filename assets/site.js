(function () {
  var METRIKA_ID = 109393654;
  var COOKIE_NOTICE_KEY = "denis-cookie-notice-v1";

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
  var globalWindow = /** @type {any} */ (window);

  function loadYandexMapsApi(callback) {
    if (globalWindow.ymaps && typeof globalWindow.ymaps.ready === "function") {
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
      globalWindow.ymaps.ready(function () {
        var coords = [55.749238, 37.419761];
        var map = new globalWindow.ymaps.Map(container, {
          center: coords,
          zoom: 13,
          controls: []
        }, {
          suppressMapOpenBlock: true,
          yandexMapDisablePoiInteractivity: true
        });

        map.behaviors.enable(["scrollZoom", "drag", "multiTouch"]);

        var placemark = new globalWindow.ymaps.Placemark(coords, {
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

    function formatReviewAuthorName(value) {
      var normalized = String(value || "").trim().replace(/\s+/g, " ");
      if (!normalized) return "Клиент";

      return normalized.split(" ").map(function (word) {
        return word.split(/([-’'])/).map(function (part) {
          if (!part || part === "-" || part === "’" || part === "'") return part;

          var withoutInitialDot = part.length === 2 && part.charAt(1) === "."
            ? part.charAt(0)
            : part;

          return withoutInitialDot.charAt(0).toLocaleUpperCase("ru-RU") +
            withoutInitialDot.slice(1).toLocaleLowerCase("ru-RU");
        }).join("");
      }).join(" ");
    }

    function createReviewCard(review) {
      var card = document.createElement("article");
      card.className = "review-card";
      card.setAttribute("data-review-api", String(review.source || ""));

      var top = document.createElement("div");
      top.className = "review-top";

      var identity = document.createElement("div");
      var author = document.createElement("h3");
      author.textContent = formatReviewAuthorName(review.authorName);

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
        var author = card.querySelector(".review-top h3");
        if (author) author.textContent = formatReviewAuthorName(author.textContent);

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

    async function loadRemoteReviews(rail) {
      if (!window.fetch) return false;

      try {
        var response = await window.fetch("/assets/data/reviews.json", {
          headers: { Accept: "application/json" },
          cache: "no-cache"
        });
        if (!response.ok) throw new Error("Не удалось загрузить отзывы");
        var payload = await response.json();
        var reviews = payload && Array.isArray(payload.reviews)
          ? payload.reviews.filter(function (review) {
              return review && review.text && Number(review.rating) >= 4;
            }).sort(function (a, b) {
              var aTime = Date.parse(a.reviewDate || "") || 0;
              var bTime = Date.parse(b.reviewDate || "") || 0;
              return bTime - aTime;
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
      } catch (_error) {
        // Если файл временно недоступен, посетитель увидит статические отзывы.
        return false;
      }
    }

    function sortReviewCardsByDate(root) {
      Array.prototype.slice.call(root.children)
        .map(function (card, position) {
          var time = card.querySelector("time[datetime]");
          return {
            card: card,
            position: position,
            timestamp: time ? Date.parse(time.getAttribute("datetime")) || 0 : 0
          };
        })
        .sort(function (a, b) {
          return b.timestamp - a.timestamp || a.position - b.position;
        })
        .forEach(function (item) {
          root.appendChild(item.card);
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

        sortReviewCardsByDate(rail);

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
