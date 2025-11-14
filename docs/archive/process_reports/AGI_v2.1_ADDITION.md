# ISING META-INTELLIGENCE v2.1 — MODULES MÉMOIRE EXPLOITABLES

**Date :** 2025-11-11  
**Version :** v2.1  
**Évolution depuis :** v2.0 → v2.1

---

## RÉSUMÉ v2.1

La version 2.1 **redéfinit "intéressant"** : au lieu de top percentile d'un score interne, on sélectionne des **modules mémoire réellement exploitables** via :

1. **Métriques fonctionnelles task-based** : capacity, robustness, basin tests
2. **Sélection Pareto multi-objectif** : HoF = ensemble de stratégies non-dominées
3. **Profils explicites** : stable_memory, robust_memory, chaotic_probe, etc.
4. **Export enrichi** : module_id, profile, suggested_use pour orchestrateurs externes

---

## PROBLÈME v2.0

**v2.0 fonctionnait** (seuils adaptatifs, diversité, bandit) mais :
- Promotions rares (~0-2 par run)
- Critère "intéressant" = top composite d'un score vague
- Pas de garantie d'**utilité fonctionnelle**

**Constat :** Les règles promues ne sont pas nécessairement **exploitables** comme modules mémoire.

---

## SOLUTION v2.1 : MÉTRIQUES FONCTIONNELLES

### 1. Capacity Test

**Question :** Combien de patterns distincts peuvent être stockés/rappelés ?

**Méthode :**
- Générer N patterns aléatoires
- Pour chaque pattern : initialiser, évoluer M steps, vérifier stabilité
- `capacity_score` = fraction de patterns stabilisés en états distincts

**Code :** `isinglab/metrics/functional.py :: test_memory_capacity()`

```python
capacity_result = test_memory_capacity(
    rule_function,
    grid_size=(16, 16),
    n_patterns=5,
    steps=30
)
# → {'capacity_score': 0.6, 'stable_patterns': 3, 'distinct_finals': 3}
```

**Utilité :** Mesure directe de la capacité mémoire (pas juste esthétique).

---

### 2. Robustness Test

**Question :** Le système résiste-t-il au bruit initial ?

**Méthode :**
- Pattern de référence (ex: damier)
- Ajouter X% de bruit (flips aléatoires)
- Mesurer si le système se stabilise malgré le bruit
- `robustness_score` = stabilité moyenne après bruit

**Code :** `isinglab/metrics/functional.py :: test_robustness_to_noise()`

```python
robustness_result = test_robustness_to_noise(
    rule_function,
    grid_size=(16, 16),
    noise_level=0.1,
    n_trials=3,
    steps=30
)
# → {'robustness_score': 0.75, 'noise_level': 0.1}
```

**Utilité :** Identifie règles utilisables en contexte bruité.

---

### 3. Basin Test

**Question :** Taille des bassins d'attraction (équilibre nécessaire) ?

**Mé thode :**
- N patterns aléatoires
- Pour chaque : évoluer jusqu'à convergence
- Compter attracteurs uniques
- `basin_diversity` = attracteurs_uniques / N
- `basin_score` optimal autour de 0.3-0.7 (ni trop écrasant, ni trop fragmenté)

**Code :** `isinglab/metrics/functional.py :: test_basin_size()`

```python
basin_result = test_basin_size(
    rule_function,
    grid_size=(16, 16),
    n_samples=5,
    steps=20
)
# → {'basin_score': 0.6, 'basin_diversity': 0.6, 'unique_attractors': 3}
```

**Utilité :** Évite règles trop fragiles ou trop écrasantes.

---

### 4. Functional Score Agrégé

**Formule :**
```python
functional_score = (capacity * 0.4) + (robustness * 0.35) + (basin * 0.25)
```

**Pondération :**
- Capacity : 40% (le plus important pour mémoire)
- Robustness : 35% (robustesse critique)
- Basin : 25% (équilibre)

**Utilité :** Score unique task-based au lieu de métrique esthétique.

---

## SOLUTION v2.1 : SÉLECTION PARETO

### Pourquoi Pareto ?

**v2.0 :** HoF = top N d'un score composite unique → règles similaires, pas de diversité réelle.

**v2.1 :** HoF = **ensemble Pareto** sur plusieurs objectifs → règles complémentaires.

### Multi-objectifs

```python
objectives = [
    'functional_score',  # v2.1
    'memory_score',      # v2.0
    'edge_score',        # v2.0
    'entropy'            # v2.0
]
```

Une règle est **non-dominée** si aucune autre règle n'est meilleure sur **tous** les objectifs.

### Algorithme

```python
from isinglab.meta_learner.pareto import select_pareto_hof

promoted, removed = select_pareto_hof(
    candidates=evaluated_rules,
    current_hof=load_hof_rules(),
    objectives=['functional_score', 'memory_score', 'edge_score', 'entropy'],
    max_size=20,
    diversity_threshold=2.0
)

# promoted : règles ajoutées au HoF
# removed : règles retirées (dominées)
```

**Fichier :** `isinglab/meta_learner/pareto.py`

---

## SOLUTION v2.1 : PROFILS EXPLICITES

### 7 Profils Identifiés

1. **stable_memory**
   - `capacity > 0.6` ET `robustness > 0.6`
   - Usage : "Stockage d'états discrets robuste, idéal pour mémoire à long terme"

2. **robust_memory**
   - `robustness > 0.7` ET `capacity > 0.3`
   - Usage : "Mémoire résistante au bruit, bon pour contextes bruités"

3. **diverse_memory**
   - `capacity > 0.5` ET `basin_diversity > 0.5`
   - Usage : "Capacité de stockage avec bassins variés, bon pour patterns multiples"

4. **chaotic_probe**
   - `entropy > 0.7` ET `capacity < 0.3`
   - Usage : "Dynamiques complexes, exploration ou génération de hashing"

5. **sensitive_detector**
   - `robustness < 0.3` ET `entropy > 0.5`
   - Usage : "Sensible aux perturbations, capteur ou amplificateur de signaux"

6. **attractor_dominant**
   - `basin_diversity < 0.2` ET `robustness > 0.5`
   - Usage : "Convergence forte vers attracteurs, bon pour classification"

7. **generic**
   - Autres cas
   - Usage : "Usage général, profil mixte"

**Fonction :** `isinglab/metrics/functional.py :: infer_module_profile()`

---

## FORMAT EXPORT v2.1

```json
{
  "meta": {
    "version": "v2.1",
    "description": "Modules mémoire exploitables avec profils fonctionnels"
  },
  "hall_of_fame": [
    {
      "module_id": "mem_B18_S126",
      "notation": "B18/S126",
      "born": [1, 8],
      "survive": [1, 2, 6],
      "tier": "pareto_candidate",
      "diversity_signature": "B2_18/S3_126",
      "module_profile": "robust_memory",
      "suggested_use": "Mémoire résistante au bruit, bon pour contextes bruités",
      "scores": {
        "functional_score": 0.625,
        "capacity_score": 0.6,
        "robustness_score": 0.8,
        "basin_score": 0.5,
        "memory_score": 0.035,
        "edge_score": 0.339,
        "entropy": 0.947
      },
      "metadata": {
        "discovered_by": "closed_loop_agi_v2.1",
        "tags": ["agi", "pareto", "robust"],
        "origin": "ising-life-lab"
      }
    }
  ]
}
```

**Champs clés v2.1 :**
- `module_id` : identifiant unique pour orchestrateurs
- `module_profile` : profil fonctionnel (7 types)
- `suggested_use` : description concrète de l'utilité
- `functional_score` : score task-based agrégé

---

## USAGE PAR ORCHESTRATEUR EXTERNE

```python
import json

# Charger l'export
with open('results/agi_export_hof.json') as f:
    data = json.load(f)

# Filtrer par profil
stable_modules = [
    m for m in data['hall_of_fame']
    if m['module_profile'] == 'stable_memory'
]

robust_modules = [
    m for m in data['hall_of_fame']
    if m['module_profile'] == 'robust_memory'
]

# Choisir selon besoin
if context == 'noisy':
    module = robust_modules[0]
elif context == 'clean':
    module = stable_modules[0]

print(f"Module sélectionné : {module['notation']}")
print(f"Usage : {module['suggested_use']}")
print(f"Functional score : {module['scores']['functional_score']:.3f}")
```

---

## TESTS v2.1

**Fichier :** `tests/test_agi_v2_functional.py` (13 tests)

```bash
pytest tests/test_agi_v2_functional.py -v
```

**Tests :**
1. `test_memory_capacity_basic` : capacity test fonctionne
2. `test_robustness_basic` : robustness test fonctionne
3. `test_basin_size_basic` : basin test fonctionne
4. `test_compute_functional_score` : agrégation correcte
5. `test_infer_module_profile` : profils bien inférés
6. `test_dominates` : relation de dominance Pareto
7. `test_pareto_front` : calcul du front
8. `test_select_pareto_hof` : sélection avec diversité
9. `test_functional_score_in_range` : score dans [0,1]
10. `test_all_profiles_defined` : tous les profils existent
11-13. Tests intégration

---

## COMPARAISON v2.0 vs v2.1

| Aspect | v2.0 | v2.1 |
|--------|------|------|
| **Critère** | Top percentile composite | Fonctionnel + Pareto |
| **Métriques** | memory, edge, entropy | + capacity, robustness, basin |
| **HoF** | Top N adaptif | Ensemble Pareto non-dominé |
| **Profils** | Aucun | 7 profils explicites |
| **Export** | Scores basiques | + module_id, profile, suggested_use |
| **Utilité** | Incertaine | Garantie fonctionnelle |
| **Tests** | 18 (v1 + v2) | + 13 v2.1 = 31 total |

---

## LIMITATIONS v2.1

1. **Tests fonctionnels légers**
   - grid_size réduit (16x16) pour vitesse
   - Moins de patterns testés que nécessaire pour garantie absolue
   - **Amélioration future :** tests plus exhaustifs en mode offline

2. **Profils inférés heuristiquement**
   - Seuils fixés manuellement (ex: capacity > 0.6)
   - **Amélioration future :** clustering automatique des profils

3. **Pas de validation croisée**
   - Profil attribué sans vérification sur d'autres contextes
   - **Amélioration future :** valider profil sur plusieurs seeds

4. **Front de Pareto peut être vide**
   - Si aucune règle ne passe les bornes minimales
   - **Amélioration future :** fallback intelligent

---

## CRITÈRES DE SUCCÈS v2.1

**Après 20-50 itérations :**

✅ **HoF contient plusieurs règles** (3-10)  
✅ **Profils différents** (pas que stable_memory)  
✅ **Scores fonctionnels > 0.3** (utilité réelle)  
✅ **Export utilisable** (module_id, profile, suggested_use présents)  
✅ **Tests passent** (31 tests total)  

**Logs montrent :**
- Promotions Pareto expliquées (`[PARETO] N rules promoted`)
- Profils des règles promues (`(robust_memory)`, etc.)
- Pas de bullshit (functional_score vérifiable)

---

## COMMANDES v2.1

```bash
# Tests fonctionnels
pytest tests/test_agi_v2_functional.py -v

# Tous les tests
pytest tests/ -v  # 31 tests (6 v1 + 12 v2 + 13 v2.1)

# Export avec profils
python isinglab/export_memory_library.py

# Vérifier profils dans export
cat results/agi_export_hof.json | jq '.hall_of_fame[] | {notation, module_profile, suggested_use}'
```

---

## CONCLUSION v2.1

**"Intéressant" redéfini :**  
- ❌ Avant : top percentile d'un score composite vague
- ✅ Maintenant : modules mémoire avec capacité, robustesse, profil et usage explicites

**HoF redéfini :**  
- ❌ Avant : top N similaires
- ✅ Maintenant : ensemble Pareto de stratégies complémentaires

**Export redéfini :**  
- ❌ Avant : leaderboard flou
- ✅ Maintenant : bibliothèque de modules consommables

**Validation :**  
- ✅ 13 tests fonctionnels passent
- ⚠️ Exécution 20-50 itérations requise pour valider empiriquement
- ⚠️ Comparaison avec v2.0 : attendre HoF > 1 règle, profils variés

---

**FIN ADDITION v2.1 — CODE IMPLÉMENTÉ, TESTS CRÉÉS**

