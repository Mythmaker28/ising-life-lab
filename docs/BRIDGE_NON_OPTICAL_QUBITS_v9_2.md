# Bridge Non-Optical Qubits (NV, Spins, Radical Pairs)

**Sources** : Quantum-Sensors-Qubits-in-Biology (datasets staging)  
**Statut** : 🟡 **Spec Prête** (Loader exists, CSV absents)

---

## Vue d'Ensemble

**Systèmes non-optical** couvrent qubits/capteurs quantiques non fluorescents :
- **NV centers** (diamant) : Temps cohérence T1/T2, température opération, ODMR
- **SiC defects** (silicon carbide) : Spin defects, biocompatibilité
- **Nuclear spins** (13C, 31P, 14N, 29Si) : Hyperfine coupling, sensibilité
- **Radical pairs** (cryptochrome, photolyase) : Magnétosensing, yield quantique

**Différence vs optical** : Métriques T1/T2 (cohérence quantique) au lieu de contrast/fluorescence.

---

## Format Attendu (Inspiré Littérature)

### Colonnes Minimales

| Colonne | Type | Description | Référence |
|---------|------|-------------|-----------|
| `system_id` | str | Identifiant unique | Standard |
| `qubit_type` | str | NV_center, SiC_defect, nuclear_spin, radical_pair | Catégories |
| `host_material` | str | Diamond, SiC, protein (cryptochrome), etc. | Matériau hôte |
| `temp_k` | float | Température opération/mesure | Standard |
| `T1_ms` | float | Temps relaxation (ms) | Quantum coherence |
| `T2_us` | float | Temps déphasage (µs) | Quantum coherence |
| `readout_type` | str | ODMR, ESR, fluorescence, magnetometry | Méthode détection |
| `integration_level` | str | in_vivo, in_vitro, solid_state, demonstrated | Contexte |
| `bio_compatible` | bool | Biocompatibilité démontrée/potentielle | Application |

### Colonnes Optionnelles

- `hyperfine_coupling_MHz` : Couplage hyperfin (spins nucléaires)
- `magnetic_field_sensitivity_nT` : Sensibilité champ magnétique (radical pairs, NV)
- `doi`, `year`, `status` : Métadonnées

---

## Exemples de Systèmes (Littérature)

### NV Centers (Diamant)

**Référence** : Schirhagl et al. 2014 Ann Rev Phys Chem, Maze et al. 2008 Nature

| Propriété | Valeur Typique |
|-----------|----------------|
| T1 | ~1-10 ms (room temp) |
| T2 | ~1-100 µs (room temp, bulk diamond) |
| T2 | ~1-2 ms (isotopically pure diamond) |
| Température | 298K → 1000K (wide range) |
| Readout | ODMR (optically detected magnetic resonance) |
| Bio-compatible | Partiellement (nanodiamonds in vivo) |

**Applications** : Magnétométrie cellulaire, thermométrie, sensing radicaux.

### SiC Defects (Silicon Carbide)

**Référence** : Lukin group, Awschalom group (2010s-2020s)

| Propriété | Valeur Typique |
|-----------|----------------|
| T1 | ~0.1-1 ms |
| T2 | ~10-100 µs |
| Température | 298K → 500K |
| Readout | ODMR, PL (photoluminescence) |
| Bio-compatible | Potentiel (biocompatibilité SiC connue) |

**Avantages** : CMOS-compatible, intégration électronique.

### Radical Pairs (Cryptochrome, Photolyase)

**Référence** : Hore & Mouritsen 2016 Ann Rev Biophys, Gauger et al. 2011 PRL

| Propriété | Valeur Typique |
|-----------|----------------|
| Lifetime | ~1-100 µs (paire radicalaire) |
| Magnetic sensitivity | ~50-500 nT (oiseaux migrateurs) |
| Température | 298K (biological) |
| Readout | Yield quantique, fluorescence, magnétométrie comportementale |
| Bio-compatible | Oui (protéines biologiques) |

**Applications** : Magnétoréception, boussole quantique biologique.

### Nuclear Spins (13C, 31P, etc.)

**Référence** : Morton et al. 2008 Nature, Taminiau et al. 2012 PRL

| Propriété | Valeur Typique |
|-----------|----------------|
| T1 | Secondes à heures (isolés) |
| T2 | Millisecondes (découplage dynamique) |
| Température | Variable (4K cryogenic → 298K) |
| Readout | NMR, hyperfine coupling avec NV |
| Bio-compatible | Oui (isotopes naturels) |

**Applications** : Mémoire quantique, qubits auxiliaires.

---

## Loader Existant (isinglab.data_bridge)

```python
from isinglab.data_bridge import load_nonoptical_systems, load_spin_qubits, load_nuclear_spins

# Hypothétique (CSV pas encore fournis)
nv_centers = load_spin_qubits(category="NV_centers")
nuclear_spins = load_nuclear_spins(isotope="13C")
```

**Statut** : Loader code existe (isinglab/data_bridge), **CSV absents** (`data/atlas_nonoptical/` vide).

---

## Usage avec ising-life-lab (Hypothétique)

### Scénario 1 : Charger & Filter NV Centers

```python
from design_space.loaders import load_generic_design_space
from design_space.selector import list_room_temp_candidates

# Charger dataset non-optical (quand disponible)
df_nv = load_generic_design_space("data/atlas_nonoptical/nv_centers.csv")

# Filtrer température ambiante
room_temp_nv = list_room_temp_candidates(df_nv)

print(f"{len(room_temp_nv)} NV centers @ room temp")
```

### Scénario 2 : Pareto T1 vs T2

```python
from design_space.pareto import compute_pareto_front, rank_pareto

# Objectifs : Maximiser T1 ET T2
objectives = {
    'T1_ms': 'max',
    'T2_us': 'max'
}

df_pareto = compute_pareto_front(df_nv, objectives)
df_ranked = rank_pareto(df_nv, objectives, tie_breakers=['T2_us'])

print(f"Pareto front: {df_pareto['is_pareto_optimal'].sum()} systèmes")
print(df_ranked.head(10)[['system_id', 'qubit_type', 'T1_ms', 'T2_us', 'is_pareto_optimal']])
```

### Scénario 3 : Comparer Optical vs Non-Optical

```python
# Optical (contrast-based)
df_optical = load_design_space()  # 180 systèmes
top_optical = df_optical.nlargest(5, 'functional_score')

# Non-optical (T2-based)
df_nonoptical = load_generic_design_space("data/atlas_nonoptical/all_qubits.csv")
top_nonoptical = df_nonoptical.nlargest(5, 'T2_us')

print("Top 5 optical (contrast):", top_optical['protein_name'].tolist())
print("Top 5 non-optical (T2):", top_nonoptical['qubit_type'].tolist())
```

---

## Actions Nécessaires

### Phase 1 : Exploration GitHub Atlas

**Objectif** : Localiser CSV non-optical (staging area ?)

**Actions** :
1. Explorer structure GitHub Quantum-Sensors-Qubits-in-Biology
2. Chercher dossiers `data/staging/`, `data/nonoptical/`, `data/processed/`
3. Identifier fichiers : `nv_centers.csv`, `sic_defects.csv`, `nuclear_spins.csv`, `radical_pairs.csv`

### Phase 2 : Téléchargement (Si Disponibles)

```bash
# Hypothétique
Invoke-WebRequest -Uri 'https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology/raw/main/data/staging/nv_centers.csv' -OutFile 'data/atlas_nonoptical/nv_centers.csv'
```

### Phase 3 : Standardisation Schéma

**Script** : `scripts/build_nonoptical_design_space.py` (à créer)

**Mapping** :
- SystemID → system_id
- Qubit_Type → qubit_type
- T1_relaxation_ms → T1_ms
- T2_coherence_us → T2_us

### Phase 4 : Tests & Validation

**Tests** : `tests/test_nonoptical_loader.py`
- Validation schema (T1 > 0, T2 > 0, temp_k > 0)
- Pareto sur T1/T2
- Comparaison optical vs non-optical (metrics différentes)

---

## Métriques Spécifiques Non-Optical

### Temps Cohérence (T1, T2)

**T1 (relaxation)** :
- Temps retour équilibre thermique
- Plus long = meilleur (moins decoherence thermique)
- Range typique : µs (mauvais) → secondes (excellent)

**T2 (déphasage)** :
- Temps cohérence superposition quantique
- Plus long = meilleur (mémoire quantique)
- Range typique : ns (inutile) → ms (excellent avec découplage)

**Relation** : Toujours T2 ≤ T1 (limite fondamentale)

### Figure de Mérite

**Q-factor** (quality factor) :
```
Q = T2 / (gate_time)
```

**Sensibilité magnétique** (pour capteurs) :
```
η = (γ × sqrt(T2)) / sqrt(V)
```
- γ : rapport gyromagnétique
- V : volume capteur

---

## Limitations & Garde-Fous

### Données Absentes

❌ **CSV non-optical** : Pas dans `data/atlas_nonoptical/` actuellement  
❌ **Littérature fragmentée** : T1/T2 dépendent fortement contexte (matériau, température, isotopes)

### Action Kill Switch

**Si après exploration GitHub Atlas** :
- Pas de CSV staging/nonoptical disponibles
- → **Documenter comme "non disponible"**, proposer contacter auteur, ne pas bloquer autres développements

### Comparaison Optical vs Non-Optical

⚠️ **Métriques incomparables directement** :
- Optical : contrast (dynamic range), brightness
- Non-optical : T1/T2 (temps cohérence)

**Pas de scoring unifié sans justification physique**. Garder séparé ou créer catégories distinctes.

---

## Contact & Contribution

**GitHub Atlas** : https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology  
**Issues** : Reporter datasets non-optical manquants

---

**Bridge non-optical : Spec prête, datasets à localiser.** 🟡

