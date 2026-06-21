# SMCU Protocol — Governance

> Model inspired by the W3C and Linux Foundation.
> The protocol belongs to the community, not to any single organization.

---

## Principles

1. **No single company controls the standard.** Anthropic, OpenAI, Google, or any other AI provider may participate but cannot unilaterally change the protocol.
2. **Changes require community consensus.** Protocol evolution follows a structured RFC process.
3. **Transparency is mandatory.** All decisions are public and archived.

---

## Decision Tiers

### Tier 1 — Schema Changes (breaking)
Requires a **super-majority (2/3) vote** from the Technical Committee.
Example: adding a required field, changing the confidence formula.

### Tier 2 — Schema Additions (non-breaking)
Requires a **simple majority (1/2 + 1)** from the Technical Committee.
Example: adding an optional field, adding a new proof type.

### Tier 3 — Documentation / Examples
Any contributor with Maintainer status can merge via pull request.
No committee vote required.

### Tier 4 — New Domain Names
Requires a public RFC with a 14-day comment period + Technical Committee vote.

---

## Technical Committee

**Composition:**
- 5 to 9 members
- No more than 2 members from the same organization
- Members serve 12-month rotating terms
- Initial committee appointed by the creator, then elected by the community

**Current founding member:**
- Daouda Abdoul Anzize (Cotonou, Bénin) — Protocol Creator

**Joining the committee:**
Open a GitHub Issue with the title `[COMMITTEE] Application — Your Name`.
Requirements: ≥ 5 merged contributions, ≥ 3 months active participation.

---

## RFC Process (Request for Comments)

```
1. OPEN ISSUE  →  Title: [RFC] Your proposal title
2. DRAFT       →  30 days public comment period
3. VOTE        →  Technical Committee votes over 7 days
4. IMPLEMENT   →  If approved, reference implementation in 60 days
5. PUBLISH     →  New schema version released with CHANGELOG entry
```

---

## Validator Independence

The validator selection algorithm (see `AGENT_GUIDE.md`) is **part of the protocol spec**
and cannot be changed by any single registry operator.
Any registry claiming SMCU compatibility must implement it exactly.

This prevents any company from stacking their own models as validators.

---

## Dispute Resolution

If two valid entries contradict each other:

1. Both entries receive a `conteste` flag
2. A dispute RFC is opened with both entries linked
3. The Technical Committee has 30 days to resolve
4. Resolution options: merge, supersede one, or keep both with explicit scope tags

---

## Amendments to This Document

This document itself requires a Tier 1 vote to amend.
