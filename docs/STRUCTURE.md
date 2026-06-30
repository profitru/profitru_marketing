# Profitru-Marketing repository structure

This repo is a **multi-page static site** (no bundler in the default workflow). The **document root for production** is the **repository root**: paths like `/blog/foo/`, `/policies/privacy-policy.html`, and `/amazon-profit-calculator/` must keep working for SEO and bookmarks. Refactors that move HTML under a new top-level folder (e.g. `public/`) require **updating every link, canonical tag, `sitemap.xml`, nginx config, and any CDN rules**�or a build step that **outputs the same URL shape**.

## What gets deployed

Upload (or sync) **the whole tree** that serves static files, not only `index.html`. At minimum the deploy bundle includes:

| Path | Role |
|------|------|
| `index.html` | Homepage |
| `contact.html`, `waitlist.html` | Lead capture |
| `styles.css`, `main.js`, `nav-dropdown.css`, `nav-dropdown.js`, `policies.css` | Shared assets (see also per-page `?v=` cache busters) |
| `contact-form.js`, `waitlist-form.js`, `amazon-profit-calculator.js`, etc. | Page-specific behaviour |
| `blog/**/index.html` | Blog articles |
| `policies/*.html` | Legal / policy pages |
| `*-profit-calculator/index.html` | SEO calculator tools (each folder is a section) |
| `logos/**` | Brand and marketplace artwork |
| `robots.txt`, `sitemap.xml` | Crawling |

Backend for forms (optional, not static hosting alone): `contact_server.py` and env from `.env.example`.

## Root directory (why it looks �flat�)

Static hosts expect `index.html` at the site root. Global CSS/JS also live at the root for **simple relative URLs** from nested pages (`../../styles.css` from `blog/...`). That is intentional; see [scripts/README.md](../scripts/README.md) for automation that touches many files.

## Server, deploy, and tools

| Path | Role |
|------|------|
| `contact_server.py` | Flask API for contact + waitlist when not using a separate API |
| `serve.py` | Local static server (if present) for quick preview |
| `deploy/` | Example nginx and hosting notes |
| `scripts/` | Python helpers; see [scripts/README.md](../scripts/README.md) |

## Shared chrome (nav / header)

The mega navigation is **duplicated across HTML files**. The canonical source for bulk updates is embedded in `scripts/apply_mega_nav.py` (template string) and the feature blog generator in `scripts/render_feature_blog_series.py`. Edits to nav CTAs or structure should be applied **here first**, then re-run or merge as needed, or updated project-wide with a focused replace.

## Configuration

- **Secrets / local env:** `.env` (gitignored). Copy from `.env.example`.
- **Public constants** (booking links, API base URLs) are currently **inlined in HTML**; a future improvement is a small build or inject step from a single config file.

## Local development

- Python virtualenvs are **not** committed; use `.venv` (or similar) locally. See root `.gitignore`.

## Further reading

- [README.md](../README.md) � canonical domain, performance, deploy steps.
- [scripts/README.md](../scripts/README.md) � what each script does.
