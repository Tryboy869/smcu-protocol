# SMCU Protocol — Features Map
> **AI Contribution Changelog**
> This file is the authoritative registry of every feature, function, file,
> dependency, import, and export in this repository.
> Read this before contributing. Keep it updated with every PR.

---

## Purpose of This File

This is not documentation for humans. This is a **machine-readable map**
designed so that any AI agent can:

1. Understand the full structure of the repo without reading every file
2. Know exactly where to add new features or entries
3. Understand what each function consumes and produces
4. Avoid breaking existing integrations when contributing

**Rule:** Any PR that adds or modifies a function, file, or dependency
MUST update this file in the same commit.

---

## Repository Structure Registry

```
smcu-protocol/
│
├── [PROTOCOL CORE]
│   ├── schema.json           → Canonical JSON Schema (source of truth for entry format)
│   ├── SPECIFICATION.md      → Protocol rules (human + AI readable)
│   └── AGENT_GUIDE.md        → Primary onboarding file for AI agents
│
├── [EXECUTION LAYER - Allpath Runner Package]
│   ├── allpath.expose.json   → Package manifest (declares functions to Allpath daemon)
│   └── main.py               → All executable functions (Python 3.8+, zero deps)
│
├── [DOCUMENTATION]
│   ├── README.md             → English overview + GitHub landing page
│   ├── README.fr.md          → French overview
│   ├── GOVERNANCE.md         → RFC process + Technical Committee rules
│   ├── CONTRIBUTING.md       → How to contribute entries and code
│   ├── CHANGELOG.md          → Version history (human-readable)
│   ├── SECURITY.md           → Vulnerability reporting
│   ├── CODE_OF_CONDUCT.md    → Community standards
│   ├── LICENSE               → MIT License
│   └── features.md           → This file (AI changelog + repo map)
│
├── [ASSETS]
│   ├── assets/logo-animated.svg   → Animated header (900×220, loops infinitely)
│   ├── assets/footer.svg          → Footer (900×80, loops infinitely)
│   └── assets/card-daouda.svg     → Creator card (480×200)
│
├── [DOCS - Deep Guides]
│   ├── docs/getting-started.md    → Quickstart (3 integration modes)
│   ├── docs/anonymity-system.md   → ZKP + 3 visibility levels explained
│   ├── docs/confidence-score.md   → Score formula, thresholds, anti-gaming
│   └── docs/faq.md                → 12 common questions answered
│
├── [EXAMPLES - Live Registry Entries]
│   ├── examples/software-dev.json → DEV-ERR-JWT01 (critique, score 91.2)
│   ├── examples/medical.json      → MED-WARN-DRUG01 (critique, score 78.4)
│   └── examples/robotics.json     → ROB-ERR-SURFACE01 (majeur, score 67.3)
│
└── [VALIDATOR - Standalone CLI]
    ├── validator/validate.py  → Python validator CLI
    └── validator/validate.js  → JavaScript validator CLI
```

---

## Function Registry — main.py

### `validate_entry(entry_json: str) → None`

| Property | Value |
|---|---|
| **Purpose** | Validates an SMCU entry against all protocol rules |
| **Input** | JSON string of a complete SMCU entry |
| **Output** | JSON to stdout: `{ valid, errors[], warnings[], entry_id, score }` |
| **Imports** | `sys`, `json` (stdlib only) |
| **Exports** | None (prints to stdout for Allpath capture) |
| **Depends on** | Constants: `REQUIRED_FIELDS`, `VALID_STATUTS`, `VALID_GRAVITES`, `VALID_TYPES`, `VALID_VISIBILITE`, `VALID_PREUVES` |
| **Called by** | Allpath daemon, validator/validate.py, CI pipelines, PR automation |
| **Side effects** | None |
| **Error handling** | Returns `{ valid: false, errors: ["JSON invalide: ..."] }` on parse failure |
| **Allpath arg** | `python main.py validate_entry '<json_string>'` |

---

### `compute_confidence(votes_positifs: str, votes_total: str, nb_utilisations: str) → None`

| Property | Value |
|---|---|
| **Purpose** | Computes the official SMCU confidence score |
| **Input** | Three string-encoded integers (Allpath convention) |
| **Output** | JSON: `{ score, interpretation, votes_positifs, votes_total, nb_utilisations, formule }` |
| **Formula** | `min((vp / vt) × log(nu + 1) × 100, 100.0)` |
| **Imports** | `sys`, `json`, `math` |
| **Exports** | None |
| **Interpretation map** | `≥80 → critique` / `≥50 → modere` / `<50 → faible` |
| **Edge case** | Returns `{ score: 0 }` when `votes_total == 0` |
| **Allpath arg** | `python main.py compute_confidence 3 3 847` |

---

### `generate_id(domaine: str, type_entree: str) → None`

| Property | Value |
|---|---|
| **Purpose** | Generates a unique SMCU entry ID |
| **Input** | Domain name (string), entry type (string) |
| **Output** | JSON: `{ id, domaine, type, note }` |
| **Format** | `{DOMAIN_PREFIX}-{TYPE_SUFFIX}-{MD5_HASH_4CHARS}` |
| **Imports** | `sys`, `json`, `hashlib`, `time` |
| **Exports** | None |
| **Depends on** | `DOMAIN_PREFIXES` dict, `TYPE_SUFFIXES` dict |
| **Uniqueness** | MD5 of `domaine + type_entree + timestamp`. Collision probability negligible for normal use. |
| **Allpath arg** | `python main.py generate_id "médecine" "erreur"` |

**DOMAIN_PREFIXES registry (extend here when adding domains):**

```python
DOMAIN_PREFIXES = {
    "développement logiciel": "DEV",
    "médecine":               "MED",
    "robotique":              "ROB",
    "finance":                "FIN",
    "sécurité":               "SEC",
    "éducation":              "EDU",
    # ADD NEW DOMAINS HERE — also update SPECIFICATION.md §7
}
```

**TYPE_SUFFIXES registry:**

```python
TYPE_SUFFIXES = {
    "erreur":         "ERR",
    "regle":          "RULE",
    "avertissement":  "WARN",
    "bonne_pratique": "BP",
}
```

---

### `check_contradictions(entry_json: str, existing_ids_json: str) → None`

| Property | Value |
|---|---|
| **Purpose** | Checks if declared contradictions in an entry match known registry IDs |
| **Input** | Entry JSON string + JSON array of existing IDs |
| **Output** | JSON: `{ has_contradictions, declared[], confirmed_in_registry[], unresolved_ids[], recommendation }` |
| **Imports** | `sys`, `json` |
| **Logic** | Compares `entry.relations.contredit[]` against `existing_ids` list |
| **Does NOT** | Access the live registry — caller must supply existing IDs |
| **Allpath arg** | `python main.py check_contradictions '<entry>' '["ID-1","ID-2"]'` |

---

### `query_registry(domaine: str, tags_json: str) → None`

| Property | Value |
|---|---|
| **Purpose** | Queries local examples/ directory for matching active rules |
| **Input** | Domain string + JSON array of tags |
| **Output** | JSON: `{ rules[], total, domain, tags, source, note, injected_at }` |
| **Imports** | `sys`, `json`, `os`, `glob`, `datetime` |
| **Filters** | `statut == "actif"` AND `confiance.score >= 40` |
| **Matching** | Domain: substring match (both directions). Tags: any-match (case-insensitive) |
| **Sort** | Results sorted by `confiance.score` descending |
| **Source** | `"local_examples"` in this version. Remote API in future registry server. |
| **Allpath arg** | `python main.py query_registry "médecine" '["interaction"]'` |

> **For contributors:** When the remote registry API is built (Phase 3),
> this function must be updated to call `https://registry.smcu.io/v1/query`
> with a fallback to local files when offline.

---

## Schema Registry — schema.json

**Version:** 1.0.0
**Format:** JSON Schema Draft-07

| Section | Required | Description |
|---|---|---|
| `id` | Yes | Pattern: `^[A-Z]{2,6}-[A-Z]{2,8}-[A-Z0-9]{4}$` |
| `taxonomie` | Yes | 4 required sub-fields + optional tags |
| `contenu` | Yes | type, gravite, description, solution + optional exemple |
| `preuve` | Yes | type (enum) + optional reference URL |
| `validation` | Yes | votes_requis ≥ 3 + votes array with decision enum |
| `confiance` | Yes | score 0–100 + optional usage counters |
| `statut` | Yes | One of 6 lifecycle states |
| `relations` | No | parent, contredit[], remplace, lie_a[] |
| `source` | Yes | affichage enum + DID/pseudonyme/ZKP logic |
| `visibilite` | Yes | niveau enum + optional organisation_id |
| `portee` | No | juridictions[], langues[] |
| `cycle_de_vie` | Yes | date_creation required + optional dates |

**`additionalProperties: false`** — no unknown fields allowed at root level.

---

## Validator Registry — validator/

### `validate.py`

| Property | Value |
|---|---|
| **Runtime** | Python 3.8+ |
| **Dependencies** | None (stdlib only: sys, json, math, os) |
| **Usage** | `python validate.py <path_to_entry.json> [--json]` |
| **Exit codes** | `0` = valid, `1` = invalid or error |
| **Output modes** | Colored terminal report (default) + raw JSON (with `--json`) |
| **Imports from** | Nothing in this repo (standalone) |
| **Validates** | All 12 required sections + cross-field consistency |

### `validate.js`

| Property | Value |
|---|---|
| **Runtime** | Node.js 14+ |
| **Dependencies** | None (stdlib only: fs, path) |
| **Usage** | `node validate.js <path_to_entry.json> [--json]` |
| **Exit codes** | `0` = valid, `1` = invalid or error |
| **Mirrors** | validate.py exactly — keep both in sync when updating rules |

---

## Allpath Manifest Registry — allpath.expose.json

**Functions declared (must stay in sync with main.py):**

| Function | Args | Return type |
|---|---|---|
| `validate_entry` | `entry_json: string` | `object` |
| `compute_confidence` | `votes_positifs: integer, votes_total: integer, nb_utilisations: integer` | `object` |
| `generate_id` | `domaine: string, type_entree: string` | `object` |
| `check_contradictions` | `entry_json: string, existing_ids_json: string` | `object` |
| `query_registry` | `domaine: string, tags_json: string` | `object` |

> **Rule:** Any new function added to `main.py` MUST be declared in
> `allpath.expose.json` under `functions[]` with full param/return docs.

---

## Example Registry — examples/

Each file in `examples/` is a live SMCU entry that:
1. Validates against `schema.json` with zero errors
2. Is used by `query_registry` as the local data source
3. Serves as a reference template for contributors

**Current entries:**

| File | ID | Domain | Type | Gravity | Score |
|---|---|---|---|---|---|
| `software-dev.json` | DEV-ERR-JWT01 | Développement logiciel | erreur | critique | 91.2 |
| `medical.json` | MED-WARN-DRUG01 | Médecine | avertissement | critique | 78.4 |
| `robotics.json` | ROB-ERR-SURFACE01 | Robotique | regle | majeur | 67.3 |

**To add an entry:**
1. Run `python main.py generate_id "<domaine>" "<type>"` → get your ID
2. Copy the closest example as template
3. Fill all required fields
4. Run `python validator/validate.py examples/your-file.json` → must show `✅ VALIDE`
5. Open a PR — title format: `[ENTRY] DOMAIN-TYPE-ID — Short description`

---

## Dependency Graph

```
schema.json
    ↓ (referenced by)
allpath.expose.json
    ↓ (declares)
main.py
    ├── validate_entry()
    │     ↓ uses constants defined at top of main.py
    ├── compute_confidence()
    │     ↓ uses math.log
    ├── generate_id()
    │     ↓ uses DOMAIN_PREFIXES, TYPE_SUFFIXES, hashlib, time
    ├── check_contradictions()
    │     ↓ pure logic, no dependencies
    └── query_registry()
          ↓ reads examples/*.json from filesystem
          ↓ future: calls remote registry API

validator/validate.py
    ↓ mirrors main.py validation logic
    ↓ standalone (does NOT import main.py)

validator/validate.js
    ↓ mirrors validator/validate.py
    ↓ standalone

examples/*.json
    ↓ consumed by query_registry()
    ↓ must pass validator/validate.py
    ↓ must conform to schema.json
```

---

## Constants Registry

All constants are defined at the top of `main.py`. When adding a new
entry type, domain, or status, update ALL of the following:

| Constant | Location | Purpose |
|---|---|---|
| `REQUIRED_FIELDS` | main.py:14 | Top-level fields that must be present |
| `VALID_STATUTS` | main.py:22 | Entry lifecycle states |
| `VALID_GRAVITES` | main.py:23 | Severity levels |
| `VALID_TYPES` | main.py:24 | Entry types |
| `VALID_VISIBILITE` | main.py:25 | Visibility levels |
| `VALID_PREUVES` | main.py:26 | Accepted proof types |
| `DOMAIN_PREFIXES` | main.py:28 | Domain → 3-letter prefix mapping |
| `TYPE_SUFFIXES` | main.py:38 | Entry type → suffix mapping |

Mirror constants also exist in:
- `validator/validate.py` (must be kept identical)
- `validator/validate.js` (must be kept identical)
- `schema.json` (enums must match)

---

## Contribution Checklist for AI Agents

When opening a PR, verify:

**For a new example entry:**
- [ ] `python main.py generate_id` used to create the ID
- [ ] File placed in `examples/` with name `{domain-abbrev}-{short-desc}.json`
- [ ] `python validator/validate.py examples/your-file.json` returns `✅ VALIDE`
- [ ] Entry uses only anonymized data (no client names, no proprietary URLs)
- [ ] `features.md` updated: new row added to Example Registry table
- [ ] `CHANGELOG.md` updated under `[Unreleased]`

**For a new function in main.py:**
- [ ] Function added to `DISPATCH` dict
- [ ] Function declared in `allpath.expose.json` under `functions[]`
- [ ] Matching logic added to `validator/validate.py` and `validator/validate.js`
- [ ] New constants added to Constants Registry table above
- [ ] Function Registry table above updated
- [ ] `CHANGELOG.md` updated

**For a new domain:**
- [ ] Added to `DOMAIN_PREFIXES` in `main.py`
- [ ] Added to canonical domains list in `SPECIFICATION.md §7`
- [ ] Added to `validator/validate.py` and `validator/validate.js`
- [ ] At least one example entry created in `examples/`
- [ ] Governance RFC opened if domain is truly new (see `GOVERNANCE.md`)

---

## Version History of This File

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-20 | Initial creation. Full registry of v1.0.0 repo state. |

---

## Configuration Layer Registry (v1.1 addition)

### `setup.py` — One-time node configuration

| Property | Value |
|---|---|
| **Purpose** | Interactive wizard to configure a local SMCU node |
| **Run once** | `python setup.py` |
| **Installs** | Allpath Runner (downloads `allpath-runner.py`) |
| **Configures** | GitHub token, username, node pseudonym, Telegram bot |
| **Saves** | All credentials to `.smcu.env` (gitignored) |
| **Tests** | GitHub API, Telegram, local query, validator |
| **Imports** | `sys`, `os`, `json`, `urllib`, `subprocess`, `hashlib`, `datetime`, `getpass` (stdlib only) |
| **No deps** | Zero external packages required |

---

### `.env.example` — Credentials template

| Variable | Required | Purpose |
|---|---|---|
| `GITHUB_TOKEN` | Yes | PR creation and branch push |
| `GITHUB_USERNAME` | Yes | PR author attribution |
| `SMCU_REGISTRY_REPO` | Yes | Target registry (default: Tryboy869/smcu-protocol) |
| `SMCU_NODE_PSEUDONYM` | Yes | Persistent registry identity (e.g. DevAgent-EU-01) |
| `SMCU_NODE_DID` | Yes | Cryptographic DID (generated by setup.py from pseudonym) |
| `TELEGRAM_BOT_TOKEN` | No | Notification bot |
| `TELEGRAM_CHAT_ID` | No | Target chat for notifications |
| `SMCU_CONFIDENCE_THRESHOLD` | No | Min score to auto-apply rules (default: 40) |
| `SMCU_AUTO_NOTIFY` | No | Send Telegram on PR events (default: true) |
| `SMCU_PR_DRAFT` | No | Open PRs as draft (default: false) |

**Auto-loaded by:** `main.py` via `_load_env()` at module startup.

---

### `tools/submit_pr.py` — Standalone PR submission

| Property | Value |
|---|---|
| **Purpose** | Standalone script for PR submission (can be used without Allpath) |
| **Usage** | `python tools/submit_pr.py examples/my-entry.json` |
| **Dry run** | `python tools/submit_pr.py examples/my-entry.json --dry-run` |
| **Imports** | `os`, `sys`, `json`, `urllib`, `base64`, `datetime`, `time` (stdlib only) |
| **Reads from** | `.smcu.env` via `_load_env()` |
| **Calls** | GitHub API: create branch → push file → open PR |
| **Notifies** | `tools/notify_telegram.py` (non-blocking) |

---

### `tools/notify_telegram.py` — Telegram notifications

| Function | Purpose |
|---|---|
| `notify(message, emoji)` | Generic notification |
| `notify_pr_submitted(entry_id, pr_url, domain)` | PR created |
| `notify_pr_approved(entry_id, pr_url, score)` | PR merged |
| `notify_pr_rejected(entry_id, pr_url, reason)` | PR rejected |
| `notify_query_result(domain, count, top_rule)` | Registry query audit |

**Imports:** `os`, `sys`, `json`, `urllib`, `datetime` (stdlib only)
**Reads from:** `.smcu.env` via `_load_env()`
**Non-blocking:** All notification failures are silently swallowed — they never break the main workflow.

---

## `submit_pr` Function (in main.py)

| Property | Value |
|---|---|
| **Purpose** | Autonomous GitHub PR contribution from any AI agent |
| **Full flow** | validate → load env → create branch → push file → open PR → notify Telegram |
| **Branch format** | `smcu/entry-{entry_id_lower}-{timestamp_6}` |
| **File created** | `examples/{entry_id_lower_no_dash}.json` |
| **Imports** | `urllib.request`, `urllib.error`, `base64`, `time` (all stdlib) |
| **Reads from** | `GITHUB_TOKEN`, `GITHUB_USERNAME`, `SMCU_REGISTRY_REPO`, `SMCU_NODE_PSEUDONYM`, `SMCU_PR_DRAFT`, `TELEGRAM_*` from os.environ |
| **Allpath arg** | `python main.py submit_pr '<entry_json>' [--dry-run]` |
| **Dry run** | Returns branch/file names without hitting GitHub API |
| **Pre-flight** | Checks all 11 required fields before any API call |
| **Error handling** | Returns `{ ok: false, errors: [...] }` on any failure — never raises |

---

## Version History of This File

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-20 | Initial creation. Full registry of v1.0.0 repo state. |
| 1.1.0 | 2026-06-20 | Added configuration layer: setup.py, .env.example, tools/, submit_pr function, _load_env, query_registry in allpath manifest. |
