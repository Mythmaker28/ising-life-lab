# AGI v2.0 — GUIDE D'UTILISATION ET EXEMPLES

**Date :** 2025-11-11  
**Version :** v2.0

Ce guide explique comment utiliser le système AGI v2.0 et interpréter ses résultats.

---

## DÉMARRAGE RAPIDE

### 1. Lancer une découverte de 20 itérations

```bash
python run_agi_v2_discovery.py
```

**Durée estimée :** 5-15 minutes selon la machine.

**Ce que vous verrez :**
```
================================================================================
AGI v2.0 DISCOVERY - 20 ITERATIONS
(Adaptive Thresholds + Diversity + Multi-Armed Bandit)
================================================================================

================================================================================
>>> ITERATION 1/20
================================================================================

================================================================
CLOSED LOOP AGI v2.0 - ITERATION (ADAPTIVE)
================================================================

STEP 1: Aggregate memory
  Aggregated 24 rules

STEP 2: Train meta-model
  Train acc: 75.00%
  Test acc: 66.67%

STEP 3: Select candidates
  [BANDIT] Arm selected: exploitation
    - exploitation: pulls=1, avg_reward=0.000
    - curiosity: pulls=0, avg_reward=0.000
    - diversity: pulls=0, avg_reward=0.000
    - random: pulls=0, avg_reward=0.000
  8 candidates via strategy 'mixed'

STEP 4: Explore candidates
  8 / 8 evaluated successfully

STEP 5: Update memory & Hall of Fame
  [ADAPTIVE] Composite threshold (p85): 0.2341
  [PROMOTED] 2 rules to HoF
     - B18/S126 (composite=0.308, memory=0.035, edge=0.339)
     - B0235/S145 (composite=0.250, memory=0.000, edge=0.192)
  [DIVERSITY] 1 candidates rejected for similarity:
     - B18/S06: Too similar to B18/S126 (dist=1)

STEP 6: Update bandit
  [BANDIT] Reward=2.287 (promotions=2, avg_composite=0.287)

[...]

--- CHECKPOINT ITERATION 5 ---
  Total mémoire: 64
  Total HoF: 3
  Promotions totales: 3

[...]

================================================================================
RECAPITULATIF FINAL (20 ITERATIONS)
================================================================================

MÉMOIRE & HoF:
  - Mémoire finale: 184 règles
  - HoF final: 5 règles
  - Promotions (non-bootstrap): 4
  - Bootstrap: 1

DIVERSITÉ:
  - Signatures uniques: 5/5

BANDIT (Multi-Armed):
  Total pulls: 20
  - exploitation: pulls=8, avg_reward=0.425
  - curiosity: pulls=6, avg_reward=0.312
  - diversity: pulls=4, avg_reward=0.289
  - random: pulls=2, avg_reward=0.201

VÉRIFICATIONS:
  [OK] Mémoire croissante
  [OK] HoF non vide
  [OK] Au moins 1 promotion non-bootstrap
  [OK] Diversité > 50%

EXPORT:
  Exécutez: python isinglab/export_memory_library.py
  Fichier généré: results/agi_export_hof.json
  Récap sauvegardé: results/agi_v2_discovery_recap.json

================================================================================
SUCCESS: Tous les checks passent. AGI v2.0 opérationnel.
================================================================================
```

---

## INTERPRÉTATION DES RÉSULTATS

### 1. Seuils Adaptatifs

```
[ADAPTIVE] Composite threshold (p85): 0.2341
```

**Ce que ça signifie :**
- Le système a calculé le 85e percentile des scores composites = 0.2341
- Seules les règles avec `composite_score >= 0.2341` peuvent être promues au HoF
- Ce seuil évolue à chaque itération en fonction des règles découvertes

**Bon signe :**
- Le seuil augmente progressivement → le système trouve de meilleures règles
- Des promotions se produisent → les critères ne sont pas trop stricts

**Mauvais signe :**
- Seuil stagne à 0 → toutes les règles sont mauvaises
- Aucune promotion malgré un seuil bas → diversité trop stricte ou pas de bon candidat

---

### 2. Promotions et Diversité

```
[PROMOTED] 2 rules to HoF
   - B18/S126 (composite=0.308, memory=0.035, edge=0.339)
   - B0235/S145 (composite=0.250, memory=0.000, edge=0.192)

[DIVERSITY] 1 candidates rejected for similarity:
   - B18/S06: Too similar to B18/S126 (dist=1)
```

**Règles promues :**
- `B18/S126` : score composite = 0.308 (> seuil 0.2341) ✅
  - `memory=0.035` : capacité mémoire faible mais non nulle
  - `edge=0.339` : robuste au bruit
  - `entropy=0.947` (inféré) : très dynamique
  
- `B0235/S145` : score composite = 0.250
  - `memory=0.000` : aucune capacité mémoire détectée
  - `edge=0.192` : moyennement robuste
  - Promu car suffisamment différent de B18/S126

**Règles rejetées :**
- `B18/S06` : trop similaire à `B18/S126`
  - Distance de Hamming = 1 (seul le `6` dans survive diffère)
  - Seuil de diversité = 2 minimum
  - Rejeté même si bon score

**Interprétation :**
- Le HoF contient des stratégies **différentes** (diversité structurelle)
- Pas de clones : B18/S0, B18/S6, B18/S126 ne coexistent pas

---

### 3. Multi-Armed Bandit

```
BANDIT (Multi-Armed):
  Total pulls: 20
  - exploitation: pulls=8, avg_reward=0.425
  - curiosity: pulls=6, avg_reward=0.312
  - diversity: pulls=4, avg_reward=0.289
  - random: pulls=2, avg_reward=0.201
```

**Ce que ça signifie :**
- **Exploitation** (pulls=8) : stratégie la plus utilisée → bandit a appris qu'elle marchait le mieux
- **avg_reward=0.425** : en moyenne, exploitation donne 0.425 de récompense
  - Reward = promotions + avg_composite des candidats
  - Plus élevé = plus de promotions et/ou meilleurs candidats
  
- **Random** (pulls=2, reward=0.201) : moins utilisé car mauvais résultats

**Bon signe :**
- Un bras domine en pulls ET en avg_reward → convergence
- Random a peu de pulls → pas de gaspillage
- Exploitation/curiosity se partagent les pulls → équilibre exploration/exploitation

**Mauvais signe :**
- Tous les bras à pulls=5 → pas de convergence (UCB1 explore encore)
- Random a le meilleur reward → le méta-modèle est mauvais
- Aucun bras ne dépasse avg_reward=0.1 → mauvaise qualité générale

---

### 4. Export Enrichi

```bash
python isinglab/export_memory_library.py
```

**Fichier généré :** `results/agi_export_hof.json`

```json
{
  "meta": {
    "version": "v2.0",
    "origin": "ising-life-lab",
    "total_hof_rules": 5
  },
  "hall_of_fame": [
    {
      "notation": "B18/S126",
      "diversity_signature": "B2_18/S3_126",
      "scores": {
        "memory_score": 0.035,
        "edge_score": 0.339,
        "entropy": 0.947,
        "composite": 0.308
      },
      "metadata": {
        "tags": ["agi", "automated", "adaptive", "low_memory", "robust", "high_entropy", "dynamic"],
        "origin": "ising-life-lab",
        "promotion_reason": "adaptive (composite=0.308)"
      }
    }
  ]
}
```

**Tags enrichis automatiques :**
- `low_memory` / `moderate_memory` / `high_memory` : capacité mémoire
- `fragile` / `moderate_edge` / `robust` : robustesse au bruit
- `static` / `moderate_entropy` / `high_entropy` + `dynamic` : dynamisme

**Usage :**
```python
# Filtrer par profil
robust_rules = [r for r in hof if 'robust' in r['metadata']['tags']]
high_memory_rules = [r for r in hof if 'high_memory' in r['metadata']['tags']]

# Grouper par signature de diversité
by_structure = defaultdict(list)
for rule in memory_library:
    by_structure[rule['diversity_signature']].append(rule)
```

---

## DIAGNOSTIC DE PROBLÈMES

### Problème 1 : HoF reste à 1 règle après 20 itérations

**Causes possibles :**
1. **Seuil percentile trop élevé** : `composite_min: 95` → top 5% uniquement
   - Solution : baisser à 85 ou 80
   
2. **Diversity_threshold trop strict** : `diversity_threshold: 5`
   - Solution : baisser à 2 ou 3
   
3. **Règles explorées sont toutes mauvaises** : mémoire originale de mauvaise qualité
   - Solution : ajouter des règles seed connues (B3/S23, B36/S23, etc.)

**Diagnostic :**
```bash
# Vérifier les seuils dans les logs
grep "ADAPTIVE" logs/agi_*.log
# Si threshold < 0.1 après 10 itérations → mauvaise qualité générale

# Vérifier combien de candidats atteignent le seuil mais sont rejetés
grep "DIVERSITY" logs/agi_*.log
# Si beaucoup de rejets → diversité trop stricte
```

---

### Problème 2 : Bandit ne converge pas (tous les bras à ~5 pulls)

**Causes :**
1. **Pas assez d'itérations** : UCB1 explore d'abord, converge après 15-30 pulls
   - Solution : lancer 30-50 itérations
   
2. **Rewards trop similaires** : tous les bras donnent ~0.2 de reward
   - Solution : ajuster la formule de reward ou augmenter batch_size
   
3. **Méta-modèle mauvais** : accuracy < 60%
   - Solution : attendre que la mémoire grandisse (>100 règles)

---

### Problème 3 : Diversité = 0% (toutes les règles similaires)

**Causes :**
1. **Fallback neighbors** : si méta-modèle skip, génère des voisins d'une seule règle
   - Solution : attendre que méta-modèle s'entraîne (>5 règles en mémoire)
   
2. **Exploration trop focalisée** : bras "exploitation" domine à 100%
   - Solution : forcer 5 premières itérations avec bras "diversity"
   
3. **Distance threshold = 0** : n'importe quelle règle passe
   - Solution : mettre à 2 minimum

---

## CONFIGURATION RECOMMANDÉE PAR SCÉNARIO

### Scénario 1 : Recherche large et rapide
```python
config = {
    'adaptive_thresholds': True,
    'hof_percentiles': {'composite_min': 80},  # Top 20%
    'diversity_threshold': 2
}
# 30 itérations, batch_size=10
```

### Scénario 2 : HoF d'élite très sélectif
```python
config = {
    'adaptive_thresholds': True,
    'hof_percentiles': {'composite_min': 95},  # Top 5%
    'diversity_threshold': 3
}
# 50 itérations, batch_size=6
```

### Scénario 3 : Maximum de diversité
```python
config = {
    'adaptive_thresholds': True,
    'hof_percentiles': {'composite_min': 85},
    'diversity_threshold': 4  # Distance élevée
}
# Forcer bras 'diversity' au début
```

---

## COMMANDES UTILES

```bash
# Lancer la découverte
python run_agi_v2_discovery.py

# Tests v2
pytest tests/test_agi_v2.py -v

# Export enrichi
python isinglab/export_memory_library.py

# Vérifier le HoF
python -c "import json; print(json.load(open('isinglab/rules/hof_rules.json'))['rules'])"

# Stats bandit
cat results/bandit_stats.json | python -m json.tool

# Récap discovery
cat results/agi_v2_discovery_recap.json | python -m json.tool

# Logs complets
tail -n 100 logs/agi_*.log
```

---

## PROCHAINES ÉTAPES

Après une découverte réussie :

1. **Analyser les règles HoF** :
   ```python
   from isinglab.rules import load_hof_rules
   hof = load_hof_rules()
   for rule in hof:
       print(f"{rule['notation']}: composite={rule.get('composite_score', 0):.3f}")
   ```

2. **Visualiser les règles** (si interface web disponible) :
   - Charger la règle dans l'explorer
   - Observer les patterns émergeants

3. **Itérer sur la config** :
   - Si HoF trop petit → baisser percentile ou diversity_threshold
   - Si HoF trop de clones → augmenter diversity_threshold
   - Si bandit ne converge pas → augmenter nombre d'itérations

4. **Intégration Cross-Project** :
   - Utiliser `agi_export_hof.json` comme bibliothèque de modules
   - Filtrer par tags (`robust`, `high_memory`, `dynamic`)
   - Composer des systèmes hybrides

---

**FIN DU GUIDE — AGI v2.0 OPÉRATIONNEL**

