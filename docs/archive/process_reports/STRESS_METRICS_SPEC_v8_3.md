# Stress Metrics Specification v8.3

**Date** : 2025-11-11  
**Statut** : 🟡 **Spécification (Données à Collecter)**

---

## Objectif

Définir les colonnes optionnelles permettant d'intégrer des **données stress-test** (pH, température, photostabilité) dans le scoring functional_score.

**Principe** : Ces colonnes sont **détectées automatiquement**. Si présentes → bonus/malus appliqués. Si absentes → score base sans ajustement.

**Pas d'invention** : On ne crée pas de fausses valeurs. Si données manquent → TODO marqué, scoring reste sur colonnes standard.

---

## Colonnes Standard (Obligatoires)

Ces colonnes existent déjà dans `qubit_design_space_v1.csv` :

| Colonne | Type | Description | Source |
|---------|------|-------------|--------|
| `contrast_normalized` | float | Contraste/dynamic range | Atlas |
| `room_temp_viable` | bool | 295-305K | Tag dérivé |
| `bio_adjacent` | bool | in_vivo/in_cellulo | Tag dérivé |
| `stable_mature` | bool | Quality tier A/B | Atlas |

**Usage** : Score base = f(contrast, room_temp, bio_adj, stable)

---

## Colonnes Stress-Test (Optionnelles)

### 1. Photostabilité

**Colonne** : `photostability_score`  
**Type** : float (0-1)  
**Définition** : Résistance au photobleaching, normalisé

**Calcul (si données disponibles)** :
```
photostability_score = 1 - (bleaching_rate / max_bleaching_rate)
```

**Sources possibles** :
- Littérature (DOI Atlas, suppléments)
- FPbase (si disponible)
- Données expérimentales (time-lapse imaging)

**Bonus dans functional_score** :
```python
if 'photostability_score' in row:
    bonus_photo = (photostability_score - 0.5) * 0.2  # -0.1 à +0.1
    score_final = score_base * (1 + bonus_photo)
```

**Exemples hypothétiques** :
- jGCaMP8s : 0.7 (modéré)
- mCherry : 0.9 (excellent)
- PA-GFP : 0.3 (faible, photoactivable)

---

### 2. Stabilité pH

**Colonne** : `contrast_ph_stability`  
**Type** : float (0-1)  
**Définition** : Inverse coefficient variation contraste sur plage pH

**Calcul (si données disponibles)** :
```
contrasts_ph = [contrast @ pH 6.5, 7.0, 7.4, 7.8, 8.0]
cv = std(contrasts_ph) / mean(contrasts_ph)
contrast_ph_stability = 1 / (1 + cv)
```

**Sources possibles** :
- Littérature (courbes contraste vs pH)
- Suppléments papiers originaux (ex: Chen et al. 2013 pour GCaMP6)

**Bonus dans functional_score** :
```python
if 'contrast_ph_stability' in row:
    bonus_ph = contrast_ph_stability * 0.1  # 0 à +0.1
    score_final = score_base * (1 + bonus_ph)
```

**Exemples hypothétiques** :
- GCaMP6s : 0.8 (stable pH 7.0-7.8)
- HyPer (pH sensor) : 0.3 (volontairement sensible pH)

---

### 3. Stabilité Température

**Colonne** : `contrast_temp_stability`  
**Type** : float (0-1)  
**Définition** : Inverse coefficient variation contraste sur plage température

**Calcul (si données disponibles)** :
```
contrasts_temp = [contrast @ 295K, 298K, 301K, 305K, 310K]
cv = std(contrasts_temp) / mean(contrasts_temp)
contrast_temp_stability = 1 / (1 + cv)
```

**Sources possibles** :
- Littérature (courbes contraste vs température)
- Données in vivo (mammifères 37°C vs cellules 25°C)

**Bonus dans functional_score** :
```python
if 'contrast_temp_stability' in row:
    bonus_temp = contrast_temp_stability * 0.1  # 0 à +0.1
    score_final = score_base * (1 + bonus_temp)
```

**Exemples hypothétiques** :
- jGCaMP8s : 0.9 (robust 295-310K)
- EGFP : 0.7 (sensibilité modérée)

---

## Implémentation dans functional_score.py

### Logique Conditionnelle (Déjà Implémentée)

```python
def compute_functional_score(row, weights=None, max_contrast=90.0):
    # Score base (colonnes standard)
    score_base = w1*contrast + w2*room_temp + w3*bio_adj + w4*stable
    
    # Ajustements stress-test (SEULEMENT si colonnes présentes)
    bonus_total = 0.0
    
    if 'photostability_score' in row.index and pd.notna(row['photostability_score']):
        bonus_total += (row['photostability_score'] - 0.5) * 0.2
    
    if 'contrast_ph_stability' in row.index and pd.notna(row['contrast_ph_stability']):
        bonus_total += row['contrast_ph_stability'] * 0.1
    
    if 'contrast_temp_stability' in row.index and pd.notna(row['contrast_temp_stability']):
        bonus_total += row['contrast_temp_stability'] * 0.1
    
    # Score final
    score_final = score_base * (1 + bonus_total)
    return max(0.0, min(1.0, score_final))
```

### Détection Automatique

Le module `apply_functional_score()` émet un **warning** si colonnes stress-test détectées :

```
UserWarning: Stress-test columns detected: ['photostability_score', 'contrast_ph_stability'].
Adjustments will be applied.
```

Si colonnes absentes → Score base, **sans crier au génie**.

---

## Workflow de Collecte de Données

### Phase 1 : Minage Littérature (Manuel)

**Action** :
1. Parcourir DOI Atlas (180 systèmes)
2. Chercher figures/tableaux contraste vs pH, T
3. Extraire valeurs numériques (OCR, tables supplémentaires)
4. Ajouter colonnes dans CSV enrichi

**Outils** :
- PubMed, Google Scholar
- Suppléments papiers (SI, Extended Data)
- Zenodo (datasets liés)

**Effort estimé** : 5-10h (manuel, tedieux)

### Phase 2 : Calcul Stabilités

**Script hypothétique** : `scripts/compute_stability_metrics.py`

```python
import pandas as pd

def compute_ph_stability(contrast_values):
    """contrast_values = [c @ pH 6.5, 7.0, 7.4, 7.8, 8.0]"""
    cv = np.std(contrast_values) / np.mean(contrast_values)
    return 1 / (1 + cv)

# Exemple : GCaMP6s
contrasts_gcamp6s = [20.0, 24.0, 26.0, 25.0, 22.0]  # Hypothétique
ph_stability = compute_ph_stability(contrasts_gcamp6s)
print(f"GCaMP6s pH stability: {ph_stability:.3f}")
```

### Phase 3 : Enrichissement CSV

**Nouveau CSV** : `outputs/qubit_design_space_v1_enriched.csv`

**Colonnes ajoutées** :
- `photostability_score` (float 0-1 ou NaN)
- `contrast_ph_stability` (float 0-1 ou NaN)
- `contrast_temp_stability` (float 0-1 ou NaN)

**Validation** :
- Pas de valeurs < 0 ou > 1
- NaN pour systèmes sans données (majoritaires initialement)
- Provenance documentée (colonne `stress_data_source` ?)

---

## Tests avec Colonnes Stress-Test

### Test Fixture Enrichi

**Fichier** : `tests/fixtures/mini_design_space_with_stress.csv`

**Contenu** : 10 systèmes mini_design_space.csv + 3 colonnes stress-test (valeurs simulées)

**Usage** : Tester logique conditionnelle functional_score

### Tests Associés

**Dans `tests/test_functional_score.py`** (déjà implémenté) :
- `test_compute_functional_score_with_bonus()` : Score avec photostabilité
- Test présence colonnes optionnelles
- Vérifier bonus appliqué correctement

---

## Limitations & TODO

### Données Actuelles

❌ **Photostabilité** : Pas de données (à miner littérature)  
❌ **Stabilité pH** : Pas de données (à miner littérature)  
❌ **Stabilité température** : Pas de données (à miner littérature)

### Actions Futures

**v8.4** : Minage littérature (5-10h manuel)  
**v8.5** : Enrichissement CSV avec colonnes stress-test  
**v8.6** : Validation scoring enrichi vs baseline

### Garde-Fous

- **Pas d'invention** : Si données manquent → NaN, pas de valeur fictive
- **Transparence** : Colonne `stress_data_source` documenter provenance
- **Validation** : Comparer scoring enrichi vs score base (overlap top 10)

---

## Exemples Hypothétiques (Illustration Seulement)

**Système robuste** :

```csv
system_id,protein_name,contrast_normalized,photostability_score,contrast_ph_stability,contrast_temp_stability,functional_score
FP_0056,jGCaMP8s,90.0,0.75,0.85,0.90,0.950
```

**Système fragile** :

```csv
system_id,protein_name,contrast_normalized,photostability_score,contrast_ph_stability,contrast_temp_stability,functional_score
FP_TEST,FragileGFP,50.0,0.30,0.40,0.50,0.520
```

**Contraste élevé mais fragile** :

```csv
system_id,protein_name,contrast_normalized,photostability_score,contrast_ph_stability,contrast_temp_stability,functional_score
FP_TEST2,HighButFragile,85.0,0.25,0.35,0.40,0.750
```

**Observation** : Scoring équilibré pénalise fragilité malgré contraste élevé.

---

## Validation Baseline

**Question** : functional_score avec stress-test apporte-t-il plus que tri contraste simple ?

**Test** :
1. Scorer 180 systèmes avec score base (sans stress-test)
2. Scorer 180 systèmes avec score enrichi (avec stress-test, hypothétique)
3. Comparer overlap top 20

**Critère succès** :
- Si overlap 18-20/20 → Score enrichi redondant
- Si overlap 12-16/20 → Score enrichi capture robustesse (bon)
- Si overlap < 10/20 → Vérifier incohérences, possibles outliers

**Validation finale** : Consulter expert domaine ou littérature.

---

## Conclusion

**Spec v8.3** : Colonnes stress-test définies, logique conditionnelle implémentée.

**État actuel** : ✅ Code prêt, 🟡 Données à collecter.

**Prochaine étape** : Minage littérature (v8.4) ou utilisation score base uniquement (valide aussi).

**Sans données inventées. Juste des specs claires.** ✅


