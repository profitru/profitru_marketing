"""Tests for marketing form anti-spam helpers."""

import os
import time

import form_security as fs


def _headers(origin: str = "https://profitru.com/waitlist.html") -> dict[str, str]:
    return {
        "Origin": origin,
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Dest": "empty",
    }


def _disable_extra_guards(monkeypatch) -> None:
    monkeypatch.setenv("FORM_REQUIRE_TURNSTILE", "false")
    monkeypatch.setenv("FORM_REQUIRE_NONCE", "false")
    monkeypatch.setenv("FORM_REQUIRE_BROWSER_HEADERS", "false")
    monkeypatch.setenv("FORM_MIN_FILL_SECONDS", "3")
    monkeypatch.setenv("FORM_GLOBAL_RATE_LIMIT_MAX", "100")


def test_spam_subject_blocked(monkeypatch):
    _disable_extra_guards(monkeypatch)
    err, silent = fs.evaluate_submission(
        kind="contact",
        ip="1.2.3.4",
        headers=_headers(),
        data={"form_started_at": int(time.time() * 1000) - 6000},
        email="real@company.com",
        subject="Claim Your Powerball Winnings Now!",
        text_parts=("spam body",),
    )
    assert err is None
    assert silent is True


def test_legit_submission_allowed(monkeypatch):
    _disable_extra_guards(monkeypatch)
    err, silent = fs.evaluate_submission(
        kind="contact",
        ip="9.9.9.9",
        headers=_headers("https://profitru.com/contact.html"),
        data={"form_started_at": int(time.time() * 1000) - 6000},
        email="seller@example.com",
        subject="Pricing for Amazon sellers",
        text_parts=("We run a small FBA business in Pune.", "Adey"),
    )
    assert err is None
    assert silent is False


def test_direct_api_without_origin_blocked(monkeypatch):
    _disable_extra_guards(monkeypatch)
    err, silent = fs.evaluate_submission(
        kind="waitlist",
        ip="8.8.8.8",
        headers={},
        data={"form_started_at": int(time.time() * 1000) - 6000},
        email="seller@example.com",
        text_parts=("hello",),
    )
    assert err is None
    assert silent is True


def test_turnstile_required_without_token_blocked(monkeypatch):
    monkeypatch.setenv("FORM_REQUIRE_TURNSTILE", "true")
    monkeypatch.setenv("TURNSTILE_SECRET_KEY", "test-secret")
    monkeypatch.setenv("FORM_REQUIRE_NONCE", "false")
    monkeypatch.setenv("FORM_REQUIRE_BROWSER_HEADERS", "false")
    err, silent = fs.evaluate_submission(
        kind="contact",
        ip="8.8.4.4",
        headers=_headers(),
        data={"form_started_at": int(time.time() * 1000) - 6000},
        email="seller@example.com",
        subject="Hello",
        text_parts=("msg",),
    )
    assert err is None
    assert silent is True


def test_rate_limit(monkeypatch):
    _disable_extra_guards(monkeypatch)
    monkeypatch.setenv("FORM_RATE_LIMIT_MAX_CONTACT", "2")
    monkeypatch.setenv("FORM_GLOBAL_RATE_LIMIT_MAX", "10")
    monkeypatch.setenv("FORM_RATE_LIMIT_WINDOW_SEC", "3600")
    fs._hits.clear()
    data = {"form_started_at": int(time.time() * 1000) - 6000}
    headers = _headers()
    for _ in range(2):
        err, silent = fs.evaluate_submission(
            kind="contact",
            ip="10.0.0.1",
            headers=headers,
            data=data,
            email="a@example.com",
            subject="Hello",
            text_parts=("msg",),
        )
        assert err is None and silent is False
    err, silent = fs.evaluate_submission(
        kind="contact",
        ip="10.0.0.1",
        headers=headers,
        data=data,
        email="a@example.com",
        subject="Hello again",
        text_parts=("msg",),
    )
    assert "Too many" in (err or "")
    assert silent is False


def test_form_nonce_is_one_time(monkeypatch):
    monkeypatch.setenv("FORM_REQUIRE_TURNSTILE", "false")
    monkeypatch.setenv("FORM_REQUIRE_BROWSER_HEADERS", "false")
    monkeypatch.setenv("FORM_REQUIRE_NONCE", "true")
    monkeypatch.setenv("FORM_MIN_FILL_SECONDS", "3")
    monkeypatch.setenv("FORM_GLOBAL_RATE_LIMIT_MAX", "100")
    monkeypatch.setenv("FORM_RATE_LIMIT_MAX_CONTACT", "10")
    monkeypatch.setenv("TURNSTILE_SECRET_KEY", "test-nonce-secret")
    fs._hits.clear()
    nonce = fs.issue_form_nonce()
    data = {"form_started_at": int(time.time() * 1000) - 6000, "form_nonce": nonce}
    err, silent = fs.evaluate_submission(
        kind="contact",
        ip="10.0.0.2",
        headers=_headers(),
        data=data,
        email="seller@example.com",
        subject="Hello",
        text_parts=("msg",),
    )
    assert err is None and silent is False


def test_form_nonce_rejects_invalid(monkeypatch):
    monkeypatch.setenv("FORM_REQUIRE_TURNSTILE", "false")
    monkeypatch.setenv("FORM_REQUIRE_BROWSER_HEADERS", "false")
    monkeypatch.setenv("FORM_REQUIRE_NONCE", "true")
    monkeypatch.setenv("FORM_MIN_FILL_SECONDS", "3")
    monkeypatch.setenv("FORM_GLOBAL_RATE_LIMIT_MAX", "100")
    monkeypatch.setenv("FORM_RATE_LIMIT_MAX_CONTACT", "10")
    fs._hits.clear()
    err, silent = fs.evaluate_submission(
        kind="contact",
        ip="10.0.0.2",
        headers=_headers(),
        data={"form_started_at": int(time.time() * 1000) - 6000, "form_nonce": "bad.token.here"},
        email="seller@example.com",
        subject="Hello",
        text_parts=("msg",),
    )
    assert err is None and silent is True


def test_browser_headers_required(monkeypatch):
    monkeypatch.setenv("FORM_REQUIRE_TURNSTILE", "false")
    monkeypatch.setenv("FORM_REQUIRE_NONCE", "false")
    monkeypatch.setenv("FORM_REQUIRE_BROWSER_HEADERS", "true")
    monkeypatch.setenv("FORM_MIN_FILL_SECONDS", "3")
    err, silent = fs.evaluate_submission(
        kind="contact",
        ip="10.0.0.3",
        headers={"Origin": "https://profitru.com/contact.html"},
        data={"form_started_at": int(time.time() * 1000) - 6000},
        email="seller@example.com",
        subject="Hello",
        text_parts=("msg",),
    )
    assert err is None and silent is True
