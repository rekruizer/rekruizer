# Service image sources

This directory contains the canonical PNG sources for service images. It lives
under `assets/source/` to keep image inputs close to the generated public
assets without mixing the two.

- `site/` contains clean images without duration labels.
- `catalog/` contains duration-specific images used by Yandex and Meta feeds.
- `tools/convert-service-images.py` converts every PNG here to a same-named
  WebP file in `assets/services/` at quality 82.
- GitHub Actions runs that conversion before validating and rendering the site.
- The PNG sources are excluded from the published GitHub Pages artifact.
- Meta images are generated separately from the catalogue WebP files as
  optimized 1200x1200 PNG derivatives.

New PNG files must use lowercase kebab-case names. Names must be unique across
the `site/` and `catalog/` directories.
