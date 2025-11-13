# ISING ↔ ATLAS BRIDGE — Mapping Conceptuel

**Date :** 2025-11-11  
**Version :** v2.1  
**Repos concernés :**
- **ising-life-lab** (ce repo, modifiable)
- **Quantum-Sensors-Qubits-in-Biology** (Atlas, read-only)

---

## OBJECTIF

Établir des **liens conceptuels heuristiques** entre :
- **Modules mémoire Ising** (règles CA avec profils fonctionnels)
- **Systèmes quantiques/biosenseurs** catalogués dans l'Atlas

**IMPORTANT :** Ce ne sont **pas des preuves expérimentales**, mais des heuristiques pour guider l'exploration future.

---

## MAPPING PROFIL ISING ↔ CLASSE ATLAS

| Profil Ising | Caractéristiques | Classes Atlas (conceptuel) | Usage typique |
|--------------|------------------|----------------------------|---------------|
| **stable_memory** | capacity > 0.6, robustness > 0.6 | NV centers (T2 > 1ms), 31P in Si, SiC defects | Mémoire quantique device-grade, stockage d'états |
| **robust_memory** | robustness > 0.7, capacity > 0.3 | Solid-state qubits (CQED), biosenseurs haute robustesse | Contextes bruités, in vivo, RF/magnetic |
| **diverse_memory** | capacity > 0.5, basin_div > 0.5 | Ensembles moléculaires, systèmes many-body | Stockage patterns multiples, multiplexing |
| **chaotic_probe** | entropy > 0.7, capacity < 0.3 | Systèmes non-Hermitiens, points exceptionnels | Exploration, hashing, amplification |
| **sensitive_detector** | robustness < 0.3, entropy > 0.5 | Radical pairs, bio-spins sous bruit | Capteurs magnétiques, senseurs sensibles |
| **attractor_dominant** | basin_div < 0.2, robustness > 0.5 | Systèmes convergents forts | Classification, read-out digital |
| **generic** | Mixte | Usage général | Prototypage, tests |

---

## PROFILS PHYSIQUES CIBLES (7 définis)

Définis dans `isinglab/integration/target_profiles.py` :

### 1. `nv_cqed_device_grade`
**Description :** NV centers in diamond, CQED-compatible  
**Exigences :** robustness > 0.7, capacity > 0.5, entropy 0.2-0.5  
**Atlas ref :** NV systems with T2 > 1ms, room temp or cryo  
**Modalités :** optical, RF, magnetic  
**Profils Ising :** stable_memory, robust_memory

### 2. `solid_state_non_optical_device_grade`
**Description :** SiC, 31P, systèmes solid-state sans optique  
**Exigences :** robustness > 0.6, capacity > 0.4, entropy 0.1-0.4  
**Atlas ref :** Solid-state with CMOS integration hints  
**Modalités :** RF, magnetic, electrical  
**Profils Ising :** stable_memory, attractor_dominant

### 3. `ep_like_sensor`
**Description :** Senseurs non-Hermitiens, points exceptionnels  
**Exigences :** robustness > 0.3, entropy 0.5-0.9 (sensibles)  
**Atlas ref :** Conceptuel (hybrid systems, coupled modes)  
**Modalités :** optical, coupled modes  
**Profils Ising :** sensitive_detector, chaotic_probe

### 4. `many_body_enhanced`
**Description :** Systèmes many-body / Ising physiques réels  
**Exigences :** robustness > 0.5, basin_div 0.4-0.8  
**Atlas ref :** Radical pairs, ensembles moléculaires  
**Modalités :** magnetic, RF, optical collective  
**Profils Ising :** diverse_memory, robust_memory

### 5. `bio_spin_radical_pair`
**Description :** Radical pairs biologiques (oiseaux, cryptochrome)  
**Exigences :** robustness > 0.4, temp 285-310K  
**Atlas ref :** Radical pairs sous bruit thermique, magnétosensors  
**Modalités :** magnetic, optical  
**Profils Ising :** robust_memory, sensitive_detector

### 6. `biosensor_high_contrast`
**Description :** Biosenseurs optiques (GCaMP, dLight, iGluSnFR)  
**Exigences :** robustness > 0.6, capacity > 0.5, entropy 0.2-0.6  
**Atlas ref :** 180 biosenseurs curés, contrast > 1.5  
**Modalités :** optical fluorescence  
**Profils Ising :** stable_memory, robust_memory

### 7. `quantum_inspired_computing`
**Description :** Modules pour calcul inspiré quantique  
**Exigences :** capacity > 0.6, basin_div 0.5-0.9  
**Atlas ref :** Conceptuel (inspiration architectures)  
**Modalités :** abstrait  
**Profils Ising :** diverse_memory, stable_memory

---

## EXEMPLES DE MAPPING

### Exemple 1 : NV Center → stable_memory

**Système Atlas :** NV center in diamond, T2 = 2ms, T = 300K, modalité optique+RF

**Exigences :**
- Robustesse élevée (environnement contrôlé)
- Capacité mémoire élevée (stockage d'états)
- Entropie modérée (pas chaotique)

**Modules Ising candidats :**
- Profil : `stable_memory`
- Caractéristiques : robustness > 0.7, capacity > 0.6, entropy 0.2-0.5
- **Actuellement ABSENT de la bibliothèque** (biais chaotic_probe)

**Action :** Forcer itérations AGI avec bras "exploitation" pour découvrir règles stables.

---

### Exemple 2 : Biosenseur GCaMP → robust_memory

**Système Atlas :** GCaMP8, calcium sensor, T = 310K, in vivo (bruité)

**Exigences :**
- Robustesse élevée (bruit biologique)
- Capacité modérée (mesures répétées)
- Entropie modérée (stable pour read-out)

**Modules Ising candidats :**
- Notation : B08/S068 (composite: 0.389)
- Labels : robust, dynamic, moderate_memory
- **Match partiel :** robuste (✅) mais trop dynamique pour biosenseur stable

**Action :** Affiner sélection avec exigence entropy < 0.6

---

### Exemple 3 : Radical Pair → sensitive_detector

**Système Atlas :** Cryptochrome, radical pair, T = 298K, magnetic sensing

**Exigences :**
- Sensibilité élevée (détection petits champs)
- Robustesse modérée (environnement bruité)
- Entropie élevée (dynamiques sensibles)

**Modules Ising candidats :**
- Notation : B18/S126 (composite: 0.308)
- Labels : high_entropy, robust, low_memory
- **Match conceptuel :** entropy élevée (✅), robuste (✅), sensible par nature

**Usage :** Module de détection/amplification sous bruit

---

## LIMITATIONS ET DISCLAIMERS

### 1. **Heuristiques conceptuelles, pas expérimentales**
Les mappings sont basés sur des analogies :
- Robustesse Ising ↔ Cohérence quantique (T2)
- Capacité Ising ↔ Capacité mémoire quantique
- Entropie Ising ↔ Dynamiques quantiques

**Aucune validation expérimentale** n'a été faite. Ce sont des hypothèses de travail.

### 2. **Bibliothèque Ising biaisée**
**État actuel :** 99% chaotic_probe (entropy élevée, low memory)  
**Cause :** AGI favorise exploration (bandit, seuils adaptatifs)  
**Impact :** Peu de modules pour NV/solid-state "device-grade" (qui nécessitent stable_memory)

### 3. **Profils fonctionnels incomplets**
**État :** `functional_score` calculé mais pas visible partout dans export  
**Impact :** Scoring basé sur métriques v2.0 (memory, edge, entropy) principalement

### 4. **Atlas utilisé en read-only conceptuel**
**Aucune donnée Atlas n'a été modifiée ou extraite programmatiquement.**  
Les liens sont textuels/conceptuels basés sur la documentation publique.

---

## VALIDATION FUTURE SUGGÉRÉE

Pour transformer ces heuristiques en preuves :

1. **Simulation physique :** Mapper règles Ising → Hamiltoniens de spins → Comparer avec systèmes Atlas
2. **ML entraîné :** Entraîner sur paires (système Atlas, module Ising) validées expérimentalement
3. **Benchmarking :** Tester modules Ising sur tâches inspirées de l'Atlas (stockage bits, détection champs faibles)

---

## USAGE API

```python
from isinglab.integration import suggest_modules_for_system

# Définir système
system = {
    'system_class': 'NV diamond',
    'modality': 'optical + RF',
    'temp_k': 300,
    'noise_environment': 'low'
}

# Suggérer modules
result = suggest_modules_for_system(system, top_k=5)

print(f"Profil cible: {result['inferred_profile']}")
for rec in result['recommendations']:
    print(f"  {rec['module_notation']}: score={rec['match_score']}")
```

**Voir :** `run_ising_atlas_bridge_demo.py` pour exemples complets.

---

## CONCLUSION

**Ce qui existe :**
- ✅ 7 profils physiques cibles définis
- ✅ Module matcher avec scoring
- ✅ API d'inférence v0.1 (heuristique)
- ✅ Script de démo fonctionnel

**Ce qui manque :**
- ⚠️ Modules stable_memory / diverse_memory (non découverts par AGI)
- ⚠️ Validation expérimentale des mappings
- ⚠️ ML entraîné (future v1.0)

**Statut :** Bridge conceptuel opérationnel, prêt pour exploration et raffinement.

---

**FIN — BRIDGE HEURISTIQUE v0.1, PAS DE BULLSHIT**

