#!/usr/bin/env python3
"""
SMCU Protocol — Allpath Runner Package
Universal Collective Memory System / The Mycelium Protocol

Author  : Daouda Abdoul Anzize
License : MIT
Repo    : https://github.com/Tryboy869/smcu-protocol
"""

import sys
import json
import math
import hashlib
import time
import os

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
REQUIRED_FIELDS = [
    "id", "taxonomie", "contenu", "preuve",
    "validation", "confiance", "statut",
    "source", "visibilite", "portee", "cycle_de_vie"
]

VALID_STATUTS    = ["actif", "conteste", "revoque", "obsolete", "archive"]
VALID_GRAVITES   = ["critique", "majeur", "mineur"]
VALID_TYPES      = ["erreur", "regle", "avertissement", "bonne_pratique"]
VALID_VISIBILITE = ["public", "organisation", "prive"]
VALID_PREUVES    = ["test_unitaire", "test_integration", "cas_clinique",
                    "simulation", "peer_review", "audit_securite"]

DOMAIN_PREFIXES = {
    "développement logiciel": "DEV",
    "developpement logiciel": "DEV",
    "médecine": "MED",
    "medecine": "MED",
    "robotique": "ROB",
    "finance": "FIN",
    "sécurité": "SEC",
    "securite": "SEC",
    "éducation": "EDU",
    "education": "EDU",
}

TYPE_SUFFIXES = {
    "erreur":          "ERR",
    "regle":           "RULE",
    "avertissement":   "WARN",
    "bonne_pratique":  "BP",
}


# ─────────────────────────────────────────────
#  FUNCTIONS
# ─────────────────────────────────────────────

def validate_entry(entry_json: str) -> None:
    """
    Validates an SMCU entry against the official v1.0 schema.
    Returns a JSON object: { valid, errors, warnings, entry_id }
    """
    try:
        entry = json.loads(entry_json)
    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "errors": [f"JSON invalide: {e}"], "warnings": [], "entry_id": None}))
        return

    errors   = []
    warnings = []

    # Required fields
    for field in REQUIRED_FIELDS:
        if field not in entry:
            errors.append(f"Champ obligatoire manquant : '{field}'")

    # Statut
    if "statut" in entry and entry["statut"] not in VALID_STATUTS:
        errors.append(f"Statut invalide : '{entry['statut']}'. Acceptés : {VALID_STATUTS}")

    # Contenu
    if "contenu" in entry:
        c = entry["contenu"]
        if "gravite" in c and c["gravite"] not in VALID_GRAVITES:
            errors.append(f"Gravité invalide : '{c['gravite']}'. Acceptées : {VALID_GRAVITES}")
        if "type" in c and c["type"] not in VALID_TYPES:
            errors.append(f"Type invalide : '{c['type']}'. Acceptés : {VALID_TYPES}")
        if "exemple" not in c:
            warnings.append("Aucun exemple fourni (recommandé pour adoption)")

    # Preuve
    if "preuve" in entry:
        p = entry["preuve"]
        if "type" in p and p["type"] not in VALID_PREUVES:
            errors.append(f"Type de preuve invalide : '{p['type']}'. Acceptés : {VALID_PREUVES}")
        if "reference" not in p:
            warnings.append("Aucune référence de preuve fournie")

    # Validation / votes
    if "validation" in entry:
        v = entry["validation"]
        if "votes_requis" in v and "votes" in v:
            if len(v["votes"]) < v["votes_requis"]:
                errors.append(
                    f"Votes insuffisants : {len(v['votes'])}/{v['votes_requis']} requis"
                )
        if "votes" in v:
            for i, vote in enumerate(v["votes"]):
                if "votant_did" not in vote:
                    errors.append(f"Vote #{i+1} : 'votant_did' manquant")
                if "decision" not in vote or vote.get("decision") not in ["approuve", "rejete", "ameliorer"]:
                    errors.append(f"Vote #{i+1} : décision invalide")

    # Visibilité
    if "visibilite" in entry and "niveau" in entry["visibilite"]:
        if entry["visibilite"]["niveau"] not in VALID_VISIBILITE:
            errors.append(f"Visibilité invalide : '{entry['visibilite']['niveau']}'")

    # Source / anonymat
    if "source" in entry:
        s = entry["source"]
        if "did" not in s:
            errors.append("Source : 'did' (identifiant cryptographique) manquant")
        if s.get("affichage") == "pseudonyme" and "pseudonyme" not in s:
            errors.append("Source : 'pseudonyme' requis quand affichage='pseudonyme'")
        if s.get("affichage") == "anonyme" and "preuve_zkp" not in s:
            warnings.append("Source anonyme : preuve ZKP recommandée pour crédibilité")

    # Relations
    if "relations" in entry:
        r = entry["relations"]
        if "parent" not in r:
            warnings.append("Aucun parent défini — hiérarchie recommandée pour le registre")

    print(json.dumps({
        "valid":    len(errors) == 0,
        "errors":   errors,
        "warnings": warnings,
        "entry_id": entry.get("id", "inconnu"),
        "score":    f"{len(errors)} erreur(s), {len(warnings)} avertissement(s)"
    }, ensure_ascii=False))


def compute_confidence(votes_positifs: str, votes_total: str, nb_utilisations: str) -> None:
    """
    Computes the SMCU confidence score.
    Formula: (votes_positifs / votes_total) × log(nb_utilisations + 1) × 100
    Capped at 100.
    """
    try:
        vp = int(votes_positifs)
        vt = int(votes_total)
        nu = int(nb_utilisations)
    except (ValueError, TypeError) as e:
        print(json.dumps({"error": f"Arguments invalides : {e}"}))
        return

    if vt == 0:
        print(json.dumps({"score": 0.0, "raison": "Aucun vote enregistré"}))
        return

    raw   = (vp / vt) * math.log(nu + 1) * 100
    score = min(round(raw, 2), 100.0)

    print(json.dumps({
        "score":          score,
        "interpretation": "critique" if score >= 80 else ("modere" if score >= 50 else "faible"),
        "votes_positifs": vp,
        "votes_total":    vt,
        "nb_utilisations": nu,
        "formule":        "(votes_positifs / votes_total) × log(nb_utilisations + 1) × 100"
    }, ensure_ascii=False))


def generate_id(domaine: str, type_entree: str) -> None:
    """
    Generates a unique SMCU entry ID.
    Format: {DOMAIN_PREFIX}-{TYPE_SUFFIX}-{HASH4}
    Example: DEV-ERR-A3F2
    """
    prefix = DOMAIN_PREFIXES.get(domaine.lower().strip(), "GEN")
    suffix = TYPE_SUFFIXES.get(type_entree.lower().strip(), "ENT")

    seed      = f"{domaine}{type_entree}{time.time()}".encode()
    hash_part = hashlib.md5(seed).hexdigest()[:4].upper()
    entry_id  = f"{prefix}-{suffix}-{hash_part}"

    print(json.dumps({
        "id":      entry_id,
        "domaine": domaine,
        "type":    type_entree,
        "note":    "Cet ID doit être vérifié contre le registre pour éviter les doublons"
    }, ensure_ascii=False))


def check_contradictions(entry_json: str, existing_ids_json: str) -> None:
    """
    Checks declared contradictions in an entry against existing registry IDs.
    """
    try:
        entry        = json.loads(entry_json)
        existing_ids = json.loads(existing_ids_json)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"JSON invalide : {e}"}))
        return

    declared   = entry.get("relations", {}).get("contredit", [])
    confirmed  = [eid for eid in declared if eid in existing_ids]
    unresolved = [eid for eid in declared if eid not in existing_ids]

    print(json.dumps({
        "has_contradictions":   len(declared) > 0,
        "declared":             declared,
        "confirmed_in_registry": confirmed,
        "unresolved_ids":       unresolved,
        "recommendation": (
            "Vérification manuelle requise pour les IDs non résolus"
            if unresolved else
            "Toutes les contradictions déclarées sont connues du registre"
        )
    }, ensure_ascii=False))


# ─────────────────────────────────────────────
#  ALLPATH RUNNER DISPATCHER
# ─────────────────────────────────────────────
DISPATCH = {
    "validate_entry":       validate_entry,
    "compute_confidence":   compute_confidence,
    "generate_id":          generate_id,
    "check_contradictions": check_contradictions,
}



def query_registry(domaine: str, tags_json: str) -> None:
    """
    Simulates a registry query for rules/errors matching a domain and tags.
    In production, this calls the remote registry API.
    For local use, it searches the examples/ directory.
    """
    import os, glob
    try:
        tags = json.loads(tags_json) if tags_json else []
    except json.JSONDecodeError:
        tags = []

    results = []
    examples_dir = os.path.join(os.path.dirname(__file__), "examples")

    if os.path.exists(examples_dir):
        for filepath in glob.glob(os.path.join(examples_dir, "*.json")):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    entry = json.load(f)

                entry_domain = entry.get("taxonomie", {}).get("domaine", "").lower()
                entry_tags   = entry.get("taxonomie", {}).get("tags", [])
                entry_status = entry.get("statut", "")
                score        = entry.get("confiance", {}).get("score", 0)

                domain_match = domaine.lower() in entry_domain or entry_domain in domaine.lower()
                tag_match    = any(t.lower() in [et.lower() for et in entry_tags] for t in tags) if tags else True

                if (domain_match or tag_match) and entry_status == "actif" and score >= 40:
                    results.append({
                        "id":          entry.get("id"),
                        "gravite":     entry.get("contenu", {}).get("gravite"),
                        "type":        entry.get("contenu", {}).get("type"),
                        "description": entry.get("contenu", {}).get("description"),
                        "solution":    entry.get("contenu", {}).get("solution"),
                        "confiance":   score,
                        "tags":        entry_tags
                    })
            except (json.JSONDecodeError, KeyError):
                continue

    results.sort(key=lambda x: x.get("confiance", 0), reverse=True)

    print(json.dumps({
        "rules":       results,
        "total":       len(results),
        "domain":      domaine,
        "tags":        tags,
        "source":      "local_examples (production: remote registry API)",
        "note":        "Only entries with statut='actif' and confiance >= 40 are returned.",
        "injected_at": __import__("datetime").datetime.utcnow().isoformat() + "Z"
    }, ensure_ascii=False))


DISPATCH["query_registry"] = query_registry



# ─────────────────────────────────────────────
#  ENV LOADER — reads .smcu.env at startup
# ─────────────────────────────────────────────
def _load_env():
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".smcu.env")
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    if key not in os.environ:
                        os.environ[key] = value.strip()

_load_env()


# ─────────────────────────────────────────────
#  SUBMIT PR — Autonomous GitHub contribution
# ─────────────────────────────────────────────
def submit_pr(entry_json: str, *flags) -> None:
    """
    Submits a validated SMCU entry as a Pull Request to the central registry.
    Requires GITHUB_TOKEN and GITHUB_USERNAME in .smcu.env or environment.

    Allpath: python main.py submit_pr '<entry_json>'
    Dry run: python main.py submit_pr '<entry_json>' --dry-run
    """
    import urllib.request as _ur
    import urllib.error   as _ue
    import base64         as _b64
    import time           as _t

    dry_run = "--dry-run" in flags

    try:
        entry = json.loads(entry_json)
    except json.JSONDecodeError as e:
        print(json.dumps({"ok": False, "errors": [f"JSON invalide: {e}"]}, ensure_ascii=False))
        return

    required = ["id","taxonomie","contenu","preuve","validation",
                "confiance","statut","source","visibilite","portee","cycle_de_vie"]
    missing = [f for f in required if f not in entry]
    if missing:
        print(json.dumps({"ok": False,
            "errors": [f"Champs manquants: {missing}. Lancer validate_entry d'abord."]},
            ensure_ascii=False))
        return

    entry_id  = entry["id"]
    domain    = entry.get("taxonomie", {}).get("domaine", "general")
    token     = os.environ.get("GITHUB_TOKEN", "")
    gh_user   = os.environ.get("GITHUB_USERNAME", "")
    reg_repo  = os.environ.get("SMCU_REGISTRY_REPO", "Tryboy869/smcu-protocol")
    pseudonym = os.environ.get("SMCU_NODE_PSEUDONYM", gh_user or "anonymous")
    is_draft  = os.environ.get("SMCU_PR_DRAFT", "false").lower() == "true"

    if not token or not gh_user:
        print(json.dumps({"ok": False,
            "errors": ["GITHUB_TOKEN et GITHUB_USERNAME non configurés. Lancer: python setup.py"]},
            ensure_ascii=False))
        return

    owner, repo = reg_repo.split("/")
    ts        = str(int(_t.time()))[-6:]
    branch    = f"smcu/entry-{entry_id.lower()}-{ts}"
    file_path = f"examples/{entry_id.lower().replace('-','_')}.json"
    file_b64  = _b64.b64encode(
        json.dumps(entry, ensure_ascii=False, indent=2).encode()
    ).decode()

    if dry_run:
        print(json.dumps({
            "ok": True, "dry_run": True,
            "branch": branch, "file": file_path, "entry_id": entry_id
        }, ensure_ascii=False))
        return

    def gh(path, method="GET", payload=None):
        url  = f"https://api.github.com{path}"
        data = json.dumps(payload).encode() if payload else None
        req  = _ur.Request(url, data=data, method=method, headers={
            "Authorization": f"token {token}",
            "Accept":        "application/vnd.github.v3+json",
            "Content-Type":  "application/json",
            "User-Agent":    "SMCU-Protocol/1.0"
        })
        with _ur.urlopen(req, timeout=20) as r:
            return json.loads(r.read())

    try:
        default_branch = gh(f"/repos/{owner}/{repo}")["default_branch"]
        base_sha = gh(f"/repos/{owner}/{repo}/git/ref/heads/{default_branch}")["object"]["sha"]
        gh(f"/repos/{owner}/{repo}/git/refs", "POST",
           {"ref": f"refs/heads/{branch}", "sha": base_sha})
        gh(f"/repos/{owner}/{repo}/contents/{file_path}", "PUT", {
            "message": f"feat(entry): add {entry_id} — {domain}",
            "content": file_b64, "branch": branch,
        })
        pr = gh(f"/repos/{owner}/{repo}/pulls", "POST", {
            "title": f"[ENTRY] {domain} — {entry_id}",
            "body": (
                f"## New SMCU Entry\n\n"
                f"**ID:** `{entry_id}` | **Domain:** {domain} | **By:** `{pseudonym}`\n\n"
                f"**Description:** {entry.get('contenu',{}).get('description','')}\n\n"
                f"**Solution:** {entry.get('contenu',{}).get('solution','')}\n\n"
                f"---\n*Awaiting 3 validator votes to merge.*"
            ),
            "head": branch, "base": default_branch, "draft": is_draft,
        })
        pr_url = pr["html_url"]

        # Telegram (non-blocking)
        tg_tok = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        tg_cid = os.environ.get("TELEGRAM_CHAT_ID", "")
        if tg_tok and tg_cid:
            try:
                msg = f"\U0001f344 *SMCU* \u2014 PR soumise\nEntry: `{entry_id}`\nPR: {pr_url}"
                tgd = json.dumps({"chat_id": tg_cid, "text": msg, "parse_mode": "Markdown"}).encode()
                tgr = _ur.Request(
                    f"https://api.telegram.org/bot{tg_tok}/sendMessage",
                    data=tgd, headers={"Content-Type": "application/json"}
                )
                _ur.urlopen(tgr, timeout=5)
            except Exception:
                pass

        print(json.dumps({
            "ok": True, "pr_url": pr_url, "branch": branch,
            "file": file_path, "entry_id": entry_id, "errors": []
        }, ensure_ascii=False))

    except _ue.HTTPError as e:
        print(json.dumps({"ok": False,
            "errors": [f"GitHub HTTP {e.code}: {e.read().decode()[:200]}"]},
            ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"ok": False, "errors": [str(e)]}, ensure_ascii=False))


DISPATCH["submit_pr"] = submit_pr


# ─────────────────────────────────────────────
#  ALLPATH RUNNER — MAIN DISPATCHER
# ─────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "error":     "Nom de fonction requis",
            "usage":     "python main.py <fonction> [args...]",
            "fonctions": list(DISPATCH.keys())
        }, ensure_ascii=False))
        sys.exit(1)

    func_name = sys.argv[1]
    args      = sys.argv[2:]

    if func_name not in DISPATCH:
        print(json.dumps({
            "error":       f"Fonction inconnue : '{func_name}'",
            "disponibles": list(DISPATCH.keys())
        }, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    DISPATCH[func_name](*args)
