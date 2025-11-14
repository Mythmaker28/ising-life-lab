# Contexte Multi-Projets v8.0-v8.2 — Cartographie de l'Écosystème

**Date** : 2025-11-11 (v8.0), Mis à jour : 2025-11-11 (v8.2)  
**Agent** : R&D Multi-Projets Toolkit  
**Objectif** : Synthèse factuelle des dépôts accessibles et de leurs connexions réalistes

---

## Évolution v8.0 → v8.2

**v8.0** : Fondations (datasets, analyse, rapports) ✅  
**v8.2** : **Consolidation** (tests, loaders, bridges, clarté usage externe) 🔄

### Changements v8.2

- ✅ **README refonte** : Focus toolkit, archivage CA, quick start design_space
- ✅ **MISSION & PLAN** : Périmètre clair, roadmap structurée
- ✅ **Loaders module** : `design_space/loaders.py` (load_atlas_optical, validate_schema)
- ✅ **Tests unitaires** : `test_loaders.py`, `test_selector.py` (fixtures mini_design_space.csv)
- ✅ **Bridges documentés** : 3 docs dédiés (Atlas ✅, fp-qubit 🟡, arrest 🔴)

**Rôle ising-life-lab clarifié** : **Toolkit d'analyse et scoring** pour projets externes (Atlas, fp-qubit, arrest).

---

## Vue d'Ensemble

Cette version v8.x marque un pivot stratégique : nous quittons l'exploration spéculative des automates cellulaires comme réservoirs universels (branche close après v7.0) pour nous concentrer sur un **toolkit R&D multi-projets** exploitant des données physiques réelles.

Quatre dépôts constituent notre écosystème :

1. **ising-life-lab** (local) — **Toolkit analyse/scoring** (noyau central)
2. **Quantum-Sensors-Qubits-in-Biology** (GitHub) — Atlas de systèmes quantiques bio/condensés
3. **fp-qubit-design** (GitHub) — Design computationnel de mutants de protéines fluorescentes
4. **arrest-molecules** (GitHub) — Framework de molécules d'arrêt et régulation biologique

---

## 1. ising-life-lab (Dépôt Local)

### Statut Actuel

**Version** : v8.2 (Consolidation)  
**Tests** : Tests unitaires design_space/ (loaders, selector) ✅  
**Branche CA-réservoir** : 🔴 CLOSE pour IA pratique (décision v7.0)  
**Rôle** : **Toolkit R&D** pour analyse/scoring qubits/biosenseurs/molécules

### Contenu Réel

**Code & Modules (Toolkit)** :
- **`design_space/`** : Module principal toolkit
  - `selector.py` : 10 fonctions filtrage/ranking (load, rank_by_integrability, filter_by_family, etc.)
  - `loaders.py` : Chargement/validation datasets (load_atlas_optical, validate_schema)
- **`isinglab.metrics`** : Métriques réutilisables (capacity, robustness, stability, basin)
- **`isinglab.data_bridge`** : Interface READ-ONLY Atlas (historique v8.0)
- `isinglab.core` : Moteurs CA 2D/3D (historique, archivé)
- `isinglab.server` : Viewer web localhost:8000 (historique)

**Données Locales** :
- `data/atlas_optical/atlas_fp_optical_v2_2_curated.csv` : **180 systèmes Tier 1** ✅
- `data/atlas_nonoptical/` : Vide (datasets à venir)
- `outputs/qubit_design_space_v1.csv` : Dataset standardisé (25 colonnes, tags dérivés)

**Tests** :
- `tests/test_loaders.py` : Validation schema, load Atlas
- `tests/test_selector.py` : Filtres, ranking, familles
- `tests/fixtures/mini_design_space.csv` : 10 systèmes exemple

**Documentation** :
- **Toolkit v8.x** (actuel) :
  - `README.md` : Vue d'ensemble toolkit, quick start
  - `docs/MISSION_v8_2.md` : Périmètre toolkit (inputs, outputs, usage)
  - `docs/PLAN_v8_2.md` : Roadmap court/moyen/long terme
  - `docs/DESIGN_SPACE_v1_REPORT.md` : Analyse 180 systèmes
  - `docs/BRIDGE_ATLAS_QUANTUM_SENSORS.md` : Format, usage, statut ✅
  - `docs/BRIDGE_FP_QUBIT_DESIGN.md` : Format, usage, statut 🟡
  - `docs/BRIDGE_ARREST_MOLECULES.md` : Format, usage, statut 🔴
- **Historique CA-réservoir** (v1-v7, archivé) :
  - `RESUME_v5_FOR_TOMMY.md` : 0/8 tâches niches
  - `docs/v7_LAST_HUNT_RESULTS.md` : Kill switch activé
  - `MISSION_v7_CA_BRANCH_CLOSED.md` : Clôture officielle

### Ce Qui a de la Valeur (Utilisable pour v8.0)

✅ **Méthodologie éprouvée** :
- Filtres durs (density, entropy, stability) pour rejeter faux signaux
- Baselines solides (ESN, Linear, Conv, Median) avant toute conclusion
- Stress-tests (multi-grilles, multi-bruit, patterns variés)
- Kill switch pour éviter chasses infinies

✅ **Outils réutilisables** :
- Métriques de stabilité d'attracteurs (transposables à systèmes moléculaires/quantiques)
- Algorithmes évolutionnaires (recherche dans espaces discrets)
- Data bridge préparé pour intégrer Atlas (nécessite téléchargement CSV)

✅ **Résultats négatifs documentés** :
- CA Life-like ne sont PAS compétitifs pour IA pratique (150h de tests rigoureux)
- Robustesse catastrophique (29/30 règles s'effondrent à 15% bruit)
- Coût prohibitif (100× plus lent que ESN, -50% performance)

### Ce Qui NE Sera PAS Utilisé

❌ **Recherche de nouvelles règles CA "magiques"** (branche close)  
❌ **Prétentions AGI via automates cellulaires** (spéculation non validée)  
❌ **Exploration aveugle sans baseline/filtre** (leçon apprise)

### Connexions Potentielles avec Autres Projets

**→ Quantum-Sensors-Qubits-in-Biology** :
- Data bridge `isinglab.data_bridge` prêt à charger CSV Atlas
- Métriques de stabilité applicables à systèmes quantiques (T1/T2, fidelity)
- Filtres durs réutilisables pour trier candidats qubits (density → état thermalisé, entropy → information)

**→ arrest-molecules** :
- Métriques d'attracteurs et de stabilité transposables aux paysages énergétiques moléculaires
- Algorithmes évolutionnaires pour explorer configurations de couplages moléculaires
- Modèles discrets (CA/Ising) comme approximations de dynamiques continues

**→ fp-qubit-design** :
- Métriques de functional_score adaptables pour scorer designs de mutants
- Stress-tests multi-conditions réutilisables pour valider robustesse designs
- Filtres durs pour rejeter mutants non réalisables physiquement

---

## 2. Quantum-Sensors-Qubits-in-Biology (Atlas GitHub)

### URL
https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology

### Description

**Atlas de systèmes quantiques biologiques et condensés** — Catalogue de qubits/capteurs quantiques (centres NV, défauts SiC, spins nucléaires, paires radicalaires, protéines fluorescentes) avec métadonnées expérimentales (T1, T2, température, biocompatibilité, etc.).

### Données Disponibles (Web Search Results)

**Structure à 3 tiers** :

| Tier | Systèmes | Statut | Fichier CSV | Usage |
|------|----------|--------|-------------|-------|
| **Tier 1: CURATED** | 180 | Métadonnées complètes, validées | `atlas_fp_optical_v2_2_curated.csv` | ✅ **Modeling, analysis** |
| **Tier 2: CANDIDATES** | 13 | Systèmes réels, métadonnées incomplètes | `atlas_fp_optical_v2_2_candidates.csv` | Manual curation queue |
| **Tier 3: UNKNOWN** | 103 | Auto-harvest, placeholders | `atlas_fp_optical_v2_2_unknown.csv` | Transparence uniquement |

**Total dataset mixte** : 296 systèmes (Tier 1+2+3), mais **seulement Tier 1 (180 systèmes) recommandé pour ML/analyse**.

### Types de Systèmes Catalogués

D'après le README GitHub (web search) :

**Optical Systems (Protéines Fluorescentes)** :
- GFP et variants (eGFP, sfGFP, mNeonGreen, etc.)
- Protéines rouges (mCherry, mScarlet, etc.)
- Photoactivables (PA-GFP, Dronpa)
- FRET pairs (CFP-YFP, etc.)

**Non-Optical Systems (mentionnés dans README)** :
- NV centers (diamant)
- SiC defects (silicon carbide)
- Nuclear spins (13C, 31P, 14N, 29Si)
- Radical pairs (cryptochrome, photolyase)
- Electron paramagnetic resonance (EPR) systems
- Many-body quantum systems

### Colonnes Attendues (Tier 1 Curated)

D'après `data/README.md` local (qui référence l'Atlas) et structure FPbase classique :

**Identifiants** :
- `system_id`, `protein_name`, `family`, `organism`

**Propriétés Optiques** :
- `ex_max` (nm), `em_max` (nm), `brightness`, `maturation_time`, `photostability`

**Propriétés Quantiques/Physiques** :
- `quantum_yield`, `lifetime` (ns), `pKa`
- `contrast_normalized` (placeholder dans Tier 3, réel dans Tier 1)

**Métadonnées** :
- `evidence_level` (A/B/C), `doi`, `year_published`

**Note** : Colonnes exactes à confirmer en téléchargeant le CSV réel. Les champs T1/T2 (temps de cohérence) sont probablement dans les datasets non-optiques (spins, NV centers), pas dans les protéines fluorescentes.

### Versions & Citation

**v2.2.2 (curated)** : 180 systèmes, modeling-ready (DOI: TBD)  
**v1.2.1 (manuscrit Frontiers)** : 66 systèmes, DOI: 10.5281/zenodo.17420604 (dataset fixé pour publication)

### Outils & API

D'après web search :

**Scripts disponibles** :
- `scripts/validate_atlas.py` : Validation datasets (ranges, DOI format, completeness)
- `scripts/qa/split_tiers.py` : Séparation reproductible Tier 1/2/3

**Dashboard statique** :
- GitHub Pages : https://mythmaker28.github.io/Quantum-Sensors-Qubits-in-Biology/
- Exploration interactive des systèmes

**Licence** :
- Data (CSV) : CC BY 4.0 (libre d'usage avec attribution)
- Code : MIT

### Connexions avec Autres Projets (Factuelles)

**→ ising-life-lab** :
- Module `isinglab.data_bridge` déjà implémenté pour charger Atlas (read-only)
- Fonction `load_optical_systems(tier="curated")` → charge Tier 1 (180 systèmes)
- Mapping heuristique des propriétés optiques → profils quantiques (cohérence, decoherence, readout)

**→ fp-qubit-design** (d'après README Atlas) :
- Utilise un snapshot Atlas v1.2 (22 systèmes, subset de v1.2.1 ?) comme training data pour ML
- Prédit propriétés spectrales et dynamic range de mutants de protéines fluorescentes
- Opportunité : mettre à jour vers v2.2.2 curated (180 systèmes) pour augmenter ensemble d'entraînement

**→ arrest-molecules** :
- Connexion conceptuelle (mentionnée dans README Atlas) : energy landscapes, arrest kinetics, metastability
- Pas de connexion technique directe identifiée (pas de CSV partagé)
- Analogie possible : paysages énergétiques moléculaires ↔ paysages énergétiques qubits

---

## 3. fp-qubit-design (GitHub)

### URL
https://github.com/Mythmaker28/fp-qubit-design

### Description (D'après README Atlas)

**Design computationnel de mutants de protéines fluorescentes optimisées** — Utilise ML (random forest, GNN potentiellement) sur données Atlas pour prédire propriétés spectrales et robustesse de variants.

### État des Connaissances (Limité)

**Données disponibles via web search** : Limitées (repo mentionné mais peu de détails dans résultats).

**Ce que l'on sait (via README Atlas)** :
- Utilise Atlas v1.2 (22 systèmes) comme source d'entraînement
- Prédit : spectral properties, dynamic range
- Objectif : design guidé de biosensors/qubits fluorescents

**Ce que l'on ne sait PAS encore** :
- Langage/framework (Python ? TensorFlow/PyTorch ?)
- Modèles ML exacts utilisés (RF, GNN, transformers ?)
- Formats de données d'entrée/sortie
- Scripts/API disponibles

**Action nécessaire** : Clone local du repo ou exploration GitHub pour détails.

### Connexions Potentielles

**→ Quantum-Sensors-Qubits-in-Biology** :
- Source de données directe (Atlas v1.2 → devrait migrer vers v2.2.2 curated pour 8× plus de données)
- Validation croisée : designs prédits par fp-qubit-design pourraient être ajoutés à l'Atlas Tier 2 (candidates)

**→ ising-life-lab** :
- Filtres physiques d'isinglab pourraient rejeter mutants non réalisables (ex: stability check, robustness to noise)
- Stress-tests multi-conditions pour valider designs avant synthèse expérimentale

**→ arrest-molecules** :
- Pas de connexion directe évidente (domaines différents : protéines vs petites molécules)

---

## 4. arrest-molecules (GitHub)

### URL
https://github.com/Mythmaker28/arrest-molecules

### Description (D'après README Atlas)

**Molecular Arrest Framework** — Théorie unificatrice pour compounds dampening en régulation biologique.

**Données** :
- 10 compounds catalogués
- 44 predictions
- FAIR² compliant (Findable, Accessible, Interoperable, Reusable + Reproducible)

### État des Connaissances (Limité)

**Données disponibles via web search** : Très limitées (repo mentionné, pas de détails structurels).

**Ce que l'on sait** :
- Framework théorique sur molécules d'arrêt
- Vocabulaire partagé avec métastabilité quantique : energy landscapes, arrest kinetics, tunneling vs activation barriers
- DOI : 10.5281/zenodo.17420685 (dataset Zenodo)

**Ce que l'on ne sait PAS encore** :
- Format de données (CSV, JSON, .xyz pour structures moléculaires ?)
- Nature des 44 predictions (Ki, ΔΔG, constantes d'arrêt ?)
- Scripts/modèles disponibles

**Action nécessaire** : Clone local du repo ou exploration GitHub pour détails.

### Connexions Potentielles

**→ ising-life-lab** :
- Métriques d'attracteurs (basin, stability) transposables aux paysages énergétiques moléculaires
- Modèles discrets (Ising/CA) comme approximations de réseaux de régulation
- Algorithmes évolutionnaires pour explorer configurations de couplages

**→ Quantum-Sensors-Qubits-in-Biology** :
- Connexion conceptuelle (mentionnée dans README Atlas) : metastabilité, paysages énergétiques
- Pas de connexion technique directe identifiée

**→ fp-qubit-design** :
- Domaines différents (petites molécules vs protéines), pas de connexion évidente

---

## Synthèse : Connexions Réalistes et Actionnables

### Axe 1 : Atlas Qubits → ising-life-lab (Prêt à Activer)

**Action immédiate** :
1. Télécharger `atlas_fp_optical_v2_2_curated.csv` (180 systèmes) depuis GitHub
2. Placer dans `ising-life-lab/data/atlas_optical/`
3. Utiliser `isinglab.data_bridge.load_optical_systems(tier="curated")`
4. Créer cartographie design space (Projet P1 v8.0)

**Livrable** : `qubit_design_space_v1.csv` avec tags (room_temp_viable, bio_adjacent, cmos_friendly)

### Axe 2 : Atlas → fp-qubit-design (Migration Données)

**Action moyen terme** :
1. Explorer structure fp-qubit-design (clone local)
2. Identifier format d'entrée attendu
3. Préparer migration Atlas v1.2 (22 systèmes) → v2.2.2 curated (180 systèmes)
4. Ajouter filtres physiques d'isinglab pour valider designs

**Livrable potentiel** : Pipeline ML augmenté avec 8× plus de données + filtres robustesse

### Axe 3 : ising-life-lab Métriques → arrest-molecules (Conceptuel)

**Action long terme** :
1. Explorer structure arrest-molecules (clone local)
2. Identifier si des modèles de paysages énergétiques existent
3. Appliquer métriques d'attracteurs d'isinglab (stability, basin) aux états d'arrêt moléculaires
4. Tester si heuristiques CA/Ising capturent aspects de régulation

**Livrable potentiel** : Analyse stabilité états d'arrêt vs oscillations dans réseaux moléculaires

### Axe 4 : Écosystème Global (Vision Long Terme)

**Bridge conceptuel** (mentionné dans README Atlas) :
```
Superconducting circuits (Nobel 2025)
    ↓
Artificial quantum systems (Atlas)
    ↓
Quantum-inspired biological computation (ising-life-lab)
    ↓
Molecular design (fp-qubit-design, arrest-molecules)
```

**Attention** : Ce bridge est **conceptuel**, pas technique. Ne pas extrapoler au-delà de ce que les données permettent.

---

## Données Manquantes & Actions Prioritaires

### Immédiatement Nécessaire (Projet P1)

✅ **Télécharger CSV Atlas curated** :
```bash
# Dans ising-life-lab/
wget -P data/atlas_optical/ https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology/raw/main/data/processed/atlas_fp_optical_v2_2_curated.csv
```

### Exploration Nécessaire (Moyen Terme)

🔍 **Clone fp-qubit-design** :
- Comprendre structure ML pipeline
- Identifier opportunités d'augmentation avec Atlas v2.2.2

🔍 **Clone arrest-molecules** :
- Télécharger dataset Zenodo (DOI: 10.5281/zenodo.17420685)
- Comprendre format des 44 predictions
- Évaluer applicabilité métriques isinglab

### Risques & Limitations

⚠️ **Colonnes T1/T2 manquantes dans optical systems** :
- Protéines fluorescentes (Atlas optical) ne mesurent PAS T1/T2 (temps de cohérence quantique)
- Ces métriques sont pertinentes pour spins/NV centers (datasets non-optical)
- **Action** : Adapter schéma de qubit_design_space_v1.csv selon données réellement disponibles

⚠️ **Datasets non-optical non accessibles actuellement** :
- Mentions de NV centers, SiC defects, spins nucléaires dans README Atlas
- Pas de CSV correspondants identifiés dans structure GitHub (ou staging area non publique ?)
- **Action** : Se concentrer sur Tier 1 optical (180 systèmes) pour P1, explorer non-optical en P2

---

## Recommandations pour v8.0

### Priorité 1 : Projet P1 — Biological Qubits Design Map (ACTIONNABLE IMMÉDIATEMENT)

**Prérequis** : Télécharger atlas_fp_optical_v2_2_curated.csv  
**Durée estimée** : 2-3h  
**Livrable** : `qubit_design_space_v1.csv` + `DESIGN_SPACE_v1_REPORT.md`

### Priorité 2 : Exploration fp-qubit-design (MOYEN TERME)

**Prérequis** : Clone local du repo  
**Durée estimée** : 3-4h  
**Livrable** : Document d'analyse structure + plan migration Atlas v2.2.2

### Priorité 3 : Exploration arrest-molecules (LONG TERME)

**Prérequis** : Clone local + dataset Zenodo  
**Durée estimée** : 4-5h  
**Livrable** : Analyse applicabilité métriques isinglab à paysages moléculaires

---

## Conclusion

Nous disposons d'un écosystème cohérent mais **partiellement connecté** :

✅ **ising-life-lab** : Boîte à outils robuste, data bridge prêt, leçons méthodologiques précieuses  
✅ **Quantum-Sensors-Qubits-in-Biology** : Dataset riche (180 systèmes curated), bien documenté, accessible  
🔍 **fp-qubit-design** : Mentionné, connexion claire avec Atlas, détails à explorer  
🔍 **arrest-molecules** : Mentionné, connexion conceptuelle, structure technique inconnue

**Stratégie v8.0** : Commencer par l'Axe 1 (Atlas → ising-life-lab), qui est **immédiatement actionnable** et fournira une base solide pour les axes 2 et 3.

**Pas de spéculation** : Toute connexion non vérifiable techniquement est marquée "conceptuelle" et ne sera pas utilisée pour justifier des implémentations sans validation.

---

**Document vivant** — Sera mis à jour au fur et à mesure de l'exploration des projets fp-qubit-design et arrest-molecules.

**Prochaine étape** : Lancer Projet P1 (Biological Qubits Design Map v1).

