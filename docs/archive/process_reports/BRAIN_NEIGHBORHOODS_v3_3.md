# Deep Brain Hunt v3.3 — Exploration Voisinage Cerveaux

**Date** : 2025-11-11  
**Phase** : A (Voisinage profond des 4 cerveaux)  
**Status** : ✅ Complété

---

## Objectif

Explorer systématiquement le voisinage immédiat des 4 cerveaux validés (B3/S23, B36/S23, B34/S34, B3/S234) pour :
1. Confirmer qu'ils sont optimaux locaux
2. Identifier d'éventuels cerveaux cachés proches
3. Cartographier le gradient de qualité

---

## Méthode

### Stratégies de Mutation
- **Mutations ±1** : Ajouter/retirer 1 chiffre sur born/survive
- **Familles structurées** : Variantes B3/S2X, B3X/S23, etc.

### Évaluation (Vectorisée)
- Multi-grilles : 32×32, 64×64
- Multi-bruits : 0%, 10%, 20%, 30%
- Life pattern capacity (5 patterns canoniques)
- Filtres durs : density < 0.05 ou > 0.95 rejetées

### Volume
- **97 règles générées** (voisins des 4 cerveaux)
- **10 hard filtered** (quasi-death/saturation)
- **64 candidats valides** évalués

---

## Résultats Globaux

### Distribution Métriques

| Métrique                  | Nombre Candidats |
|---------------------------|------------------|
| High functional (>0.05)   | **4**            |
| High life_capacity (≥0.70)| **26**           |
| High robustness (>0.25)   | **4**            |

### Top 4 Candidats Distincts (hors 4 cerveaux originaux)

#### 1. **B6/S23** ⭐⭐⭐⭐⭐

**Métriques initiales (32×32)** :
- Functional: **0.750** (meilleur score trouvé)
- Life capacity: 0.480
- Robustness: **1.000** (parfait)

**Investigation profonde** :
- **Multi-grilles** :
  - 16×16 → 256×256 : functional stable 0.750 (sauf 256×256: 0.520)
  - Performance cohérente sur grilles moyennes
  
- **Robustness exceptionnelle** :
  - **1.000 sur tous niveaux de bruit** (0% → 50%)
  - Aucune dégradation mesurée
  
- **Life patterns (64×64)** :
  - 3/5 patterns survivent : block, glider, beacon
  - Oscillateurs period-2 (blinker, toad) meurent
  
- **Long-term dynamics (500 steps)** :
  - Density finale : **0.061** (stable, σ=0.000)
  - Entropy : 0.030 (faible diversité)
  - **Convergence vers état sparse stable**

**Profil** : Règle ultra-robuste à born minimal (B6 seul), converge vers états stables très pauvres. Robustesse maximale au bruit mais diversité structurelle limitée.

**Verdict** : **Candidat cerveau "Ultra-Robust Sparse"**. Usage : Module de filtrage extrême / stabilisation bruit élevé. Pas adapté comme mémoire riche (life_capacity limitée).

---

#### 2. **B3/S2345** ⭐⭐⭐

**Métriques initiales (32×32)** :
- Functional: **0.575**
- Life capacity: **0.680** (5/5 patterns survivent)
- Robustness: 0.750

**Investigation profonde** :
- **Multi-grilles** :
  - 16×16: func=0.750
  - 32×32: func=0.570
  - 64×64: func=0.640
  - 128×128: func=0.340
  - 256×256: func=0.000
  - **Dégradation avec taille** → problème d'échelle
  
- **Robustness** :
  - Variable (0.2 → 1.0) selon noise_level
  - Moyenne ~0.7 (correcte mais pas exceptionnelle)
  
- **Life patterns (64×64)** :
  - **5/5 patterns survivent** (tous !)
  - Glider et toad : périodicité approximative
  - Score global : 0.640
  
- **Long-term dynamics (500 steps)** :
  - Density finale : **0.560** (stable, σ=0.000)
  - Entropy : 0.097 (meilleure que B6/S23)
  - Convergence vers état dense stable

**Profil** : Extension de B3/S234 (ajoute S5), meilleure life_capacity, mais instable grandes grilles.

**Verdict** : **Candidat intéressant mais limité**. Bon pour grilles petites/moyennes (<128). Dégradation grandes grilles = problème sérieux. Pas adapté comme cerveau générique.

---

#### 3. **B3/S1234** ⭐

**Métriques** :
- Functional: 0.154
- Life capacity: 0.520 (4/5 patterns)
- Robustness: 0.583

**Profil** : Extension B3/S234 (ajoute S1), capacité fonctionnelle faible.

**Verdict** : Intérêt limité. Pas meilleur que B3/S234.

---

#### 4. **B3/S2346** ⭐

**Métriques** :
- Functional: 0.087
- Life capacity: 0.680 (5/5 patterns)
- Robustness: 0.417

**Profil** : Variante B3/S234 (remplace S5 par S6).

**Verdict** : Intérêt limité. Légèrement inférieur à B3/S234.

---

## Analyse Structurelle

### Par Born
- **B3** : 18 règles, avg_life=0.682, avg_func=0.045
- **B36** : 15 règles, avg_life=0.685, avg_func=0.000
- **B6** : 1 règle (B6/S23), func=0.750 ⭐

### Par Survive
- **S23** : 23 règles, avg_life=0.610, avg_func=0.033
- **S234** : 11 règles, avg_life=0.625
- **S2345** : 1 règle (B3/S2345), func=0.575 ⭐

**Observation** : Born minimal (B6) et Survive étendu (S2345) produisent les candidats les plus fonctionnels.

---

## Conclusions

### Cerveaux Validés Confirmés

Les **4 cerveaux originaux** restent les références :
- **B3/S23** (Life) : Équilibre optimal life_capacity (0.70) + stabilité
- **B36/S23** (HighLife) : Réplication
- **B34/S34** (34 Life) : Front-end (limité)
- **B3/S234** : Variante dense stable (0.68)

### Nouveau Candidat Sérieux

**B6/S23** : Candidat **"5ème cerveau"** avec profil distinct :
- **Robustesse exceptionnelle** (1.000 sur tous bruits)
- **Stabilité parfaite** (long-term)
- **Life capacity limitée** (0.48 vs 0.68-0.70 pour les autres)

**Usage recommandé** : Module ultra-robuste pour :
- Filtrage signaux extrêmement bruités (>40% noise)
- Stabilisation/nettoyage post-traitement
- Front-end encore plus robuste que B34/S34

**Limitation** : Pas adapté comme mémoire riche (diversité structurelle faible).

### Candidats Rejetés

- **B3/S2345** : Intéressant petites grilles mais **instable grandes grilles** → rejet comme cerveau générique
- **B3/S1234, B3/S2346** : Pas d'avantage sur B3/S234

---

## Recommandations

### Accepter B6/S23 comme 5ème Cerveau

**Justification** :
1. Profil **clairement distinct** des 4 autres (robustness extrême vs life_capacity)
2. Métriques **supérieures** sur dimension spécifique (robustness 1.000 constant)
3. Usage pratique clair (filtrage bruit élevé)

**Statut proposé** : **Module "Ultra-Robust Filter"**

### Rejeter B3/S2345

Malgré functional=0.575 intéressant, la **dégradation grandes grilles** (func → 0 à 256×256) est rédhibitoire. Pas fiable comme cerveau générique.

---

## Limites & Biais

1. **Voisinage local seulement** : Mutations ±1 limitent exploration radicale
2. **Functional_score = 0 pour majorité** : Métrique memory_capacity reste trop stricte
3. **Grilles max 64×64** pour voisinage (256×256 seulement pour investigation profonde)

---

## Phase B : Next Steps

**Zones sous-explorées à cibler** :
1. **Minimal born** : B0, B1, B2 seuls (hors B6 déjà testé)
2. **High sensitivity** : born ⊃ {5,6,7}, survive restreints
3. **Symétries/duals** : Exploitation rule_ops

---

**Fichiers générés** :
- `results/brain_neighborhoods_v3_3.json` : Données brutes
- `results/deep_investigation_v3_3.json` : Investigation B6/S23, B3/S2345 (partiel, crash JSON)
- `docs/BRAIN_NEIGHBORHOODS_v3_3.md` : Ce rapport

**Status** : Phase A complète. **B6/S23 = candidat sérieux 5ème cerveau**.




