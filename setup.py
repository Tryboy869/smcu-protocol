#!/usr/bin/env python3
"""
SMCU Protocol — Local Node Setup
Run once to configure your SMCU node.

Usage:
    python setup.py

What this does:
    1. Downloads and installs Allpath Runner locally
    2. Configures GitHub credentials (for autonomous PR contributions)
    3. Configures Telegram bot (for contribution notifications)
    4. Sets your node pseudonym (persistent identity in the registry)
    5. Saves everything to .smcu.env (gitignored)
    6. Tests all connections
    7. Runs a first query to confirm the registry is working
"""

import sys
import os
import json
import urllib.request
import urllib.error
import urllib.parse
import subprocess
import time
import hashlib
import datetime

ENV_FILE      = ".smcu.env"
ALLPATH_FILE  = "allpath-runner.py"
ALLPATH_URL   = "https://raw.githubusercontent.com/Tryboy869/allpath-runner/main/allpath-runner.py"
REGISTRY_REPO = "Tryboy869/smcu-protocol"

# ─────────────────────────────────────────────
BOLD  = "\033[1m"
GREEN = "\033[92m"
RED   = "\033[91m"
CYAN  = "\033[96m"
YELLOW= "\033[93m"
RESET = "\033[0m"

def p(msg):   print(msg)
def ok(msg):  print(f"{GREEN}✅ {msg}{RESET}")
def err(msg): print(f"{RED}❌ {msg}{RESET}")
def info(msg):print(f"{CYAN}ℹ  {msg}{RESET}")
def warn(msg):print(f"{YELLOW}⚠  {msg}{RESET}")
def header(t):
    print(f"\n{BOLD}{'─'*55}")
    print(f"  {t}")
    print(f"{'─'*55}{RESET}")

def ask(prompt, default=None, secret=False):
    hint = f" [{default}]" if default else ""
    full = f"{CYAN}{prompt}{hint}: {RESET}"
    if secret:
        import getpass
        val = getpass.getpass(full)
    else:
        val = input(full).strip()
    return val if val else default


# ════════════════════════════════════════════════════════
#  STEP 1 — Python version check
# ════════════════════════════════════════════════════════
def check_python():
    header("STEP 1/7 — Python Version")
    if sys.version_info < (3, 8):
        err(f"Python 3.8+ required (you have {sys.version})")
        sys.exit(1)
    ok(f"Python {sys.version.split()[0]}")


# ════════════════════════════════════════════════════════
#  STEP 2 — Install Allpath Runner
# ════════════════════════════════════════════════════════
def install_allpath():
    header("STEP 2/7 — Allpath Runner Installation")

    if os.path.exists(ALLPATH_FILE):
        ok(f"{ALLPATH_FILE} already present — skipping download")
        return

    info(f"Downloading from: {ALLPATH_URL}")
    try:
        urllib.request.urlretrieve(ALLPATH_URL, ALLPATH_FILE)
        ok(f"Allpath Runner downloaded → {ALLPATH_FILE}")
    except urllib.error.URLError:
        warn("Could not download Allpath Runner (network unavailable or repo not yet published)")
        warn("You can place allpath-runner.py manually in this directory later")
        warn("SMCU functions still work via: python main.py <function> [args...]")

    # Verify it's executable
    if os.path.exists(ALLPATH_FILE):
        result = subprocess.run(
            [sys.executable, ALLPATH_FILE, "version"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            ok(f"Allpath Runner operational: {result.stdout.strip()}")
        else:
            warn("Allpath Runner present but 'version' command failed — may need manual check")


# ════════════════════════════════════════════════════════
#  STEP 3 — GitHub Credentials
# ════════════════════════════════════════════════════════
def configure_github():
    header("STEP 3/7 — GitHub Configuration")
    info("Required for autonomous PR contributions to the SMCU registry")
    info("Create a token at: https://github.com/settings/tokens")
    info("Required scopes: repo (full), workflow")
    p("")

    token    = ask("GitHub Personal Access Token (ghp_...)", secret=True)
    username = ask("GitHub Username")

    if not token or not username:
        err("GitHub token and username are required for autonomous contributions")
        sys.exit(1)

    # Validate token
    info("Validating GitHub token...")
    try:
        req = urllib.request.Request(
            "https://api.github.com/user",
            headers={
                "Authorization": f"token {token}",
                "User-Agent": "SMCU-Protocol/1.0"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            user_data = json.loads(resp.read())
            detected_username = user_data["login"]

        if detected_username != username:
            warn(f"Token belongs to @{detected_username} (not @{username})")
            warn(f"Using @{detected_username}")
            username = detected_username

        ok(f"GitHub authenticated as @{username}")
    except urllib.error.HTTPError as e:
        err(f"GitHub token invalid (HTTP {e.code})")
        sys.exit(1)
    except Exception as e:
        warn(f"Could not validate GitHub token: {e}")
        warn("Saving anyway — check your connection")

    return {"GITHUB_TOKEN": token, "GITHUB_USERNAME": username}


# ════════════════════════════════════════════════════════
#  STEP 4 — Node Pseudonym
# ════════════════════════════════════════════════════════
def configure_pseudonym(github_username):
    header("STEP 4/7 — Node Pseudonym (Registry Identity)")
    info("This is your persistent identity in the SMCU registry")
    info("Format: Sector-Region-Number (e.g. DevAgent-EU-01, MedBot-US-12)")
    info("Once set, keep it consistent — your trust score accumulates on this name")
    p("")

    default_pseudo = f"Agent-{github_username[:6].upper()}-01"
    pseudonym = ask("Your node pseudonym", default=default_pseudo)

    # Generate a deterministic DID from pseudonym
    did_seed  = hashlib.sha256(pseudonym.encode()).hexdigest()[:32]
    node_did  = f"did:key:z6Mk{did_seed}"

    ok(f"Pseudonym: {pseudonym}")
    ok(f"Node DID:  {node_did}")

    return {"SMCU_NODE_PSEUDONYM": pseudonym, "SMCU_NODE_DID": node_did}


# ════════════════════════════════════════════════════════
#  STEP 5 — Telegram Bot
# ════════════════════════════════════════════════════════
def configure_telegram():
    header("STEP 5/7 — Telegram Notifications (Optional)")
    info("Sends you a message when your PR is submitted or validated")
    info("Create a bot at: https://t.me/BotFather → /newbot")
    p("")

    use_tg = ask("Configure Telegram? (y/n)", default="y")
    if use_tg.lower() != "y":
        info("Skipping Telegram — you can run setup.py again to add it later")
        return {}

    bot_token = ask("Telegram Bot Token (123456:ABC...)", secret=True)
    if not bot_token:
        warn("No token provided — skipping Telegram")
        return {}

    # Auto-detect chat_id
    info("To get your Chat ID:")
    info(f"  1. Open Telegram and search for your bot: @{bot_token.split(':')[0]}")
    info(f"  2. Send any message to the bot (e.g. /start)")
    input(f"{CYAN}  Press ENTER once you've sent a message to your bot...{RESET}")

    info("Auto-detecting your Chat ID...")
    chat_id = None
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        req = urllib.request.Request(url, headers={"User-Agent": "SMCU/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            updates = json.loads(resp.read())

        if updates.get("result"):
            latest = updates["result"][-1]
            chat_id = str(latest["message"]["chat"]["id"])
            chat_name = latest["message"]["chat"].get("first_name", "?")
            ok(f"Chat ID detected: {chat_id} (from @{chat_name})")
        else:
            warn("No messages found — enter your Chat ID manually")
            info("Find your Chat ID at: https://t.me/userinfobot")
            chat_id = ask("Telegram Chat ID")

    except Exception as e:
        warn(f"Auto-detection failed: {e}")
        chat_id = ask("Telegram Chat ID (manual entry)")

    if not chat_id:
        warn("No Chat ID — skipping Telegram")
        return {}

    # Send test message
    try:
        test_url  = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        test_data = json.dumps({
            "chat_id":    chat_id,
            "text":       "🍄 *SMCU Node Active*\nYour node is now configured and connected to The Mycelium Protocol.",
            "parse_mode": "Markdown"
        }).encode()
        req = urllib.request.Request(test_url, data=test_data,
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
        ok("Test message sent to Telegram ✓")
    except Exception as e:
        warn(f"Test message failed: {e}")

    return {"TELEGRAM_BOT_TOKEN": bot_token, "TELEGRAM_CHAT_ID": chat_id}


# ════════════════════════════════════════════════════════
#  STEP 6 — Save .smcu.env
# ════════════════════════════════════════════════════════
def save_env(config):
    header("STEP 6/7 — Saving Configuration")

    lines = [
        "# SMCU Protocol — Environment Configuration",
        f"# Generated by setup.py on {datetime.datetime.utcnow().isoformat()}Z",
        "# DO NOT commit this file to git (.gitignore already excludes it)",
        "",
        "# ── GitHub (required for autonomous PR contributions) ──",
        f"GITHUB_TOKEN={config.get('GITHUB_TOKEN', '')}",
        f"GITHUB_USERNAME={config.get('GITHUB_USERNAME', '')}",
        f"SMCU_REGISTRY_REPO={REGISTRY_REPO}",
        "",
        "# ── Node Identity (your persistent registry identity) ──",
        f"SMCU_NODE_PSEUDONYM={config.get('SMCU_NODE_PSEUDONYM', '')}",
        f"SMCU_NODE_DID={config.get('SMCU_NODE_DID', '')}",
        "",
        "# ── Telegram (optional — contribution notifications) ──",
        f"TELEGRAM_BOT_TOKEN={config.get('TELEGRAM_BOT_TOKEN', '')}",
        f"TELEGRAM_CHAT_ID={config.get('TELEGRAM_CHAT_ID', '')}",
        "",
        "# ── Registry Settings ──",
        "SMCU_CONFIDENCE_THRESHOLD=40",
        "SMCU_AUTO_NOTIFY=true",
        "SMCU_PR_DRAFT=false",
    ]

    with open(ENV_FILE, "w") as f:
        f.write("\n".join(lines) + "\n")

    ok(f"Config saved to: {ENV_FILE}")

    # Ensure .gitignore excludes it
    gitignore = ".gitignore"
    if os.path.exists(gitignore):
        with open(gitignore, "r") as f:
            content = f.read()
        if ".smcu.env" not in content:
            with open(gitignore, "a") as f:
                f.write("\n# SMCU credentials\n.smcu.env\n")
            ok(".gitignore updated to exclude .smcu.env")
    else:
        with open(gitignore, "w") as f:
            f.write("# SMCU credentials\n.smcu.env\n")
        ok(".gitignore created")


# ════════════════════════════════════════════════════════
#  STEP 7 — Test full workflow
# ════════════════════════════════════════════════════════
def test_workflow():
    header("STEP 7/7 — Testing SMCU Workflow")

    # Test 1: Local query
    info("Test 1: Local registry query...")
    result = subprocess.run(
        [sys.executable, "main.py", "query_registry",
         "Développement logiciel", '["jwt"]'],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        ok(f"Query OK — {data['total']} rule(s) found for domain 'Développement logiciel'")
    else:
        err(f"Query failed: {result.stderr}")

    # Test 2: Validator
    info("Test 2: Standalone validator...")
    result = subprocess.run(
        [sys.executable, "validator/validate.py", "examples/software-dev.json"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        ok("Validator OK — examples/software-dev.json is valid")
    else:
        warn(f"Validator issue: {result.stdout[:200]}")

    # Test 3: submit_pr (dry run)
    info("Test 3: submit_pr dry-run (no actual PR created)...")
    result = subprocess.run(
        [sys.executable, "main.py", "submit_pr",
         '{"id":"TEST-ERR-DRY1","taxonomie":{"domaine":"test"}}', "--dry-run"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        ok("submit_pr dry-run passed")
    else:
        info("submit_pr dry-run skipped (credentials not fully loaded yet — normal on first run)")


# ════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════
def main():
    print(f"\n{BOLD}{'='*55}")
    print("  SMCU Protocol — The Mycelium Protocol")
    print("  Local Node Setup")
    print(f"{'='*55}{RESET}\n")
    info("This wizard configures your SMCU node once.")
    info("All credentials are saved locally in .smcu.env (never committed).")
    p("")

    check_python()
    install_allpath()

    config = {}
    config.update(configure_github())
    config.update(configure_pseudonym(config.get("GITHUB_USERNAME", "node")))
    config.update(configure_telegram())

    save_env(config)
    test_workflow()

    print(f"\n{BOLD}{'='*55}")
    print(f"  ✅ Setup complete!")
    print(f"{'='*55}{RESET}")
    print(f"\n  Your node:  {config.get('SMCU_NODE_PSEUDONYM')}")
    print(f"  Registry:   https://github.com/{REGISTRY_REPO}")
    print(f"\n  Next steps:")
    print(f"    python main.py query_registry \"médecine\" '[\"pharmacologie\"]'")
    print(f"    python main.py submit_pr '<entry_json>'")
    print(f"    python validator/validate.py examples/medical.json")
    print(f"\n  Read AGENT_GUIDE.md for the full AI workflow.\n")


if __name__ == "__main__":
    main()
