# Scripts

Small Python utilities for this static site. Run from repo root unless noted.

| Script | Purpose |
|--------|---------|
| [`apply_mega_nav.py`](apply_mega_nav.py) | Replace legacy flat `<nav class="nav-links">` with the mega-menu block, and ensure `nav-dropdown.css` / `nav-dropdown.js` are linked (with correct `../` depth). The `NAV` string inside is the **template** for the shared header�edit there, then re-run against pages that still use the old markup, or use as reference for manual merges. |
| [`render_feature_blog_series.py`](render_feature_blog_series.py) | Generate the long-form **feature series** blog HTML under `blog/<slug>/index.html` from the `SERIES_ORDER` list and embedded templates. Use when adding or regenerating those articles. |
| [`fix_static_dir_urls.py`](fix_static_dir_urls.py) | Rewrite internal links that end with a **trailing slash** to explicit `.../index.html` so S3 + CloudFront (REST origin) return 200 instead of 404. Safe to re-run; skips external URLs, hash-only links, and paths whose last segment looks like a file. |

**Python:** 3.10+ recommended (`from __future__ import annotations` where used).
