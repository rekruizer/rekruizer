(function () {
  "use strict";

  function initReview() {
    var rating = document.querySelector(".rating");
    var stars = Array.prototype.slice.call(document.querySelectorAll("[data-rating]"));
    var stages = Array.prototype.slice.call(document.querySelectorAll("[data-stage]"));
    var reviewLinks = Array.prototype.slice.call(document.querySelectorAll("[data-review-url]"));

    if (!rating || !stars.length || !stages.length) return;

    reviewLinks.forEach(function (link) {
      var url = link.dataset.reviewUrl.trim();
      link.hidden = !url;

      if (url) {
        link.href = url;
      } else {
        link.removeAttribute("href");
      }
    });

    function paint(value, className) {
      stars.forEach(function (star) {
        star.classList.toggle(className, Number(star.dataset.rating) <= value);
      });
    }

    function clearPreview() {
      stars.forEach(function (star) {
        star.classList.remove("is-preview");
      });
    }

    function showStage(name) {
      stages.forEach(function (stage) {
        var isTarget = stage.dataset.stage === name;
        stage.classList.remove("is-active");
        stage.hidden = !isTarget;

        if (isTarget) {
          window.requestAnimationFrame(function () {
            stage.classList.add("is-active");
          });
        }
      });
    }

    function selectRating(value) {
      clearPreview();
      paint(value, "is-selected");

      stars.forEach(function (star) {
        star.setAttribute(
          "aria-checked",
          Number(star.dataset.rating) === value ? "true" : "false"
        );
      });

      window.setTimeout(function () {
        if (value <= 3) {
          showStage("feedback");
        } else {
          showStage("platforms");
        }
      }, 120);
    }

    function resetRating() {
      clearPreview();
      stars.forEach(function (star) {
        star.classList.remove("is-selected");
        star.setAttribute("aria-checked", "false");
      });
      showStage("rating");
    }

    rating.addEventListener("click", function (event) {
      var star = event.target.closest("[data-rating]");
      if (!star || !rating.contains(star)) return;
      selectRating(Number(star.dataset.rating));
    });

    rating.addEventListener("mouseover", function (event) {
      var star = event.target.closest("[data-rating]");
      if (star) paint(Number(star.dataset.rating), "is-preview");
    });

    rating.addEventListener("mouseleave", clearPreview);

    rating.addEventListener("focusin", function (event) {
      var star = event.target.closest("[data-rating]");
      if (star) paint(Number(star.dataset.rating), "is-preview");
    });

    rating.addEventListener("focusout", function (event) {
      if (!rating.contains(event.relatedTarget)) clearPreview();
    });

    document.querySelectorAll("[data-back]").forEach(function (button) {
      button.addEventListener("click", resetRating);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initReview, { once: true });
  } else {
    initReview();
  }
})();
