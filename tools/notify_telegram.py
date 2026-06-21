#!/usr/bin/env python3
"""
SMCU Protocol — Telegram Notifier
Sends notifications to the configured Telegram bot.

Usage (standalone):
    python tools/notify_telegram.py "Your message here"

Usage (from code):
    from tools.notify_telegram import notify
    notify("PR submitted: DEV-ERR-A3F2 → https://github.com/.../pull/42")

Environment variables required:
    TELEGRAM_BOT_TOKEN
    TELEGRAM_CHAT_ID
"""

import os
import sys
import json
import urllib.request
import urllib.error
import datetime

ENV_FILE = ".smcu.env"


def _load_env():
    """Load .smcu.env if environment variables are not already set."""
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    if key.strip() not in os.environ:
                        os.environ[key.strip()] = value.strip()


def notify(message: str, emoji: str = "🍄") -> dict:
    """
    Send a Telegram notification.

    Args:
        message: Plain text or Markdown message
        emoji:   Emoji prefix (default: 🍄)

    Returns:
        { "ok": bool, "error": str|None }
    """
    _load_env()

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id   = os.environ.get("TELEGRAM_CHAT_ID",   "")

    if not bot_token or not chat_id:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not configured"}

    full_message = f"{emoji} *SMCU Protocol*\n\n{message}"
    url  = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = json.dumps({
        "chat_id":    chat_id,
        "text":       full_message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json", "User-Agent": "SMCU/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return {"ok": result.get("ok", False), "message_id": result.get("result", {}).get("message_id")}
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"HTTP {e.code}: {e.read().decode()}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def notify_pr_submitted(entry_id: str, pr_url: str, domain: str) -> dict:
    """Notify when a PR is submitted to the registry."""
    msg = (
        f"📬 *New contribution submitted*\n"
        f"Entry: `{entry_id}`\n"
        f"Domain: {domain}\n"
        f"PR: {pr_url}\n"
        f"Status: Awaiting 3 validator votes"
    )
    return notify(msg)


def notify_pr_approved(entry_id: str, pr_url: str, score: float) -> dict:
    """Notify when a PR is approved and merged."""
    msg = (
        f"✅ *Contribution approved!*\n"
        f"Entry: `{entry_id}`\n"
        f"Confidence score: {score}\n"
        f"PR: {pr_url}\n"
        f"Now active in the registry — all agents will learn from this."
    )
    return notify(msg, emoji="✅")


def notify_pr_rejected(entry_id: str, pr_url: str, reason: str) -> dict:
    """Notify when a PR is rejected."""
    msg = (
        f"❌ *Contribution rejected*\n"
        f"Entry: `{entry_id}`\n"
        f"Reason: {reason}\n"
        f"PR: {pr_url}\n"
        f"Review the feedback and resubmit."
    )
    return notify(msg, emoji="❌")


def notify_query_result(domain: str, count: int, top_rule: str = None) -> dict:
    """Notify when registry is queried (useful for audit logging via Telegram)."""
    msg = (
        f"🔍 *Registry queried*\n"
        f"Domain: {domain}\n"
        f"Rules found: {count}\n"
        f"{f'Top rule: `{top_rule}`' if top_rule else ''}"
    )
    return notify(msg, emoji="🔍")


# ─────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/notify_telegram.py <message>")
        sys.exit(1)

    message = " ".join(sys.argv[1:])
    result  = notify(message)

    if result.get("ok"):
        print(f"✅ Notification sent (message_id: {result.get('message_id')})")
    else:
        print(f"❌ Failed: {result.get('error')}")
        sys.exit(1)
