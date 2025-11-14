# Plan Commit — Toolkit Core r1

**Branche** : `toolkit-core-r1`  
**Objectif** : Release propre, stable, documentée

---

## Fichiers à Commiter (Essentiels Seulement)

### Racine

```
README.md               # Refonte v8.2-v9, focus toolkit, test 30s
CHANGELOG.md            # Historique v8.0 → toolkit-core-r1
RELEASE_NOTES_TOOLKIT_CORE_R1.md  # Notes release
LICENSE                 # MIT
requirements.txt        # Dépendances
setup.py                # Installation package
.gitignore              # Ignorer __pycache__, venv, outputs temp
```

### Modules Toolkit

```
design_space/__init__.py     # API publique (19 fonctions)
design_space/loaders.py      # Chargement/validation (6 fonctions)
design_space/selector.py     # Filtrage/sélection (10 fonctions)
design_space/pareto.py       # Multi-objectifs (3 fonctions)

metrics/__init__.py          # API publique metrics
metrics/functional_score.py  # Scoring (4 fonctions)
```

### Scripts

```
scripts/build_design_space_v1.py    # Construction CSV standardisé
scripts/score_fp_predictions.py      # CLI scorer ML predictions
```

### Tests

```
tests/test_loaders.py           # 15 tests
tests/test_selector.py          # 24 tests
tests/test_functional_score.py  # 18 tests
tests/test_pareto.py            # 13 tests
tests/fixtures/mini_design_space.csv        # 10 systèmes
tests/fixtures/mock_fp_predictions.csv      # 10 mutants
tests/test_metrics_calibration_v3_4.py      # 12 tests skipped (CA historique)
```

**(Autres tests isinglab existants conservés si pertinents)**

### Données

```
data/atlas_optical/atlas_fp_optical_v2_2_curated.csv  # 180 systèmes Tier 1
data/atlas_nonoptical/  # Vide (spec prête, datasets absents)
data/README.md          # Provenance Atlas

outputs/qubit_design_space_v1.csv  # CSV standardisé
```

### Documentation

```
docs/STATE_v9_0.md                          # Vision consolidée (ENTRÉE PRINCIPALE)
docs/MISSION_v8_2.md                        # Périmètre toolkit
docs/PLAN_v8_2.md                           # Roadmap
docs/DESIGN_SPACE_v1_REPORT.md              # Analyse 180 systèmes
docs/STRESS_METRICS_SPEC_v8_3.md            # Spec stress-test (données absentes)
docs/BRIDGE_ATLAS_QUANTUM_SENSORS.md        # ✅ Opérationnel
docs/BRIDGE_FP_QUBIT_DESIGN.md              # ✅ Opérationnel
docs/BRIDGE_ARREST_MOLECULES.md             # 🔴 Spéculatif
docs/BRIDGE_NON_OPTICAL_QUBITS_v9_2.md      # 🟡 Spec prête
docs/MULTIPROJECT_CONTEXT_v8.md             # Cartographie écosystème
docs/ISING_TOOLKIT_FOR_PROJECTS_v8.md       # Réutilisation métriques

docs/archive/README.md                      # Explication archive
docs/archive/*                              # Documents historiques (conservés traçabilité)
```

---

## Fichiers À NE PAS Commiter (Bruit Temporaire)

### Racine (Archivés ou Ignorés)

- Multiples `RESUME_v*.md` (→ docs/archive/)
- Multiples `MISSION_v*.md` (→ docs/archive/)
- Multiples `STATUS_*.md` (→ docs/archive/)
- Multiples `RAPPORT_*.md` (→ docs/archive/ sauf RAPPORT_v9_0.md)
- Fichiers temporaires (HOTFIX, FIX, DEMAIN, EXAMPLE, etc. → archive/)

### Dossiers Temporaires

- `ising-life-lab-temp/`
- `ising-memory-ai-lab/auto-memory-research-*.json`
- `outputs/quick/` (résultats scans temporaires)

---

## Commandes Git

### Créer Branche

```bash
git checkout -b toolkit-core-r1
```

### Ajouter Fichiers Essentiels

```bash
# Racine
git add README.md CHANGELOG.md RELEASE_NOTES_TOOLKIT_CORE_R1.md
git add LICENSE requirements.txt setup.py .gitignore

# Modules toolkit
git add design_space/ metrics/

# Scripts
git add scripts/build_design_space_v1.py
git add scripts/score_fp_predictions.py

# Tests
git add tests/test_loaders.py tests/test_selector.py
git add tests/test_functional_score.py tests/test_pareto.py
git add tests/fixtures/mini_design_space.csv
git add tests/fixtures/mock_fp_predictions.csv
git add tests/test_metrics_calibration_v3_4.py

# Données
git add data/atlas_optical/atlas_fp_optical_v2_2_curated.csv
git add data/README.md
git add outputs/qubit_design_space_v1.csv

# Documentation
git add docs/STATE_v9_0.md
git add docs/MISSION_v8_2.md docs/PLAN_v8_2.md
git add docs/DESIGN_SPACE_v1_REPORT.md
git add docs/STRESS_METRICS_SPEC_v8_3.md
git add docs/BRIDGE_ATLAS_QUANTUM_SENSORS.md
git add docs/BRIDGE_FP_QUBIT_DESIGN.md
git add docs/BRIDGE_ARREST_MOLECULES.md
git add docs/BRIDGE_NON_OPTICAL_QUBITS_v9_2.md
git add docs/MULTIPROJECT_CONTEXT_v8.md
git add docs/ISING_TOOLKIT_FOR_PROJECTS_v8.md
git add docs/archive/README.md

# (Optionnel : autres tests isinglab si pertinents)
```

### Commit

```bash
git commit -m "Toolkit core r1: Stable design_space API, metrics, bridges, tests

- design_space module: loaders (6), selector (10), pareto (3) = 19 fonctions
- metrics module: functional_score (4 fonctions)
- Scripts: build design_space, score ML predictions
- Tests: 70 tests toolkit (100% pass), 154 total (12 CA skipped)
- Dataset: Atlas Tier 1 (180 systèmes optical)
- Bridges: Atlas ✅, fp-qubit ✅, non-optical 🟡 spec, arrest 🔴 spec
- Documentation: STATE_v9_0, bridges, CHANGELOG
- Archive: ~40 docs historiques → docs/archive/ (traçabilité)

Limitations assumées:
- Données stress-test (photostabilité, pH, temp): spec prête, données absentes
- Datasets non-optical: format défini, CSV absents
- arrest-molecules: bridge spec, données ΔG absentes
- fp-qubit scorer: testé mock, pas vraies prédictions

Résultats mesurés:
- Top système: jGCaMP8s (90× contrast, score 1.0)
- 68% room temp, 92% bio-adjacent, 39% high contrast

Phase CA-reservoir (v1-v7): Close, historique archivé."
```

### Push

```bash
git push origin toolkit-core-r1
```

---

## Vérification Pré-Commit

```bash
# Tests toolkit uniquement
pytest tests/test_loaders.py tests/test_selector.py tests/test_functional_score.py tests/test_pareto.py -q
# 70 passed ✅

# API importable
python -c "from design_space import *; from metrics import *; print('OK')"
# OK ✅

# Scorer opérationnel
python scripts/score_fp_predictions.py --input tests/fixtures/mock_fp_predictions.csv --output /tmp/test.csv
# SUCCESS ✅
```

---

**Plan prêt. Exécution sur demande utilisateur.** ✅


