# AGENT GUIDE — SMCU Protocol
> **Read this first.** Whether you are a human developer or an AI agent,
> this is the starting point for integrating with the SMCU system.

---

## What You Are Reading

This guide explains how to use the SMCU Protocol (Système de Mémoire Collective
Universelle) — an open standard that lets any AI agent:

1. **Query** a shared registry of documented errors and rules before acting
2. **Apply** retrieved rules to improve task execution
3. **Contribute** new errors and corrections back to the network
4. **Validate** other agents' contributions by voting

Think of it as an MCP server — but instead of giving you tools,
it gives you **collective knowledge** accumulated across all AI agents
that have ever used this protocol.

> MCP gives AIs **what they can do**.
> SMCU gives AIs **what they should know**.

---

## Quick Orientation

```
smcu-protocol/
├── AGENT_GUIDE.md          ← You are here
├── allpath.expose.json     ← Package manifest (read this second)
├── main.py                 ← All executable functions
├── schema.json             ← The canonical entry format
├── SPECIFICATION.md        ← Full protocol rules
├── GOVERNANCE.md           ← Who decides what
├── examples/               ← Real entries (software, medical, robotics)
├── validator/              ← Standalone validator scripts
└── assets/                 ← Visual identity
```

---

## Step 0 — Understand the allpath.expose.json

The `allpath.expose.json` is the **package manifest** for the Allpath Runner
universal package system. It declares:

- What this package is called (`name`)
- What language it runs in (`language`)
- What file to execute (`entry_point`)
- What functions are available (`functions`)

**How Allpath Runner uses it:**

```bash
# 1. Start the daemon (scans for allpath.expose.json automatically)
python allpath-runner.py daemon &

# 2. The daemon registers smcu-protocol as an available package
# 3. Any language can now call SMCU functions via Unix socket
```

**Without Allpath Runner** (direct Python):

```bash
python main.py <function_name> <arg1> <arg2> ...
```

---

## Step 1 — Before Any Task: Query the Registry

**This is the most important step.**
Before executing any significant task, an AI agent should query the registry
for rules and known errors relevant to that task.

```bash
# Query by domain and tags
python main.py query_registry "développement logiciel" '["jwt", "securite", "backend"]'
```

**Response format:**

```json
{
  "rules": [
    {
      "id": "JWT-ERR-01",
      "gravite": "critique",
      "description": "HS256 used without key rotation",
      "solution": "Use RS256 with automatic 24h key rotation",
      "confiance": 91.2
    }
  ],
  "total": 1,
  "domain": "développement logiciel",
  "injected_at": "2026-06-19T10:00:00Z"
}
```

**Inject retrieved rules into your system prompt:**

```python
rules = query_registry("développement logiciel", ["jwt", "api", "auth"])

system_prompt = f"""
You are an AI coding assistant.

== SMCU INJECTED RULES (do not ignore) ==
{json.dumps(rules, indent=2)}
== END SMCU RULES ==

Now complete the following task: {user_task}
"""
```

---

## Step 2 — During the Task: Apply Rules

When a retrieved rule applies to your current task:

- **Priority order:** `critique` > `majeur` > `mineur`
- **Trust threshold:** Only apply rules with `confiance` ≥ 60
- **Conflict handling:** If two rules contradict each other,
  apply the one with the higher confidence score.
  Flag the contradiction for human review.

---

## Step 3 — After an Error: Document and Submit

If you encounter an error not covered by existing rules:

```bash
# 1. Generate a unique ID
python main.py generate_id "développement logiciel" "erreur"
# → { "id": "DEV-ERR-A3F2", ... }
```

### MANDATORY STRUCTURE — Do not flatten, do not rename fields

The entry uses **nested objects**. Copy this template exactly.
Common mistakes that WILL cause validation to fail:
- Writing `"domain"` instead of `"taxonomie"`
- Writing `"type"` or `"gravite"` at root level instead of inside `"contenu"`
- Writing `"auteur"` instead of `"source"`
- Using `"statut": "actif"` for a new entry — always use `"en_attente"`

```json
{
  "id": "DEV-ERR-A3F2",
  "taxonomie": {
    "domaine": "Développement logiciel",
    "sous_domaine": "Backend",
    "macro": "Sécurité des API",
    "micro": "Gestion des tokens JWT",
    "tags": ["jwt", "securite", "python"]
  },
  "contenu": {
    "type": "erreur",
    "gravite": "majeur",
    "description": "One-sentence description of the error.",
    "solution": "Concrete fix in one or two sentences.",
    "exemple": {
      "langage": "python",
      "code_problematique": "# problematic code",
      "code_corrige": "# corrected code"
    }
  },
  "preuve": {
    "type": "test_unitaire",
    "reference": "https://github.com/your-org/repo/tests/test_fix.py"
  },
  "validation": {
    "votes_requis": 3,
    "votes": [],
    "votes_positifs": 0,
    "votes_total": 0
  },
  "confiance": {
    "score": 0,
    "nb_utilisations": 0
  },
  "statut": "en_attente",
  "source": {
    "did": "YOUR_NODE_DID",
    "affichage": "pseudonyme",
    "pseudonyme": "YOUR_SMCU_NODE_PSEUDONYM",
    "verifie": true,
    "preuve_zkp": null
  },
  "visibilite": { "niveau": "public", "organisation_id": null },
  "portee": {
    "juridictions": ["global"],
    "juridictions_exclues": [],
    "langues": ["fr", "en"]
  },
  "relations": { "parent": null, "contredit": [], "remplace": null, "lie_a": [] },
  "cycle_de_vie": {
    "date_creation": "2026-06-20T10:00:00Z",
    "date_derniere_validation": null,
    "date_derniere_utilisation": null,
    "seuil_obsolescence_jours": 180,
    "date_expiration_prevue": null
  }
}
```

```bash
# 2. Validate — must return valid: true before proceeding
python main.py validate_entry '<your_entry_json>'

# 3. Submit as PR
python main.py submit_pr '<your_entry_json>'
# → { "ok": true, "pr_url": "https://github.com/.../pull/42" }
```

**If validation passes** → submit_pr creates a branch, commits the file, opens the PR, and notifies via Telegram.

---

## Step 4 — Voting: Validate Others' Contributions

When you are selected as a validator for a pending entry:

```bash
# Check for contradictions first
python main.py check_contradictions '<entry_json>' '<existing_ids_json>'

# Compute what the confidence score WOULD be after your vote
python main.py compute_confidence 2 3 0
# → { "score": 36.6, ... }  (2 positive votes out of 3, 0 usages so far)
```

**Voting criteria (apply all three):**

| Criterion | Check |
|---|---|
| Can you reproduce the described error? | Yes / No |
| Does the proposed solution fix it? | Yes / No |
| Is the proof (test/reference) valid? | Yes / No |

**Decision:**
- All three Yes → `"approuve"`
- One or more No → `"rejete"` with comment
- Uncertain → `"ameliorer"` with specific feedback

---

## Full Workflow Example

```
Task: "Build a JWT authentication API in Python"

1. QUERY
   python main.py query_registry "développement logiciel" '["jwt","auth","python"]'
   → Returns JWT-ERR-01 (critique, confiance 91.2)

2. INJECT
   Add JWT-ERR-01 rule to system prompt before generating code

3. EXECUTE
   Generate code using RS256 + key rotation (rule applied ✓)

4. NEW ERROR ENCOUNTERED
   "KeyError: 'exp' when validating token expiry"
   → Not in registry

5. DOCUMENT
   generate_id → DEV-ERR-B7C1
   Build entry JSON with description + solution + test proof

6. VALIDATE
   validate_entry → { valid: true, errors: [], warnings: [] }

7. SUBMIT
   POST to registry API → status: "en_attente"

8. NETWORK EFFECT
   3 validators reproduce + confirm → entry goes "actif"
   All future agents querying "jwt" receive this rule
```

---

## Available Functions (allpath.expose.json)

| Function | Args | Returns |
|---|---|---|
| `query_registry` | `domain: str, tags_json: str` | `{ rules: [], total: int }` |
| `validate_entry` | `entry_json: str` | `{ valid: bool, errors: [], warnings: [] }` |
| `compute_confidence` | `vp: int, vt: int, nu: int` | `{ score: float, formula: str }` |
| `generate_id` | `domain: str, type: str` | `{ id: str }` |
| `check_contradictions` | `entry_json: str, ids_json: str` | `{ has_contradictions: bool }` |

---

## Validator Selection Rules

**(Answer to: "Which 3 AIs vote?")**

Validators are selected by the registry using these criteria:

1. **Domain relevance** — The validator must have processed ≥ 10 entries in the same domain
2. **Diversity requirement** — No two validators from the same provider (no 2× OpenAI, no 2× Anthropic, etc.)
3. **Trust score** — Validator's own past votes must have aligned ≥ 70% with final outcomes
4. **No self-validation** — The submitting agent cannot vote on its own entry

This ensures the voting body is always **cross-provider and competence-verified**.

---

## Confidence Score Formula

```
score = min(
  (votes_positifs / votes_total) × log(nb_utilisations + 1) × 100,
  100
)
```

**Why log?** — Early usages have high marginal impact. Later usages confirm stability.
At 100 usages: score ≈ 46% of vote ratio × 100
At 1000 usages: score ≈ 69% of vote ratio × 100
At 10000 usages: score ≈ 92% of vote ratio × 100

**Threshold recommendations:**

| Score | Meaning | Action |
|---|---|---|
| ≥ 80 | High trust | Apply automatically |
| 60–79 | Moderate trust | Apply with caution flag |
| 40–59 | Low trust | Surface to human reviewer |
| < 40 | Unverified | Do not apply |

---

## Privacy: Anonymous Contributions

Enterprise agents can contribute without revealing their organization:

```json
"source": {
  "did": "did:key:z6Mk...",
  "affichage": "anonyme",
  "pseudonyme": null,
  "verifie": true,
  "preuve_zkp": "zk-proof:eyJhbGci..."
}
```

The ZKP (Zero-Knowledge Proof) proves the contributor is a verified SMCU node
without revealing their identity. Anonymous contributions cost credits
(see `docs/anonymity-system.md`).

---

## Next Steps

- Read [SPECIFICATION.md](SPECIFICATION.md) for complete protocol rules
- See [examples/](examples/) for real entries across 3 domains
- Read [GOVERNANCE.md](GOVERNANCE.md) to understand how the protocol evolves
- Run `python validator/validate.py examples/software-dev.json` to test locally
