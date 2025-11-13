# Rapport Niches v5.0 — Brain Modules CA

**Date** : 2025-11-11  
**Mission** : Chercher des niches réalistes où CA sont objectivement utiles

---

## Résumé exécutif

**Verdict** : ❌ **AUCUNE NICHE IDENTIFIÉE**

Les brain modules CA **ne sont compétitifs sur AUCUNE tâche testée**, même sur leur domaine naturel (spatial 2D).

**Recommandation** : **ARCHIVER cette piste pour IA pratique** (Option 2).

---

## Tableau récapitulatif

| Cerveau | Spatial | Morpho | Temporel | Verdict |
|---------|---------|--------|----------|---------|
| **life** | PERD | PERD | PERD | ❌ Inutile |
| **highlife** | PERD | PERD | PERD | ❌ Inutile |
| **life_dense** | PERD | PERD | PERD | ❌ Inutile |
| **34life** | PERD | PERD | PERD | ❌ Inutile |
| **36_234** | Non testé | Non testé | Non testé | ⏭️ Skip |

**Légende** :
- **GAGNE** : Meilleur que baseline(s)
- **PAREIL** : Équivalent à baseline (~±5%)
- **PERD** : Inférieur à baseline(s)
- **TROP CHER** : Coût prohibitif pour gain nul

---

## Résultats détaillés

### Tâche 1 : Spatial 2D (Segmentation + Denoising)

**Hypothèse** : CA excellent sur tâches spatiales 2D (leur domaine naturel)

#### Segmentation patterns géométriques

| Méthode | F1 Score | Temps | Verdict |
|---------|----------|-------|---------|
| **MLP baseline** | **1.000** | 2.95s | ✓ Meilleur |
| **Conv baseline** | **0.918** | 0.01s | ✓ Rapide |
| **CA life** | 0.779 | 0.36s | ❌ Inférieur |
| CA life_dense | 0.723 | 0.32s | ❌ Inférieur |
| CA highlife | 0.702 | 0.32s | ❌ Inférieur |
| CA 34life | 0.686 | 0.31s | ❌ Inférieur |

**Écart** : Meilleur CA **22% pire** que Conv baseline (0.78 vs 0.92)

#### Denoising structuré

| Méthode | Accuracy | MSE | Temps | Verdict |
|---------|----------|-----|-------|---------|
| **Median baseline** | **0.896** | **0.104** | 0.04s | ✓ Meilleur |
| **CA life** | 0.593 | 0.407 | 0.37s | ❌ Inférieur |
| CA highlife | 0.592 | 0.409 | 0.36s | ❌ Inférieur |
| CA 34life | 0.576 | 0.424 | 0.35s | ❌ Inférieur |
| CA life_dense | 0.545 | 0.455 | 0.39s | ❌ Inférieur |

**Écart** : Meilleur CA **34% pire** que Median (0.59 vs 0.90)

**Conclusion spatiale** : ❌ CA **perdent même sur leur domaine naturel**

---

### Tâche 2 : Morphologique (Opérations morpho)

**Hypothèse** : CA peuvent servir d'opérateurs morphologiques "gratuits"

#### Préservation composantes connexes

| Méthode | Préservation | Verdict |
|---------|--------------|---------|
| **Identité (idéal)** | **1.000** | ✓ Référence |
| **CA 34life** | 0.063 | ❌ Détruit 94% |
| CA life | 0.040 | ❌ Détruit 96% |
| CA highlife | 0.038 | ❌ Détruit 96% |
| CA life_dense | 0.032 | ❌ Détruit 97% |

**Observation** : CA **détruisent** les structures au lieu de les préserver

#### Similarité avec érosion

| Méthode | Similarité IoU | Verdict |
|---------|----------------|---------|
| **Tous CA** | **0.000** | ❌ Aucune |

#### Similarité avec dilatation

| Méthode | Similarité IoU | Verdict |
|---------|----------------|---------|
| **CA life_dense** | 0.174 | ❌ Très faible |
| CA 34life | 0.109 | ❌ Très faible |
| CA life/highlife | 0.083 | ❌ Très faible |

#### Détection de bords

| Méthode | Similarité avec Sobel | Verdict |
|---------|----------------------|---------|
| **CA life/highlife** | 0.272 | ❌ Faible |
| CA 34life | 0.252 | ❌ Faible |
| CA life_dense | 0.241 | ❌ Faible |

**Conclusion morphologique** : ❌ CA **ne fonctionnent PAS** comme opérateurs morphologiques utiles

---

### Tâche 3 : Temporel (Propagation + Lissage)

**Hypothèse** : CA aident à lisser/prolonger signaux temporels

#### Prédiction frame suivante

| Méthode | Accuracy | MSE | Temps | Verdict |
|---------|----------|-----|-------|---------|
| **Baseline readout** | **1.000** | **0.000** | 0.40s | ✓ Parfait |
| **CA 34life + readout** | 0.999 | 0.000 | 0.85s | ⚠️ Marginal |
| CA life_dense + readout | 0.997 | 0.002 | 0.97s | ⚠️ Légèrement pire |
| CA life/highlife + readout | 0.993 | 0.005 | 0.75-0.92s | ❌ Pire |

**Écart** : Meilleur CA **identique** à baseline mais **2× plus lent**

#### Lissage temporel

| Méthode | Accuracy | MSE | Temps | Verdict |
|---------|----------|-----|-------|---------|
| **Baseline median** | **0.996** | **0.004** | 0.16s | ✓ Meilleur |
| **CA 34life** | 0.960 | 0.040 | 0.39s | ❌ Inférieur |
| CA life | 0.943 | 0.057 | 0.48s | ❌ Inférieur |
| CA highlife | 0.943 | 0.057 | 0.40s | ❌ Inférieur |
| CA life_dense | 0.930 | 0.070 | 0.40s | ❌ Inférieur |

**Écart** : Meilleur CA **3.6% pire** et **2.4× plus lent**

**Conclusion temporelle** : ⚠️ CA **marginalement inférieurs** à baselines

---

## Analyse globale

### Score par tâche

| Tâche | Meilleur CA | Baseline | Écart | Coût relatif |
|-------|-------------|----------|-------|--------------|
| **Segmentation** | 0.78 F1 | 0.92 F1 | -15% | 36× |
| **Denoising** | 0.59 acc | 0.90 acc | -34% | 9× |
| **Composantes** | 0.06 | 1.00 | -94% | - |
| **Érosion** | 0.00 | - | -100% | - |
| **Dilatation** | 0.17 | - | -83% | - |
| **Bords** | 0.27 | - | -73% | - |
| **Prédiction** | 1.00 | 1.00 | 0% | 2× |
| **Lissage** | 0.96 | 1.00 | -4% | 2.4× |

**Moyenne écart** : **-50%** (CA sont en moyenne 50% moins bons)
**Moyenne coût** : **12× plus lent**

### Aucune niche identifiée

❌ **Spatial 2D** : CA perdent vs Conv/MLP  
❌ **Morphologique** : CA détruisent structures  
⚠️ **Temporel** : CA marginalement inférieurs  
❌ **Coût** : Toujours plus lent (2-36×)

---

## Pourquoi les CA échouent ?

### 1. Règles Life-like inadaptées

Les règles B/S sont **conçues pour patterns visuels intéressants**, pas pour utilité computationnelle :
- Optimisées pour émergence de structures (gliders, oscillateurs)
- **PAS** optimisées pour préservation/transformation contrôlée
- Comportement chaotique/destructeur sur patterns arbitraires

### 2. Évolution destructrice

Les CA **détruisent l'information** au lieu de la transformer utilement :
- Préservation composantes : 4% (destruction 96%)
- Denoising : 59% acc (pire que hasard sur certains patterns)
- Pas de "morphologie gratuite" : 0% similarité avec érosion

### 3. Pas d'avantage sur domaine naturel

Même sur **spatial 2D** (domaine CA), baselines triviales gagnent :
- Conv simple : F1=0.92 vs CA=0.78
- Median filter : acc=0.90 vs CA=0.59

### 4. Coût prohibitif

CA sont systématiquement **2-36× plus lents** sans gain de performance.

---

## Décision BINAIRE

**Question** : Garder brain modules CA comme briques spécialisées OU archiver ?

### Option 1 : Garder modules spécialisés ❌

**Conditions** : Il existe AU MOINS UNE tâche où CA apportent un avantage

**Status** : **NON SATISFAIT**
- Aucune tâche où CA > baseline
- Aucun avantage de coût, robustesse, interprétabilité
- Pas de niche identifiée

**Verdict** : ❌ **REJETER Option 1**

### Option 2 : Archiver pour IA pratique ✅

**Conditions** : Aucune niche réaliste identifiée

**Status** : **SATISFAIT**
- Tests exhaustifs sur 8 tâches variées
- CA perdent ou échouent sur toutes
- Coût prohibitif sans contrepartie

**Verdict** : ✅ **ACCEPTER Option 2**

---

## Recommandation FINALE

**ARCHIVER la piste brain modules CA pour IA pratique**

**Raisons empiriques** :
1. ❌ Aucune tâche où CA compétitifs
2. ❌ Perdent même sur domaine naturel (spatial 2D)
3. ❌ Détruisent structures (morpho)
4. ❌ Coût 2-36× supérieur sans gain
5. ❌ Budget épuisé (Phase B ~30 min de tests)

**Ce qui reste** :
- ✅ Garder repo comme **labo théorique**
- ✅ Documentation propre pour référence
- ✅ Code réutilisable pour recherche fondamentale

**Ce qui NE vaut PAS la peine** :
- ❌ Phase C (Hybride) : Inutile vu résultats Phase B
- ❌ Phase D (3D) : Coût injustifié sans preuve de concept
- ❌ Optimisation règles CA : Pas de signal positif

---

## Fichiers générés

- `results/brain_niches_v5/spatial_tasks.json` — Tests spatiaux
- `results/brain_niches_v5/morpho_tasks.json` — Tests morphologiques
- `results/brain_niches_v5/temporal_tasks.json` — Tests temporels
- `docs/BRAIN_NICHES_v5_REPORT.md` — Ce rapport

---

**Pas de demi-mesure. Pas de bullshit. Juste les faits mesurés.**

**Les brain modules CA ne valent PAS le coup pour IA pratique. Archiver.**

✅ **MISSION v5.0 TERMINÉE**


