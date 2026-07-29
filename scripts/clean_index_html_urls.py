#!/usr/bin/env python3
"""
Normalize marketing URLs to clean directory form (no .../index.html).

Rewrites href/content attributes, profitru.com quoted URLs (JSON-LD), and sitemap <loc>.
Safe to re-run. Skips external non-profitru hosts and hash-only links.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]


def clean_url(u: str) -> str | None:
    """Return cleaned URL, or None if unchanged / not applicable."""
    if not u or u.startswith("#") or u.startswith("mailto:") or u.startswith("tel:"):
        return None
    if u.startswith("//"):
        return None

    if u.startswith("http://") or u.startswith("https://"):
        sp = urlsplit(u)
        if sp.netloc and "profitru.com" not in sp.netloc and "profitru.in" not in sp.netloc:
            return None
        path = sp.path or "/"
        if path.endswith("/index.html"):
            new_path = path[: -len("index.html")]  # keep trailing /
        elif path == "/index.html":
            new_path = "/"
        elif path.endswith("index.html"):
            new_path = path[: -len("index.html")]
            if not new_path.endswith("/"):
                new_path += "/"
        else:
            return None
        return urlunsplit((sp.scheme, sp.netloc, new_path, sp.query, sp.fragment))

    # Absolute site path
    if u.startswith("/"):
        if u == "/index.html":
            return "/"
        if u.endswith("/index.html"):
            return u[: -len("index.html")]
        if u.endswith("index.html"):
            base = u[: -len("index.html")]
            return base if base.endswith("/") else base + "/"
        return None

    # Relative
    if u == "index.html":
        return "./"
    if u.endswith("/index.html"):
        return u[: -len("index.html")]
    if u.endswith("index.html"):
        base = u[: -len("index.html")]
        return base if base.endswith("/") else (base + "/" if base else "./")
    return None


def patch_html(text: str) -> tuple[str, int]:
    changed = 0

    def sub_attr(m: re.Match[str]) -> str:
        nonlocal changed
        attr, quote, val = m.group(1), m.group(2), m.group(3)
        nu = clean_url(val)
        if nu is None or nu == val:
            return m.group(0)
        changed += 1
        return f"{attr}={quote}{nu}{quote}"

    # href, content (canonical/og), and JSON-LD item urls sometimes use content=
    out = re.sub(r"(href|content)=([\"'])([^\"']+)\2", sub_attr, text)

    def sub_quoted(m: re.Match[str]) -> str:
        nonlocal changed
        u = m.group(1)
        nu = clean_url(u)
        if nu is None or nu == u:
            return m.group(0)
        changed += 1
        return f'"{nu}"'

    out = re.sub(r'"(https://(?:www\.)?profitru\.(?:com|in)[^"]*)"', sub_quoted, out)
    return out, changed


def patch_sitemap(text: str) -> tuple[str, int]:
    changed = 0

    def sub_loc(m: re.Match[str]) -> str:
        nonlocal changed
        u = m.group(1)
        nu = clean_url(u)
        if nu is None or nu == u:
            return m.group(0)
        changed += 1
        return f"<loc>{nu}</loc>"

    return re.sub(r"<loc>([^<]+)</loc>", sub_loc, text), changed


def main() -> int:
    total = 0
    for p in sorted(ROOT.rglob("*.html")):
        if "scripts" in p.parts:
            continue
        raw = p.read_text(encoding="utf-8")
        new, n = patch_html(raw)
        if n:
            p.write_text(new, encoding="utf-8")
            print(f"{p.relative_to(ROOT)}: {n}")
            total += n

    sm = ROOT / "sitemap.xml"
    if sm.is_file():
        raw = sm.read_text(encoding="utf-8")
        new, n = patch_sitemap(raw)
        if n:
            sm.write_text(new, encoding="utf-8")
            print(f"sitemap.xml: {n}")
            total += n

    print(f"Done. {total} replacement(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
