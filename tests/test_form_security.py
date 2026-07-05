"""Tests for marketing form anti-spam helpers."""

import os
import time

import form_security as fs


def test_spam_subject_blocked():
    err, silent = fs.evaluate_submission(
        kind="contact",
        ip="1.2.3.4",
        data={"form_started_at": int(time.time() * 1000) - 5000},
        email="real@company.com",
        subject="Claim Your Powerball Winnings Now!",
        text_parts=("spam body",),
    )
    assert err is None
    assert silent is True


def test_legit_submission_allowed():
    err, silent = fs.evaluate_submission(
        kind="contact",
        ip="9.9.9.9",
        data={"form_started_at": int(time.time() * 1000) - 5000},
        email="seller@example.com",
        subject="Pricing for Amazon sellers",
        text_parts=("We run a small FBA business in Pune.", "Adey"),
    )
    assert err is None
    assert silent is False


def test_fast_bot_blocked():
    err, silent = fs.evaluate_submission(
        kind="waitlist",
        ip="8.8.8.8",
        data={"form_started_at": int(time.time() * 1000) - 500},
        email="seller@example.com",
        text_parts=("hello",),
    )
    assert err is None
    assert silent is True


def test_rate_limit(monkeypatch):
    monkeypatch.setenv("FORM_RATE_LIMIT_MAX_CONTACT", "2")
    monkeypatch.setenv("FORM_RATE_LIMIT_WINDOW_SEC", "3600")
    fs._hits.clear()
    data = {"form_started_at": int(time.time() * 1000) - 5000}
    for _ in range(2):
        err, silent = fs.evaluate_submission(
            kind="contact",
            ip="10.0.0.1",
            data=data,
            email="a@example.com",
            subject="Hello",
            text_parts=("msg",),
        )
        assert err is None and silent is False
    err, silent = fs.evaluate_submission(
        kind="contact",
        ip="10.0.0.1",
        data=data,
        email="a@example.com",
        subject="Hello again",
        text_parts=("msg",),
    )
    assert "Too many" in (err or "")
    assert silent is False
