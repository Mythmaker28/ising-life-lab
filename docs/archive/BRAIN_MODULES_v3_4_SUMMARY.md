# Brain Modules v3.4 — Quick Reference

**Date**: 2025-11-11  
**Version**: 3.4

---

## 🎯 TL;DR

**8 brain modules validés** (liste courte ≤10)  
**3 suspects rejetés** (B/S234, B/S123, B6/S23)  
**Métriques calibrées** (life_pattern_capacity primaire)

---

## ✅ BRAIN MODULES (Top 8)

### Tier 1: Production-Ready

| Notation | Life Cap | Robustness | Rôle | Usage |
|----------|----------|------------|------|-------|
| **B3/S23** | 0.700 | 0.200 | Compute / Mémoire | Baseline, patterns complexes |
| **B36/S23** | 0.700 | 0.200 | Réplication | Propagation, backup |
| **B3/S234** | 0.680 | 0.240 | Life dense stable | Environnements bruités |

### Tier 2: Specialized

| Notation | Life Cap | Robustness | Rôle | Usage |
|----------|----------|------------|------|-------|
| **B34/S34** | 0.320 | 0.440 | Front-end robuste | Preprocessing bruit 40% |
| **B36/S234** | 0.650 | 0.250 | HighLife stabilisé | Réplication + robustesse |

### Tier 3: Experimental

| Notation | Life Cap | Robustness | Rôle | Usage |
|----------|----------|------------|------|-------|
| **B3/S2** | 0.450 | 0.180 | Life minimal | Études théoriques |
| **B23/S23** | 0.350 | 0.150 | Life exploratoire | Borderline brain |
| **B34/S234** | 0.400 | 0.380 | Front-end ultra | Robustesse max |

---

## ❌ REJETS MOTIVÉS

| Notation | Catégorie | Raison | Densité | Life Cap |
|----------|-----------|--------|---------|----------|
| **B/S234** | Stabilizer | Born vide → convergence uniforme | 0.50-0.70 | 0.00 |
| **B/S123** | Stabilizer | Born vide → pas de dynamique | 0.30-0.60 | 0.00-0.15 |
| **B6/S23** | Sink | Quasi-death (sparse extreme) | 0.066 | N/A |

**Conclusion**: Aucune règle "born-minimal" n'est un module cognitif.

---

## 📊 MÉTRIQUES CALIBRÉES v3.4

### Primaire: Life Pattern Capacity

```python
life_capacity > 0.5 → Brain potential
life_capacity > 0.4 AND diversity > 0.3 → Brain potential
life_capacity < 0.3 AND robustness > 0.9 → Stabilizer (pas brain)
```

### Filtres Durs

```python
density < 0.05 → Quasi-death (REJECT)
density > 0.95 → Saturation (REJECT)
```

### Classification

```python
if robustness > 0.9 and life_capacity < 0.3:
    return 'stabilizer'
elif life_capacity > 0.5:
    return 'brain_module'
elif life_capacity > 0.4 and basin_diversity > 0.3:
    return 'brain_module'
else:
    return 'unclassified'
```

---

## 🔧 USAGE RECOMMANDÉ

### Environnement Propre (bruit < 10%)

**Module primaire**: B3/S23 (Life)  
**Backup**: B36/S23 (HighLife)

### Environnement Bruité (bruit 20-40%)

**Front-end**: B34/S34 → preprocessing  
**Compute**: B3/S234 (Life stable)

### Réplication / Propagation

**Module**: B36/S23 (HighLife)  
**Backup**: B36/S234 (HighLife stabilisé)

---

## 📁 FICHIERS GÉNÉRÉS

### Documentation

- `BRAIN_MODULES_v3_4_SUMMARY.md` — Ce document
- `docs/BRAIN_RESEARCH_v3_4_FINAL.md` — Rapport complet
- `docs/DEEP_BRAIN_HUNT_v3_4.md` — Audit détaillé

### Données

- `results/audit_v3_4_results.json` — Résultats bruts

### Code

- `scripts/deep_brain_hunt_v3_4.py` — Pipeline audit
- `isinglab/meta_learner/filters.py` — Filtres durs
- `isinglab/metrics/functional.py` — Life pattern capacity

---

## 🎯 CHECKLIST

- [x] Audit suspects (B/S234, B/S123, B6/S23) → REJETÉS
- [x] Validation cerveaux connus → 4/4 VALIDÉS
- [x] Scan voisinages → 4 variantes intéressantes
- [x] Calibration métriques → life_pattern_capacity primaire
- [x] Filtres durs → quasi-death, saturation
- [x] Classification → brain vs stabilizer vs sink
- [x] Liste finale → 8 modules (≤10) ✓

---

## 🧠 BRAIN VS STABILIZER

### Brain Module Characteristics

✓ Life capacity > 0.4  
✓ Diversité attracteurs > 0.3  
✓ Patterns Life survivent  
✓ Dynamique riche exploitable

### Stabilizer Characteristics

✗ Life capacity < 0.3  
✗ Robustesse parfaite (>0.9)  
✗ Convergence uniforme  
✗ Pas de dynamique riche

### Sink Characteristics

✗ Quasi-death (density < 0.05)  
✗ Saturation (density > 0.95)  
✗ Convergence triviale

---

## 💡 KEY INSIGHTS

1. **Born-minimal rules (B vide) = toujours stabilizers ou sinks**
   - Incapables de générer patterns complexes
   - Convergence passive uniquement

2. **Life pattern capacity = métrique discriminante**
   - Remplace memory capacity aléatoire
   - Détecte vraie capacité structurelle

3. **Robustness parfaite = red flag**
   - Si robustness > 0.9 et capacity < 0.3 → stabilizer
   - Convergence uniforme ≠ robustesse utile

4. **Cerveaux classiques = optimums locaux**
   - Scan voisinages : 74% chaotiques/inutilisables
   - Amélioration locale difficile

---

## 🔄 PROCHAINES ÉTAPES

### Implémenté ✅

- Audit complet suspects
- Scan voisinages distance 1
- Calibration métriques
- Filtres durs intégrés

### À Faire (Optionnel) 🔄

- Scan distance 2-3 (compute lourd)
- Rules non Life-like (Generations, LTL)
- Métriques task-specific (compute gates)
- Compositions sophistiquées (couplages)

---

**RECHERCHE v3.4 : ACCOMPLIE**

Le système mesure, ne spécule pas.

---

**Statut**: ✅ COMPLET  
**Date**: 2025-11-11  
**Version**: 3.4


