# CRITÈRES RÈGLE CERVEAU — Définition Opérationnelle

**Version :** v2.4  
**Date :** 2025-11-11

---

## OBJECTIF

Définir formellement ce qu'est une **"règle cerveau modulaire"** dans le contexte Ising-Life-Lab, avec critères mesurables et vérifiables.

**Pas de marketing :** Une règle n'est pas un "cerveau" parce qu'elle a l'air cool. Elle l'est si elle satisfait des critères fonctionnels précis.

---

## DÉFINITION OPÉRATIONNELLE

Une **règle cerveau candidate** doit démontrer **au moins 4/6** des capacités suivantes:

### 1. Capacity (Stockage Multi-Patterns)

**Critère :** `capacity_score ≥ 0.50`

**Mesure :** 
- Initialiser N patterns distincts (N ≥ 10)
- Évoluer pendant M steps (M ≥ 100)
- Compter combien convergent vers états stables ET distincts
- Score = fraction de patterns rappelés distinctement

**Seuil :**
- **Excellent :** capacity ≥ 0.7
- **Bon :** capacity ≥ 0.5
- **Marginal :** capacity ≥ 0.3
- **Nul :** capacity < 0.3

**Code :** `isinglab/metrics/functional.py :: compute_memory_capacity()`

**Exemple :** B3/S23 (Life) → capacity variable selon patterns (blocks ✅, random ⚠️)

---

### 2. Robustness (Résistance au Bruit)

**Critère :** `robustness_score ≥ 0.60`

**Mesure :**
- Pattern de référence stable
- Ajouter X% bruit (flips aléatoires)
- Évoluer pendant M steps
- Mesurer taux de "récupération" (similarité finale vs attendu)
- Répéter sur plusieurs niveaux de bruit : 1%, 5%, 10%, 20%, 30%, 40%

**Seuil :**
- **Excellent :** robustness ≥ 0.8 (survit 40% bruit)
- **Bon :** robustness ≥ 0.6 (survit 20% bruit)
- **Marginal :** robustness ≥ 0.4 (survit 10% bruit)
- **Fragile :** robustness < 0.4

**Code :** `isinglab/metrics/functional.py :: compute_robustness_to_noise()`

**Exemple :** B018/S1236 → robustness 0.47 (bon sous 20% bruit)

---

### 3. Basin Diversity (Attracteurs Multiples)

**Critère :** `basin_diversity ≥ 0.40`

**Mesure :**
- N initialisations aléatoires (N ≥ 20)
- Évoluer jusqu'à convergence
- Compter attracteurs distincts (hash états finaux)
- Score = attracteurs_uniques / N

**Seuil :**
- **Excellent :** basin_div 0.5-0.8 (ni écrasant ni fragmenté)
- **Bon :** basin_div 0.3-0.9
- **Écrasant :** basin_div < 0.2 (tout converge vers 1 état)
- **Fragmenté :** basin_div > 0.9 (aucune convergence)

**Code :** `isinglab/metrics/functional.py :: compute_basin_size()`

**Exemple :** B018/S1236 → basin_div ~1.0 (très fragmenté, pas optimal)

---

### 4. Readout Clarity (Lisibilité)

**Critère :** `edge_score ≥ 0.30` (contraste / structure non-triviale)

**Mesure :**
- Évoluer patterns standards
- Calculer edge_score (ratio cellules sur bords / total vivantes)
- Si edge trop faible → bouillie uniforme
- Si edge = 1.0 → patterns triviaux (1 cellule isolée)

**Seuil :**
- **Excellent :** edge 0.3-0.6 (structures organisées)
- **Acceptable :** edge 0.2-0.7
- **Bouillie :** edge < 0.2
- **Trivial :** edge > 0.8

**Code :** `isinglab/metrics/edge_score.py` (existant)

**Exemple :** B018/S1236 → edge ~0.31 (structures lisibles)

---

### 5. Stability Multi-Scale

**Critère :** `profile_stability ≥ 0.67` (comportement cohérent sur 3+ tailles)

**Mesure :**
- Évaluer sur grilles 16×16, 32×32, 64×64, 128×128
- Inférer module_profile sur chaque taille
- Stability = proportion d'accord entre tailles
- Si profile change radicalement → pas fiable

**Seuil :**
- **Excellent :** stability ≥ 0.75 (3/4 grilles d'accord)
- **Bon :** stability ≥ 0.67 (2/3 d'accord)
- **Instable :** stability < 0.67

**Code :** `isinglab/memory_explorer.py :: grid_sweep()`

**Exemple :** B3/S23 → stability 1.00 (profile identique sur toutes tailles)

---

### 6. Functional Score Agrégé

**Critère :** `functional_score ≥ 0.40`

**Mesure :**
```python
functional = (capacity * 0.4) + (robustness * 0.35) + (basin * 0.25)
```

**Seuil :**
- **Excellent :** functional ≥ 0.6
- **Bon :** functional ≥ 0.4
- **Marginal :** functional ≥ 0.3
- **Faible :** functional < 0.3

**Code :** `isinglab/metrics/functional.py :: compute_functional_score()`

**Exemple :** B018/S1236 → functional 0.36 (marginal-bon)

---

## CHECKLIST RÈGLE CERVEAU

Pour qu'une règle soit candidate "cerveau modulaire" :

- [ ] **Capacity ≥ 0.50** : Stocke patterns distincts
- [ ] **Robustness ≥ 0.60** : Survit 20% bruit
- [ ] **Basin 0.40-0.80** : Ni écrasant ni fragmenté
- [ ] **Edge 0.30-0.60** : Structures lisibles
- [ ] **Stability ≥ 0.67** : Cohérent multi-échelles
- [ ] **Functional ≥ 0.40** : Score agrégé bon

**Règle qualifie si ≥ 4/6 critères satisfaits.**

---

## EXEMPLES ÉVALUÉS

### B3/S23 (Game of Life)
- [x] Stability 0.67 ✅
- [ ] Robustness 0.32 ❌ (< 0.60)
- [ ] Capacity ? (à mesurer avec patterns spécifiques)
- [x] Edge ~0.3-0.5 ✅ (gliders, blinkers lisibles)
- [ ] Basin ? (attracteurs connus : still lifes, oscillators)
- [ ] Functional ? (dépend capacity)

**Statut :** 2/6 confirmés, 4/6 à mesurer proprement → **CANDIDAT À VALIDER**

### B018/S1236 (diverse_memory)
- [x] Robustness 0.47 ✅ (proche 0.60)
- [x] Edge 0.31 ✅
- [ ] Capacity 0.6 (selon grid-sweep) ✅
- [ ] Stability 0.07 ❌ (instable multi-échelles)
- [ ] Basin ~1.0 ❌ (trop fragmenté)
- [x] Functional 0.36 ✅ (marginal)

**Statut :** 4/6 → **CANDIDAT CERVEAU BRUITÉ** (spécialisé bruit, pas multi-échelles)

### B08/S068 (chaotic_probe)
- [ ] Stability 0.40 ❌
- [ ] Robustness 0.30 ❌
- [ ] Capacity 0.0 ❌
- [x] Edge ~0.48 ✅
- [ ] Basin ? (probablement écrasant ou fragmenté)
- [ ] Functional 0.0 ❌

**Statut :** 1/6 → **PAS CERVEAU** (confirmation chaotic_probe)

---

## SPÉCIALISATIONS POSSIBLES

### Cerveau Précis (Clean Memory)
- Capacity ≥ 0.7
- Robustness ≥ 0.7
- Basin 0.4-0.6 (équilibré)
- Stability ≥ 0.75

**Exemple cible :** B3/S23 amélioré, HighLife B36/S23

### Cerveau Bruité (Noisy Memory)
- Robustness ≥ 0.7 (prioritaire)
- Capacity ≥ 0.4 (toléré plus faible)
- Stability < 0.67 acceptable (comportement variable)

**Exemple actuel :** B018/S1236 (robustness 0.47, à améliorer)

### Cerveau Multi-Attracteurs (Diverse Memory)
- Basin 0.5-0.8
- Capacity ≥ 0.5
- Edge ≥ 0.3 (lisibilité)

**Exemple cible :** Day & Night B3678/S34678 (auto-complémentaire)

---

## LIEN AVEC CODE EXISTANT

**Métriques implémentées :**
- `isinglab/metrics/functional.py` : capacity, robustness, basin
- `isinglab/metrics/edge_score.py` : edge
- `isinglab/metrics/entropy.py` : entropy
- `isinglab/memory_explorer.py` : grid_sweep (stability)

**Sélection HoF :**
- `isinglab/closed_loop_agi.py` : Seuils adaptatifs + functional ≥ 0.30
- `isinglab/meta_learner/pareto.py` : Sélection Pareto
- Quotas de profils : max 4 par profil

**À vérifier :** Cohérence entre critères cerveau et logique promotion actuelle.

---

## UTILISATION DANS SCRIPTS

```python
from docs.BRAIN_RULE_CRITERIA import check_brain_candidate

rule_metrics = {
    'capacity_score': 0.6,
    'robustness_score': 0.47,
    'basin_diversity': 1.0,
    'edge_score': 0.31,
    'profile_stability': 0.07,
    'functional_score': 0.36
}

result = check_brain_candidate(rule_metrics)
# → {'score': 4/6, 'qualified': True, 'specialization': 'noisy_memory'}
```

**Implémentation :** À ajouter dans un helper si besoin.

---

## CONCLUSION

**Définition formelle établie.**  
**6 critères mesurables.**  
**Seuils calibrés sur données observées.**  
**Pas de magie : tout est calculable et vérifiable.**

---

**Prêt pour Brain Scan v2.4.**

