# Integration Module — Ising ↔ Physical Systems Bridge

Ce module fournit des bridges conceptuels entre modules mémoire Ising
et systèmes physiques réels (Atlas Quantum-Sensors-Qubits-in-Biology).

---

## MODULES

### `target_profiles.py`
7 profils physiques cibles (NV, SiC, biosenseurs, radical pairs, etc.)

### `module_matcher.py`
Scoring et ranking de modules Ising pour profils cibles

### `profile_inference.py`
API d'inférence v0.1 (heuristique déterministe)

---

## USAGE

```python
from isinglab.integration import suggest_modules_for_system

system = {
    'system_class': 'NV diamond',
    'modality': 'optical + RF',
    'temp_k': 300,
    'noise_environment': 'low'
}

result = suggest_modules_for_system(system, top_k=5)
print(f"Profil: {result['inferred_profile']}")
for rec in result['recommendations']:
    print(f"  {rec['module_notation']}: score={rec['match_score']}")
```

**Script démo :** `run_ising_atlas_bridge_demo.py`

---

## DISCLAIMERS

- **Heuristiques conceptuelles**, pas validations expérimentales
- **Atlas utilisé read-only** (liens textuels uniquement)
- **Version 0.1** : règles fixes, future v1.0 nécessitera ML

---

**Voir :** `docs/ISING_ATLAS_BRIDGE.md` pour détails complets.

