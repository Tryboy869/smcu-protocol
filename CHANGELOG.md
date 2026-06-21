# Changelog

All notable changes to the SMCU Protocol are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [1.0.0] — 2026-06-19

### Added
- Schema v1.0 with all required and optional fields
- Four-level taxonomy (domaine / sous_domaine / macro / micro)
- Five entry lifecycle statuses (en_attente, actif, conteste, revoque, obsolete, archive)
- Confidence score formula: `min((vp/vt) × log(nu+1) × 100, 100)`
- Three anonymity levels: public, pseudonyme, anonyme (ZKP)
- Validator selection rules (cross-provider, competence-verified)
- Allpath Runner package with four functions: validate_entry, compute_confidence, generate_id, check_contradictions
- Animated SVG visual identity (The Mycelium Protocol branding)
- AGENT_GUIDE.md for AI-native onboarding
- SPECIFICATION.md with full protocol rules
- GOVERNANCE.md with RFC process and Technical Committee model
- Examples: software-dev, medical, robotics
- Contradiction handling with `contredit` / `remplace` relation fields
- Jurisdiction scoping (`portee.juridictions`)
- Parent/child hierarchy (`relations.parent`)

### Architecture
- Protocol layer: schema.json + SPECIFICATION.md
- Execution layer: main.py (Allpath Runner package)
- Governance layer: GOVERNANCE.md
- Onboarding layer: AGENT_GUIDE.md

---

## [Unreleased]

### Planned for v1.1
- `query_registry` function (most critical missing piece)
- SDK for JavaScript
- Public reference registry API (hosted)
- Bootstrap seed entries (first 30 across 6 domains)

### Planned for v2.0
- Distributed registry (no single host)
- Cross-registry federation protocol
- Embedded systems support (robotics, IoT)
