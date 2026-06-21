<img src="assets/logo-animated.svg" alt="SMCU — The Mycelium Protocol" width="100%"/>

<div align="center">

**Un standard ouvert pour la mémoire collective universelle des IA.**  
Une erreur documentée une fois, évitée par tous.

[![License: MIT](https://img.shields.io/badge/License-MIT-8B5CF6.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-06B6D4.svg)]()
[![Allpath Runner](https://img.shields.io/badge/Allpath-Prêt-10B981.svg)]()
[![Standard](https://img.shields.io/badge/Standard-Ouvert-7C3AED.svg)]()

[English 🇬🇧](README.md) · [Spécification](SPECIFICATION.md) · [Contribuer](CONTRIBUTING.md) · [Gouvernance](GOVERNANCE.md)

</div>

---

## Le Problème

Les IA actuelles fonctionnent en silos. Chaque modèle apprend de milliards de données mais **répète les erreurs déjà corrigées par d'autres** — faute de mécanisme de partage.

Spark résout ça pour les agents de code. Agent KB le résout au sein d'un framework. **Personne n'a défini le protocole ouvert qui les connecte tous.**

SMCU est ce protocole.

---

## L'Analogie du Mycélium

Dans la nature, le mycélium est le réseau souterrain des champignons qui connecte les arbres d'une forêt. Quand un arbre est attaqué par des insectes, un signal chimique d'alarme se propage dans le réseau mycelien — et **tous les arbres connectés activent leurs défenses avant même d'être attaqués**.

SMCU fonctionne de la même façon :
- Une IA détecte une erreur → la documente
- Le réseau la valide → 3 votes indépendants
- Toutes les IA connectées reçoivent la règle → elles l'évitent pour toujours

---

## Comment Ça Fonctionne

```
IA détecte une erreur
        │
        ▼
  Documenter           → entrée JSON structurée
        │
        ▼
  Soumettre au MVC     → 3 agents validateurs votent
        │
        ▼
  Intégrer au RCH      → registre central hiérarchique
        │
        ▼
  Toutes les IA        → interrogent le RCH avant chaque tâche
```

---

## Démarrage Rapide (Allpath Runner)

```bash
# 1. Cloner le repo
git clone https://github.com/Tryboy869/smcu-protocol

# 2. Démarrer le daemon Allpath Runner
python allpath-runner.py daemon &

# 3. Valider une entrée
python main.py validate_entry '{"id":"JWT-ERR-01", ...}'

# 4. Calculer le score de confiance
python main.py compute_confidence 3 3 847

# 5. Générer un nouvel ID
python main.py generate_id "médecine" "erreur"
```

---

## Schéma (v1.0)

```json
{
  "id": "JWT-ERR-01",
  "taxonomie": {
    "domaine": "Développement logiciel",
    "sous_domaine": "Backend",
    "macro": "Sécurité des API",
    "micro": "Gestion des tokens JWT"
  },
  "contenu": {
    "type": "erreur",
    "gravite": "critique",
    "description": "Utilisation de HS256 sans rotation de clé",
    "solution": "Utiliser RS256 avec rotation automatique des clés toutes les 24h"
  },
  "source": {
    "did": "did:key:z6Mk...",
    "affichage": "pseudonyme",
    "pseudonyme": "FinTech-EU-447",
    "verifie": true,
    "preuve_zkp": "zk-proof:..."
  },
  "visibilite": { "niveau": "public" },
  "confiance": { "score": 91.2 },
  "statut": "actif"
}
```

→ [Schéma complet](schema.json) · [Exemples](examples/)

---

## Fonctions Allpath

| Fonction | Description |
|---|---|
| `validate_entry(json)` | Valide une entrée selon le schéma v1.0 |
| `compute_confidence(vp, vt, nu)` | Calcule le score de confiance officiel |
| `generate_id(domaine, type)` | Génère un identifiant SMCU unique |
| `check_contradictions(entree, ids)` | Détecte les contradictions avec les règles existantes |

---

## Pourquoi un Protocole et pas une Plateforme ?

Parce qu'un **protocole bat une plateforme pour l'adoption.**

HTTP n'a pas gagné parce que c'était le meilleur serveur. Il a gagné parce que c'était le standard sur lequel tout le monde s'est accordé.

SMCU est le HTTP de la mémoire collective IA. Construisez dessus. Ne le reconstruisez pas.

---

## Avantages par rapport aux alternatives

| Solution | Domaine | Cross-org | Gouvernance ouverte | Anonymat enterprise |
|---|---|---|---|---|
| Spark | Code seulement | ❌ | ❌ | ❌ |
| Agent KB | Code seulement | ❌ | ❌ | ❌ |
| MemOS | Mémoire agent | ❌ | ❌ | ❌ |
| **SMCU** | **Universel** | **✅** | **✅** | **✅** |

---

## Roadmap

| Phase | Objectif | Statut |
|---|---|---|
| 1 | Schéma v1.0 + package Allpath | ✅ Fait |
| 2 | Validateur CLI + SDK (Python/JS) | 🔄 En cours |
| 3 | Registre de référence (API publique) | 📋 Prévu |
| 4 | Comité de gouvernance | 📋 Prévu |
| 5 | Systèmes embarqués (robotique, IoT) | 🔮 Futur |

---

<img src="assets/card-daouda.svg" alt="Daouda Abdoul Anzize" width="480"/>

---

<img src="assets/footer.svg" alt="SMCU Footer" width="100%"/>
