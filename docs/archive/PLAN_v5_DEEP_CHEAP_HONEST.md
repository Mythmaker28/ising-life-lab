# Plan v5.0 — "Deep, Cheap & Honest"

**Objectif** : Trouver des niches réalistes où les brain modules CA sont objectivement utiles, ou conclure qu'il faut archiver cette piste.

---

## Phase A : Modèle de Coût & 3D (PRIORITÉ)

**Objectif** : Quantifier le coût computationnel 2D vs 3D, établir un budget

**Actions** :
1. Créer `isinglab/core/ca3d_vectorized.py` — Moteur CA 3D vectorisé
2. Créer `scripts/benchmark_cost_v5.py` — Mesure coût 2D/3D
3. Fit modèle : time_per_update = f(dimensions)
4. Établir budget : max 10^7 updates par campagne
5. Documenter : `docs/COST_MODEL_v5.md`

**Décision** : Si 3D trop cher → skip Phase D

---

## Phase B : Tâches Niches (CŒUR)

**Objectif** : Chercher où CA peuvent briller

### B1. Tâches spatiales 2D/3D
- Segmentation patterns géométriques
- Denoising structuré (domaines/cellules)
- **Baseline** : Conv simple, MLP
- **Verdict** : CA gagne/perd

### B2. Tâches morphologiques
- Composantes connexes
- Érosion/dilatation
- Détection frontières
- **Baseline** : Opérateurs morpho classiques
- **Verdict** : CA utile comme "morphologie gratuite" ?

### B3. Tâches temporelles couplées espace
- Propagation/réparation patterns
- Lissage temporel
- **Baseline** : Filtering classique
- **Verdict** : CA apporte quoi ?

**Fichiers** :
- `scripts/test_spatial_tasks_v5.py`
- `scripts/test_morpho_tasks_v5.py`
- `scripts/test_temporal_tasks_v5.py`
- `results/brain_niches_v5/*.json`
- `docs/BRAIN_NICHES_v5_REPORT.md`

---

## Phase C : IA Hybride Minimale

**Objectif** : CA + readout vs readout seul

**Pipeline** :
- Input → [optionnel: CA k steps] → Linear/MLP readout
- Comparer : avec/sans CA

**Tâches** : 1-2 meilleures de Phase B

**Fichiers** :
- `isinglab/hybrid/pipelines_v5.py`
- `scripts/benchmark_hybrid_v5.py`
- `docs/HYBRID_RESULTS_v5.md`

**Décision** : CA + readout > readout seul avec marge ? → niche potentielle

---

## Phase D : 3D Validation (SI COÛT OK)

**Objectif** : Valider 3D sur tâche ciblée

**Conditions** : Cost model permet, Phase B montre potentiel

**Actions** :
- 2-3 règles 3D (Life 3D, spin-glass-like)
- 1 tâche spatiale 3D (denoising volumes)
- Mesure : performance vs coût

**Décision** : 3D ne donne rien / coûte trop → STOP

---

## Phase E : Rapport Final

**Fichiers obligatoires** :

1. **`RESUME_v5_FOR_TOMMY.md`** — 1 page
   - Où CA utiles
   - Où CA inutiles
   - Niche ou fermeture dossier

2. **`docs/BRAIN_NICHES_v5_REPORT.md`** — Tableau
   - Lignes = cerveaux
   - Colonnes = tâches
   - Valeurs = gagne/pareil/perd/trop cher

3. **Recommandation BINAIRE** :
   - **Option 1** : Garder 1-2 modules comme briques spécialisées (X, Y)
   - **Option 2** : Archiver piste CA pour IA pratique

**PAS DE DEMI-MESURE**

---

## Règles d'exécution

- ✅ Autonome : propose, exécute, conclue
- ✅ Honnête : si rien ne marche, le dire
- ✅ Budget coût : respecter limites
- ✅ Pas d'AGI bullshit
- ✅ Décision binaire finale

---

**Démarrage immédiat Phase A**

