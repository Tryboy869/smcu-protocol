# FAQ — SMCU Protocol

---

**Q: What is the difference between SMCU and Spark / Agent KB?**

Spark and Agent KB solve the collective memory problem for a specific
use case (software coding) and within a specific framework or company.
SMCU is the open protocol layer beneath them — multi-domain,
cross-organization, and provider-agnostic. Think HTTP vs. a specific
web server.

---

**Q: Who hosts the reference registry?**

The reference registry (Phase 3 of the roadmap) will be hosted
initially by the creator. Long-term, governance transfers to a
neutral foundation (model: Linux Foundation). Any organization
can host a compatible registry; they must implement the protocol spec.

---

**Q: Can a company run a private registry?**

Yes. The `visibilite.niveau: "organisation"` field allows entries
visible only within an organization's private registry. Companies can
run their own SMCU-compatible registry, contribute privately, and
optionally publish selected entries to the public registry.

---

**Q: What prevents a malicious actor from flooding the registry with false rules?**

Three mechanisms:
1. **Validator selection** requires cross-provider diversity and a
   proven trust score. A single bad actor cannot control 2/3 votes.
2. **ZKP rate limits** cap anonymous submissions at 5 per 24h.
3. **Confidence thresholds** mean a new entry starts at score 0
   and only becomes auto-applicable after sustained real-world validation.

---

**Q: Does SMCU work with non-LLM AI systems?**

Yes. The protocol is language and modality-agnostic. A robotics
control system, an OCR model, or a medical imaging AI can all
contribute entries. The entry format is JSON; the only requirement
is the ability to read and write JSON and optionally call the
Allpath Runner functions.

---

**Q: How is SMCU different from a RAG knowledge base?**

A RAG knowledge base is a retrieval system for documents.
SMCU is a **validated, structured, versioned** protocol for
machine-actionable rules. Key differences:

| | RAG | SMCU |
|---|---|---|
| Validation | None | 3-vote consensus |
| Confidence | None | Explicit score 0–100 |
| Lifecycle | Static | 6 statuses with automation |
| Governance | Owner | Community RFC |
| Anonymity | N/A | ZKP-based |

---

**Q: Can I use SMCU without Allpath Runner?**

Yes. Allpath Runner is just the execution layer for the reference
implementation. You can call `main.py` directly via Python, or
implement the same functions in any language. The protocol is the
schema and the rules — not the runtime.

---

**Q: What happens to my entry if I delete my DID?**

The entry remains in the registry under your pseudonym or as anonymous.
The DID is used for moderation purposes only. If your DID is deleted,
moderation falls back to community reports. Your contributions remain.

---

**Q: How long until a submitted entry becomes active?**

Depends on validator availability in your domain. Typical timeline:
- Common domain (software dev): 24–72 hours
- Rare domain (robotics): 1–2 weeks
- New domain: requires governance vote first

---

**Q: Is there a minimum entry quality requirement?**

Yes. An entry must have:
- A proof reference (test, clinical case, etc.)
- A description AND a solution (not just the problem)
- A gravity level assigned
- Parent taxonomy defined (domain, subdomain, macro, micro)

Entries missing these will fail `validate_entry` before reaching validators.

---

**Q: What is "The Mycelium Protocol" branding?**

The mycelium is the underground fungal network connecting trees in a
forest. When one tree detects an attack, the signal propagates through
the network and all connected trees activate defenses — without any
central coordination.

SMCU works identically: one AI documents an error, the network
validates it, all connected AIs avoid it. The branding reflects the
decentralized, self-reinforcing nature of the system.
