# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 1.0.x | ✅ Yes |

## Reporting a Vulnerability

**Do not open a public GitHub Issue for security vulnerabilities.**

Send a report to: `anzize.contact@proton.me`
Subject line: `[SMCU SECURITY] Brief description`

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (optional)

**Response time:** We aim to acknowledge within 48 hours and resolve within 14 days.

## Scope

Security issues relevant to SMCU include:

- **Registry poisoning** — A malicious actor submitting false or harmful rules
- **Validator collusion** — Coordinated manipulation of the voting process
- **ZKP bypass** — Breaking the anonymity system to reveal contributor identity
- **Schema injection** — Malformed entries that could corrupt a registry implementation
- **Confidence score manipulation** — Artificially inflating a rule's trust score

## Out of Scope

- Vulnerabilities in Allpath Runner itself (report to the Allpath Runner repo)
- Issues in third-party registry implementations
