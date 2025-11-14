# Plan v8.2 — Roadmap Toolkit

**Date** : 2025-11-11  
**Version** : 8.2 (Consolidation)  
**Objectif** : Roadmap court/moyen/long terme ising-life-lab

---

## Stratégie Globale

**v8.0-v8.1** : Fondations (datasets, analyse, rapports) ✅  
**v8.2** : Consolidation (tests, loaders, bridges, clarté) ✅  
**v8.3** : **Features Functional** (scoring, stress-test, bridge fp-qubit) ✅ COMPLÉTÉ  
**v8.4** : Features avancées (Pareto, enrichissement données, dashboard)  
**v8.5+** : Extensions (non-optical, arrest, conformations)

---

## Court Terme (v8.2, Semaines 1-2)

### Phase A : Vitrine ✅ COMPLÉTÉ

- [x] Réécrire README.md (focus toolkit, archiver CA)
- [x] Créer docs/MISSION_v8_2.md (périmètre, inputs/outputs)
- [x] Créer docs/PLAN_v8_2.md (ce document)

### Phase B : Solidification Code 🔄 EN COURS

**Priorité** : Rendre le toolkit utilisable par projets externes

#### B.1 Loaders (`design_space/loaders.py`)

```python
# À implémenter
def load_atlas_optical(tier="curated", data_dir="data/atlas_optical")
def load_generic_design_space(csv_path)
def validate_design_space_schema(df, expected_columns)
```

**Statut** : 🔄 En création  
**Tests** : `tests/test_loaders.py`  
**Deadline** : Semaine 1

#### B.2 Tests Unitaires

**Fichiers à créer** :
- `tests/fixtures/mini_design_space.csv` (10 systèmes)
- `tests/test_loaders.py` (validation schema, load Atlas)
- `tests/test_selector.py` (filtres, ranking, familles)

**Couverture cible** : ≥80% sur design_space/  
**Deadline** : Semaine 1-2

#### B.3 Docstrings & Type Hints

**Modules concernés** :
- `design_space/selector.py` : Ajouter docstrings détaillées
- `design_space/loaders.py` : Docstrings + examples
- Type hints partout (Python 3.9+)

**Deadline** : Semaine 2

### Phase C : Bridges Multi-Projets 🔄 EN COURS

**Objectif** : Documenter usage externe clair

#### C.1 Bridge Atlas ✅ Opérationnel

**Doc** : `docs/BRIDGE_ATLAS_QUANTUM_SENSORS.md`  
**Contenu** :
- Format Tier 1 (colonnes, types)
- Usage `load_atlas_optical()` + `selector.py`
- Exemple complet (load → filter → rank)
- Statut : ✅ Données disponibles (180 systèmes)

**Deadline** : Semaine 1

#### C.2 Bridge fp-qubit-design 🟡 À Explorer

**Doc** : `docs/BRIDGE_FP_QUBIT_DESIGN.md`  
**Actions** :
1. Clone local fp-qubit-design
2. Identifier format outputs ML (CSV mutants prédits ?)
3. Définir loader hypothétique
4. Proposer filtres physiques post-ML
5. Statut : 🟡 Prêt (exploration nécessaire)

**Deadline** : Semaine 2

#### C.3 Bridge arrest-molecules 🔴 Spéculatif

**Doc** : `docs/BRIDGE_ARREST_MOLECULES.md`  
**Actions** :
1. Clone local arrest-molecules
2. Télécharger dataset Zenodo (DOI: 10.5281/zenodo.17420685)
3. Identifier format (10 compounds, 44 predictions)
4. Proposer métriques stabilité (si ΔG disponibles)
5. Statut : 🔴 Spéculatif (données énergétiques nécessaires)

**Deadline** : Semaine 2 (doc uniquement, implémentation si données OK)

### Phase D : Nettoyage & Cohérence

**Fichiers à mettre à jour** :
- `docs/MULTIPROJECT_CONTEXT_v8.md` : Acter toolkit, pointer bridges
- `RESUME_v8_POUR_TOMMY.md` : Intégrer v8.2
- Vérifier cohérence mentions v8.x dans tous docs

**Deadline** : Fin semaine 2

---

## Réalisé v8.3 (Semaine 3)

### Features Functional ✅ COMPLÉTÉ

#### functional_score Module

✅ **`metrics/functional_score.py`** :
- `compute_functional_score(row)` : Score 0-1 basé sur colonnes réelles
- `apply_functional_score(df)` : Application à DataFrame complet
- `explain_score(row)` : Explication détaillée composantes
- `get_score_weights(mode)` : 3 modes pondération (default, high_contrast, bio_focus)

✅ **Formule base** :
```
score = 0.4×contrast + 0.25×room_temp + 0.20×bio_adj + 0.15×stable
```

✅ **Colonnes stress-test optionnelles** (détectées automatiquement) :
- photostability_score (bonus -0.1 à +0.1)
- contrast_ph_stability (bonus 0 à +0.1)
- contrast_temp_stability (bonus 0 à +0.1)

✅ **Tests** : `tests/test_functional_score.py` (20+ tests, tous passent)

#### Stress-Test Specification

✅ **`docs/STRESS_METRICS_SPEC_v8_3.md`** :
- Définition 3 colonnes optionnelles (photostabilité, pH, température)
- Logique conditionnelle implémentée (détection automatique)
- Workflow collecte données (littérature, calculs)
- Garde-fous (pas d'invention données)

#### Bridge fp-qubit-design Concret

✅ **`scripts/score_fp_predictions.py`** :
- CLI pour scorer CSV prédictions ML
- Harmonisation format fp-qubit → design_space
- Filtres physiques (contraste ≥1.0, longueurs d'onde 300-700nm, confidence)
- Output : CSV trié par functional_score + rank

✅ **Tests** : Mock predictions (10 mutants) scored avec succès
- Top: MUT_004 (GCaMP6s mutant, 45× contrast, score 0.850)

✅ **`docs/BRIDGE_FP_QUBIT_DESIGN.md`** : Statut upgraded ✅ Opérationnel

---

## Moyen Terme (v8.4, Semaines 4-6)

### Enrichissement Données

**Atlas stress-test data** :
- Miner littérature pour contraste vs pH (6.5-8.0)
- Miner littérature pour contraste vs température (295-310K)
- Ajouter colonnes `contrast_ph_*`, `contrast_temp_*`
- Source : PubMed, DOI Atlas, suppléments papiers

**Objectif** : Valider hypothèses robustesse environnementale  
**Deadline** : Semaine 4

### Scoring Avancé

**functional_score adapté** :
```python
def functional_score_biosensor(df, weights={'contrast': 0.4, 'robustness': 0.3, 'integration': 0.3}):
    # Score adapté domaine biosenseurs
    # Validation vs baseline (tri contraste simple)
    pass
```

**Métriques robustesse** :
- `robustness_ph` : Variance contraste sur plage pH
- `robustness_temp` : Variance contraste sur plage température
- `robustness_photobleaching` : Si données disponibles

**Validation** : Toujours comparer à baseline triviale  
**Deadline** : Semaine 5

### Exploration fp-qubit-design

**Actions** :
1. Clone local, comprendre structure ML pipeline
2. Identifier opportunités intégration (filtres, validation)
3. Proposer migration Atlas v1.2 (22 sys) → v2.2.2 (180 sys)
4. Documenter bénéfices attendus (8× plus de données)

**Deadline** : Semaine 6

---

## Long Terme (v8.4+, Mois 2-3)

### Pareto Multi-Objectifs

**Module** : `design_space/pareto.py`

```python
def find_pareto_frontier(df, objectives=['contrast_normalized', 'robustness_score', '-synthesis_cost']):
    # Trade-offs contraste vs robustesse vs coût
    # Visualisation scatter 2D/3D
    pass
```

**Objectifs** :
- Contraste (maximiser)
- Robustesse (maximiser)
- Coût synthèse (minimiser, si données disponibles)

**Deadline** : Mois 2

### Dashboard Interactif

**Tech** : Plotly Dash ou Streamlit

**Features** :
- Upload CSV custom
- Filtres interactifs (sliders temp, contraste, famille)
- Scatter plots dynamiques (ex vs em, contraste vs temp)
- Export candidats sélectionnés (CSV, JSON)

**Deadline** : Mois 2-3

### Datasets Non-Optical

**Sources** :
- Atlas non-optical (NV centers, SiC defects, spins nucléaires)
- Radical pairs (cryptochrome, photolyase)
- Many-body quantum systems

**Actions** :
1. Explorer structure GitHub Atlas (staging area ?)
2. Contacter auteur si CSV non publics
3. Adapter loaders pour non-optical
4. Documenter T1/T2 (temps cohérence) vs optical properties

**Deadline** : Mois 3

### Intégration arrest-molecules

**Prérequis** : Données ΔG/Ea disponibles

**Actions** :
1. Télécharger dataset Zenodo
2. Extraire paysages énergétiques (ΔG, barrières)
3. Appliquer métriques stabilité (`basin`, `stability`)
4. Valider vs données cinétiques (si disponibles)

**Deadline** : Mois 3 (si données OK)

### Modèles Conformationnels

**Sources** :
- PDB (structures expérimentales)
- AlphaFold (prédictions)

**Actions** :
1. Télécharger structures protéines Atlas (ex: GCaMP, Archon1)
2. Calculer ΔΔG (FoldX, Rosetta) pour mutants
3. Analyser B-factors (flexibilité)
4. Appliquer `basin_diversity` aux conformations

**Deadline** : Mois 3+ (long terme)

---

## Très Long Terme (v9.0+, Mois 4+)

### Machine Learning Filters

**Objectif** : Prédire propriétés manquantes (photostabilité, maturation time)

**Approche** :
1. Entraîner modèles simples (random forest) sur subset avec données complètes
2. Prédire propriétés manquantes pour reste du dataset
3. **Valider prédictions** : Subset test indépendant, comparaison littérature
4. Marquer prédictions clairement ("predicted", pas "measured")

**Garde-fou** : Pas de ML sans validation solide

### Cross-Project Integration

**Objectif** : Unifier pipelines Atlas → fp-qubit → arrest → ising-life-lab

**Actions** :
1. Schéma standardisé universel (qubits, molécules, biosenseurs)
2. API commune (load, validate, filter, score, export)
3. Plugins pour projets externes (pip install ising-toolkit)

### Publication Académique

**Si résultats significatifs** :
- Paper méthodo (metrics, baselines, kill switch)
- Dataset release (Zenodo DOI)
- Code release (GitHub + PyPI)

---

## Métriques de Succès

### v8.2 (Consolidation)

- [x] README clair, focus toolkit
- [ ] Tests ≥80% coverage design_space/
- [ ] 3 bridges documentés (Atlas ✅, fp-qubit 🟡, arrest 🔴)
- [ ] Loaders opérationnels avec validation
- [ ] Zéro régression (tests existants passent)

### v8.3 (Features Avancées)

- [ ] functional_score validé vs baseline
- [ ] Données stress-test intégrées (pH, temp)
- [ ] fp-qubit-design exploré, roadmap définie

### v8.4+ (Extensions)

- [ ] Dashboard interactif déployé
- [ ] Datasets non-optical intégrés
- [ ] Pareto multi-objectifs opérationnel

---

## Dépendances Bloquantes

| Item | Dépend De | Statut |
|------|-----------|--------|
| **Tests design_space** | loaders.py créé | 🔄 En cours |
| **Bridge fp-qubit** | Clone local repo | ⏳ À faire |
| **Bridge arrest** | Dataset Zenodo téléchargé | ⏳ À faire |
| **functional_score** | Données stress-test | ⏳ À faire |
| **Dashboard** | Pareto implémenté | ⏳ Futur |
| **Non-optical** | CSV Atlas disponibles | ⏳ Incertain |

---

## Risques & Mitigation

### Risque 1 : Données Manquantes

**Impact** : Bloque enrichissement (stress-test, non-optical)

**Mitigation** :
- Miner littérature manuellement (PubMed, Google Scholar)
- Contacter auteurs Atlas pour CSV staging
- Accepter limitations, documenter clairement

### Risque 2 : Complexité Tests

**Impact** : Couverture <80%, bugs non détectés

**Mitigation** :
- Créer fixtures simples (mini CSV 10 lignes)
- Tests unitaires petits, focalisés (1 fonction = 1 test)
- CI/CD futur (GitHub Actions) si repo public

### Risque 3 : Bridges Non Utilisés

**Impact** : Effort documentation inutile si projets externes n'intègrent pas

**Mitigation** :
- Docs claires, exemples concrets
- Proposer PRs aux projets externes si pertinent
- Accepter que certains bridges restent théoriques

---

## Communication

### Issues & Discussions

**GitHub Issues** (si repo public) :
- Feature requests
- Bug reports
- Questions usage

**Tags** :
- `enhancement` : Nouvelles features
- `bug` : Corrections
- `documentation` : Améliorations docs
- `good first issue` : Pour contributeurs externes

### Changelog

**Fichier** : `CHANGELOG.md` (à créer)

**Format** :
```markdown
## [8.2.0] - 2025-11-11

### Added
- design_space/loaders.py (load_atlas_optical, validate_schema)
- Tests unitaires (test_loaders, test_selector)
- Bridges docs (Atlas, fp-qubit, arrest)

### Changed
- README.md refonte complète (focus toolkit)
- docs/MISSION_v8_2.md (périmètre clair)

### Fixed
- (aucune régression)
```

---

## Conclusion

**v8.2 = Consolidation** : Bases solides avant features avancées  
**v8.3-v8.4 = Features** : Scoring, Pareto, dashboard  
**v8.5+ = Extensions** : Non-optical, arrest, conformations

**Principe** : Chaque version doit rendre le toolkit **un peu plus utilisable** que la précédente.

**Sans bullshit. Juste une roadmap honnête.** ✅

