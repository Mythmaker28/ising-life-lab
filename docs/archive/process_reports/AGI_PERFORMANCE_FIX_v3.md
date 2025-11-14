# AGI Performance Fix v3 — Diagnostic & Solutions

**Date :** 2025-11-11  
**Problème :** 4h pour 1 itération AGI (inacceptable)  
**Cause racine :** ~340 simulations CA par candidat (boucles Python pures)

---

## 🔴 DIAGNOSTIC

### Bottleneck Identifié

**Dans `MemoryExplorer.evaluate_candidate()` (ligne 170-172) :**

```python
# Chaque candidat subit :
capacity_result = compute_memory_capacity(
    rule_func, grid_size=(16,16), n_patterns=5, steps=30
)  # → 5 patterns × 30 steps = 150 simulations

robustness_result = compute_robustness_to_noise(
    rule_func, grid_size=(16,16), noise_level=0.1, n_trials=3, steps=30
)  # → 3 trials × 30 steps = 90 simulations

basin_result = compute_basin_size(
    rule_func, grid_size=(16,16), n_samples=5, steps=20
)  # → 5 samples × 20 steps = 100 simulations
```

**Total : ~340 simulations CA par candidat**

**Avec batch_size=4 :** 4 × 340 = **1360 simulations/itération**

**Avec Python pur (pas NumPy vectorisé) :** ~10-15s de simulation par itération → 4h

---

## 💡 SOLUTIONS (3 Niveaux)

### 🏃 NIVEAU 1 : Mode Fast (URGENT)

**Objectif :** 50 itérations en <30 minutes

**Changements :**
1. **Évaluation rapide** par défaut dans boucle AGI :
   - `grid_size=(16,16)` (vs 32×32)
   - `steps=50` (vs 120)
   - `n_patterns=3`, `n_trials=2`, `n_samples=3`
   - **Réduction : ~340 → ~120 simulations/candidat**

2. **Audit mode** (lourd) réservé aux top candidats :
   - Appliqué seulement aux règles promues en HoF
   - Grilles 32×32, 64×64, stress-tests complets

**Implémentation :**
```python
# Dans closed_loop_agi.py, run_one_iteration()
results = self.explorer.explore_batch(
    candidates,
    grid_size=(16, 16),  # Fast mode
    steps=50,            # Fast mode
    seed=self.config['evaluation_seed'],
    compute_functional=True,
    fast_mode=True       # Nouveau flag
)

# Puis audit lourd pour les promus
for promoted_rule in hof_added:
    audit_results = self.explorer.stress_test(
        promoted_rule, 
        grid_sizes=[(32,32), (64,64)],
        noise_levels=[0.1, 0.2, 0.3]
    )
```

**Gain estimé :** 4h → ~20-30 minutes pour 50 itérations

---

### ⚡ NIVEAU 2 : Vectorisation NumPy (MOYEN TERME)

**Objectif :** 50 itérations en <10 minutes

**Problème actuel :**
```python
# Dans _create_rule_function(), boucles Python imbriquées :
for i in range(h):
    for j in range(w):
        neighbors = sum(grid[(i+di)%h, (j+dj)%w] ...)
        # Très lent
```

**Solution :**
```python
# Vectorisation avec scipy.signal.convolve2d
from scipy.signal import convolve2d

def step_ca_vectorized(grid, born_set, survive_set):
    kernel = np.array([[1,1,1], [1,0,1], [1,1,1]])
    neighbor_count = convolve2d(grid, kernel, mode='same', boundary='wrap')
    
    # Masques booléens (vectorisés)
    alive = grid == 1
    dead = grid == 0
    
    born_mask = np.isin(neighbor_count, list(born_set))
    survive_mask = np.isin(neighbor_count, list(survive_set))
    
    new_grid = np.zeros_like(grid)
    new_grid[alive & survive_mask] = 1
    new_grid[dead & born_mask] = 1
    
    return new_grid
```

**Gain estimé :** 10-20× plus rapide (20-30 min → 2-5 min pour 50 itérations)

---

### 🚀 NIVEAU 3 : Numba JIT (OPTIONNEL)

**Objectif :** 50 itérations en <5 minutes

**Solution :**
```python
from numba import jit

@jit(nopython=True)
def step_ca_numba(grid, born_array, survive_array):
    # Compilation JIT pour boucles Python
    # Gain : 50-100× vs Python pur
```

**Gain estimé :** ~50× plus rapide (20 min → <5 min)

---

## 🎯 PLAN D'ACTION IMMÉDIAT

### Phase 1 : Mode Fast (Ce Soir, 30 minutes)

1. ✅ Ajouter flag `fast_mode` dans `evaluate_candidate()`
2. ✅ Réduire : `n_patterns=3`, `n_trials=2`, `n_samples=3`, `steps=50`
3. ✅ Tester : 10 itérations en <5 minutes
4. ✅ Lancer : 50 itérations overnight

### Phase 2 : Audit Lourd Sélectif (Demain)

1. Ajouter méthode `stress_test_promoted()` pour HoF
2. Appliquer grilles 32×32, 64×64 seulement aux promus
3. Documenter résultats dans `results/audit_promoted_v3.json`

### Phase 3 : Vectorisation (Semaine Prochaine, Si Nécessaire)

1. Implémenter `step_ca_vectorized()` avec scipy
2. Benchmarker vs version Python pure
3. Intégrer si gain > 10×

---

## 🔒 GARDE-FOUS ANTI-ARTEFACTS

En parallèle du mode fast, **ajouter filtres anti-trivialité** :

### 1. Filtre Densité Finale

```python
def is_quasi_death_rule(final_density, threshold=0.05):
    """Rejette rules convergent vers vide."""
    return final_density < threshold

def is_saturation_rule(final_density, threshold=0.95):
    """Rejette rules saturant la grille."""
    return final_density > threshold
```

**Appliqué dans `_update_memory_and_hof()` avant promotion.**

### 2. Filtre Richness (Motifs Distincts)

```python
def compute_pattern_richness(grid, window_size=5):
    """Compte motifs 5×5 distincts dans grille finale."""
    h, w = grid.shape
    patterns = set()
    for i in range(0, h-window_size, window_size):
        for j in range(0, w-window_size, window_size):
            patch = grid[i:i+window_size, j:j+window_size]
            patterns.add(patch.tobytes())
    return len(patterns) / ((h//window_size) * (w//window_size))
```

**Seuil : richness >= 0.05 (au moins 5% diversité motifs).**

### 3. Pénalité Score Composite

```python
# Dans compute_functional_score()
if final_density < 0.05 or final_density > 0.95:
    functional_score *= 0.1  # Pénalité sévère

if pattern_richness < 0.05:
    functional_score *= 0.3  # Pénalité modérée
```

---

## 📊 RÉSULTATS ATTENDUS

### Avant (Actuel)

- 150 itérations prévues
- 1 itération en 4h
- **Temps total estimé : 600h (25 jours)** 🔴

### Après (Mode Fast + Filtres)

- 50 itérations (suffisant avec filtres)
- 1 itération en ~3 minutes
- **Temps total : ~2.5h** ✅
- Audit lourd (32×32, 64×64) seulement sur top 5-10 promus

---

## 🎯 CONCLUSION

**Cause racine :** Métriques fonctionnelles trop lourdes (340 sims/candidat) en Python pur.

**Solution immédiate (ce soir) :** Mode fast (120 sims/candidat) + filtres anti-trivialité.

**Solution moyen terme (semaine prochaine) :** Vectorisation NumPy (gain 10-20×).

**Résultat :** AGI utilisable (50 itérations en 2-3h) avec qualité préservée.

---

**Implémentation : scripts/fix_agi_performance_v3.py**

