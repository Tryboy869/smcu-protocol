# Contributing to SMCU Protocol

Thank you for helping grow the collective memory network.

---

## What You Can Contribute

| Type | How |
|---|---|
| New entry (example) | Add a `.json` file in `examples/` |
| Bug in validator | Open an Issue + Pull Request |
| New domain proposal | Open an RFC Issue (see `GOVERNANCE.md`) |
| Schema improvement | Open an RFC Issue |
| Documentation fix | Direct Pull Request |
| New SDK language | Open an Issue first to coordinate |

---

## Submitting an Example Entry

1. Fork the repository
2. Copy `examples/software-dev.json` as a starting point
3. Fill in all required fields (run the validator to check)
4. Name the file: `examples/{domain}-{short-description}.json`
5. Open a Pull Request with title: `[EXAMPLE] Domain — Short description`

**Validate before submitting:**
```bash
python validator/validate.py examples/your-new-file.json
```

---

## Code Contributions

- Python: follow PEP 8, no external dependencies in `main.py`
- All functions must print JSON to stdout (Allpath convention)
- Add a test in `validator/` for any new function
- One feature per Pull Request

---

## Pull Request Checklist

- [ ] Validator passes on my entry / change
- [ ] I have not included any proprietary code or data
- [ ] My entry uses only anonymized information (no client names, no internal URLs)
- [ ] I have read and accept the Code of Conduct

---

## Seed Contributors

We are actively looking for the first 10 entries across these domains:
- `Médecine` (any subspecialty)
- `Robotique` (any platform)
- `Finance` (any instrument)

First contributors in each domain receive **Founding Contributor** status
in the registry and in `CHANGELOG.md`.
