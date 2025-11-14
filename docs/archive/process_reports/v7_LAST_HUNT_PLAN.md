# v7.0 — Plan de Chasse Finale Brain Modules CA

**Date** : 2025-11-11  
**Objectif** : Dernière recherche structurée, rationnelle, avec kill switch

---

## Contexte

Après v5.0, le verdict est clair :
- **0/8 tâches** où CA brain modules compétitifs
- **-50% performance moyenne**, **12× plus lent**
- **Aucune niche réaliste identifiée**

Cette campagne v7.0 est la **dernière passe sérieuse** avant clôture définitive de la branche CA-réservoir pour IA pratique.

---

## Espace exploré (COMPACT, RATIONNEL)

### 1. Mutations locales des 5 brain modules v3.5

**Seeds** : `life`, `highlife`, `life_dense`, `34life`, `36_234`

**Mutations autorisées** :
- Distance Hamming 1-2 sur `born` ou `survive`
- Ajout/retrait d'une valeur dans B ou S
- Exemple : B3/S23 → B3/S234 (déjà testé), B3/S24, B34/S23, etc.

**Exclusions strictes** :
- `born` vide (règle triviale)
- Quasi-death (density < 0.05 après 50 steps)
- Explosion (density > 0.98 après 50 steps)
- Règles déjà testées dans v3.5-v5.0

**Budget** : Maximum **30 règles candidates** (5 seeds × 6 mutations max)

### 2. Règles 3D inspirées physiquement

**Hypothèse** : Peut-être que 3D offre des dynamiques plus riches.

**Règles testées** :
- `life3d` (B4/S34) — Analogue 3D de Life
- `445` (B4/S45) — Structures stables 3D
- `567` (B567/S567) — Dense 3D

**Tailles testées** :
- 16³ (4096 cells, coût estimé : 0.17 ms/step)
- 24³ (13824 cells, coût estimé : 0.5 ms/step)

**Budget** : Maximum **6 règles 3D** (3 règles × 2 tailles)

**Justification** : Coût 3D est raisonnable (voir `COST_MODEL_v5.md`). Si aucun signal positif → abandon définitif 3D.

---

## Critères de succès (STRICTS, NON-NÉGOCIABLES)

Une règle n'est considérée comme **découverte significative** que si elle satisfait **TOUS** les critères suivants :

### 1. Non-trivialité

- `0.05 < density < 0.98` après 50 steps (multi-seed, 10 runs)
- Rejette : stabilizers, sinks, quasi-death, bruit blanc

### 2. Capacité structurée

- `life_pattern_capacity` > **0.50** (au moins 50% des patterns Life canoniques préservés)
- Plusieurs attracteurs / motifs distincts (pas juste un motif gelé)

### 3. Robustesse

- Supporte au moins **15% de bruit** sans s'effondrer en trivialité
- `robustness_score` > **0.40**

### 4. Tâche concrète (AU MOINS UNE)

Choisir **intelligemment** une tâche adaptée aux CA (pas NARMA19 pour le folklore) :

**Tâches candidates** :
- **Pattern completion visuel** (compléter patterns partiels)
- **Détection de structures** (identifier gliders, oscillateurs)
- **Segmentation spatiale** (séparer régions connexes)

**Critère de réussite** :
- Performance ≥ baseline linéaire/ESN simple
- Ratio perf/coût ≤ **5-10×** (max 10× plus cher pour un gain mesurable)

**Si ces critères ne sont PAS remplis** → Ce n'est pas un "cerveau", c'est un jouet. On le documente et on passe à autre chose.

---

## Budget estimé

### 2D

- 30 règles candidates
- 10 runs × 50 steps × 32×32 grid
- Temps estimé : **~20 minutes** (vectorisation)

### 3D

- 6 règles candidates
- 10 runs × 50 steps × 16³ ou 24³
- Temps estimé : **~10 minutes**

**Total** : **~30 minutes** de calcul

**Acceptable** : Oui. C'est une dernière passe compacte, pas un bruteforce.

---

## Métriques utilisées

### Filtres durs (pré-sélection)

1. **Density check** : 0.05 < density < 0.98
2. **Entropy check** : entropy > 0.1 (pas sink)
3. **Stability check** : Pas d'explosion/mort en 50 steps

### Métriques de capacité

1. **life_pattern_capacity** : Préservation patterns Life canoniques (block, blinker, glider, toad, beacon)
2. **memory_capacity** : Nombre de patterns distincts stabilisables
3. **robustness_to_noise** : Résistance au bruit (10%, 15%, 20%)

### Benchmark tâche

1. **Pattern completion** : Compléter patterns partiels (50% masqués)
2. **Baseline** : Régression linéaire + ESN simple
3. **Métrique** : Accuracy + temps de calcul

---

## Kill Switch (AUTOMATIQUE)

**Condition de déclenchement** :

Si **AUCUNE** règle candidate ne satisfait les critères de succès (section ci-dessus), alors :

1. **Arrêt immédiat** de la recherche CA-réservoir
2. **Création** de `MISSION_v7_CA_BRANCH_CLOSED.md`
3. **Archivage** de la branche pour IA pratique
4. **Pivot** vers agent R&D multi-projets

**Pas de "une dernière petite mutation"**. Pas de "peut-être avec un autre encodage". **C'est fini.**

---

## Justification de l'espace exploré

### Pourquoi mutations locales ?

- Les brain modules v3.5 sont les **meilleurs** trouvés après 150h de recherche
- Si une règle "cerveau" existe, elle est probablement **proche** de ces seeds
- Distance Hamming 1-2 couvre le voisinage immédiat sans explosion combinatoire

### Pourquoi 3D ?

- Hypothèse : Dynamiques 3D plus riches (26 voisins vs 8)
- Coût raisonnable (voir `COST_MODEL_v5.md`)
- Si aucun signal positif → abandon définitif 3D

### Pourquoi PAS de bruteforce ?

- Espace B/S est gigantesque (2^9 × 2^9 = 262k règles 2D)
- v3.x-v5.x ont déjà exploré largement sans succès
- Recherche locale ciblée est plus efficace

---

## Protocole d'exécution

### 1. Génération des candidats

- Mutations locales des 5 seeds (distance Hamming 1-2)
- Filtrage dur immédiat (density, entropy, stability)
- Sélection top 30 règles 2D + 6 règles 3D

### 2. Évaluation complète

- Pour chaque règle candidate :
  - `life_pattern_capacity` (patterns Life canoniques)
  - `robustness_to_noise` (10%, 15%, 20%)
  - `memory_capacity` (10 patterns aléatoires)
  - Benchmark tâche (pattern completion)

### 3. Comparaison baselines

- Régression linéaire (Ridge)
- ESN simple (100 neurones)
- Métrique : Accuracy + temps de calcul

### 4. Verdict

- Si au moins UNE règle passe tous les critères → **Découverte significative**
- Sinon → **Kill Switch activé**

---

## Conditions de réouverture (FUTURES)

Si la branche CA-réservoir est close, elle pourra être **rouverte** uniquement si :

1. **Nouveaux outils** : Hardware dédié (FPGA, ASIC) rendant le coût négligeable
2. **Nouvelles règles** : Découverte de règles CA optimisées pour computing (pas Life-like)
3. **Nouvelle théorie** : Avancée théorique prouvant que CA peuvent surpasser RNN sur certaines tâches

**Pas de réouverture** pour :
- "J'ai une intuition"
- "Peut-être avec un autre encodage"
- "On n'a pas essayé TOUTES les règles"

---

## Fichiers générés

- `scripts/run_last_brain_hunt_v7.py` — Script de campagne
- `results/last_brain_hunt_v7_candidates.json` — Règles candidates
- `results/last_brain_hunt_v7_results.json` — Résultats détaillés
- `docs/v7_LAST_HUNT_RESULTS.md` — Rapport final

---

## Résumé exécutif

**Espace** : 30 règles 2D + 6 règles 3D (mutations locales des 5 seeds)

**Critères** : Non-trivialité + Capacité structurée + Robustesse + Tâche concrète

**Budget** : ~30 minutes de calcul

**Kill Switch** : Si aucune règle ne passe → Clôture définitive branche CA-réservoir

**Honnêteté** : Pas de bullshit. Si ça ne marche pas, on l'admet et on passe à autre chose.

---

**C'est la dernière chance. Soit on trouve quelque chose de solide, soit on clôture proprement.**


