# Mission v8.2 — Périmètre Toolkit

**Date** : 2025-11-11  
**Version** : 8.2 (Consolidation)  
**Objectif** : Définir clairement le périmètre d'ising-life-lab comme toolkit R&D multi-projets

---

## Identité

**Ising-Life-Lab** est un **toolkit d'analyse et de scoring** pour systèmes quantiques et biosenseurs.

**Rôle** : Pont méthodologique entre projets (Atlas, fp-qubit-design, arrest-molecules), fournissant :
- Chargement & validation datasets standardisés
- Métriques robustes (intégrabilité, contraste, robustesse)
- Filtres & classements de candidats
- Documentation usage externe

---

## Périmètre

### Ce Que Nous Faisons

✅ **Analyser** : Charger CSV/JSON, valider schémas, détecter anomalies  
✅ **Filtrer** : Sélectionner candidats selon critères (température, contraste, contexte biologique)  
✅ **Scorer** : Calculer métriques combinées (intégrabilité, robustesse, stabilité)  
✅ **Documenter** : Rapports clairs, gaps identifiés, recommandations actionnables  
✅ **Connecter** : Bridges lecture-seule vers projets externes (Atlas, fp-qubit, arrest)

### Ce Que Nous NE Faisons PAS

❌ **Prédire** : Pas de ML/DL entraîné dans ce repo (ça reste dans fp-qubit-design)  
❌ **Simuler** : Pas de MD/DFT/simulations physiques lourdes  
❌ **Modifier datasets externes** : Read-only sur Atlas, fp-qubit, arrest  
❌ **Prétendre à l'AGI** : Branche CA-réservoir close, focus outils concrets

---

## Inputs Attendus

### Format CSV Standardisé

**Colonnes minimales** (design_space) :
- `system_id` (str) : Identifiant unique
- `protein_name` / `molecule_name` (str) : Nom système
- `family` (str) : Catégorie fonctionnelle (Calcium, Voltage, etc.)
- `temp_k` (float) : Température opération (Kelvin)
- `contrast_normalized` (float) : Contraste/dynamic range
- `integration_level` (str) : Contexte (in_vivo, in_cellulo, in_vitro, unknown)
- `status` (str) : Maturité (A, B, C, unknown)

**Colonnes optionnelles** :
- `ph`, `excitation_nm`, `emission_nm`, `doi`, `year`, etc.

**Validation** :
- Pas de duplicates sur `system_id`
- Ranges valides (`temp_k` ≥ 0, `contrast_normalized` > 0)
- Colonnes critiques non vides

### Sources Supportées

1. **Atlas Quantum Sensors** (Tier 1 curated) : 180 systèmes optical ✅
2. **Atlas non-optical** : NV centers, spins (à venir) 🟡
3. **fp-qubit-design outputs** : Mutants prédits (à explorer) 🟡
4. **arrest-molecules** : Compounds + ΔG (spéculatif) 🔴

---

## Outputs Produits

### 1. CSV Standardisés

**Fichier** : `outputs/qubit_design_space_v1.csv`  
**Contenu** : Dataset nettoyé avec tags dérivés (room_temp_viable, bio_adjacent, high_contrast, etc.)

### 2. Métriques & Scores

**Fonctions** (dans `design_space/selector.py`) :
- `rank_by_integrability(df, top_n)` → Score 0-6 combinant temp/contexte/contraste/maturité
- `list_*_candidates()` → Filtres booléens sur tags
- `get_stats_summary(df)` → Statistiques globales

### 3. Rapports Markdown

**Exemples** :
- `docs/DESIGN_SPACE_v1_REPORT.md` : Analyse 180 systèmes (top candidats, gaps, recommandations)
- `docs/BRIDGE_*.md` : Format/usage bridges multi-projets

### 4. Visualisations (Futur v8.3+)

**Prévues** :
- Scatter plots (contraste vs température, excitation vs émission)
- Histogrammes (distribution familles, niveaux intégration)
- Heatmaps (corrélations métriques)

---

## Usage Type

### Cas 1 : Sélection Biosenseur pour Expérience

```python
from design_space.selector import load_design_space, filter_by_family, rank_by_integrability

# Charger design space
df = load_design_space()

# Filtrer calcium sensors
calcium = filter_by_family(df, "Calcium")

# Ranker par intégrabilité
top_calcium = rank_by_integrability(calcium, top_n=5)

# Sélectionner candidat
candidate = top_calcium.iloc[0]
print(f"Candidat recommandé : {candidate['protein_name']} (contraste {candidate['contrast_normalized']:.1f}×)")
```

### Cas 2 : Validation Dataset Externe

```python
from design_space.loaders import validate_design_space_schema

# Charger dataset externe
import pandas as pd
external_df = pd.read_csv("external_project/mutants_predicted.csv")

# Valider schéma
report = validate_design_space_schema(external_df, expected_columns=['system_id', 'family', 'temp_k'])

# Afficher warnings/erreurs
if report['errors']:
    print("Erreurs détectées :")
    for error in report['errors']:
        print(f"  - {error}")
```

### Cas 3 : Comparaison Multi-Familles

```python
from design_space.selector import load_design_space, filter_by_family

df = load_design_space()

families = ['Calcium', 'Voltage', 'Dopamine']
for family in families:
    subset = filter_by_family(df, family)
    median_contrast = subset['contrast_normalized'].median()
    print(f"{family}: {len(subset)} systèmes, contraste médian {median_contrast:.2f}×")
```

---

## Dépendances

### Obligatoires

```
pandas >= 1.5.0
numpy >= 1.23.0
pytest >= 7.0.0  # Pour tests
```

### Optionnelles (Futur)

```
matplotlib >= 3.5.0  # Visualisations
seaborn >= 0.12.0    # Heatmaps
plotly >= 5.0.0      # Dashboard interactif
```

---

## Maintenance & Évolution

### Ajout Nouveau Dataset

1. Placer CSV dans `data/` (ex: `data/new_qubits/dataset.csv`)
2. Créer loader dans `design_space/loaders.py` :
   ```python
   def load_new_qubits(path="data/new_qubits/dataset.csv"):
       df = pd.read_csv(path)
       # Standardiser colonnes
       # Valider
       return df
   ```
3. Ajouter tests dans `tests/test_loaders.py`
4. Documenter dans `docs/BRIDGE_NEW_QUBITS.md`

### Ajout Nouvelle Métrique

1. Implémenter dans `design_space/metrics.py` (à créer) :
   ```python
   def calculate_new_metric(df):
       # Calcul
       return df['new_metric']
   ```
2. Ajouter tests dans `tests/test_metrics.py`
3. Documenter formule/baseline dans rapport
4. **Valider vs baseline** : Toujours comparer à méthode triviale

### Ajout Bridge Multi-Projets

1. Lire repo externe (lecture seule)
2. Identifier format/colonnes clés
3. Créer `docs/BRIDGE_PROJECT_NAME.md` :
   - Format minimal attendu
   - Exemple usage loaders + selector
   - Statut (✅🟡🔴)
4. Implémenter loader si données disponibles
5. Ajouter tests

---

## Principes Directeurs

### Rigueur Scientifique

- **Baselines obligatoires** : Toute métrique validée vs méthode triviale
- **Tests systématiques** : Toute fonction = au moins 1 test unitaire
- **Transparence** : Gaps/limitations clairement marqués
- **Reproductibilité** : Seed fixe, versions dépendances documentées

### Pas de Spéculation

- **Données manquantes** : Noter "unknown" ou "TODO", ne pas inventer
- **Connexions projets** : Seulement si données/format connus
- **Métriques** : Seulement si définition mathématique claire + validable

### Kill Switch

- **Si pas de signal positif après exploration raisonnable** (3-4h) : documenter échec, archiver, passer à autre chose
- **Pas de "une dernière petite tentative"**

---

## Contact & Contribution

**Roadmap** : Voir `docs/PLAN_v8_2.md`  
**Issues** : Problèmes/suggestions bienvenues  
**Pull Requests** : Suivre principes ci-dessus (tests, baselines, docs)

---

**Mission v8.2** : Faire d'ising-life-lab un **toolkit clair, robuste et exploitable** par projets externes.

**Sans bullshit. Juste des outils mesurés.** ✅

