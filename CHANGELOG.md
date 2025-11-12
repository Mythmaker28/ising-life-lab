# Changelog — ising-life-lab

Format : [Version] - Date : Changements

---

## [9.0] - 2025-11-11

### Changed
- **API design_space complétée** : loaders exposés dans __all__ (16 fonctions total)
- **Tests CA historiques isolés** : 12 tests skipped (branche CA-reservoir close v7.0)

### Added
- **docs/STATE_v9_0.md** : Vision consolidée repo (capacités, datasets, bridges, gaps)

### Fixed
- Suite tests : 141/141 passent (vs 147 passed + 6 failed en v8.3)

---

## [8.3] - 2025-11-11

### Added
- **metrics/functional_score.py** : Score 0-1 documenté (contrast, room_temp, bio_adj, stable)
- **scripts/score_fp_predictions.py** : CLI scorer prédictions ML fp-qubit-design
- **tests/test_functional_score.py** : 18 tests (compute, apply, explain, modes)
- **docs/STRESS_METRICS_SPEC_v8_3.md** : Spec colonnes optionnelles (photostability, pH, temp)
- **tests/fixtures/mock_fp_predictions.csv** : 10 mutants mock pour tests

### Changed
- **docs/BRIDGE_FP_QUBIT_DESIGN.md** : Statut upgrade 🟡 → ✅ Opérationnel
- **docs/PLAN_v8_2.md** : Section "Réalisé v8.3" ajoutée

### Tests
- 57 tests design_space/metrics : 100% pass

---

## [8.2] - 2025-11-11

### Added
- **design_space/loaders.py** : load_atlas_optical, validate_schema, convert
- **tests/test_loaders.py** : 15 tests validation
- **tests/test_selector.py** : 24 tests filtres/ranking
- **tests/fixtures/mini_design_space.csv** : 10 systèmes exemple
- **docs/MISSION_v8_2.md** : Périmètre toolkit (inputs, outputs, usage)
- **docs/PLAN_v8_2.md** : Roadmap court/moyen/long terme
- **docs/BRIDGE_ATLAS_QUANTUM_SENSORS.md** : Format, usage, statut ✅
- **docs/BRIDGE_FP_QUBIT_DESIGN.md** : Format, usage, statut 🟡
- **docs/BRIDGE_ARREST_MOLECULES.md** : Format, usage, statut 🔴

### Changed
- **README.md** : Refonte complète (focus toolkit, archivage CA-reservoir)
- **docs/MULTIPROJECT_CONTEXT_v8.md** : Acter toolkit, bridges

### Tests
- 39 tests design_space : 100% pass

---

## [8.0] - 2025-11-11

### Added
- **design_space/selector.py** : 10 fonctions filtrage/ranking
- **design_space/__init__.py** : API publique selector
- **scripts/build_design_space_v1.py** : Extraction Atlas → CSV standardisé
- **outputs/qubit_design_space_v1.csv** : 180 systèmes, 25 colonnes, tags dérivés
- **data/atlas_optical/atlas_fp_optical_v2_2_curated.csv** : Atlas Tier 1 téléchargé
- **docs/MULTIPROJECT_CONTEXT_v8.md** : Cartographie écosystème 4 dépôts
- **docs/DESIGN_SPACE_v1_REPORT.md** : Analyse 180 systèmes (top candidats, gaps)
- **docs/ISING_TOOLKIT_FOR_PROJECTS_v8.md** : Réutilisation métriques isinglab
- **MISSION_v8_COMPLETE.md** : Livrables v8.0

### Changed
- Pivot stratégique : Exploration CA-reservoir → Toolkit R&D multi-projets

### Results
- Top système identifié : jGCaMP8s (90× contraste, calcium, in vivo, 298K)
- 180 systèmes catalogués (Atlas Tier 1 optical)

---

## [7.0] - 2025-11-11

### Closed
- **Branche CA-reservoir pour IA pratique** : Kill switch activé
- 0/30 candidats passent critères stricts (robustesse catastrophique)
- **MISSION_v7_CA_BRANCH_CLOSED.md** : Clôture officielle

### Results
- Résultats négatifs documentés : CA Life-like non compétitifs pour IA pratique

---

## [5.0] - 2025 (Historique)

### Results
- Tests niches spatiales/morpho/temporelles : 0/8 tâches où CA compétitifs
- Recommandation : Archiver pour IA pratique
- **RESUME_v5_FOR_TOMMY.md**

---

## [4.0] - 2025 (Historique)

### Results
- Reservoir computing : CA 2× pires, 100× plus lents vs ESN
- **docs/BRAIN_RESERVOIR_v4_REPORT.md**

---

## [1.0-3.x] - 2024-2025 (Historique)

### Added
- Exploration règles CA Life-like
- Métriques (capacity, robustness, basin, stability)
- Brain modules identifiés (life, highlife, 34life, etc.)
- Moteurs CA 2D/3D vectorisés

---

**Format** : [Semantic Versioning](https://semver.org/)  
**Conventions** : Added/Changed/Fixed/Removed/Closed

