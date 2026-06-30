#!/usr/bin/env python3
"""One-off: replace flat nav with mega dropdown nav, add nav-dropdown.css and nav-dropdown.js."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

NAV = r"""        <nav class="nav-links nav-links--mega" id="nav-menu" aria-label="Primary">
          <div class="nav-mega" data-nav-dropdown>
            <button type="button" class="nav-mega__btn" id="nav-btn-product" aria-expanded="false" aria-controls="nav-panel-product" aria-haspopup="true">Product</button>
            <div class="nav-mega__panel" id="nav-panel-product" role="region" aria-labelledby="nav-btn-product" hidden>
              <div class="nav-mega__stack">
                <a href="/#pains">Problem</a>
                <a href="/#how">How it works</a>
                <a href="/#features">What you get</a>
                <a href="/#demo">See it in action</a>
                <a href="/#faq">FAQ</a>
                <a href="/#cta">Get started</a>
                <a href="/#built-for">Why Profitru</a>
              </div>
            </div>
          </div>
          <div class="nav-mega" data-nav-dropdown>
            <button type="button" class="nav-mega__btn" id="nav-btn-resources" aria-expanded="false" aria-controls="nav-panel-resources" aria-haspopup="true">Resources</button>
            <div class="nav-mega__panel" id="nav-panel-resources" role="region" aria-labelledby="nav-btn-resources" hidden>
              <div class="nav-mega__stack">
                <a href="/#guides">Guides hub</a>
                <a href="/blog/index.html">Blog</a>
              </div>
            </div>
          </div>
          <div class="nav-mega" data-nav-dropdown>
            <button type="button" class="nav-mega__btn" id="nav-btn-company" aria-expanded="false" aria-controls="nav-panel-company" aria-haspopup="true">Company</button>
            <div class="nav-mega__panel" id="nav-panel-company" role="region" aria-labelledby="nav-btn-company" hidden>
              <div class="nav-mega__stack">
                <a href="/contact.html">Contact</a>
                <a href="/policies/index.html">Policies &amp; legal</a>
              </div>
            </div>
          </div>
          <a href="/waitlist.html" class="btn btn-primary nav-mega__cta">Join the waitlist</a>
          <a href="https://bookings.cloud.microsoft/book/Proiftrudemo@profitru.com/" class="nav-mega__login" target="_blank" rel="noopener noreferrer">Book a demo</a>
          <a href="https://profitru.app/login" class="nav-mega__login">Log in</a>
        </nav>"""

NAV_RE = re.compile(
    r'<nav class="nav-links"[^>]*id="nav-menu"[^>]*>.*?</nav>',
    re.DOTALL,
)


def prefix_for(path: Path) -> str:
    rel = path.relative_to(ROOT)
    depth = len(rel.parent.parts)
    return "../" * depth


def add_assets(html: str, pfx: str) -> str:
    if "nav-dropdown.css" in html:
        return html
    ins_css = f'\n  <link rel="stylesheet" href="{pfx}nav-dropdown.css?v=2026-04-25">'
    m = re.search(
        r'(<link rel="stylesheet" href="[^"]*styles\.css[^"]*">)', html, re.IGNORECASE
    )
    if m:
        i = m.end()
        return html[:i] + ins_css + html[i:]
    return html

def add_js(html: str, pfx: str) -> str:
    if "nav-dropdown.js" in html:
        return html
    ins = f'  <script src="{pfx}nav-dropdown.js?v=2026-04-25" defer></script>\n'
    # After main.js (any query string)
    m = re.search(
        r'(<script src="[^"]*main\.js[^"]*"[^>]*></script>\s*)', html, re.IGNORECASE
    )
    if m:
        return html[: m.end()] + ins + html[m.end() :]
    # Fallback: before </body>
    return re.sub(r"</body>", ins + r"</body>", html, count=1)


def process_file(p: Path) -> bool:
    t = p.read_text(encoding="utf-8")
    if 'id="nav-menu"' not in t:
        return False
    m = NAV_RE.search(t)
    if not m:
        if "nav-links--mega" in t:
            return False
        print("skip (no match):", p, file=sys.stderr)
        return False
    t = NAV_RE.sub(NAV, t, count=1)
    pfx = prefix_for(p)
    t = add_assets(t, pfx)
    t = add_js(t, pfx)
    p.write_text(t, encoding="utf-8")
    print("ok", p.relative_to(ROOT))
    return True


def main() -> None:
    n = 0
    for p in sorted(ROOT.rglob("*.html")):
        if "node_modules" in p.parts:
            continue
        if process_file(p):
            n += 1
    print("updated", n, "files")


if __name__ == "__main__":
    main()
