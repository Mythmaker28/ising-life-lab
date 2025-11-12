# Bridge fp-qubit-design

**Projet** : fp-qubit-design  
**GitHub** : https://github.com/Mythmaker28/fp-qubit-design  
**Statut** : ✅ **Opérationnel** (Script scorer prêt, format défini)

---

## Vue d'Ensemble

**fp-qubit-design** utilise ML (random forest, potentiellement GNN) pour prédire propriétés de mutants de protéines fluorescentes optimisées (biosenseurs/qubits).

**Integration ising-life-lab** : Filtres physiques post-ML, validation designs, Pareto multi-objectifs (contraste vs robustesse vs coût).

---

## État Actuel des Connaissances

### Informations Disponibles (via README Atlas)

**Données d'entraînement** : Atlas v1.2 (22 systèmes, subset de v1.2.1 Frontiers)  
**Objectif** : Prédire propriétés spectrales et dynamic range de mutants  
**Technologies pressenties** : Random forest, potentiellement GNN

### Informations Confirmées (Web Search fp-qubit-design)

✅ **Langage** : Python ≥3.11  
✅ **État projet** : v2.2.2 (balanced), 221 systèmes utiles, 30 familles  
✅ **ML status** : NO-GO sur critères stricts (R² < 0.20, MAE > 7.81)  
✅ **Mode opératoire** : **Shortlists expérimentales** (pas prédictions ML fiables)  
✅ **Deliverables** : 
  - `shortlist_top12_final.csv` : 12 candidats validation expérimentale
  - `shortlist_lab_sheet.csv` : Feuille labo complète
  - `plate_layout_96.csv`, `plate_layout_24.csv` : Layouts plaques
  - `protocol_skeleton.md` : Protocole mesures spectrales
  - `filters_recommendations.md` : Fenêtres exc/émission

**Source** : [fp-qubit-design GitHub](https://github.com/Mythmaker28/fp-qubit-design)

---

## Actions Nécessaires (Exploration)

### Phase 1 : Clone & Analyse Structure

```bash
# Clone local fp-qubit-design (si pas déjà fait)
cd ..
git clone https://github.com/Mythmaker28/fp-qubit-design.git
cd fp-qubit-design

# Lister structure
ls -R

# Identifier fichiers clés
find . -name "*.py" -o -name "*.md" -o -name "*.csv" -o -name "*.json"
```

**Objectifs** :
1. Identifier pipeline ML (train/predict scripts)
2. Comprendre format inputs (features, séquences ?)
3. Comprendre format outputs (colonnes prédites)
4. Localiser dataset training (Atlas v1.2, 22 systèmes)

### Phase 2 : Opportunités Integration ising-life-lab

**Opportunité 1 : Migration Données v1.2 → v2.2.2**

**Gain** : ×8 plus de données (22 → 180 systèmes curated)

**Actions** :
1. Vérifier compatibilité format Atlas v1.2 vs v2.2.2
2. Mapper colonnes Atlas v2.2.2 → features fp-qubit
3. Ré-entraîner modèles ML sur 180 systèmes
4. Valider sur subset test indépendant

**Risques** :
- Features manquantes dans v2.2.2 (improbable, v2 plus complet)
- Biais distribution (v1.2 peut-être plus homogène)

**Opportunité 2 : Filtres Physiques Post-ML**

**Objectif** : Rejeter mutants prédits mais non réalisables physiquement

**Filtres proposés** (inspirés ising-life-lab) :

```python
def filter_ml_predictions(df_predicted):
    """
    Applique filtres durs aux prédictions ML
    Inspiré méthodologie ising-life-lab (filtres density, entropy, stability)
    """
    # Filtre 1 : Contraste >= 1.0 (minimum réaliste)
    df = df_predicted[df_predicted['contrast_pred'] >= 1.0].copy()
    
    # Filtre 2 : Stokes shift >= 10nm (séparation spectrale)
    df = df[df['stokes_shift_pred'] >= 10].copy()
    
    # Filtre 3 : Longueurs d'onde biologiques (300-700nm)
    df = df[(df['ex_nm_pred'] >= 300) & (df['ex_nm_pred'] <= 700)].copy()
    df = df[(df['em_nm_pred'] >= 300) & (df['em_nm_pred'] <= 700)].copy()
    
    # Filtre 4 : Robustness proxy (si disponible)
    if 'robustness_pred' in df.columns:
        df = df[df['robustness_pred'] >= 0.3].copy()
    
    print(f"Filtered: {len(df_predicted)} → {len(df)} designs")
    return df
```

**Validation** : Comparer % rejet vs baseline (random rejection).

**Opportunité 3 : Pareto Multi-Objectifs**

**Objectif** : Trade-offs contraste vs robustesse vs coût synthèse

```python
from design_space.pareto import find_pareto_frontier  # À créer

def pareto_mutant_designs(df_predicted):
    """
    Trouve frontière Pareto : maximiser contraste/robustesse, minimiser coût
    """
    objectives = {
        'contrast': df_predicted['contrast_pred'].values,
        'robustness': df_predicted['robustness_pred'].values,
        'cost': -df_predicted['synthesis_cost'].values  # Négatif = minimiser
    }
    
    pareto_indices = find_pareto_frontier(objectives)
    return df_predicted.iloc[pareto_indices]
```

**Limitation** : Nécessite estimation coût synthèse (nombre mutations, complexité repliement).

---

## Format Attendu (Spécifié v8.3)

### Inputs ML (À Confirmer par Exploration)

**Format recommandé** : CSV avec séquences + metadata

| Colonne | Type | Description | Obligatoire |
|---------|------|-------------|-------------|
| `sequence` | str | Séquence protéine (FASTA) | Oui |
| `mutations` | str | Mutations vs wild-type (ex: "V163A,Y145F") | Optionnel |
| `parent_protein` | str | Protéine de référence (ex: "EGFP") | Recommandé |
| `structure_pdb` | str | PDB ID (pour GNN) | Optionnel |

### Outputs ML (Format Supporté par ising-life-lab)

**Format CSV minimal** :

| Colonne | Type | Description | Obligatoire |
|---------|------|-------------|-------------|
| `mutant_id` | str | Identifiant mutant | Oui |
| `parent_protein` | str | Protéine référence | Recommandé |
| `contrast_pred` | float | Contraste prédit | **Oui** |
| `excitation_nm_pred` | float | Excitation prédite (nm) | Optionnel |
| `emission_nm_pred` | float | Émission prédite (nm) | Optionnel |
| `confidence` | float | Confiance prédiction (0-1) | Optionnel |
| `mutations` | str | Mutations appliquées | Optionnel |

**Colonnes stress-test (optionnelles)** :
- `photostability_score` (0-1)
- `contrast_ph_stability` (0-1)
- `contrast_temp_stability` (0-1)

---

## Usage avec ising-life-lab (Opérationnel v8.3)

### Scénario 1 : Scorer Mutants Prédits (Script Prêt)

```bash
# Depuis ising-life-lab/
python scripts/score_fp_predictions.py \
    --input ../fp-qubit-design/outputs/mutants_predicted.csv \
    --output outputs/fp_mutants_scored.csv \
    --min-contrast 1.0 \
    --min-confidence 0.5 \
    --top-n 50
```

**Output** : CSV trié par functional_score avec colonnes :
- Toutes colonnes d'origine
- `functional_score` (0-1)
- `rank` (1, 2, 3...)

### Scénario 2 : Filtrer & Ranker en Python

```python
import sys
sys.path.insert(0, "path/to/ising-life-lab")

from metrics.functional_score import apply_functional_score
from scripts.score_fp_predictions import harmonize_fp_predictions, filter_predictions
import pandas as pd

# 1. Charger prédictions fp-qubit-design
df_pred = pd.read_csv("../fp-qubit-design/outputs/mutants_predicted.csv")

# 2. Harmoniser schéma
df_harmonized = harmonize_fp_predictions(df_pred)

# 3. Filtrer (contraste >= 5.0, confiance >= 0.7)
df_filtered = filter_predictions(df_harmonized, min_contrast=5.0, min_confidence=0.7)

# 4. Scorer
df_scored = apply_functional_score(df_filtered, sort=True)

# 5. Top 10
print(df_scored.head(10)[['system_id', 'protein_name', 'contrast_normalized', 'functional_score']])
```

### Scénario 3 : Exemple Complet (Mock Data)

```bash
# Test avec mock predictions (inclus dans ising-life-lab)
python scripts/score_fp_predictions.py \
    --input tests/fixtures/mock_fp_predictions.csv \
    --output outputs/mock_fp_scored.csv \
    --min-contrast 1.0

# Output:
# Top 5:
#  rank system_id protein_name  contrast_normalized  functional_score
#     1   MUT_004      GCaMP6s                 45.0          0.850000
#     2   MUT_005      GCaMP6s                 38.2          0.789556
#     3   MUT_009         EGFP                 18.5          0.614444
#     4   MUT_008     mScarlet                 15.8          0.590444
#     5   MUT_001         EGFP                 12.5          0.561111
```

---

## Roadmap Integration

### ✅ v8.3 (Complété)

**Actions réalisées** :
- [x] Format CSV défini (inputs/outputs ML supportés)
- [x] Script scorer implémenté (`scripts/score_fp_predictions.py`)
- [x] Fonctions harmonisation/filtrage opérationnelles
- [x] Tests mock predictions (10 mutants, scoring validé)
- [x] Documentation usage (3 scénarios concrets)

**Résultat** : Bridge opérationnel, script prêt à recevoir CSV fp-qubit-design

### 🔄 v8.4 (Prochain)

**Actions à venir** :
1. [ ] Clone local fp-qubit-design (exploration structure réelle)
2. [ ] Tester script scorer sur vraies prédictions fp-qubit (si disponibles)
3. [ ] Proposer migration Atlas v1.2 (22 sys) → v2.2.2 (180 sys)
4. [ ] Créer module `design_space/pareto.py` (multi-objectifs)

**Deadline** : Semaines 3-4

---

## Risques & Mitigation

### Risque 1 : Repo Vide/Inaccessible

**Impact** : Bloque intégration

**Mitigation** :
- Vérifier accès GitHub (repo public/privé ?)
- Contacter auteur si nécessaire
- Documenter comme "spéculatif" si inaccessible

### Risque 2 : Format Incompatible

**Impact** : Migration v1.2 → v2.2.2 difficile

**Mitigation** :
- Mapper colonnes manuellement
- Créer script conversion robuste
- Valider sur subset commun (22 systèmes v1.2 ∈ v2.2.2)

### Risque 3 : Filtres Trop Restrictifs

**Impact** : Rejette trop de mutants (faux négatifs)

**Mitigation** :
- Tester seuils filtres (ex: contraste ≥ 0.5 vs ≥ 1.0)
- Valider sur subset expérimental (si disponible)
- Documenter % rejet et justifier

---

## Contact & Contribution

**Issues fp-qubit-design** : https://github.com/Mythmaker28/fp-qubit-design/issues  
**Issues ising-life-lab** : (votre repo)

**Suggestions** :
- Migration Atlas v2.2.2 (×8 plus de données)
- Filtres physiques post-ML
- Pareto multi-objectifs

---

**Bridge fp-qubit-design ↔ ising-life-lab : Prêt (Exploration Nécessaire) 🟡**

**Potentiel ×8 augmentation données ML, filtres robustesse, Pareto.**

