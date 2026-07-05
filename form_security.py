"""Rate limits, spam checks, and optional Turnstile verification for public forms."""

from __future__ import annotations

import json
import os
import re
import threading
import time
import urllib.parse
import urllib.request
from collections import defaultdict, deque
from typing import Any

_SPAM_SUBJECT_PATTERNS = (
    re.compile(r"powerball", re.I),
    re.compile(r"\bwinn(?:ing|er)s?\b", re.I),
    re.compile(r"\bcasino\b", re.I),
    re.compile(r"\bviagra\b", re.I),
    re.compile(r"\bcialis\b", re.I),
    re.compile(r"\bbitcoin\b.*\b(?:giveaway|airdrop)\b", re.I),
    re.compile(r"\b(?:make|earn)\s+money\s+fast\b", re.I),
    re.compile(r"\bseo\s+services?\b", re.I),
    re.compile(r"https?://", re.I),
)

_SPAM_BODY_PATTERNS = (
    re.compile(r"powerball", re.I),
    re.compile(r"\bcasino\b", re.I),
    re.compile(r"\bviagra\b", re.I),
    re.compile(r"\bclick here\b.*\bhttp", re.I),
    re.compile(r"\b(?:unsubscribe|opt.?out)\b.*http", re.I),
)

_DISPOSABLE_DOMAINS = frozenset(
    {
        "mailinator.com",
        "guerrillamail.com",
        "tempmail.com",
        "10minutemail.com",
        "yopmail.com",
        "throwaway.email",
        "getnada.com",
        "sharklasers.com",
    }
)

_lock = threading.Lock()
_hits: dict[str, deque[float]] = defaultdict(deque)


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, str(default)))
    except ValueError:
        return default


def forms_enabled() -> bool:
    return os.environ.get("FORM_SUBMISSIONS_ENABLED", "true").lower() in ("1", "true", "yes")


def client_ip(headers: dict[str, str], remote_addr: str | None) -> str:
    forwarded = (headers.get("X-Forwarded-For") or headers.get("X-Real-IP") or "").strip()
    if forwarded:
        return forwarded.split(",")[0].strip()
    return (remote_addr or "unknown").strip() or "unknown"


def rate_limit_exceeded(kind: str, ip: str) -> bool:
    window = _env_int("FORM_RATE_LIMIT_WINDOW_SEC", 3600)
    max_hits = _env_int("FORM_RATE_LIMIT_MAX_CONTACT", 5) if kind == "contact" else _env_int(
        "FORM_RATE_LIMIT_MAX_WAITLIST", 3
    )
    now = time.time()
    key = f"{kind}:{ip}"
    with _lock:
        bucket = _hits[key]
        while bucket and now - bucket[0] > window:
            bucket.popleft()
        if len(bucket) >= max_hits:
            return True
        bucket.append(now)
    return False


def _looks_spam(*parts: str) -> bool:
    subject = parts[0] if parts else ""
    for pattern in _SPAM_SUBJECT_PATTERNS:
        if pattern.search(subject):
            return True
    body = " ".join(parts[1:])
    url_count = len(re.findall(r"https?://", body, flags=re.I))
    if url_count > 2:
        return True
    for pattern in _SPAM_BODY_PATTERNS:
        if pattern.search(body):
            return True
    return False


def disposable_email(email: str) -> bool:
    domain = email.rsplit("@", 1)[-1].lower().strip()
    return domain in _DISPOSABLE_DOMAINS


def form_timing_ok(data: dict[str, Any]) -> bool:
    raw = data.get("form_started_at")
    if raw in (None, ""):
        return False
    try:
        started_ms = int(raw)
    except (TypeError, ValueError):
        return False
    now_ms = int(time.time() * 1000)
    elapsed = (now_ms - started_ms) / 1000.0
    min_sec = _env_float("FORM_MIN_FILL_SECONDS", 3.0)
    max_sec = _env_float("FORM_MAX_FILL_SECONDS", 7200.0)
    return min_sec <= elapsed <= max_sec


def verify_turnstile(token: str, remote_ip: str | None) -> bool:
    secret = os.environ.get("TURNSTILE_SECRET_KEY", "").strip()
    if not secret:
        return True
    if not (token or "").strip():
        return False
    payload = urllib.parse.urlencode(
        {
            "secret": secret,
            "response": token.strip(),
            "remoteip": (remote_ip or "").strip(),
        }
    ).encode()
    req = urllib.request.Request(
        "https://challenges.cloudflare.com/turnstile/v0/siteverify",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode())
    except Exception:
        return False
    return body.get("success") is True


def turnstile_required() -> bool:
    return bool(os.environ.get("TURNSTILE_SECRET_KEY", "").strip())


def evaluate_submission(
    *,
    kind: str,
    ip: str,
    data: dict[str, Any],
    email: str,
    subject: str = "",
    text_parts: tuple[str, ...] = (),
) -> tuple[str | None, bool]:
    """
    Returns (error_message, silent_spam).
    silent_spam=True means return HTTP 200 to the client without sending mail.
    """
    if not forms_enabled():
        return ("Form submissions are temporarily unavailable. Please email support@profitru.com.", False)

    if rate_limit_exceeded(kind, ip):
        return ("Too many submissions from your network. Please try again later.", False)

    if not form_timing_ok(data):
        return (None, True)

    if turnstile_required() and not verify_turnstile(str(data.get("turnstile_token") or ""), ip):
        return ("Security check failed. Please refresh the page and try again.", False)

    if disposable_email(email):
        return (None, True)

    combined = (subject, *text_parts)
    if _looks_spam(*combined):
        return (None, True)

    return (None, False)
