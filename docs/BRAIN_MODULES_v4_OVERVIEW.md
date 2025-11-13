# Brain Modules v4.0 — Vue d'ensemble

**Date** : 2025-01-XX  
**Objectif** : Catalogue canonique des 5 brain modules validés v3.5

---

## Vue d'ensemble

Ce document décrit les propriétés dynamiques, scores et rôles recommandés pour chaque brain module validé.

**Note importante** : Les métriques suivantes sont **MESURÉES** (résultats de `results/brain_validation_v3.json`) sauf indication contraire.

---

## Module 1 : Life (B3/S23)

### Propriétés

- **Notation** : B3/S23
- **Born** : [3]
- **Survive** : [2, 3]
- **Profile** : sparse_memory
- **Tier** : 1

### Scores mesurés

- **Life capacity** : 0.70 (MESURÉ)
- **Robustness** : 0.20 (MESURÉ)
- **Functional score** : 0.00 (MESURÉ)

### Propriétés dynamiques

- **Patterns Life canoniques** : 4/5 fonctionnent bien (block, blinker, toad, beacon)
- **Glider** : Survit mais score partiel (0.30) — mouvement complique périodicité
- **Stabilité** : Excellente sur patterns Life standards
- **Densité finale** : 0.003-0.006 (sparse)

### Rôle recommandé

**Compute / Mémoire propre / Référence**

- Module baseline pour patterns Life canoniques
- Usage : traitement de données propres, référence pour comparaisons
- Limitation : Robustesse au bruit limitée (0.20)

---

## Module 2 : HighLife (B36/S23)

### Propriétés

- **Notation** : B36/S23
- **Born** : [3, 6]
- **Survive** : [2, 3]
- **Profile** : replicator
- **Tier** : 1

### Scores mesurés

- **Life capacity** : 0.70 (MESURÉ)
- **Robustness** : 0.20 (MESURÉ)
- **Functional score** : 0.00 (MESURÉ)

### Propriétés dynamiques

- **Patterns Life canoniques** : Identiques à B3/S23 (4/5 fonctionnent bien)
- **Différence B6** : Permet réplication additionnelle (replicators)
- **Comportement** : Life-compatible avec capacité additionnelle
- **Densité finale** : 0.003-0.006 (sparse)

### Rôle recommandé

**Réplication / Propagation**

- Module pour réplication/propagation de patterns
- Usage : systèmes nécessitant duplication de structures
- Avantage : Compatible Life + réplication additionnelle

---

## Module 3 : Life Dense (B3/S234)

### Propriétés

- **Notation** : B3/S234
- **Born** : [3]
- **Survive** : [2, 3, 4]
- **Profile** : dense_memory
- **Tier** : 1

### Scores mesurés

- **Life capacity** : 0.68 (MESURÉ)
- **Robustness** : 0.24 (MESURÉ — meilleur que les autres)
- **Functional score** : 0.00 (MESURÉ)

### Propriétés dynamiques

- **Patterns Life canoniques** : 5/5 survivent (tous patterns fonctionnent)
- **Glider + Toad** : Scores partiels (0.50) — périodicité approximative
- **Stabilité additionnelle** : S4 (survie à 4 voisins) ajoute robustesse
- **Densité finale** : 0.004-0.059 (variable selon pattern)

### Rôle recommandé

**Variante Life dense/stable**

- Module pour mémoire Life avec tolérance bruit accrue
- Usage : Backup module, variante robuste de Life
- Avantage : Robustesse supérieure (0.24 vs 0.20)

---

## Module 4 : 34 Life (B34/S34)

### Propriétés

- **Notation** : B34/S34
- **Born** : [3, 4]
- **Survive** : [3, 4]
- **Profile** : robust_frontend
- **Tier** : 1

### Scores mesurés

- **Life capacity** : 0.32 (MESURÉ — limité)
- **Robustness** : 0.20 (MESURÉ)
- **Functional score** : 0.00 (MESURÉ)

### Propriétés dynamiques

- **Patterns Life canoniques** : Seulement 2/5 survivent
  - ✅ **OK** : block (0.80), glider (0.80)
  - ❌ **MORTS** : blinker, toad, beacon (oscillateurs period-2)
- **Comportement** : Préserve still-lifes + spaceships, **tue oscillateurs period-2**
- **Densité finale** : 0.003-0.005 (sparse)

### Rôle recommandé

**Front-end robuste / Filtrage**

- ⚠️ **Limitation importante** : Ne pas utiliser pour mémoire patterns complexes
- Usage : Pré-processing de signaux bruités, filtrage
- **Non compatible** comme module mémoire Life générique

---

## Module 5 : HighLife Stabilisé (B36/S234)

### Propriétés

- **Notation** : B36/S234
- **Born** : [3, 6]
- **Survive** : [2, 3, 4]
- **Profile** : spin_glass_like
- **Tier** : 2

### Scores mesurés

- **Life capacity** : 0.68 (HEURISTIQUE — basé sur documentation v3.4)
- **Robustness** : 0.25 (HEURISTIQUE — basé sur documentation v3.4)
- **Functional score** : 0.00 (HEURISTIQUE)

### Propriétés dynamiques

- **Comportement** : HighLife + S4 (stabilité accrue)
- **Profil** : Réplication + robustesse combinées
- **Note** : Moins testé que les 4 autres modules

### Rôle recommandé

**Backup / HighLife stabilisé**

- Module de backup pour réplication + robustesse
- Usage : Alternative à HighLife avec stabilité améliorée
- **Note** : Tier 2 — nécessite validation supplémentaire

---

## Comparaison rapide

| Module | Life Cap | Robustness | Tier | Usage principal |
|--------|----------|------------|------|-----------------|
| **Life** | 0.70 | 0.20 | 1 | Compute / Mémoire référence |
| **HighLife** | 0.70 | 0.20 | 1 | Réplication / Propagation |
| **Life Dense** | 0.68 | **0.24** | 1 | Variante robuste Life |
| **34 Life** | **0.32** | 0.20 | 1 | Front-end / Filtrage |
| **36_234** | 0.68 | 0.25 | 2 | Backup stabilisé |

---

## Recommandations d'usage

### Pour mémoire séquentielle

1. **Life** (B3/S23) — Baseline
2. **Life Dense** (B3/S234) — Si besoin robustesse accrue

### Pour réplication

1. **HighLife** (B36/S23) — Standard
2. **36_234** (B36/S234) — Si besoin stabilité additionnelle

### Pour filtrage robuste

1. **34 Life** (B34/S34) — ⚠️ Usage spécialisé uniquement

---

## Notes importantes

### Métriques mesurées vs heuristiques

- **MESURÉ** : Modules 1-4 (résultats `brain_validation_v3.json`)
- **HEURISTIQUE** : Module 5 (B36/S234) — basé sur documentation v3.4, nécessite validation

### Limitations identifiées

1. **Functional score = 0** pour tous modules
   - Métrique memory_capacity trop stricte (patterns aléatoires instables)
   - Life pattern capacity plus fiable

2. **Robustness faible** (0.20-0.25)
   - Métrique basée sur damier pattern → peu représentatif
   - Amélioration nécessaire : tester sur patterns Life réels

3. **34 Life limité** (life_capacity = 0.32)
   - Ne préserve pas oscillateurs period-2
   - Usage restreint au filtrage

---

## Fichiers associés

- `isinglab/brain_modules.py` — Code source du catalogue
- `results/brain_modules_library_v4.json` — Export JSON
- `results/brain_validation_v3.json` — Résultats validation détaillés
- `docs/BRAIN_VALIDATION_v3_1.md` — Rapport validation complet

---

**Status** : Catalogue v4.0 — 5 modules documentés (4 mesurés, 1 heuristique)



