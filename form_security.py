"""Rate limits, spam checks, and Turnstile verification for public forms."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import threading
import time
import urllib.parse
import urllib.request
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

_SPAM_SUBJECT_PATTERNS = (
    re.compile(r"powerball", re.I),
    re.compile(r"\bwinn(?:ing|er)s?\b", re.I),
    re.compile(r"\bcasino\b", re.I),
    re.compile(r"\bviagra\b", re.I),
    re.compile(r"\bcialis\b", re.I),
    re.compile(r"\bbitcoin\b.*\b(?:giveaway|airdrop)\b", re.I),
    re.compile(r"\b(?:make|earn)\s+money\s+fast\b", re.I),
    re.compile(r"\bseo\s+services?\b", re.I),
    re.compile(r"\bjewel(?:l)?ery\b", re.I),
    re.compile(r"https?://", re.I),
    re.compile(r"^[A-Z0-9\s!?]{20,}$"),  # shouty spam subjects
    re.compile(r"\bloan\b", re.I),
    re.compile(r"\bcrypto\b", re.I),
    re.compile(r"\bforex\b", re.I),
)

_SPAM_BODY_PATTERNS = (
    re.compile(r"powerball", re.I),
    re.compile(r"\bcasino\b", re.I),
    re.compile(r"\bviagra\b", re.I),
    re.compile(r"\bclick here\b.*\bhttp", re.I),
    re.compile(r"\b(?:unsubscribe|opt.?out)\b.*http", re.I),
    re.compile(r"\bjewel(?:l)?ery\b.*\binquir", re.I),
    re.compile(r"\b(?:dear\s+(?:sir|madam|customer|user))\b", re.I),
    re.compile(r"\b(?:whatsapp|telegram)\b.*\b(?:\+?\d{10,}|http)", re.I),
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
        "temp-mail.org",
        "guerrillamailblock.com",
        "maildrop.cc",
        "dispostable.com",
        "fakeinbox.com",
    }
)

_ALLOWED_ORIGIN_SUFFIXES = (
    "profitru.com",
    "profitru.in",
    "localhost",
    "127.0.0.1",
)

_ALLOWED_TURNSTILE_HOSTNAMES = (
    "profitru.com",
    "www.profitru.com",
    "profitru.in",
    "www.profitru.in",
    "localhost",
    "127.0.0.1",
)

_lock = threading.Lock()
_hits: dict[str, deque[float]] = defaultdict(deque)


def _nonce_secret() -> bytes:
    for name in ("FORM_NONCE_SECRET", "TURNSTILE_SECRET_KEY"):
        raw = os.environ.get(name, "").strip()
        if raw:
            return raw.encode()
    return b"profitru-marketing-nonce-dev"


def _turnstile_store_path() -> Path:
    configured = os.environ.get("FORM_FALLBACK_DIR", "").strip()
    if configured:
        base = Path(configured).expanduser()
    else:
        base = Path(__file__).resolve().parent / "data" / "submissions"
    base.mkdir(parents=True, exist_ok=True)
    return base / ".turnstile_used.json"


def _turnstile_token_already_used(token_key: str, ttl: int) -> bool:
    """Cross-process Turnstile replay guard (works with multiple gunicorn workers)."""
    digest = hashlib.sha256(token_key.encode()).hexdigest()
    now = time.time()
    path = _turnstile_store_path()
    with _lock:
        try:
            if path.exists():
                store = json.loads(path.read_text(encoding="utf-8"))
            else:
                store = {}
        except (OSError, json.JSONDecodeError):
            store = {}
        store = {k: v for k, v in store.items() if float(v) >= now}
        if digest in store:
            return True
        store[digest] = now + ttl
        try:
            path.write_text(json.dumps(store), encoding="utf-8")
        except OSError as exc:
            log.warning("turnstile replay store write failed: %s", exc)
        return False


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


def _normalize_env_value(raw: str) -> str:
    """Strip whitespace, optional quotes, and systemd-unfriendly inline # comments."""
    value = raw.strip()
    if "#" in value:
        value = value.split("#", 1)[0].strip()
    return value.strip('"').strip("'")


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return _normalize_env_value(raw).lower() in ("1", "true", "yes", "on")


def _env_bool(name: str, default: bool) -> bool:
    return env_bool(name, default)


def forms_enabled() -> bool:
    return _env_bool("FORM_SUBMISSIONS_ENABLED", True)


def turnstile_site_key() -> str:
    return os.environ.get("TURNSTILE_SITE_KEY", "").strip()


def turnstile_secret_configured() -> bool:
    return bool(os.environ.get("TURNSTILE_SECRET_KEY", "").strip())


def turnstile_required() -> bool:
    """Require a valid Turnstile token before sending mail (default: true)."""
    if not _env_bool("FORM_REQUIRE_TURNSTILE", True):
        return False
    return turnstile_secret_configured()


def form_nonce_required() -> bool:
    return _env_bool("FORM_REQUIRE_NONCE", True)


def issue_form_nonce() -> str:
    """Signed nonce valid on any gunicorn worker (no in-memory store)."""
    ttl = _env_int("FORM_NONCE_TTL_SEC", 900)
    expires = int(time.time()) + ttl
    rnd = secrets.token_urlsafe(16)
    payload = f"{expires}.{rnd}"
    sig = hmac.new(_nonce_secret(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"


def consume_form_nonce(raw: str) -> bool:
    if not form_nonce_required():
        return True
    token = (raw or "").strip()
    if not token or token.count(".") != 2:
        log.info("form nonce missing or malformed")
        return False
    expires_s, rnd, sig = token.split(".", 2)
    try:
        expires = int(expires_s)
    except ValueError:
        log.info("form nonce expiry invalid")
        return False
    if expires < time.time():
        log.info("form nonce expired")
        return False
    payload = f"{expires_s}.{rnd}"
    expected = hmac.new(_nonce_secret(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        log.info("form nonce signature invalid")
        return False
    return True


def client_ip(headers: dict[str, str], remote_addr: str | None) -> str:
    forwarded = (headers.get("X-Forwarded-For") or headers.get("X-Real-IP") or "").strip()
    if forwarded:
        return forwarded.split(",")[0].strip()
    return (remote_addr or "unknown").strip() or "unknown"


def origin_allowed(headers: dict[str, str]) -> bool:
    if not _env_bool("FORM_REQUIRE_ALLOWED_ORIGIN", True):
        return True
    origin = (headers.get("Origin") or headers.get("Referer") or "").strip().lower()
    if not origin:
        return False
    return any(suffix in origin for suffix in _ALLOWED_ORIGIN_SUFFIXES)


def browser_submission_ok(headers: dict[str, str]) -> bool:
    """Reject scripted POSTs that lack browser fetch metadata."""
    if not _env_bool("FORM_REQUIRE_BROWSER_HEADERS", True):
        return True
    mode = (headers.get("Sec-Fetch-Mode") or "").lower()
    site = (headers.get("Sec-Fetch-Site") or "").lower()
    dest = (headers.get("Sec-Fetch-Dest") or "").lower()
    if not mode or not site:
        return False
    if mode not in ("cors", "same-origin"):
        return False
    if site not in ("same-origin", "same-site"):
        return False
    if dest and dest not in ("empty",):
        return False
    return True


def _rate_limit_hit(key: str, window: int, max_hits: int) -> bool:
    now = time.time()
    with _lock:
        bucket = _hits[key]
        while bucket and now - bucket[0] > window:
            bucket.popleft()
        if len(bucket) >= max_hits:
            return True
        bucket.append(now)
    return False


def global_rate_limit_exceeded(ip: str) -> bool:
    window = _env_int("FORM_GLOBAL_RATE_LIMIT_WINDOW_SEC", 3600)
    max_hits = _env_int("FORM_GLOBAL_RATE_LIMIT_MAX", 2)
    return _rate_limit_hit(f"global:{ip}", window, max_hits)


def rate_limit_exceeded(kind: str, ip: str) -> bool:
    window = _env_int("FORM_RATE_LIMIT_WINDOW_SEC", 3600)
    max_hits = _env_int("FORM_RATE_LIMIT_MAX_CONTACT", 1) if kind == "contact" else _env_int(
        "FORM_RATE_LIMIT_MAX_WAITLIST", 1
    )
    return _rate_limit_hit(f"{kind}:{ip}", window, max_hits)


def _looks_spam(*parts: str) -> bool:
    subject = parts[0] if parts else ""
    for pattern in _SPAM_SUBJECT_PATTERNS:
        if pattern.search(subject):
            return True
    body = " ".join(parts[1:])
    url_count = len(re.findall(r"https?://", body, flags=re.I))
    if url_count > 1:
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
    min_sec = _env_float("FORM_MIN_FILL_SECONDS", 8.0)
    max_sec = _env_float("FORM_MAX_FILL_SECONDS", 7200.0)
    return min_sec <= elapsed <= max_sec


def _turnstile_hostname_ok(hostname: str) -> bool:
    host = (hostname or "").lower().strip()
    if not host:
        return False
    return any(host == allowed or host.endswith(f".{allowed}") for allowed in _ALLOWED_TURNSTILE_HOSTNAMES)


def verify_turnstile(token: str, remote_ip: str | None, *, expected_action: str = "") -> bool:
    secret = os.environ.get("TURNSTILE_SECRET_KEY", "").strip()
    if not secret:
        return False
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
    except Exception as exc:
        log.warning("turnstile verify request failed: %s", exc)
        return False
    if not body.get("success"):
        log.info("turnstile verify rejected: %s", body.get("error-codes"))
        return False
    if not _turnstile_hostname_ok(str(body.get("hostname") or "")):
        log.info("turnstile hostname rejected: %s", body.get("hostname"))
        return False
    if expected_action:
        action = str(body.get("action") or "").strip()
        if action and action != expected_action:
            log.info("turnstile action rejected: got %r expected %r", action, expected_action)
            return False
    token_key = token.strip()
    ttl = _env_int("TURNSTILE_TOKEN_TTL_SEC", 600)
    if _turnstile_token_already_used(token_key, ttl):
        log.info("turnstile token replay blocked")
        return False
    return True


def evaluate_submission(
    *,
    kind: str,
    ip: str,
    headers: dict[str, str],
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

    if turnstile_required() and not turnstile_secret_configured():
        log.error("FORM_REQUIRE_TURNSTILE is on but TURNSTILE_SECRET_KEY is missing")
        return ("Form is temporarily unavailable. Please email support@profitru.com.", False)

    if not origin_allowed(headers):
        log.info("form block [%s] %s: origin not allowed", kind, ip)
        return (None, True)

    if not browser_submission_ok(headers):
        log.info("form block [%s] %s: browser headers", kind, ip)
        return (None, True)

    if global_rate_limit_exceeded(ip):
        return ("Too many submissions from your network. Please try again later.", False)

    if rate_limit_exceeded(kind, ip):
        return ("Too many submissions from your network. Please try again later.", False)

    if not form_timing_ok(data):
        log.info("form block [%s] %s: timing", kind, ip)
        return (None, True)

    if not consume_form_nonce(str(data.get("form_nonce") or "")):
        log.info("form block [%s] %s: form nonce", kind, ip)
        return (None, True)

    if turnstile_required():
        token = str(data.get("turnstile_token") or "").strip()
        if not verify_turnstile(token, ip, expected_action=kind):
            log.info("form block [%s] %s: turnstile", kind, ip)
            return (None, True)

    if disposable_email(email):
        log.info("form block [%s] %s: disposable email", kind, ip)
        return (None, True)

    combined = (subject, *text_parts)
    if _looks_spam(*combined):
        log.info("form block [%s] %s: spam content", kind, ip)
        return (None, True)

    return (None, False)
