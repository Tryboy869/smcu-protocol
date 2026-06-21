#!/usr/bin/env node
/**
 * SMCU Protocol — Standalone Validator (JavaScript)
 * Usage: node validate.js <path_to_entry.json>
 *        node validate.js examples/software-dev.json
 *        node validate.js examples/software-dev.json --json
 */

const fs   = require("fs");
const path = require("path");

const REQUIRED_FIELDS    = ["id","taxonomie","contenu","preuve","validation","confiance","statut","source","visibilite","portee","cycle_de_vie"];
const REQUIRED_TAXONOMIE = ["domaine","sous_domaine","macro","micro"];
const REQUIRED_CONTENU   = ["type","gravite","description","solution"];

const VALID_STATUTS    = ["actif","conteste","revoque","obsolete","archive","en_attente"];
const VALID_GRAVITES   = ["critique","majeur","mineur"];
const VALID_TYPES      = ["erreur","regle","avertissement","bonne_pratique"];
const VALID_VISIBILITE = ["public","organisation","prive"];
const VALID_PREUVES    = ["test_unitaire","test_integration","cas_clinique","simulation","peer_review","audit_securite"];
const VALID_DECISIONS  = ["approuve","rejete","ameliorer"];
const VALID_AFFICHAGE  = ["public","pseudonyme","anonyme"];

// ─────────────────────────────────────────────
function validate(entry) {
  const errors   = [];
  const warnings = [];

  const check = (condition, msg) => { if (!condition) errors.push(msg); };

  // Required top-level fields
  for (const f of REQUIRED_FIELDS) {
    check(f in entry, `Champ requis manquant : '${f}'`);
  }

  // ID format
  if ("id" in entry) {
    const parts = entry.id.split("-");
    check(parts.length >= 3, `ID '${entry.id}' invalide. Format attendu : DOM-TYPE-HASH`);
  }

  // Taxonomie
  if ("taxonomie" in entry) {
    const t = entry.taxonomie;
    for (const f of REQUIRED_TAXONOMIE) {
      check(f in t && t[f], `taxonomie.${f} requis et non vide`);
    }
    if (!t.tags || t.tags.length === 0) {
      warnings.push("taxonomie.tags vide — réduit la découvrabilité");
    }
  }

  // Contenu
  if ("contenu" in entry) {
    const c = entry.contenu;
    for (const f of REQUIRED_CONTENU) {
      check(f in c && c[f], `contenu.${f} requis et non vide`);
    }
    if ("gravite" in c) check(VALID_GRAVITES.includes(c.gravite), `contenu.gravite invalide : '${c.gravite}'`);
    if ("type"    in c) check(VALID_TYPES.includes(c.type),       `contenu.type invalide : '${c.type}'`);
    if (!("exemple" in c)) warnings.push("contenu.exemple absent — recommandé pour adoption");
  }

  // Preuve
  if ("preuve" in entry) {
    const p = entry.preuve;
    check("type" in p, "preuve.type requis");
    if ("type" in p) check(VALID_PREUVES.includes(p.type), `preuve.type invalide : '${p.type}'`);
    if (!p.reference) warnings.push("preuve.reference absent — réduira la confiance des validateurs");
  }

  // Validation / votes
  if ("validation" in entry) {
    const v = entry.validation;
    if ("votes_requis" in v) {
      check(Number.isInteger(v.votes_requis) && v.votes_requis >= 3,
            `validation.votes_requis doit être ≥ 3 (actuel : ${v.votes_requis})`);
    }
    if ("votes" in v) {
      v.votes.forEach((vote, i) => {
        check("votant_did" in vote, `vote[${i}].votant_did manquant`);
        check("decision" in vote && VALID_DECISIONS.includes(vote.decision),
              `vote[${i}].decision invalide. Acceptés : ${VALID_DECISIONS.join(", ")}`);
        check("timestamp" in vote, `vote[${i}].timestamp manquant`);
      });
    }
    if ("votes_positifs" in v && "votes_total" in v) {
      check(v.votes_positifs <= v.votes_total, "votes_positifs ne peut pas dépasser votes_total");
    }
  }

  // Confiance
  if ("confiance" in entry && "score" in entry.confiance) {
    const s = entry.confiance.score;
    check(s >= 0 && s <= 100, `confiance.score doit être entre 0 et 100 (actuel : ${s})`);
    if (s < 40) warnings.push(`confiance.score faible (${s}) — non appliquée automatiquement`);
  }

  // Statut
  if ("statut" in entry) {
    check(VALID_STATUTS.includes(entry.statut), `statut invalide : '${entry.statut}'`);
  }

  // Source
  if ("source" in entry) {
    const s = entry.source;
    if (s.affichage) {
      check(VALID_AFFICHAGE.includes(s.affichage), `source.affichage invalide : '${s.affichage}'`);
      if (s.affichage === "pseudonyme") check(s.pseudonyme, "source.pseudonyme requis");
      if (s.affichage === "anonyme")    check(s.preuve_zkp,  "source.preuve_zkp requis");
      if (["public","pseudonyme"].includes(s.affichage)) check(s.did, "source.did requis");
    }
  }

  // Visibilité
  if ("visibilite" in entry) {
    const niv = entry.visibilite.niveau;
    check(VALID_VISIBILITE.includes(niv), `visibilite.niveau invalide : '${niv}'`);
    if (niv === "organisation" && !entry.visibilite.organisation_id) {
      errors.push("visibilite.organisation_id requis quand niveau='organisation'");
    }
  }

  // Relations
  if ("relations" in entry && !("parent" in entry.relations)) {
    warnings.push("relations.parent absent — hiérarchie recommandée");
  }

  return {
    valid:    errors.length === 0,
    entry_id: entry.id || "inconnu",
    errors,
    warnings,
    summary:  `${errors.length} erreur(s), ${warnings.length} avertissement(s)`
  };
}

// ─────────────────────────────────────────────
function printReport(result) {
  const R = "\x1b[0m", BOLD = "\x1b[1m";
  const G = "\x1b[92m", RED = "\x1b[91m", Y = "\x1b[93m";

  const status = result.valid ? `${G}✅ VALIDE${R}` : `${RED}❌ INVALIDE${R}`;
  console.log(`\n${BOLD}SMCU Validator — ${result.entry_id}${R}`);
  console.log(`Status : ${status}`);
  console.log(`Résumé : ${result.summary}\n`);

  if (result.errors.length)   { console.log(`${RED}${BOLD}Erreurs:${R}`);          result.errors.forEach(e => console.log(`  ${RED}✗${R} ${e}`)); }
  if (result.warnings.length) { console.log(`\n${Y}${BOLD}Avertissements:${R}`);   result.warnings.forEach(w => console.log(`  ${Y}⚠${R} ${w}`)); }
  console.log();
}

// ─────────────────────────────────────────────
const args     = process.argv.slice(2);
const filePath = args.find(a => !a.startsWith("--"));
const jsonMode = args.includes("--json");

if (!filePath) {
  console.log("Usage: node validate.js <chemin_vers_entree.json> [--json]");
  process.exit(1);
}

if (!fs.existsSync(filePath)) {
  console.error(`Erreur : fichier introuvable : '${filePath}'`);
  process.exit(1);
}

let entry;
try {
  entry = JSON.parse(fs.readFileSync(filePath, "utf-8"));
} catch (e) {
  console.error(`Erreur JSON : ${e.message}`);
  process.exit(1);
}

const result = validate(entry);
printReport(result);
if (jsonMode) console.log(JSON.stringify(result, null, 2));

process.exit(result.valid ? 0 : 1);
