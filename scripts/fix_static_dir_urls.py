#!/usr/bin/env python3
"""
Rewrite internal marketing URLs that end in a trailing slash to explicit .../index.html
so CloudFront + S3 (REST origin) and similar stacks return 200 instead of 404.

Safe to re-run; skips external links, hash links, and paths whose last segment looks like a file.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]


def last_segment_looks_like_file(seg: str) -> bool:
    if not seg or seg in (".", ".."):
        return False
    return "." in seg


def fix_url(u: str) -> str | None:
    if not u.endswith("/"):
        return None
    if u.startswith("//"):
        return None
    if u.startswith("#") or u.startswith("/#"):
        return None

    if u.startswith("http://") or u.startswith("https://"):
        sp = urlsplit(u)
        path = sp.path or "/"
        if path in ("/", ""):
            return None
        parts = [p for p in path.split("/") if p]
        if parts and last_segment_looks_like_file(parts[-1]):
            return None
        new_path = path.rstrip("/") + "/index.html"
        return urlunsplit((sp.scheme, sp.netloc, new_path, sp.query, sp.fragment))

    if u.startswith("/"):
        parts = [p for p in u.split("/") if p]
        if parts and last_segment_looks_like_file(parts[-1]):
            return None
        return u.rstrip("/") + "/index.html"

    parts = [p for p in u.split("/") if p]
    if parts and last_segment_looks_like_file(parts[-1]):
        return None
    return u.rstrip("/") + "/index.html"


def patch_html(text: str) -> tuple[str, int]:
    changed = 0

    def sub_attr(m: re.Match[str]) -> str:
        nonlocal changed
        attr, quote, val = m.group(1), m.group(2), m.group(3)
        nu = fix_url(val)
        if nu is None or nu == val:
            return m.group(0)
        changed += 1
        return f"{attr}={quote}{nu}{quote}"

    out = re.sub(r"(href|content)=([\"'])([^\"']+)\2", sub_attr, text)
    return out, changed


def patch_quoted_profitru_urls(text: str) -> tuple[str, int]:
    """JSON-LD and inline JSON: \"https://profitru.com/foo/\" -> .../index.html"""
    changed = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal changed
        u = m.group(1)
        nu = fix_url(u)
        if nu is None or nu == u:
            return m.group(0)
        changed += 1
        return f'"{nu}"'

    out = re.sub(r'"(https://profitru\.com/[^"]*/)"', repl, text)
    return out, changed


def patch_sitemap(text: str) -> tuple[str, int]:
    changed = 0

    def sub_loc(m: re.Match[str]) -> str:
        nonlocal changed
        u = m.group(1)
        nu = fix_url(u)
        if nu is None or nu == u:
            return m.group(0)
        changed += 1
        return f"<loc>{nu}</loc>"

    out = re.sub(r"<loc>([^<]+)</loc>", sub_loc, text)
    return out, changed


def main() -> int:
    total = 0
    for p in sorted(ROOT.rglob("*.html")):
        if p.parts[-2:] == ("scripts", p.name):
            continue
        raw = p.read_text(encoding="utf-8")
        new, n1 = patch_html(raw)
        new, n2 = patch_quoted_profitru_urls(new)
        n = n1 + n2
        if n:
            p.write_text(new, encoding="utf-8")
            parts = []
            if n1:
                parts.append(f"{n1} attr")
            if n2:
                parts.append(f"{n2} quoted")
            print(f"{p.relative_to(ROOT)}: {', '.join(parts)}")
            total += n

    sm = ROOT / "sitemap.xml"
    if sm.is_file():
        raw = sm.read_text(encoding="utf-8")
        new, n = patch_sitemap(raw)
        if n:
            sm.write_text(new, encoding="utf-8")
            print(f"sitemap.xml: {n} <loc>(s)")
            total += n

    print(f"Done. {total} replacement(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
