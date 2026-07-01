#!/usr/bin/env python3
"""
Serve the marketing site and:
  - POST /api/contact (general contact form)
  - POST /api/waitlist (beta waitlist: notify support + thank-you to user)

Usage:
  cp .env.example .env   # then edit SMTP_* and secrets
  pip install -r requirements.txt
  python contact_server.py

Open http://127.0.0.1:8080/contact.html or /waitlist.html
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _valid_email(s: str) -> bool:
    return bool(s) and len(s) <= 254 and _EMAIL_RE.match(s) is not None


def _valid_phone(s: str) -> bool:
    """Require a plausible phone: length after normalisation, at least 8 digits."""
    if not s or len(s) > 30:
        return False
    digits = sum(1 for c in s if c.isdigit())
    return digits >= 8


def _smtp_timeout() -> float:
    try:
        return float(os.environ.get("SMTP_TIMEOUT", "30"))
    except ValueError:
        return 30.0


def _smtp_send_message(msg: EmailMessage) -> None:
    host = os.environ.get("SMTP_HOST", "").strip()
    if not host:
        raise RuntimeError("SMTP_HOST is not set")

    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER", "").strip()
    password = os.environ.get("SMTP_PASSWORD", "").strip()
    use_ssl = os.environ.get("SMTP_USE_SSL", "").lower() == "true" or port == 465
    use_tls = os.environ.get("SMTP_USE_TLS", "true").lower() == "true"
    timeout = _smtp_timeout()

    if use_ssl:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host, port, context=context, timeout=timeout) as smtp:
            if user:
                smtp.login(user, password)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(host, port, timeout=timeout) as smtp:
            smtp.ehlo()
            if use_tls:
                context = ssl.create_default_context()
                smtp.starttls(context=context)
                smtp.ehlo()
            if user:
                smtp.login(user, password)
            smtp.send_message(msg)


def _fallback_dir() -> Path:
    configured = os.environ.get("FORM_FALLBACK_DIR", "").strip()
    if configured:
        return Path(configured).expanduser()
    return ROOT / "data" / "submissions"


def _append_form_fallback(kind: str, payload: dict) -> Path:
    """Persist a submission when SMTP is unavailable so nothing is lost."""
    out_dir = _fallback_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "kind": kind,
        "received_at": datetime.now(timezone.utc).isoformat(),
        **payload,
    }
    out_path = out_dir / f"{kind}.jsonl"
    with out_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return out_path


def _smtp_from_addr(default: str) -> str:
    """Office 365 requires the SMTP From address to match the authenticated mailbox."""
    smtp_user = os.environ.get("SMTP_USER", "").strip()
    configured = os.environ.get("CONTACT_FROM_EMAIL", default).strip() or default
    if smtp_user and configured.lower() != smtp_user.lower():
        log.warning(
            "CONTACT_FROM_EMAIL (%s) differs from SMTP_USER (%s); using SMTP_USER for SMTP From",
            configured,
            smtp_user,
        )
        return smtp_user
    return configured or smtp_user or default


def _send_contact_email(
    *,
    name: str,
    reply_email: str,
    phone: str,
    subject: str,
    body: str,
) -> None:
    to_addr = os.environ.get("CONTACT_TO_EMAIL", "support@profitru.com").strip()
    from_addr = _smtp_from_addr(to_addr)

    text = (
        f"Name: {name}\n"
        f"Email: {reply_email}\n"
        f"Contact number: {phone}\n"
        f"Reply-To: {reply_email}\n"
        f"Subject (from form): {subject}\n"
        f"---\n\n"
        f"{body}\n"
    )

    msg = EmailMessage()
    msg["Subject"] = f"[Profitru contact] {subject}"
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Reply-To"] = reply_email
    msg.set_content(text)
    _smtp_send_message(msg)


def _send_waitlist_emails(
    *,
    name: str,
    reply_email: str,
    phone: str,
    company: str,
    role: str,
    marketplaces: str,
    message: str,
) -> None:
    """Notify support; optional auto-ack to the user."""
    to_addr = os.environ.get("WAITLIST_TO_EMAIL", "support@profitru.com").strip()
    if not to_addr:
        to_addr = "support@profitru.com"
    from_addr = _smtp_from_addr(to_addr)

    internal = (
        f"New waitlist sign-up (marketing site)\n"
        f"---\n"
        f"Name: {name}\n"
        f"Email: {reply_email}\n"
        f"Phone: {phone}\n"
        f"Business / company: {company}\n"
        f"Role: {role}\n"
        f"Marketplaces / channels: {marketplaces or '(not provided)'}\n"
        f"---\n"
        f"Message:\n{message}\n"
    )

    msg_in = EmailMessage()
    msg_in["Subject"] = f"[Profitru waitlist] {name} ({reply_email})"
    msg_in["From"] = from_addr
    msg_in["To"] = to_addr
    msg_in["Reply-To"] = reply_email
    msg_in.set_content(internal)
    _smtp_send_message(msg_in)

    send_ack = os.environ.get("WAITLIST_SEND_ACK", "true").lower() in ("1", "true", "yes")
    if not send_ack or not from_addr or not _valid_email(reply_email):
        return

    ack_body = (
        f"Hi {name},\n\n"
        f"Thank you for your interest in Profitru. We have received your details and will "
        f"keep you in mind as we open more capacity.\n\n"
        f"We will notify you at this email address when you are eligible to access the product.\n\n"
        f"If you have questions in the meantime, you can reach us at support@profitru.com.\n\n"
        f"— The Profitru team\n"
    )
    msg_ack = EmailMessage()
    msg_ack["Subject"] = "We received your Profitru waitlist request"
    msg_ack["From"] = from_addr
    msg_ack["To"] = reply_email
    msg_ack.set_content(ack_body)
    _smtp_send_message(msg_ack)


@app.route("/api/contact", methods=["POST"])
def api_contact():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Expected JSON body"}), 400

    # Honeypot: leave empty (bots often fill hidden fields)
    if str(data.get("company") or "").strip():
        log.info("contact: honeypot triggered, returning ok")
        return jsonify({"ok": True})

    name = str(data.get("name") or "").strip()
    email = str(data.get("email") or "").strip()
    phone = str(data.get("phone") or "").strip()
    subject = str(data.get("subject") or "").strip()
    message = str(data.get("message") or "").strip()

    if not name or len(name) > 200:
        return jsonify({"error": "Please enter your name."}), 400
    if not _valid_email(email):
        return jsonify({"error": "Please enter a valid email address."}), 400
    if not _valid_phone(phone):
        return jsonify({"error": "Please enter a valid contact number (include country code if outside India)."}), 400
    if not subject or len(subject) > 300:
        return jsonify({"error": "Please enter a short subject or question line."}), 400
    if not message or len(message) > 10000:
        return jsonify({"error": "Please enter a message (up to about 10,000 characters)."}), 400

    try:
        _send_contact_email(
            name=name, reply_email=email, phone=phone, subject=subject, body=message
        )
    except Exception:
        log.exception("contact: SMTP send failed")
        try:
            saved = _append_form_fallback(
                "contact",
                {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "subject": subject,
                    "message": message,
                },
            )
            log.warning("contact: saved fallback submission to %s", saved)
            return jsonify({"ok": True, "queued": True, "email_sent": False})
        except Exception:
            log.exception("contact: fallback save failed")
            return jsonify({"error": "Could not send your message. Please try email or try again later."}), 502

    log.info("contact: sent ok for %s subject=%r", email, subject[:80])
    return jsonify({"ok": True, "email_sent": True})


@app.route("/api/waitlist", methods=["POST"])
def api_waitlist():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Expected JSON body"}), 400

    if str(data.get("url") or "").strip():
        log.info("waitlist: honeypot triggered, returning ok")
        return jsonify({"ok": True})

    name = str(data.get("name") or "").strip()
    email = str(data.get("email") or "").strip()
    phone = str(data.get("phone") or "").strip()
    company = str(data.get("company") or "").strip()
    role = str(data.get("role") or "").strip()
    marketplaces = str(data.get("marketplaces") or "").strip()
    message = str(data.get("message") or "").strip()

    if not name or len(name) > 200:
        return jsonify({"error": "Please enter your name."}), 400
    if not _valid_email(email):
        return jsonify({"error": "Please enter a valid email address."}), 400
    if not _valid_phone(phone):
        return (
            jsonify(
                {
                    "error": "Please enter a valid contact number (include country code if outside India)."
                }
            ),
            400,
        )
    if not company or len(company) > 200:
        return jsonify({"error": "Please enter your business or company name."}), 400
    if not role or len(role) > 200:
        return jsonify({"error": "Please enter your role."}), 400
    if len(marketplaces) > 500:
        return jsonify({"error": "Marketplaces field is too long."}), 400
    if not message or len(message) > 10000:
        return (
            jsonify(
                {
                    "error": "Please tell us a bit about what you are looking for (up to about 10,000 characters).",
                }
            ),
            400,
        )

    try:
        _send_waitlist_emails(
            name=name,
            reply_email=email,
            phone=phone,
            company=company,
            role=role,
            marketplaces=marketplaces,
            message=message,
        )
    except Exception:
        log.exception("waitlist: SMTP send failed")
        try:
            saved = _append_form_fallback(
                "waitlist",
                {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "company": company,
                    "role": role,
                    "marketplaces": marketplaces,
                    "message": message,
                },
            )
            log.warning("waitlist: saved fallback submission to %s", saved)
            return jsonify({"ok": True, "queued": True, "email_sent": False})
        except Exception:
            log.exception("waitlist: fallback save failed")
            return (
                jsonify(
                    {
                        "error": "Could not send your request. Please try again or email support@profitru.com directly.",
                    }
                ),
                502,
            )

    log.info("waitlist: sent ok for %s", email)
    return jsonify({"ok": True, "email_sent": True})


@app.route("/api/health", methods=["GET"])
def api_health():
    smtp_host = os.environ.get("SMTP_HOST", "").strip()
    fallback = _fallback_dir()
    return jsonify(
        {
            "ok": True,
            "smtp_configured": bool(smtp_host),
            "fallback_dir": str(fallback),
            "fallback_writable": fallback.exists() and os.access(fallback, os.W_OK)
            if fallback.exists()
            else True,
        }
    )


@app.route("/")
def index():
    return send_from_directory(ROOT, "index.html")


@app.route("/<path:path>")
def static_or_html(path: str):
    if path.startswith("api/") or path == "api":
        return jsonify({"error": "Not found"}), 404
    candidate = ROOT / path
    if candidate.is_file():
        return send_from_directory(ROOT, path)
    return jsonify({"error": "Not found"}), 404


def main() -> None:
    p = argparse.ArgumentParser(description="Profitru marketing + contact API")
    p.add_argument(
        "--host",
        default=os.environ.get("CONTACT_SERVER_HOST", "127.0.0.1"),
        help="Bind address (default from CONTACT_SERVER_HOST or 127.0.0.1)",
    )
    p.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("CONTACT_SERVER_PORT", "8080")),
        help="Port (default from CONTACT_SERVER_PORT or 8080)",
    )
    args = p.parse_args()
    if not (ROOT / ".env").is_file():
        log.warning("No .env file in %s - copy .env.example to .env and set SMTP_*", ROOT)
    log.info(
        "Serving %s - /api/contact and /api/waitlist on http://%s:%s",
        ROOT,
        args.host,
        args.port,
    )
    app.run(host=args.host, port=args.port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
