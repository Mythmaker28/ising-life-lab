# Data Directory - Biological Qubits Atlas Integration

**Ce répertoire est destiné à recevoir les CSV exportés du [Biological Qubits Atlas](https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology).**

## Structure Recommandée

```
data/
├── atlas_optical/
│   ├── atlas_fp_optical_v2_2.csv              # Full dataset (296 systems, mixed)
│   ├── atlas_fp_optical_v2_2_curated.csv      # RECOMMENDED: Tier 1 only (180 systems)
│   ├── atlas_fp_optical_v2_2_candidates.csv   # Tier 2 (13 systems, incomplete)
│   └── atlas_fp_optical_v2_2_unknown.csv      # Tier 3 (103 systems, placeholder)
│
└── atlas_nonoptical/
    ├── spin_qubit_candidates.csv              # NV centers, SiC defects, etc.
    ├── nuclear_spin_candidates.csv            # 13C, 31P, 14N, 29Si, etc.
    ├── radical_pair_candidates.csv            # Cryptochrome, photolyase, etc.
    └── candidates_needing_curation.csv        # FPbase harvest (844 systems)
```

## Comment Obtenir les Fichiers

### Option 1: Téléchargement Direct (Recommandé pour Tier 1 Curated)

```bash
# Optical systems (curated, modeling-ready)
wget -P data/atlas_optical/ https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology/raw/main/data/processed/atlas_fp_optical_v2_2_curated.csv
```

### Option 2: Clone du Repo Atlas

```bash
# Clone dans un répertoire temporaire
git clone https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology.git /tmp/atlas

# Copie des fichiers pertinents
cp /tmp/atlas/data/processed/atlas_fp_optical_v2_2*.csv data/atlas_optical/
cp /tmp/atlas/data/staging/*_candidates.csv data/atlas_nonoptical/

# Nettoyage
rm -rf /tmp/atlas
```

### Option 3: Copie Manuelle

Si vous avez déjà un clone local de l'Atlas, copiez simplement les CSV nécessaires :

```bash
cp /path/to/Quantum-Sensors-Qubits-in-Biology/data/processed/*.csv data/atlas_optical/
cp /path/to/Quantum-Sensors-Qubits-in-Biology/data/staging/*.csv data/atlas_nonoptical/
```

## Utilisation dans Ising Life Lab

Une fois les CSV en place, utilisez le data bridge :

```python
from isinglab.data_bridge import load_optical_systems, load_spin_qubits, load_nuclear_spins
from isinglab.data_bridge import map_system_properties

# Charger les systèmes optiques (Tier 1 recommandé)
optical = load_optical_systems(tier="curated")  # 180 systems

# Charger les systèmes non-optiques
spins = load_spin_qubits()
nuclear = load_nuclear_spins()

# Mapper les propriétés (heuristique déterministe)
optical_mapped = map_system_properties(optical)

print(f"Loaded {len(optical_mapped)} optical systems")
print(optical_mapped[['protein_name', 'modality', 'coherence_class']].head())
```

## Notes Importantes

1. **READ-ONLY** : Ising Life Lab ne modifie JAMAIS les CSV source
2. **Data Tiers** : Privilégiez `atlas_fp_optical_v2_2_curated.csv` pour modélisation/ML
3. **Missing Data** : Si un CSV n'existe pas, `atlas_loader.py` lève une erreur claire
4. **Schemas** : Les loaders sont tolérants aux colonnes manquantes (→ `unknown`)

## Provenance & Citation

**Atlas Source** : [Mythmaker28/Quantum-Sensors-Qubits-in-Biology](https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology)

**Citation (Curated v2.2.2)** :
```bibtex
@dataset{biological_qubits_atlas_v2_2_curated,
  title  = {Biological Qubits \& Quantum Sensors Atlas v2.2.2 (Curated)},
  author = {Mythmaker28},
  year   = {2025},
  systems = {180},
  url    = {https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology}
}
```

**License Atlas** : CC BY 4.0 (data), MIT (code)

