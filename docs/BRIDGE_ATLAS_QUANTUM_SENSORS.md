# Bridge Atlas Quantum Sensors

**Projet** : Quantum-Sensors-Qubits-in-Biology  
**GitHub** : https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology  
**Statut** : ✅ **Opérationnel** (180 systèmes Tier 1 curated disponibles)

---

## Vue d'Ensemble

**Atlas** catalogue des systèmes quantiques biologiques et condensés (protéines fluorescentes, NV centers, spins, radical pairs) avec métadonnées expérimentales.

**Integration ising-life-lab** : Lecture seule des CSV Atlas pour analyse, filtrage, scoring via design_space/.

---

## Format Données

### Tier 1 Curated (Optical, 180 systèmes)

**Fichier** : `atlas_fp_optical_v2_2_curated.csv`  
**Téléchargement** :
```bash
Invoke-WebRequest -Uri 'https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology/raw/main/data/processed/atlas_fp_optical_v2_2_curated.csv' -OutFile 'data/atlas_optical/atlas_fp_optical_v2_2_curated.csv'
```

**Colonnes clés** :

| Colonne | Type | Description | Exemple |
|---------|------|-------------|---------|
| `SystemID` | str | Identifiant unique | FP_0056 |
| `protein_name` | str | Nom protéine | jGCaMP8s |
| `family` | str | Catégorie fonctionnelle | Calcium |
| `is_biosensor` | bool/float | Biosenseur (1.0) ou passif (0.0) | 1.0 |
| `contrast_value` | float | Contraste mesuré | 90.0 |
| `contrast_unit` | str | Unité contraste | fold |
| `contrast_normalized` | float | Contraste normalisé | 90.0 |
| `quality_tier` | str | Niveau maturité | A, B, C, unknown |
| `context` | str | Contexte expérimental | in_vivo(neurons) |
| `temperature_K` | float | Température (Kelvin) | 298.0 |
| `pH` | float | pH | 7.4 |
| `doi` | str | Référence publication | 10.1126/science.abd2659 |
| `pmcid` | str | PubMed Central ID | PMC8654344 |
| `year` | int | Année publication | 2019 |
| `excitation_nm` | float | Excitation (nm) | 488.0 |
| `emission_nm` | float | Émission (nm) | 510.0 |
| `stokes_shift_nm` | float | Décalage Stokes (nm) | 22.0 |
| `method` | str | Type de lecture | fluorescence, FRET |
| `assay` | str | Type d'essai | calcium_imaging, voltage_imaging |

**Note** : Certaines colonnes peuvent être NaN (ex: excitation_nm, emission_nm pour certains systèmes).

### Tiers Autres (À explorer)

| Tier | Systèmes | Statut | Usage |
|------|----------|--------|-------|
| **Tier 1 (curated)** | 180 | ✅ Complet | Modélisation, analyse |
| Tier 2 (candidates) | 13 | 🟡 Incomplet | Curation manuelle |
| Tier 3 (unknown) | 103 | 🔴 Placeholder | Transparence uniquement |
| **Mixed (all)** | 296 | ⚠️ Mixte | Non recommandé pour ML |

### Non-Optical (À venir)

**Systèmes mentionnés** (pas encore téléchargés) :
- NV centers (diamant)
- SiC defects (silicon carbide)
- Nuclear spins (13C, 31P, 14N, 29Si)
- Radical pairs (cryptochrome, photolyase)
- Many-body quantum systems

**Action nécessaire** : Explorer structure GitHub Atlas (staging area ?), ou contacter auteur.

---

## Usage avec ising-life-lab

### 1. Charger Atlas avec Loaders

```python
from design_space.loaders import load_atlas_optical

# Charger Tier 1 curated (180 systèmes)
df_atlas = load_atlas_optical(tier="curated")

print(f"Loaded {len(df_atlas)} systems")
print(df_atlas[['SystemID', 'protein_name', 'family', 'contrast_normalized']].head())
```

### 2. Standardiser Schéma

```python
from design_space.loaders import convert_atlas_to_design_space

# Convertir vers schéma design_space standardisé
df_std = convert_atlas_to_design_space(df_atlas, platform="fluorescent_protein")

# Vérifier colonnes standardisées
print(df_std.columns.tolist())
# → ['system_id', 'protein_name', 'family', 'temp_k', 'contrast_normalized', 'platform', ...]
```

### 3. Filtrer & Ranker avec Selector

```python
from design_space.selector import (
    rank_by_integrability,
    filter_by_family,
    list_high_contrast_candidates
)

# Filtrer calcium sensors
calcium = filter_by_family(df_std, "Calcium")
print(f"{len(calcium)} calcium sensors")

# Top 5 par intégrabilité
top5_calcium = rank_by_integrability(calcium, top_n=5)
print(top5_calcium[['protein_name', 'contrast_normalized', 'integration_level']])

# High contrast (≥10×)
high_contrast = list_high_contrast_candidates(df_std, min_contrast=10.0)
print(f"{len(high_contrast)} high contrast systems")
```

### 4. Pipeline Complet (Exemple)

```python
from design_space.loaders import load_atlas_optical, validate_design_space_schema
from design_space.selector import rank_by_integrability, get_system_by_id

# 1. Charger Atlas
df = load_atlas_optical(tier="curated")

# 2. Valider
from design_space.loaders import validate_design_space_schema
report = validate_design_space_schema(df, strict=False)
print(report.summary())

# 3. Ranker
top10 = rank_by_integrability(df, top_n=10)

# 4. Sélectionner candidat
best_id = top10['system_id'].iloc[0]
best_system = get_system_by_id(df, best_id)

print(f"\nCandid at recommandé:")
print(f"  Protéine: {best_system['protein_name']}")
print(f"  Famille: {best_system['family']}")
print(f"  Contraste: {best_system['contrast_normalized']:.1f}×")
print(f"  DOI: {best_system['doi']}")
```

---

## Output Attendu

### Exemple Output : Top 5 Calcium Sensors

```
protein_name  family   contrast_normalized  integration_level  integrability_score
jGCaMP8s      Calcium                 90.0            in_vivo                  6.0
jGCaMP8f      Calcium                 78.0            in_vivo                  6.0
jGCaMP7s      Calcium                 50.0            in_vivo                  6.0
jGCaMP7f      Calcium                 45.0            in_vivo                  6.0
XCaMP-Gs      Calcium                 45.0            in_vivo                  6.0
```

---

## Limitations & Gaps Identifiés

### Colonnes Manquantes (Tier 1 Optical)

❌ **Photostabilité** (photobleaching rate) : Absent  
❌ **Brillance absolue** (quantum_yield × extinction_coeff) : Absent  
❌ **Maturation time** : Absent  
❌ **Données stress-test** (contraste vs pH, température) : Absent

**Action** : Enrichir en minant littérature (PubMed, suppléments DOI).

### Colonnes Optiques Parfois Manquantes

⚠️ **excitation_nm**, **emission_nm** : Quelques NaN (ex: dLight1.3b, iGluSnFR-A184S)

**Action** : Compléter ou accepter NaN, documenter clairement.

### Datasets Non-Optical

❌ **NV centers, SiC, spins nucléaires** : Pas de CSV disponibles localement

**Action** : Explorer GitHub Atlas, contacter auteur, ou attendre release future.

---

## Provenance & Citation

**Source** : Quantum-Sensors-Qubits-in-Biology v2.2.2  
**Auteur** : Mythmaker28  
**Licence** : CC BY 4.0 (données), MIT (code)

**Citation (Tier 1 curated)** :
```bibtex
@dataset{biological_qubits_atlas_v2_2_curated,
  title  = {Biological Qubits \& Quantum Sensors Atlas v2.2.2 (Curated)},
  author = {Mythmaker28},
  year   = {2025},
  systems = {180},
  url    = {https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology}
}
```

**Citation manuscrit Frontiers (v1.2.1, 66 systèmes)** :  
DOI: 10.5281/zenodo.17420604

---

## Roadmap Integration

### ✅ v8.0-v8.2 (Complété / En cours)

- [x] Téléchargement Atlas Tier 1 curated (180 systèmes)
- [x] Loaders (`load_atlas_optical`, `convert_atlas_to_design_space`)
- [x] Validation schéma (`validate_design_space_schema`)
- [x] Module selector (10 fonctions filtrage/ranking)
- [x] Rapport d'analyse (DESIGN_SPACE_v1_REPORT.md)

### 🔄 v8.3 (Prochain)

- [ ] Enrichissement colonnes (photostabilité, brillance, stress-test data)
- [ ] functional_score adapté biosenseurs (validation vs baseline)
- [ ] Exploration datasets non-optical (NV centers, spins)

### 🔮 v8.4+ (Futur)

- [ ] Dashboard interactif (scatter plots, filtres dynamiques)
- [ ] Pareto multi-objectifs (contraste vs robustesse vs coût)
- [ ] Modèles conformationnels (PDB/AlphaFold, ΔΔG)

---

## Contact & Contribution

**Issues Atlas** : https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology/issues  
**Issues ising-life-lab** : (votre repo)

**Suggestions** :
- Nouvelles colonnes utiles (ex: photostabilité)
- Datasets non-optical à intégrer
- Améliorations loaders/selector

---

**Bridge Atlas ↔ ising-life-lab : Opérationnel ✅**

**180 systèmes disponibles, analysables, scorables.**


