#!/usr/bin/env python3
"""Send a test email using .env SMTP settings. Run on the marketing server after editing .env."""

from __future__ import annotations

import os
import sys
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from contact_server import _email_routing_info, _inbox_for_kind, _smtp_from_addr, _smtp_send_message


def main() -> int:
    info = _email_routing_info()
    to_addr = _inbox_for_kind("waitlist")
    from_addr = _smtp_from_addr(to_addr)
    print("SMTP user:", info["smtp_user"] or "(not set)")
    print("SMTP from:", from_addr)
    print("Waitlist notifications ->", info["waitlist_to_email"])
    print("Waitlist thank-you ack:", info["waitlist_send_ack"])
    print("Same-mailbox loop risk:", info["same_mailbox_loop"])
    print()
    print(f"Sending test message to {to_addr} ...")

    msg = EmailMessage()
    msg["Subject"] = "[Profitru test] Waitlist SMTP check"
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(
        "If you received this, marketing form SMTP delivery is working.\n"
        "Delete this message after confirming.\n"
    )
    try:
        _smtp_send_message(msg)
    except Exception as exc:
        print("FAILED:", exc)
        err = str(exc)
        if "535" in err or "Authentication unsuccessful" in err:
            print()
            print("535 usually means Microsoft 365 rejected SMTP login for this mailbox.")
            print("Checklist:")
            print("  1. SMTP_USER must be the full address, e.g. info@profitru.com")
            print("  2. If MFA is on, SMTP_PASSWORD must be an app password (not the normal login password)")
            print("  3. Enable SMTP AUTH for this mailbox in Exchange admin:")
            print("     Mailboxes -> info@ -> Email apps -> Authenticated SMTP = enabled")
            print("  4. Or PowerShell: Set-CASMailbox -Identity info@profitru.com -SmtpClientAuthenticationDisabled $false")
            print("  5. Set CONTACT_FROM_EMAIL=info@profitru.com to match SMTP_USER")
        return 1
    print("OK: test email sent. Check the inbox (and spam folder) for", to_addr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
