# Release Notes — Toolkit Core r1

**Date** : 2025-11-11  
**Version** : toolkit-core-r1  
**Statut** : Stable, Testé, Documenté

---

## Vue d'Ensemble

**Première release publique** d'ising-life-lab comme **toolkit R&D** pour analyse/scoring de systèmes quantiques et biosenseurs.

**Périmètre** :
- Chargement & validation datasets standardisés (CSV)
- Filtrage & sélection de candidats (température, contraste, contexte biologique)
- Scoring fonctionnel (intégrabilité, robustesse)
- Optimisation multi-objectifs (Pareto)
- Bridges vers projets externes (Atlas, fp-qubit-design)

**Phase CA-reservoir** : Archivée (v1-v7). Outils réutilisés, exploration close.

---

## Capacités Livrées

### Module design_space (19 fonctions)

**Loaders** (6 fonctions) :
- `load_atlas_optical(tier)` : Charge Atlas Tier 1/2/3
- `load_generic_design_space(path)` : Charge CSV standardisé
- `validate_design_space_schema(df)` : Validation colonnes/ranges
- `convert_atlas_to_design_space(df)` : Mapping Atlas → schema standard
- `list_available_atlas_tiers()` : Liste tiers disponibles
- `get_column_summary(df)` : Résumé colonnes

**Selector** (10 fonctions) :
- `load_design_space()` : Charge outputs/qubit_design_space_v1.csv
- `rank_by_integrability(df, top_n)` : Score 0-6 combiné
- `list_room_temp_candidates(df)` : Filtre 295-310K
- `list_bio_adjacent_candidates(df)` : Filtre in_vivo/in_cellulo
- `list_high_contrast_candidates(df, min)` : Filtre contraste ≥ seuil
- `list_near_infrared_candidates(df)` : Filtre émission ≥650nm
- `filter_by_family(df, family)` : Filtre par catégorie
- `get_system_by_id(df, id)` : Détails complets système
- `get_families(df)` : Liste familles disponibles
- `get_stats_summary(df)` : Stats globales

**Pareto** (3 fonctions) :
- `compute_pareto_front(df, objectives)` : Identification systèmes Pareto-optimaux
- `rank_pareto(df, objectives, tie_breakers)` : Classement Pareto → tie-breakers
- `get_pareto_summary(df, objectives)` : Stats front (count, %, ranges)

### Module metrics

**functional_score** (4 fonctions) :
- `compute_functional_score(row, weights, max_contrast)` : Score 0-1 ligne unique
- `apply_functional_score(df, weights, sort)` : Score DataFrame complet
- `explain_score(row, weights)` : Debug composantes
- `get_score_weights(mode)` : 3 modes (default, high_contrast, bio_focus)

### Scripts

**score_fp_predictions.py** : CLI scorer prédictions ML
```bash
python scripts/score_fp_predictions.py \
    --input predictions.csv \
    --output scored.csv \
    --min-contrast 1.0 \
    --top-n 50
```

---

## Dataset Inclus

**Atlas Tier 1 (180 systèmes)** :
- Protéines fluorescentes (GCaMP, ASAP, GRAB, etc.)
- Métadonnées validées (contraste, température, contexte, DOI)
- Source : [Quantum-Sensors-Qubits-in-Biology v2.2.2](https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology)

**Fichiers** :
- `data/atlas_optical/atlas_fp_optical_v2_2_curated.csv` (180 systèmes, 42 colonnes)
- `outputs/qubit_design_space_v1.csv` (standardisé, 25 colonnes, tags dérivés)

---

## Tests

**Suite toolkit** : **70 tests, 100% pass**
- test_loaders.py : 15 tests (validation, load Atlas)
- test_selector.py : 24 tests (filtres, ranking)
- test_functional_score.py : 18 tests (compute, apply, explain)
- test_pareto.py : 13 tests (front, ranking, summary)

**Suite complète (avec historique isinglab)** : **154 tests pass, 12 skipped** (CA historiques)

```bash
pytest tests/ -q
# 154 passed, 12 skipped in 6.7s
```

---

## Documentation

### Essentiels (Lire en premier)

1. **README.md** : Quick start, usage, installation
2. **CHANGELOG.md** : Historique versions v8.0 → toolkit-core-r1
3. **docs/STATE_v9_0.md** : Vision consolidée (capacités, datasets, gaps)

### Bridges Projets Externes

- **docs/BRIDGE_ATLAS_QUANTUM_SENSORS.md** : Format, usage Atlas (✅ Opérationnel, 180 systèmes)
- **docs/BRIDGE_FP_QUBIT_DESIGN.md** : Format, usage fp-qubit (✅ Opérationnel, scorer prêt)
- **docs/BRIDGE_NON_OPTICAL_QUBITS_v9_2.md** : Format NV/spins (🟡 Spec prête, CSV absents)
- **docs/BRIDGE_ARREST_MOLECULES.md** : Format arrest (🔴 Spéculatif, données ΔG absentes)

### Specs & Rapports

- **docs/MISSION_v8_2.md** : Périmètre toolkit
- **docs/PLAN_v8_2.md** : Roadmap
- **docs/DESIGN_SPACE_v1_REPORT.md** : Analyse 180 systèmes (top candidats, gaps)
- **docs/STRESS_METRICS_SPEC_v8_3.md** : Colonnes optionnelles stress-test (spec, données absentes)

### Archive Historique

**docs/archive/** : ~40 documents verbeux phases exploration (v1-v9). Conservés pour traçabilité, **non nécessaires** pour usage toolkit.

---

## Limitations Assumées

### Données Absentes

❌ **Photostabilité, stabilité pH/température** : Spécifiées (STRESS_METRICS_SPEC), données à collecter (littérature, 5-10h)  
❌ **Datasets non-optical** : Format défini, CSV absents (`data/atlas_nonoptical/` vide)  
❌ **arrest-molecules** : Bridge spec prêt, données ΔG absentes

### Bridges Non Testés en Réel

🟡 **fp-qubit-design** : Script scorer opérationnel sur mock (10 mutants). Pas testé sur vraies prédictions fp-qubit (shortlists expérimentales, pas flux continu ML).

### Validation Littérature

🟡 **functional_score** : Heuristique raisonnable (contraste, température, bio, maturité). Pas validée formellement vs papiers originaux (recherche web limitée).

---

## Résultats Mesurés

### Top 5 Systèmes (functional_score, 180 systèmes réels)

| Rang | Protéine | Famille | Contraste | Score | Contexte |
|------|----------|---------|-----------|-------|----------|
| 1 | jGCaMP8s | Calcium | 90.0× | 1.000 | in vivo, 298K |
| 2 | jGCaMP8f | Calcium | 78.0× | 0.947 | in vivo, 298K |
| 3 | jGCaMP7s | Calcium | 50.0× | 0.822 | in vivo, 298K |
| 4 | jGCaMP7f | Calcium | 45.0× | 0.800 | in vivo, 298K |
| 5 | XCaMP-Gs | Calcium | 45.0× | 0.800 | in vivo, 298K |

**Observation** : Dominance calcium sensors (GCaMP family, neurosciences).

### Statistiques Dataset

- 180 systèmes catalogués (protéines fluorescentes)
- 30 familles (Calcium 22%, Voltage 12%, Dopamine 7%, etc.)
- 68% room temp viable (295-310K)
- 92% bio-adjacent (in vivo/in cellulo)
- 39% high contrast (≥5.0)

---

## Prochaines Étapes Suggérées

### Court Terme

1. Enrichir données stress-test (photostabilité 5-10 systèmes pilotes via littérature)
2. Explorer datasets non-optical (GitHub Atlas staging, contacter auteur)
3. Tester scorer sur vraies shortlists fp-qubit-design (si disponibles localement)

### Moyen Terme

1. Dashboard interactif (Plotly Dash : scatter plots, filtres dynamiques)
2. Module visualizations (scatter, histogrammes, heatmaps)
3. Validation littérature functional_score (PubMed, papiers GCaMP/Archon)

### Long Terme

1. Integration arrest-molecules (si données ΔG Zenodo disponibles)
2. Datasets non-optical complets (NV centers, spins, radical pairs)
3. Publication académique (si résultats significatifs)

---

## Installation & Usage

### Installation

```bash
git clone https://github.com/[...]/ising-life-lab.git
cd ising-life-lab
python -m pip install -e .
```

### Test 30s

```bash
pytest tests/ -q  # 154 passed, 12 skipped
python scripts/score_fp_predictions.py \
    --input tests/fixtures/mock_fp_predictions.csv \
    --output outputs/test.csv
```

### Usage Python

```python
from design_space import load_design_space, rank_by_integrability, compute_pareto_front
from metrics import apply_functional_score

# Charger & scorer
df = load_design_space()
df_scored = apply_functional_score(df, sort=True)

# Pareto
df_pareto = compute_pareto_front(df_scored, {
    'functional_score': 'max',
    'contrast_normalized': 'max'
})

print(f"Top: {df_scored.iloc[0]['protein_name']} (score {df_scored.iloc[0]['functional_score']:.3f})")
```

---

## Citation

```bibtex
@software{ising_life_lab_toolkit_core_r1,
  title = {Ising-Life-Lab: Quantum \& Biosensor Design Space Toolkit},
  author = {Lepesteur, Tommy (Mythmaker28)},
  version = {toolkit-core-r1},
  year = {2025},
  url = {https://github.com/Mythmaker28/ising-life-lab}
}
```

**Licence** : MIT (code), CC BY 4.0 (données Atlas)

---

## Remerciements

**Données** : Biological Qubits Atlas v2.2.2 (Mythmaker28)  
**Méthodo** : Leçons branche CA-reservoir (v1-v7) — filtres, baselines, kill switch

---

**Toolkit core r1 : Stable, testé, documenté, prêt pour usage externe.** ✅

