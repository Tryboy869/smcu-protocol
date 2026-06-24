#!/usr/bin/env python3
"""
SMCU Protocol — Standalone Validator CLI
Usage: python validate.py <path_to_entry.json>
       python validate.py examples/software-dev.json
"""

import sys
import json
import math
import os

# ─────────────────────────────────────────────
REQUIRED_FIELDS = [
    "id", "taxonomie", "contenu", "preuve",
    "validation", "confiance", "statut",
    "source", "visibilite", "portee", "cycle_de_vie"
]
REQUIRED_TAXONOMIE  = ["domaine", "sous_domaine", "macro", "micro"]
REQUIRED_CONTENU    = ["type", "gravite", "description", "solution"]
REQUIRED_VALIDATION = ["votes_requis", "votes", "votes_positifs", "votes_total"]

VALID_STATUTS    = ["actif", "conteste", "revoque", "obsolete", "archive", "en_attente"]
VALID_GRAVITES   = ["critique", "majeur", "mineur"]
VALID_TYPES      = ["erreur", "regle", "avertissement", "bonne_pratique"]
VALID_VISIBILITE = ["public", "organisation", "prive"]
VALID_PREUVES    = [
    "test_unitaire", "test_integration", "cas_clinique",
    "simulation", "peer_review", "audit_securite"
]
VALID_DECISIONS  = ["approuve", "rejete", "ameliorer"]
VALID_AFFICHAGE  = ["public", "pseudonyme", "anonyme"]

CONFIDENCE_THRESHOLD_HIGH   = 80
CONFIDENCE_THRESHOLD_MEDIUM = 60
CONFIDENCE_THRESHOLD_LOW    = 40


def _check(condition, errors, message):
    if not condition:
        errors.append(message)


def validate(entry: dict) -> dict:
    errors   = []
    warnings = []

    # ── Top-level required fields
    for f in REQUIRED_FIELDS:
        _check(f in entry, errors, f"Champ requis manquant : '{f}'")

    # ── ID format
    if "id" in entry:
        parts = entry["id"].split("-")
        _check(len(parts) >= 3, errors,
               f"ID '{entry['id']}' invalide. Format attendu : DOM-TYPE-HASH (ex: DEV-ERR-A3F2)")

    # ── Taxonomie
    if "taxonomie" in entry:
        t = entry["taxonomie"]
        for f in REQUIRED_TAXONOMIE:
            _check(f in t and t[f], errors, f"taxonomie.{f} requis et non vide")
        if "tags" not in t or not t.get("tags"):
            warnings.append("taxonomie.tags vide — réduit la découvrabilité de l'entrée")

    # ── Contenu
    if "contenu" in entry:
        c = entry["contenu"]
        for f in REQUIRED_CONTENU:
            _check(f in c and c[f], errors, f"contenu.{f} requis et non vide")
        if "gravite" in c:
            _check(c["gravite"] in VALID_GRAVITES, errors,
                   f"contenu.gravite invalide : '{c['gravite']}'. Acceptés : {VALID_GRAVITES}")
        if "type" in c:
            _check(c["type"] in VALID_TYPES, errors,
                   f"contenu.type invalide : '{c['type']}'. Acceptés : {VALID_TYPES}")
        if "exemple" not in c:
            warnings.append("contenu.exemple absent — fortement recommandé pour adoption")

    # ── Preuve
    if "preuve" in entry:
        p = entry["preuve"]
        _check("type" in p, errors, "preuve.type requis")
        if "type" in p:
            _check(p["type"] in VALID_PREUVES, errors,
                   f"preuve.type invalide : '{p['type']}'. Acceptés : {VALID_PREUVES}")
        if "reference" not in p or not p.get("reference"):
            warnings.append("preuve.reference absent — réduira la confiance des validateurs")

    # ── Validation / votes
    if "validation" in entry:
        v = entry["validation"]
        for f in REQUIRED_VALIDATION:
            _check(f in v, errors, f"validation.{f} requis")
        if "votes_requis" in v:
            vr = v["votes_requis"]
            _check(isinstance(vr, int) and vr >= 3, errors,
                   f"validation.votes_requis doit être ≥ 3 (actuel : {vr})")
        # Only check vote count when statut is 'actif'
        if entry.get("statut") == "actif" and "votes_requis" in v and "votes" in v:
            vr = v["votes_requis"]
            if len(v["votes"]) < vr:
                errors.append(f"Votes insuffisants pour statut 'actif': {len(v['votes'])}/{vr}")
        if "votes" in v:
            for i, vote in enumerate(v.get("votes", [])):
                _check("votant_did" in vote, errors, f"vote[{i}].votant_did manquant")
                _check("decision" in vote and vote.get("decision") in VALID_DECISIONS, errors,
                       f"vote[{i}].decision invalide. Acceptés : {VALID_DECISIONS}")
                _check("timestamp" in vote, errors, f"vote[{i}].timestamp manquant")
        # Positifs coherence
        if all(k in v for k in ["votes_positifs", "votes_total"]):
            _check(v["votes_positifs"] <= v["votes_total"], errors,
                   "votes_positifs ne peut pas dépasser votes_total")

    # ── Confiance
    if "confiance" in entry:
        conf = entry["confiance"]
        if "score" in conf:
            s = conf["score"]
            _check(0 <= s <= 100, errors, f"confiance.score doit être entre 0 et 100 (actuel : {s})")
            if s < CONFIDENCE_THRESHOLD_LOW:
                warnings.append(f"confiance.score faible ({s}) — entrée non appliquée automatiquement")

    # ── Statut
    if "statut" in entry:
        _check(entry["statut"] in VALID_STATUTS, errors,
               f"statut invalide : '{entry['statut']}'. Acceptés : {VALID_STATUTS}")

    # ── Source
    if "source" in entry:
        s = entry["source"]
        if s.get("affichage") in VALID_AFFICHAGE:
            aff = s["affichage"]
            if aff == "pseudonyme":
                _check("pseudonyme" in s and s["pseudonyme"], errors,
                       "source.pseudonyme requis quand affichage='pseudonyme'")
            if aff == "anonyme":
                _check("preuve_zkp" in s and s["preuve_zkp"], errors,
                       "source.preuve_zkp requis quand affichage='anonyme'")
            if aff in ("public", "pseudonyme"):
                _check("did" in s, errors, "source.did requis pour affichage public ou pseudonyme")
        else:
            errors.append(f"source.affichage invalide. Acceptés : {VALID_AFFICHAGE}")

    # ── Visibilité
    if "visibilite" in entry:
        niv = entry["visibilite"].get("niveau")
        _check(niv in VALID_VISIBILITE, errors,
               f"visibilite.niveau invalide : '{niv}'. Acceptés : {VALID_VISIBILITE}")
        if niv == "organisation":
            _check(entry["visibilite"].get("organisation_id"), errors,
                   "visibilite.organisation_id requis quand niveau='organisation'")

    # ── Relations
    if "relations" in entry:
        r = entry["relations"]
        if "parent" not in r:
            warnings.append("relations.parent absent — hiérarchie du registre recommandée")

    # ── Cycle de vie
    if "cycle_de_vie" in entry:
        cdv = entry["cycle_de_vie"]
        _check("date_creation" in cdv, errors, "cycle_de_vie.date_creation requis")

    return {
        "valid":         len(errors) == 0,
        "entry_id":      entry.get("id", "inconnu"),
        "errors":        errors,
        "warnings":      warnings,
        "summary":       f"{len(errors)} erreur(s), {len(warnings)} avertissement(s)"
    }


def print_report(result: dict):
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    RESET  = "\033[0m"
    BOLD   = "\033[1m"

    status = f"{GREEN}✅ VALIDE{RESET}" if result["valid"] else f"{RED}❌ INVALIDE{RESET}"
    print(f"\n{BOLD}SMCU Validator — {result['entry_id']}{RESET}")
    print(f"Status : {status}")
    print(f"Résumé : {result['summary']}\n")

    if result["errors"]:
        print(f"{RED}{BOLD}Erreurs:{RESET}")
        for e in result["errors"]:
            print(f"  {RED}✗{RESET} {e}")

    if result["warnings"]:
        print(f"\n{YELLOW}{BOLD}Avertissements:{RESET}")
        for w in result["warnings"]:
            print(f"  {YELLOW}⚠{RESET} {w}")

    print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate.py <chemin_vers_entree.json>")
        print("Exemple: python validate.py examples/software-dev.json")
        sys.exit(1)

    path = sys.argv[1]

    if not os.path.exists(path):
        print(f"Erreur : fichier introuvable : '{path}'")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        try:
            entry = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Erreur JSON : {e}")
            sys.exit(1)

    result = validate(entry)
    print_report(result)

    # Output JSON for piping
    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
