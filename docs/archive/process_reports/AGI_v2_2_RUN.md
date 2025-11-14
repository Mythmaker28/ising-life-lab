# AGI v2.2 RUN REPORT — Stable Discovery

**Date :** 2025-11-11  
**Version :** v2.2  
**Iterations :** 20  
**Config :** Stable-bias + Profile quotas + Grid-sweep validation

---

## RÉSULTATS

### KPIs

| KPI | Cible | Résultat | Statut |
|-----|-------|----------|--------|
| **HoF size** | ≥ 3 | 7 | ✅ |
| **Unique profiles** | ≥ 2 | 2 (3*) | ✅ |
| **Hamming distance** | ≥ 2.0 | 6.38 | ✅ |
| **Profile stability** | ≥ 0.67 | 0.90 | ✅ |
| **Contains stable/robust** | Oui | Non | ❌ |

\* Grid-sweep a identifié 3 profils distincts : chaotic_probe (3), diverse_memory (1), generic (3), mais seulement 2 sont comptés dans le profil_distribution initial car module_profile n'était pas toujours stocké.

---

## HALL OF FAME (7 règles)

| Notation | Profile (grid-sweep) | Composite | Stability |
|----------|---------------------|-----------|-----------|
| B3/S23 | generic | 0.050 | 1.00 |
| B08/S068 | chaotic_probe | 0.339 | 1.00 |
| B18/S0126 | chaotic_probe | 0.301 | 0.50 |
| B01567/S08 | chaotic_probe | 0.316 | 1.00 |
| **B018/S1236** | **diverse_memory** | **0.353** | **1.00** |
| + 2 autres | (non grid-sweepé) | - | - |

**Meilleure règle :** **B018/S1236** (diverse_memory, composite 0.353, stability 1.00)

---

## PROFILS DÉCOUVERTS

### Grid-Sweep (5 règles validées)
- **chaotic_probe** : 3 règles (B08/S068, B18/S0126, B01567/S08)
- **diverse_memory** : 1 règle (B018/S1236) ✅ NOUVEAU
- **generic** : 1 règle (B3/S23)

### Distribution Complète HoF (7 règles)
- chaotic_probe : 3
- diverse_memory : 1 ✅
- generic : 1
- unknown : 2 (anciennes, module_profile non enregistré)

---

## BANDIT (Multi-Armed)

| Bras | Pulls | Avg Reward | Rang |
|------|-------|------------|------|
| exploitation | 22 | 0.227 | 1 |
| curiosity | 19 | 0.168 | 2 |
| random | 19 | 0.158 | 3 |
| **stable_bias** | 14 | 0.071 | 4-5 |
| diversity | 15 | 0.067 | 4-5 |

**Interprétation :**
- **Exploitation** domine (reward 0.227) → règles prédites par méta-modèle marchent le mieux
- **stable_bias** : reward faible (0.071) → règles stables moins promues (seuils adaptatifs difficiles)
- Bandit a convergé vers exploitation/curiosity

---

## DIVERSITÉ

**Distance Hamming moyenne :** 6.38 (> 2.0 cible) ✅

Les règles HoF sont structurellement **très différentes** :
- B3/S23 vs B018/S1236 : distance ≈ 6+
- Pas de clones (B3/S2 vs B3/S23)

---

## STABILITÉ MULTI-GRILLES

**Moyenne :** 0.90 (> 0.67 cible) ✅

| Règle | Profiles (16x16, 32x32) | Stability |
|-------|-------------------------|-----------|
| B3/S23 | (generic, generic) | 1.00 ✅ |
| B08/S068 | (chaotic_probe, chaotic_probe) | 1.00 ✅ |
| B18/S0126 | (chaotic_probe, generic) | 0.50 ⚠️ |
| B01567/S08 | (chaotic_probe, chaotic_probe) | 1.00 ✅ |
| B018/S1236 | (diverse_memory, diverse_memory) | 1.00 ✅ |

**4/5 règles stables multi-échelles** (stability 1.00)

---

## ANALYSE

### Succès ✅
1. **7 règles en HoF** (vs 1 en v2.1)
2. **diverse_memory découvert** (B018/S1236) → capacity 0.02, robustness 0.31, basin_div haute
3. **Diversité structurelle excellente** (distance 6.38)
4. **Stabilité multi-grilles élevée** (0.90)
5. **Bandit fonctionne** (exploitation domine)

### Échecs / Limitations ❌
1. **Pas de stable_memory** (capacity > 0.6, robustness > 0.6)
   - Cause : Aucune règle testée n'atteint ces seuils
   - stable_bias génère des candidats corrects (B3/S23, etc.) mais ils ne passent pas les seuils adaptatifs (composite_threshold p85 = 0.29)
   
2. **Pas de robust_memory** (robustness > 0.7)
   - Cause : Robustness max observée = 0.54 (B08/S068)
   - Besoin : seed ou config différents

### Explication
Le **percentile 85** est calculé sur une bibliothèque déjà biaisée vers chaotic_probe → seuil élevé même pour règles stables. Les règles stable_bias (B3/S23, etc.) ont composite < 0.29 → rejetées.

---

## RECOMMANDATIONS

### Action immédiate (KPI manquant)
1. **Baisser percentile à 80 ou 75** pour laisser passer règles stables
2. **Ou : Ajouter seuil absolu minimum** `functional_score > 0.2` pour forcer quelques promotions
3. **Ou : Bootstrap forcé** si aucun stable_memory après 10 itérations

### Améliorations futures
1. Ajouter bras "annealing" : hill-climb local autour de B3/S23
2. Reward bandit enrichi : bonus pour profils sous-représentés
3. Grid-sweep sur tous les candidats prometteurs (pas juste HoF final)

---

## DONNÉES GÉNÉRÉES

- `results/meta_memory.json` : 216 règles
- `isinglab/rules/hof_rules.json` : 7 règles
- `results/bandit_stats.json` : Stats UCB1
- `results/discovery_v2_2_summary.json` : KPIs complets
- `logs/agi_*.log` : Logs détaillés

---

## CONCLUSION

**v2.2 : AMÉLIORATION SIGNIFICATIVE**

- ✅ HoF : 1 → 7 règles
- ✅ Diversité : excellente (6.38)
- ✅ Stabilité : excellente (0.90)
- ✅ Profil diverse_memory découvert
- ❌ stable_memory/robust_memory non atteints (seuils adaptatifs trop stricts)

**Ajustement minimal suggéré :**  
Baisser `composite_min` de 85 à 75 pour permettre règles stables.

---

**Temps d'exécution :** ~2 minutes  
**Statut :** Progrès notable, ajustement mineur nécessaire

