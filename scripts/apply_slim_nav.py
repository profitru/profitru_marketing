#!/usr/bin/env python3
"""Replace mega-nav with slim flat nav across all HTML pages."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEMO = "https://bookings.cloud.microsoft/book/Proiftrudemo@profitru.com/"
TRIAL = "https://profitru.app/signup"
LOGIN = "https://profitru.app/login"
LINKEDIN_BAD = "https://www.linkedin.com/in/profitru-app-0b4692402/index.html"
LINKEDIN_OK = "https://www.linkedin.com/in/profitru-app-0b4692402/"

NAV = f"""        <nav class="nav-links nav-links--slim" id="nav-menu" aria-label="Primary">
          <a href="/product/">Product</a>
          <a href="/compare/">Compare</a>
          <a href="/blog/">Guides</a>
          <a href="{DEMO}" class="nav-slim__link" target="_blank" rel="noopener noreferrer">Book a demo</a>
          <a href="{LOGIN}" class="nav-slim__link">Log in</a>
          <a href="{TRIAL}" class="btn btn-primary nav-slim__cta">Start free trial</a>
        </nav>"""

NAV_RE = re.compile(
    r'<nav class="nav-links[^"]*"[^>]*id="nav-menu"[^>]*>.*?</nav>',
    re.DOTALL,
)

FOOTER_PRODUCT_RE = re.compile(
    r'(<div class="footer-col">\s*<h3>Product</h3>\s*)(.*?)(</div>)',
    re.DOTALL,
)

FOOTER_PRODUCT = f"""<a href="/product/">Product</a>
          <a href="/compare/">Compare</a>
          <a href="{TRIAL}">Start free trial</a>
          <a href="{LOGIN}">Log in</a>
          <a href="{DEMO}" target="_blank" rel="noopener noreferrer">Book a demo</a>
        """


def prefix_for(path: Path) -> str:
    rel = path.relative_to(ROOT)
    depth = len(rel.parent.parts)
    return "../" * depth


def ensure_redesign_css(html: str, pfx: str) -> str:
    if "redesign-2026.css" in html:
        return html
    ins = f'\n  <link rel="stylesheet" href="{pfx}redesign-2026.css?v=2026-07-27">'
    m = re.search(
        r'(<link rel="stylesheet" href="[^"]*styles\.css[^"]*">)', html, re.IGNORECASE
    )
    if m:
        return html[: m.end()] + ins + html[m.end() :]
    return html


def process_file(p: Path) -> bool:
    t = p.read_text(encoding="utf-8")
    changed = False

    if LINKEDIN_BAD in t:
        t = t.replace(LINKEDIN_BAD, LINKEDIN_OK)
        changed = True

    if 'id="nav-menu"' in t:
        m = NAV_RE.search(t)
# Force re-apply even if slim nav already present
        if m:
            t = NAV_RE.sub(NAV, t, count=1)
            changed = True
        elif m is None and "nav-links--mega" in t:
            print("warn: nav not matched:", p, file=sys.stderr)

    def repl_footer(match: re.Match[str]) -> str:
        return match.group(1) + FOOTER_PRODUCT + match.group(3)

    new_t, n = FOOTER_PRODUCT_RE.subn(repl_footer, t, count=1)
    if n:
        t = new_t
        changed = True

    # Sticky CTA on homepage-style pages
    if 'data-sticky-cta' in t and "Join the waitlist" in t:
        t2 = t.replace(
            'href="/waitlist.html" class="btn btn-primary sticky-cta__btn">Join the waitlist</a>',
            f'href="{TRIAL}" class="btn btn-primary sticky-cta__btn">Start free trial</a>',
        )
        if t2 != t:
            t = t2
            changed = True

    pfx = prefix_for(p)
    t2 = ensure_redesign_css(t, pfx)
    if t2 != t:
        t = t2
        changed = True

    if changed:
        p.write_text(t, encoding="utf-8")
        print("ok", p.relative_to(ROOT))
    return changed


def main() -> None:
    n = 0
    for p in sorted(ROOT.rglob("*.html")):
        if "node_modules" in p.parts or ".pytest_cache" in p.parts:
            continue
        if process_file(p):
            n += 1
    print("updated", n, "files")


if __name__ == "__main__":
    main()
