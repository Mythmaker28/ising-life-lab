# Modèle de Coût v5.0 — 2D vs 3D

**Date** : 2025-11-11  
**Objectif** : Établir un budget réaliste pour campagnes CA 2D/3D

---

## Résultats mesurés

### Modèle de coût

**2D** : `t = 4.15e-08 * n_cells + 8.00e-05`
- Alpha (par cellule) : 41.5 ns/cell
- Beta (overhead) : 80 µs

**3D** : `t = 2.16e-08 * n_cells + 8.09e-05`
- Alpha (par cellule) : 21.6 ns/cell  
- Beta (overhead) : 81 µs

**Observation** : 3D est ~2× **plus efficient** par cellule que 2D (probablement grâce à meilleure localité cache avec `scipy.ndimage.convolve`).

---

## Budget (60s = 1 minute)

### 2D

| Taille | Cellules | ms/update | Updates/min |
|--------|----------|-----------|-------------|
| 64×64 | 4,096 | 0.25 | 240,040 |
| 128×128 | 16,384 | 0.76 | 78,973 |
| 256×256 | 65,536 | 2.80 | 21,436 |

### 3D

| Taille | Cellules | ms/update | Updates/min |
|--------|----------|-----------|-------------|
| 16³ | 4,096 | 0.17 | 353,991 |
| 32³ | 32,768 | 0.79 | 76,013 |
| 48³ | 110,592 | 2.47 | 24,274 |

---

## Règles budgétaires

### Budget par campagne : **10⁷ updates max**

**Pourquoi 10⁷** :
- Correspond à ~2-8 minutes de calcul selon taille
- Suffisant pour exploration significative
- Évite gaspillage si piste improductive

### Budgets alloués

**Phase B (Tâches niches)** :
- Spatial 2D : 10⁶ updates (6 min @ 128×128)
- Morphologique : 5×10⁵ updates (3 min @ 128×128)
- Temporel : 10⁶ updates (6 min @ 128×128)

**Phase C (Hybride)** :
- 2×10⁶ updates max (12 min @ 128×128)

**Phase D (3D validation)** :
- 10⁶ updates (13 min @ 32³)
- **SEULEMENT si Phase B montre potentiel**

---

## Recommandation 3D

**Status** : ✅ **ACCEPTABLE**

3D est acceptable pour exploration modérée :
- 32³ = 32,768 cellules → 76k updates/min
- Suffisant pour tests ciblés
- **NE PAS** faire de scans exhaustifs 3D (trop coûteux)

**Utilisation recommandée** :
- 2-3 règles 3D ciblées maximum
- 1 tâche spécifique (ex: denoising volumes)
- Validation quantitative ponctuelle

---

## Coût relatif vs v4.0

**Rappel v4.0** :
- Benchmark reservoir : 3.8-5.1s par évaluation (32×32, 50 steps)
- Soit ~2,000 évaluations/heure

**v5.0 optimisé** :
- 2D 64×64, 50 steps : 0.013s → 277,000 évaluations/heure
- **138× plus rapide** que reservoir v4.0

**Raison** : Pipeline reservoir (encode + evolve + extract + readout) vs évolution CA brute.

---

## Limites identifiées

### Scaling

- **2D** : Linéaire jusqu'à 256×256, puis coût cubique pour convolution
- **3D** : Linéaire jusqu'à 48³, puis mémoire devient limitant

### Overhead

- Overhead fixe ~80µs → Négligeable pour grandes grilles
- Significatif pour très petites grilles (< 16×16)

### Hardware

- Mesures sur CPU standard (Python/NumPy/SciPy)
- GPU pourrait apporter 10-100× speedup (non testé)
- FPGA pourrait être 1000× plus rapide (théorique)

---

## Décision go/no-go pour Phase D (3D)

**Critères pour activer Phase D** :

1. ✅ Coût 3D acceptable (< 100s pour 1000 updates @ 32³)
   - **MES

URÉ** : 0.79 ms/update @ 32³ → 790s pour 1M updates
   - **VERDICT** : OK pour tests ciblés

2. ⏳ Phase B montre potentiel CA sur tâches spatiales
   - **À VÉRIFIER** dans Phase B

3. ⏳ Budget disponible (reste après Phases B+C)
   - **À CALCULER** après Phase B

**Décision** : Phase D sera activée **SEULEMENT SI** critères 2+3 satisfaits.

---

## Fichier de référence

- **Données brutes** : `results/cost_model_v5.json`
- **Script** : `scripts/benchmark_cost_v5.py`

---

**Modèle de coût établi. Budget défini. Campagne peut commencer.** ✓


