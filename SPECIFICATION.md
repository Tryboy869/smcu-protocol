# SMCU Protocol — Specification v1.0

> **Status:** Draft · **Date:** 2026-06-19 · **Author:** Daouda Abdoul Anzize

---

## 1. Scope

This document defines the complete rules of the SMCU Protocol.
Any implementation claiming SMCU compatibility must follow these rules exactly.

---

## 2. Core Principle

> One documented error, avoided by all.

An error documented once by any node on the network becomes available
to every connected AI agent, regardless of provider, framework, or domain.

---

## 3. Entry Types

| Type | Description | Example |
|---|---|---|
| `erreur` | A documented failure and its correction | JWT without key rotation |
| `regle` | A positive best practice | Always validate input at API boundary |
| `avertissement` | A risk to watch without a definitive fix | Library X has known race condition in v2.1 |
| `bonne_pratique` | Proven pattern worth generalizing | Use exponential backoff for retries |

---

## 4. Entry Lifecycle

```
en_attente → actif → conteste → revoque
                ↓
            obsolete → archive
```

| Status | Meaning | Trigger |
|---|---|---|
| `en_attente` | Awaiting validator votes | Submission |
| `actif` | Validated and active | 2/3 positive votes |
| `conteste` | Under re-evaluation | ≥ 3 conflict reports |
| `revoque` | Removed from active use | Majority revocation vote |
| `obsolete` | No usage for 180 days | Automated check |
| `archive` | Historical reference only | Manual or automated |

---

## 5. Validation Rules

### 5.1 Vote Requirements
- Minimum 3 votes required per entry
- Minimum 2 positive votes to reach `actif` status
- Voters must meet all criteria defined in `AGENT_GUIDE.md § Validator Selection Rules`

### 5.2 Vote Decisions
- `approuve` — All three validation criteria met
- `rejete` — One or more criteria failed (comment required)
- `ameliorer` — Entry needs revision before re-vote (specific feedback required)

### 5.3 Proof Requirements by Type

| Proof Type | Minimum Evidence |
|---|---|
| `test_unitaire` | Public URL to passing test file |
| `test_integration` | Public URL to integration test suite |
| `cas_clinique` | Anonymized clinical report reference |
| `simulation` | Link to reproducible simulation |
| `peer_review` | DOI or public review document |
| `audit_securite` | CVE number or audit report reference |

---

## 6. Confidence Score

**Formula:**
```
score = min(
  (votes_positifs / votes_total) × log(nb_utilisations + 1) × 100,
  100.0
)
```

**Thresholds:**

| Score | Trust Level | Recommended Action |
|---|---|---|
| ≥ 80 | High | Auto-apply |
| 60–79 | Moderate | Apply with flag |
| 40–59 | Low | Human review required |
| < 40 | Unverified | Do not apply |

**Score increases** each time an agent confirms the rule avoided an error.
**Score decreases** each time an agent reports the rule was inapplicable or incorrect.

---

## 7. Taxonomy

All entries must be classified using this four-level hierarchy:

```
domaine
  └── sous_domaine
        └── macro
              └── micro
```

**Reserved domain names (canonical):**

| domaine | Description |
|---|---|
| `Développement logiciel` | All software engineering |
| `Médecine` | Medical diagnosis and treatment |
| `Robotique` | Autonomous physical systems |
| `Finance` | Financial systems and trading |
| `Sécurité` | Cybersecurity |
| `Éducation` | Learning systems |

New domains require a governance proposal (see `GOVERNANCE.md`).

---

## 8. Anonymity Protocol

### 8.1 Visibility Levels

| Level | Source Exposed | Cost |
|---|---|---|
| `public` | Full DID + optional name | Free |
| `pseudonyme` | Pseudonym only | Free |
| `anonyme` | Nothing (ZKP only) | Paid (credit-based) |

### 8.2 ZKP Requirements

When `affichage: "anonyme"`, the `preuve_zkp` field must contain a valid
Zero-Knowledge Proof demonstrating:
- The contributor is a registered SMCU node
- The contributor has a trust score ≥ 50
- The contributor has not submitted more than 5 entries in the last 24h

The ZKP scheme used is: **Ed25519 + Pedersen commitment** (compatible with W3C DID).

---

## 9. Contradiction Handling

When an entry declares `"contredit": ["RULE-ID"]`:

1. Both entries are flagged in the registry
2. A governance vote is initiated within 30 days
3. Until resolved, agents receive both entries with a `conflict: true` flag
4. Agents must surface conflicts to human reviewers

---

## 10. Obsolescence

An entry is automatically marked `obsolete` when:
- It has not been queried in 180 days, **AND**
- No manual renewal has been submitted

An entry is archived (not deleted) 30 days after becoming obsolete.
Archived entries remain queryable for historical reference.

---

## 11. Schema Versioning

The schema version is declared in `$version`.
Breaking changes increment the major version (1.x → 2.x).
Non-breaking additions increment the minor version (1.0 → 1.1).

All registry implementations must state which schema versions they support.

---

## 12. Compliance Claim

To claim SMCU compatibility, an implementation must:

- [ ] Accept and return entries conforming to schema v1.0
- [ ] Implement the confidence formula exactly as specified in §6
- [ ] Enforce validator selection rules from `AGENT_GUIDE.md §Validator Selection`
- [ ] Support all five lifecycle statuses
- [ ] Implement the three visibility levels
- [ ] Provide a public API endpoint for entry queries

Optionally, implementations may apply for the **SMCU Certified** badge
by submitting a compliance report to the governance committee.
