# Scripts

Small Python utilities for this static site. Run from repo root unless noted.

| Script | Purpose |
|--------|---------|
| [`apply_mega_nav.py`](apply_mega_nav.py) | Replace legacy flat `<nav class="nav-links">` with the mega-menu block, and ensure `nav-dropdown.css` / `nav-dropdown.js` are linked (with correct `../` depth). The `NAV` string inside is the **template** for the shared header�edit there, then re-run against pages that still use the old markup, or use as reference for manual merges. |
| [`render_feature_blog_series.py`](render_feature_blog_series.py) | Generate the long-form **feature series** blog HTML under `blog/<slug>/index.html` from the `SERIES_ORDER` list and embedded templates. Use when adding or regenerating those articles. |
| [`clean_index_html_urls.py`](clean_index_html_urls.py) | Normalize links/canonicals/sitemap from `.../index.html` to clean directory URLs (`/blog/`, `/product/`, …). Preferred for the current gunicorn + nginx deploy. |
| [`fix_static_dir_urls.py`](fix_static_dir_urls.py) | **Legacy / S3-only:** rewrite trailing-slash URLs *to* `.../index.html`. Do **not** run this against the live nginx+gunicorn site. |

**Python:** 3.10+ recommended (`from __future__ import annotations` where used).
