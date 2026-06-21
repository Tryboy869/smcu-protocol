#!/usr/bin/env python3
"""
SMCU Protocol — Autonomous PR Submitter
Allows AI agents to contribute entries to the central registry without
manual intervention each session.

Usage (standalone):
    python tools/submit_pr.py examples/my-new-entry.json
    python tools/submit_pr.py --json '{"id":"DEV-ERR-X001",...}'

Usage (from main.py via Allpath):
    python main.py submit_pr '<entry_json>'

Environment variables required:
    GITHUB_TOKEN
    GITHUB_USERNAME
    SMCU_REGISTRY_REPO   (default: Tryboy869/smcu-protocol)
    SMCU_NODE_PSEUDONYM  (for PR attribution)

Optional:
    SMCU_PR_DRAFT        (true = open as draft, default: false)
    SMCU_AUTO_NOTIFY     (true = send Telegram notification, default: true)
"""

import os
import sys
import json
import urllib.request
import urllib.error
import urllib.parse
import base64
import datetime
import time

ENV_FILE = ".smcu.env"

# ─────────────────────────────────────────────
def _load_env():
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    if key not in os.environ:
                        os.environ[key] = value.strip()


def _github_request(path: str, method: str = "GET", payload: dict = None) -> dict:
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise RuntimeError("GITHUB_TOKEN not set. Run setup.py first.")

    url = f"https://api.github.com{path}"
    data = json.dumps(payload).encode() if payload else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={
            "Authorization": f"token {token}",
            "Accept":        "application/vnd.github.v3+json",
            "Content-Type":  "application/json",
            "User-Agent":    "SMCU-Protocol/1.0"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"GitHub API {method} {path} → HTTP {e.code}: {body}")


def _validate_entry_locally(entry: dict) -> dict:
    """Run basic validation before attempting PR."""
    errors = []
    required = ["id", "taxonomie", "contenu", "preuve", "validation",
                "confiance", "statut", "source", "visibilite", "portee", "cycle_de_vie"]
    for f in required:
        if f not in entry:
            errors.append(f"Missing required field: '{f}'")

    if entry.get("statut") not in (None, "en_attente", "actif"):
        errors.append(f"statut must be 'en_attente' for new contributions (got '{entry['statut']}')")

    if "id" in entry:
        parts = entry["id"].split("-")
        if len(parts) < 3:
            errors.append(f"ID format invalid: '{entry['id']}' (expected DOMAIN-TYPE-HASH4)")

    return {"valid": len(errors) == 0, "errors": errors}


def submit_pr(entry_json_or_path: str, dry_run: bool = False) -> dict:
    """
    Submit an SMCU entry as a Pull Request to the central registry.

    Args:
        entry_json_or_path: JSON string or file path to the entry
        dry_run:            If True, simulate without creating the PR

    Returns:
        { "ok": bool, "pr_url": str|None, "branch": str, "errors": [] }
    """
    _load_env()

    # ── Load entry ──
    if os.path.exists(entry_json_or_path):
        with open(entry_json_or_path, "r", encoding="utf-8") as f:
            entry = json.load(f)
    else:
        try:
            entry = json.loads(entry_json_or_path)
        except json.JSONDecodeError as e:
            return {"ok": False, "errors": [f"Invalid JSON: {e}"], "pr_url": None}

    # ── Validate locally first ──
    validation = _validate_entry_locally(entry)
    if not validation["valid"]:
        return {"ok": False, "errors": validation["errors"], "pr_url": None}

    entry_id = entry["id"]
    domain   = entry.get("taxonomie", {}).get("domaine", "general")
    github_user   = os.environ.get("GITHUB_USERNAME", "")
    registry_repo = os.environ.get("SMCU_REGISTRY_REPO", "Tryboy869/smcu-protocol")
    pseudonym     = os.environ.get("SMCU_NODE_PSEUDONYM", github_user)
    is_draft      = os.environ.get("SMCU_PR_DRAFT", "false").lower() == "true"

    owner, repo = registry_repo.split("/")

    # ── Generate unique branch name ──
    ts     = str(int(time.time()))[-6:]
    branch = f"smcu/entry-{entry_id.lower()}-{ts}"

    # ── File path in the repo ──
    file_name  = f"{entry_id.lower().replace('-', '_')}.json"
    file_path  = f"examples/{file_name}"
    file_content = json.dumps(entry, ensure_ascii=False, indent=2)
    file_b64   = base64.b64encode(file_content.encode()).decode()

    if dry_run:
        return {
            "ok":       True,
            "dry_run":  True,
            "branch":   branch,
            "file":     file_path,
            "pr_title": f"[ENTRY] {domain} — {entry_id}",
            "pr_url":   None,
            "errors":   []
        }

    try:
        # ── Get default branch SHA ──
        repo_info   = _github_request(f"/repos/{owner}/{repo}")
        default_branch = repo_info.get("default_branch", "main")
        branch_info = _github_request(f"/repos/{owner}/{repo}/git/ref/heads/{default_branch}")
        base_sha    = branch_info["object"]["sha"]

        # ── Create new branch ──
        _github_request(
            f"/repos/{owner}/{repo}/git/refs",
            method="POST",
            payload={"ref": f"refs/heads/{branch}", "sha": base_sha}
        )

        # ── Commit the entry file ──
        _github_request(
            f"/repos/{owner}/{repo}/contents/{file_path}",
            method="PUT",
            payload={
                "message":  f"feat(entry): add {entry_id} — {domain}",
                "content":  file_b64,
                "branch":   branch,
            }
        )

        # ── Create Pull Request ──
        pr_title = f"[ENTRY] {domain} — {entry_id}"
        pr_body  = (
            f"## SMCU Protocol — New Entry Contribution\n\n"
            f"**Entry ID:** `{entry_id}`\n"
            f"**Domain:** {domain}\n"
            f"**Type:** {entry.get('contenu', {}).get('type', '?')}\n"
            f"**Gravity:** {entry.get('contenu', {}).get('gravite', '?')}\n"
            f"**Submitted by:** `{pseudonym}`\n"
            f"**Visibility:** {entry.get('visibilite', {}).get('niveau', '?')}\n\n"
            f"### Description\n"
            f"{entry.get('contenu', {}).get('description', '_No description_')}\n\n"
            f"### Solution\n"
            f"{entry.get('contenu', {}).get('solution', '_No solution_')}\n\n"
            f"### Proof\n"
            f"Type: `{entry.get('preuve', {}).get('type', '?')}`\n"
            f"Reference: {entry.get('preuve', {}).get('reference', '_None provided_')}\n\n"
            f"---\n"
            f"*Submitted autonomously by an SMCU node at "
            f"{datetime.datetime.utcnow().isoformat()}Z*\n"
            f"*Requires 3 validator votes to be merged.*\n\n"
            f"**Validator checklist:**\n"
            f"- [ ] Can reproduce the described error\n"
            f"- [ ] Proposed solution is correct\n"
            f"- [ ] Proof reference is valid\n"
        )

        pr_data = _github_request(
            f"/repos/{owner}/{repo}/pulls",
            method="POST",
            payload={
                "title": pr_title,
                "body":  pr_body,
                "head":  branch,
                "base":  default_branch,
                "draft": is_draft,
            }
        )

        pr_url = pr_data["html_url"]

        # ── Add labels ──
        try:
            _github_request(
                f"/repos/{owner}/{repo}/issues/{pr_data['number']}/labels",
                method="POST",
                payload={"labels": ["contribution", "awaiting-validation"]}
            )
        except Exception:
            pass  # Labels may not exist yet — not critical

        # ── Telegram notification ──
        if os.environ.get("SMCU_AUTO_NOTIFY", "true").lower() == "true":
            try:
                sys.path.insert(0, os.path.dirname(__file__))
                from notify_telegram import notify_pr_submitted
                notify_pr_submitted(entry_id, pr_url, domain)
            except Exception:
                pass  # Notifications are non-blocking

        return {
            "ok":     True,
            "pr_url": pr_url,
            "branch": branch,
            "file":   file_path,
            "entry_id": entry_id,
            "errors": []
        }

    except Exception as e:
        return {
            "ok":     False,
            "errors": [str(e)],
            "pr_url": None,
            "branch": branch
        }


# ─────────────────────────────────────────────
if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Usage:")
        print("  python tools/submit_pr.py examples/my-entry.json")
        print("  python tools/submit_pr.py --json '{\"id\":\"DEV-ERR-X001\",...}'")
        print("  python tools/submit_pr.py examples/my-entry.json --dry-run")
        sys.exit(1)

    dry_run = "--dry-run" in args
    args    = [a for a in args if a != "--dry-run"]

    if "--json" in args:
        idx    = args.index("--json")
        source = args[idx + 1]
    else:
        source = args[0]

    result = submit_pr(source, dry_run=dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["ok"] else 1)
