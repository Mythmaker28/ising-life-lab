# Guide d'Intégration : Biological Qubits Atlas ↔ Ising Life Lab

**Objectif** : Utiliser les données réelles du [Biological Qubits Atlas](https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology) pour guider l'exploration de régimes CA/Ising.

**⚠️ DISCLAIMER CRITIQUE** : Les mappings Atlas → CA/Ising sont des **analogies conceptuelles heuristiques**, PAS des prédictions quantiques. Voir `docs/CONNECTIONS.md` pour les limites fondamentales.

---

## 📊 Types de Systèmes Supportés

### 1. Systèmes Optiques (Fluorescent Proteins)

**Source Atlas** : `data/processed/atlas_fp_optical_v2_2_curated.csv`  
**Nombre** : 180 systèmes curés (Tier 1)  
**Exemples** : GCaMP8s, ASAP4e, dLight1.4, iGluSnFR, etc.

**Propriétés mappées** :
- `modality` : optical
- `temperature_regime` : physiological (270-320 K pour la plupart)
- `coherence_class` : basé sur `contrast_normalized` (proxy heuristique)

**Limitation** : Les FPs n'ont pas de T₂ quantique mesuré. On utilise le contraste comme proxy de "stabilité de signal".

### 2. Spin Qubits (Solid-State Defects)

**Source Atlas** : `data/staging/spin_qubit_candidates.csv`  
**Nombre** : ~10 systèmes  
**Exemples** : NV⁻ center (diamond), VSi (4H-SiC), SiV⁻, P1 center, etc.

**Propriétés mappées** :
- `modality` : spin
- `temperature_regime` : variable (cryogenic → room temp)
- `coherence_class` : basé sur `T2_microseconds` (vraies mesures quantiques)

**Avantage** : T₂ quantique réel disponible (1-600,000 µs selon système).

### 3. Nuclear Spins

**Source Atlas** : `data/staging/nuclear_spin_candidates.csv`  
**Nombre** : ~8 systèmes  
**Exemples** : ¹³C (diamond), ³¹P (silicon), ¹⁴N (NV intrinsic), ²⁹Si, etc.

**Propriétés mappées** :
- `modality` : nuclear
- `temperature_regime` : souvent cryogenic (2-4 K), quelques room temp
- `coherence_class` : basé sur `T2_milliseconds` (très longues cohérences)

**Caractéristique** : Cohérences record (jusqu'à 30 s pour ³¹P).

### 4. Radical Pairs

**Source Atlas** : `data/staging/radical_pair_candidates.csv`  
**Nombre** : ~8 systèmes  
**Exemples** : Cryptochrome 4, DNA photolyase, Photosystem II, etc.

**Propriétés mappées** :
- `modality` : radical_pair
- `temperature_regime` : physiological (298 K typiquement)
- `coherence_class` : basé sur `timescale_ns` (échelles nanoseconde)

**Spécificité** : Sensibles aux champs magnétiques (magnetic field effect).

---

## 🔧 Installation & Setup

### 1. Obtenir les CSV Atlas

#### Option A: Téléchargement Direct (Recommandé)

```bash
# Créer la structure
mkdir -p data/atlas_optical data/atlas_nonoptical

# Optical systems (Tier 1 curated - RECOMMANDÉ)
wget -P data/atlas_optical/ https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology/raw/main/data/processed/atlas_fp_optical_v2_2_curated.csv

# Non-optical systems (candidates)
wget -P data/atlas_nonoptical/ https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology/raw/main/data/staging/spin_qubit_candidates.csv
wget -P data/atlas_nonoptical/ https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology/raw/main/data/staging/nuclear_spin_candidates.csv
wget -P data/atlas_nonoptical/ https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology/raw/main/data/staging/radical_pair_candidates.csv
```

#### Option B: Clone Atlas Repo

```bash
# Clone temporaire
git clone https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology.git /tmp/atlas

# Copie sélective
cp /tmp/atlas/data/processed/atlas_fp_optical_v2_2_curated.csv data/atlas_optical/
cp /tmp/atlas/data/staging/*_candidates.csv data/atlas_nonoptical/

# Cleanup
rm -rf /tmp/atlas
```

### 2. Vérifier Installation

```python
from isinglab.data_bridge import list_available_datasets

datasets = list_available_datasets()
print(f"Available datasets: {datasets}")
```

---

## 🚀 Utilisation (Workflow Complet)

### Workflow 1: Exploration Simple

```python
from isinglab.data_bridge import load_optical_systems, map_system_properties

# 1. Charger systèmes optiques (READ-ONLY)
df = load_optical_systems(tier="curated")

# 2. Mapper propriétés
df_mapped = map_system_properties(df)

# 3. Explorer
print(df_mapped[['protein_name', 'family', 'modality', 'coherence_class']].head(10))
print(df_mapped['coherence_class'].value_counts())
```

### Workflow 2: Génération de Profils Cibles

```python
from isinglab.data_bridge import load_optical_systems, map_system_properties, generate_system_profiles
from isinglab.mapping_profiles import get_target_profile_for_system

# 1. Charger & mapper
df = load_optical_systems(tier="curated")
df_mapped = map_system_properties(df)

# 2. Sélectionner un système d'intérêt (ex: GCaMP8s)
gcamp8s = df_mapped[df_mapped['protein_name'] == 'jGCaMP8s'].iloc[0]

# 3. Générer profil cible CA/Ising
profile = get_target_profile_for_system(
    modality=gcamp8s['modality'],
    temperature_regime=gcamp8s['temperature_regime'],
    coherence_class=gcamp8s['coherence_class']
)

print("Target CA/Ising profile for jGCaMP8s:")
print(f"  Suggested regimes: {profile['suggested_regimes']}")
print(f"  Target edge_score: {profile['target_metrics']['edge_score']}")
print(f"  Target memory_score: {profile['target_metrics']['memory_score']}")
print(f"  Rationale: {profile['rationale']}")
```

### Workflow 3: Regime Search (Complet)

```python
from isinglab.data_bridge import load_optical_systems, map_system_properties
from isinglab.mapping_profiles import get_target_profile_for_system
from isinglab.pipelines import run_regime_search

# 1. Charger systèmes
df = load_optical_systems(tier="curated")
df_mapped = map_system_properties(df)

# 2. Filtrer systèmes à longue cohérence (high contrast)
long_coherence = df_mapped[df_mapped['contrast_normalized'] > 30.0]
print(f"Found {len(long_coherence)} high-contrast systems (proxy for stability)")

# 3. Générer profil typique
profile = get_target_profile_for_system(
    modality="optical",
    temperature_regime="physiological",
    coherence_class="long"
)

# 4. Rechercher régimes CA/Ising
results_df, top_rules = run_regime_search(
    target_profile=profile,
    rule_pool=list(range(0, 256)),  # Full elementary CA space
    ca_type="elementary",
    grid_size=100,
    steps=200,
    seeds_per_rule=3,
    base_seed=42,
    output_dir="outputs/optical_long_coherence"
)

# 5. Analyser résultats
print(f"\\nEvaluated {len(results_df)} rules")
print(f"\\nTop 5 matching rules:")
for i, rule_data in enumerate(top_rules[:5]):
    print(f"  {i+1}. Rule {rule_data['rule']:3d} : "
          f"edge={rule_data['edge_score']:.3f}, "
          f"memory={rule_data['memory_score']:.3f}, "
          f"match_score={rule_data['match_score']:.3f}")

# 6. Exports disponibles
print(f"\\nResults exported to:")
print(f"  - outputs/optical_long_coherence/regime_search_results.csv")
print(f"  - outputs/optical_long_coherence/top_rules.json")
```

### Workflow 4: Batch Analysis (Multi-Systèmes)

```python
from isinglab.data_bridge import load_optical_systems, map_system_properties
from isinglab.mapping_profiles import get_target_profile_for_system
from isinglab.pipelines import batch_regime_search

# 1. Charger et grouper par famille
df = load_optical_systems(tier="curated")
df_mapped = map_system_properties(df)

families_of_interest = ['Calcium', 'Voltage', 'Dopamine']

profiles = []
for family in families_of_interest:
    family_systems = df_mapped[df_mapped['family'] == family]
    
    if len(family_systems) > 0:
        # Utiliser le système avec le plus haut contraste
        top_system = family_systems.nlargest(1, 'contrast_normalized').iloc[0]
        
        profile = get_target_profile_for_system(
            modality=top_system['modality'],
            temperature_regime=top_system['temperature_regime'],
            coherence_class=top_system['coherence_class']
        )
        profile['system_id'] = f"{family}_{top_system['protein_name']}"
        profiles.append(profile)

# 2. Batch search
results = batch_regime_search(
    systems_profiles=profiles,
    rule_pool=list(range(0, 100)),  # Quick scan
    grid_size=50,
    steps=100,
    seeds_per_rule=2,
    output_dir="outputs/batch_family_comparison"
)

print(f"\\nBatch search completed for {len(profiles)} families")
print("Results in: outputs/batch_family_comparison/")
```

---

## 🔬 Systèmes Non-Optiques (Spin, Nuclear, Radical Pair)

### Spin Qubits

```python
from isinglab.data_bridge import load_spin_qubits, map_system_properties
from isinglab.mapping_profiles import get_target_profile_for_system

# Charger NV centers, SiC defects, etc.
spins = load_spin_qubits()
spins_mapped = map_system_properties(spins)

# NV center à température ambiante
nv_room_temp = spins_mapped[spins_mapped['label'].str.contains('room temp', na=False)].iloc[0]

profile_nv = get_target_profile_for_system(
    modality="spin",
    temperature_regime="physiological",
    coherence_class="long"  # NV- a T₂ ~ 1.8 ms à 298 K
)

print(f"NV center profile: {profile_nv['suggested_regimes']}")
```

### Nuclear Spins

```python
from isinglab.data_bridge import load_nuclear_spins

nuclear = load_nuclear_spins()
nuclear_mapped = map_system_properties(nuclear)

# 31P in silicon: T₂ = 30 s (record)
p31 = nuclear_mapped[nuclear_mapped['nucleus'] == '31P'].iloc[0]

print(f"31P coherence class: {p31['coherence_class']}")  # "record"
print(f"Temperature regime: {p31['temperature_regime']}")  # "cryogenic"

# Profil cible: stable attractors, très haute mémoire
profile_p31 = get_target_profile_for_system(
    modality="nuclear",
    temperature_regime="cryogenic",
    coherence_class="record"
)

print(f"Suggested CA regimes: {profile_p31['suggested_regimes']}")
# → ["stable_attractors", "limit_cycles", "edge_of_chaos"]
```

### Radical Pairs

```python
from isinglab.data_bridge import load_radical_pairs

radical = load_radical_pairs()
radical_mapped = map_system_properties(radical)

# Cryptochrome 4 (bird magnetoreception)
cry4 = radical_mapped[radical_mapped['protein_or_complex'].str.contains('Cryptochrome 4', na=False)].iloc[0]

profile_cry4 = get_target_profile_for_system(
    modality="radical_pair",
    temperature_regime="physiological",
    coherence_class="medium"  # ns-µs timescales
)

print(f"Cryptochrome 4 target regimes: {profile_cry4['suggested_regimes']}")
```

---

## 📈 Analyse Cross-Modality (Comparaison)

Comparer les profils de régimes suggérés pour différentes classes de systèmes :

```python
from isinglab.data_bridge import (
    load_optical_systems,
    load_spin_qubits,
    load_nuclear_spins,
    map_system_properties
)
from isinglab.mapping_profiles import get_target_profile_for_system
import pandas as pd

# Charger tous les types
optical = map_system_properties(load_optical_systems(tier="curated"))
spins = map_system_properties(load_spin_qubits())
nuclear = map_system_properties(load_nuclear_spins())

# Profils représentatifs
profiles_comparison = []

# Optical: GCaMP8s (calcium sensor, très haut contraste)
if len(optical) > 0:
    gcamp = optical[optical['protein_name'] == 'jGCaMP8s']
    if len(gcamp) > 0:
        profile = get_target_profile_for_system("optical", "physiological", "long")
        profile['system_example'] = "jGCaMP8s (Calcium, 90x contrast)"
        profiles_comparison.append(profile)

# Spin: NV center (room temp, ms coherence)
if len(spins) > 0:
    nv = spins[spins['label'].str.contains('NV', na=False)]
    if len(nv) > 0:
        profile = get_target_profile_for_system("spin", "physiological", "long")
        profile['system_example'] = "NV- center (T₂ ~ 1.8 ms)"
        profiles_comparison.append(profile)

# Nuclear: 31P (cryogenic, record coherence)
if len(nuclear) > 0:
    p31 = nuclear[nuclear['nucleus'] == '31P']
    if len(p31) > 0:
        profile = get_target_profile_for_system("nuclear", "cryogenic", "record")
        profile['system_example'] = "31P in silicon (T₂ ~ 30 s)"
        profiles_comparison.append(profile)

# Comparaison
print("\\n" + "=" * 80)
print("CROSS-MODALITY COMPARISON")
print("=" * 80)
for i, prof in enumerate(profiles_comparison):
    print(f"\\n{i+1}. {prof['system_example']}")
    print(f"   Suggested regimes: {', '.join(prof['suggested_regimes'])}")
    print(f"   Target edge_score: {prof['target_metrics']['edge_score']}")
    print(f"   Target memory_score: {prof['target_metrics']['memory_score']}")
    print(f"   Rationale: {prof['rationale'][:80]}...")
```

**Insight attendu** :
- Optical long coherence + Nuclear record → Profils similaires (high memory, stable attractors)
- Radical pairs (short timescale) → Profils différents (higher entropy, mixing)

---

## 🤖 Utilisation par Agents IA

### Agent Pattern: Systematic Exploration

```python
from isinglab.data_bridge import load_optical_systems, map_system_properties
from isinglab.mapping_profiles import get_target_profile_for_system
from isinglab.pipelines import run_regime_search
import json

def ai_agent_explore_atlas():
    """
    Agent IA autonome pour explorer Atlas → CA/Ising mappings.
    """
    # 1. Load & map
    df = load_optical_systems(tier="curated")
    df_mapped = map_system_properties(df)
    
    # 2. Group by family
    families = df_mapped['family'].unique()
    
    all_results = {}
    
    for family in families:
        if family == "Unknown":
            continue
        
        # Get representative system (highest contrast)
        family_systems = df_mapped[df_mapped['family'] == family]
        rep_system = family_systems.nlargest(1, 'contrast_normalized').iloc[0]
        
        # Generate profile
        profile = get_target_profile_for_system(
            modality=rep_system['modality'],
            temperature_regime=rep_system['temperature_regime'],
            coherence_class=rep_system['coherence_class']
        )
        
        # Search CA space (quick)
        results_df, top_rules = run_regime_search(
            target_profile=profile,
            rule_pool=list(range(0, 256)),
            grid_size=50,
            steps=100,
            seeds_per_rule=2,
            base_seed=42 + hash(family) % 1000,  # Deterministic per family
            output_dir=None  # Don't save (agent handles storage)
        )
        
        all_results[family] = {
            "representative_system": rep_system['protein_name'],
            "top_rule": top_rules[0]['rule'],
            "top_edge_score": top_rules[0]['edge_score'],
            "top_memory_score": top_rules[0]['memory_score'],
            "profile": profile
        }
    
    # 3. Agent stores results
    with open("outputs/agent_atlas_exploration.json", 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    return all_results

# Run agent
if __name__ == "__main__":
    results = ai_agent_explore_atlas()
    print(f"Agent explored {len(results)} families")
    print("Results: outputs/agent_atlas_exploration.json")
```

---

## 📊 Schemas Attendus

### Optical Systems (Curated)

Colonnes clés :
- `SystemID` : Identifiant unique (FP_0001, etc.)
- `protein_name` : Nom canonique (GCaMP8s, ASAP4e, etc.)
- `family` : Calcium | Voltage | Dopamine | Glutamate | pH | H2O2 | cAMP | GFP-like | RFP | etc.
- `contrast_normalized` : Contraste normalisé (fold-change ou ΔF/F₀ + 1)
- `temperature_K` : Température opératoire (typiquement 298-310 K)
- `doi` : DOI de la source primaire

### Spin Qubits

Colonnes clés :
- `id` : SPIN_NV_001, etc.
- `label` : Description textuelle
- `system_type` : NV_center | SiC_defect | SiV_center | P1_center | etc.
- `T2_microseconds` : Temps de cohérence T₂ (µs)
- `temperature_K` : Température de mesure
- `measurement_method` : ODMR | pulsed_ESR | etc.

### Nuclear Spins

Colonnes clés :
- `id` : NUC_13C_001, etc.
- `nucleus` : 13C | 31P | 14N | 29Si | 15N | 1H
- `system_type` : diamond_NV_coupled | phosphorus_donor | silicon_bulk | etc.
- `T2_milliseconds` : Temps de cohérence T₂ (ms)
- `temperature_K` : Température

### Radical Pairs

Colonnes clés :
- `id` : RP_CRY_001, etc.
- `protein_or_complex` : Cryptochrome 4 | DNA photolyase | etc.
- `timescale_ns` : Échelle de temps des dynamiques (ns)
- `field_sensitivity_uT` : Sensibilité au champ magnétique (µT)
- `temperature_K` : Température

---

## ⚠️ Limitations & Interprétation

### Ce que les Mappings FONT

✅ **Structurer l'exploration** : Guider une IA pour chercher des régimes CA/Ising pertinents  
✅ **Analogies qualitatives** : "Longue cohérence → haute mémoire, stabilité"  
✅ **Heuristiques traçables** : Toutes les règles dans le code source  

### Ce que les Mappings NE FONT PAS

❌ **Prédire T₂ quantique** à partir de métriques CA/Ising  
❌ **Modéliser le comportement quantique réel** des systèmes  
❌ **Remplacer les simulations quantiques** (DFT, tensor networks, etc.)  

### Validité Scientifique

**Question** : "Est-ce que `edge_score` prédit la qualité d'un qubit biologique ?"  
**Réponse** : **NON**. Les métriques CA/Ising capturent des propriétés dynamiques **classiques**. Elles peuvent *inspirer* des hypothèses (ex: "systèmes edge-of-chaos pourraient être computationnels"), mais nécessitent validation expérimentale.

**Question** : "Pourquoi faire ça alors ?"  
**Réponse** : Pour **générer des hypothèses structurées** et **explorer l'espace de design** de manière systématique. C'est un outil d'exploration, pas de prédiction.

---

## 🔗 Références

- **Atlas Source** : [Mythmaker28/Quantum-Sensors-Qubits-in-Biology](https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology)
- **Data Tiers** : Voir `docs/DATA_TIERS.md` dans l'Atlas
- **Theoretical Foundation** : `docs/THEORETICAL_FOUNDATION.md` (dans ce repo)
- **Connections & Disclaimers** : `docs/CONNECTIONS.md`

---

## 📝 Citation

Si vous utilisez l'intégration Atlas → Ising Life Lab dans vos travaux :

```bibtex
@software{ising_life_lab_2025,
  title = {Ising Life Lab: CA/Ising Exploration Framework with Biological Qubits Atlas Integration},
  author = {Mythmaker28},
  year = {2025},
  url = {https://github.com/Mythmaker28/ising-life-lab}
}

@dataset{biological_qubits_atlas_v2_2_curated,
  title = {Biological Qubits \& Quantum Sensors Atlas v2.2.2 (Curated)},
  author = {Mythmaker28},
  year = {2025},
  systems = {180},
  url = {https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology}
}
```

---

**Dernière mise à jour** : 2025-11-10  
**Version** : vFINAL (post-merge Atlas integration)

