# ISING META-INTELLIGENCE v2.2 — README

**Date :** 2025-11-11  
**Version :** v2.2 (Stable Discovery)  
**Statut :** ✅ OPÉRATIONNEL

---

## QUICK START

```bash
# Tests complets (60 tests)
pytest tests/ -v

# Export modules AGI
python -m isinglab.export_memory_library

# Démo bridge Ising-Atlas
python run_ising_atlas_bridge_demo.py

# Découverte v2.2 (20 itérations)
python run_v2_2_stable_discovery.py
```

---

## FONCTIONNALITÉS

### AGI Core (v1.1-v2.2)
- Mémoire persistante (meta_memory.json)
- Bootstrap automatique
- Seuils adaptatifs (percentiles)
- Filtre diversité (Hamming)
- Multi-armed bandit UCB1 (5 bras)

### Métriques Fonctionnelles (v2.1)
- Capacity : patterns distincts stockés
- Robustness : résistance au bruit
- Basin : équilibre attracteurs
- Functional score agrégé

### Profils Modules (v2.1-v2.2)
- stable_memory : stockage robuste
- robust_memory : contextes bruités
- **diverse_memory : bassins variés** ✅ DÉCOUVERT
- chaotic_probe : exploration, hashing
- sensitive_detector : capteurs sensibles
- attractor_dominant : classification
- generic : usage général

### Bridge Ising ↔ Atlas (v2.1)
- 7 profils physiques cibles (NV, SiC, biosenseurs, etc.)
- Module matcher avec scoring
- API inférence v0.1

### Stable Discovery (v2.2)
- **Bras stable_bias** : génère règles B≤3, S⊃{2,3}
- **Quotas par profil** : max 4 de chaque
- **Grid-sweep** : validation multi-échelles
- **Profile stability** : 0.90 en moyenne

---

## RÉSULTATS v2.2

**HoF :** 7 règles (vs 1 en v2.1)  
**Profils :** 2-3 distincts (chaotic_probe, diverse_memory, generic)  
**Diversité :** 6.38 (excellent)  
**Stabilité :** 0.90 (excellent)

**Meilleur module :** **B018/S1236** (diverse_memory, stability 1.00)

---

## TESTS

```bash
pytest tests/ -q
# ✅ 60 passed in 8.61s
```

- v1.1 : 6 tests (core)
- v2.0 : 12 tests (adaptive, bandit, diversity)
- v2.1 : 10 tests (functional, Pareto)
- **v2.2 : 3 tests** (stable_bias, grid_sweep, quotas)
- Intégration : 29 tests

---

## DOCUMENTATION

### Rapports
- `STATUS_v2.2_FINAL.md` : Statut et résultats v2.2
- `docs/RUN_REPORTS/AGI_v2_2_RUN.md` : Rapport détaillé 20 itérations

### Guides
- `docs/AGI_v2_RAPPORT.md` : Rapport technique v2.0
- `docs/AGI_v2.1_ADDITION.md` : Ajouts v2.1
- `docs/AGI_v2.1_TRENDS_MAPPING.md` : Mappings Atlas
- `docs/ISING_ATLAS_BRIDGE.md` : Bridge détaillé

### Références
- `VALIDATION_FINALE.md` : Validation complète
- `SUGGESTIONS_POUR_LA_SUITE.md` : Suggestions futures

---

## LIMITATIONS

1. **stable_memory non découvert** : Seuils adaptatifs trop stricts pour règles stables
2. **Bandit stable_bias** : Reward faible (0.071) → règles rejetées
3. **Bibliothèque biaisée** : Toujours 85% chaotic_probe

**Ajustement suggéré :** Baisser percentile à 75 OU ajouter seuil absolu functional_score > 0.3

---

## PROCHAINES ÉTAPES

1. Baisser `composite_min` à 75 pour inclure stable_memory
2. Ajouter bootstrap par profil manquant (forcer si absent après 10 iter)
3. Reward bandit enrichi (bonus profils sous-représentés)

---

## COMMANDES UTILES

```bash
# Tests
pytest tests/test_v2_2_stable_bias.py -v  # 3 tests v2.2
pytest tests/ -v  # 60 tests total

# Découverte
python run_v2_2_stable_discovery.py  # 20 iter avec rapport

# Export
python -m isinglab.export_memory_library

# Bridge Atlas
python run_ising_atlas_bridge_demo.py  # 3 scénarios
```

---

## ✅ CONCLUSION

**v2.2 : PROGRÈS MAJEUR**

- ✅ HoF × 7 (vs 1 en v2.1)
- ✅ diverse_memory découvert (première règle non-chaotique)
- ✅ Stabilité multi-grilles 0.90
- ✅ Diversité 6.38
- ✅ 60 tests passent
- ⚠️ stable_memory/robust_memory : ajustement mineur nécessaire

**Le système génère maintenant des modules crédibles et diversifiés. L'objectif est presque atteint.**

---

**SYSTÈME OPÉRATIONNEL — 4/5 KPIs ATTEINTS ✅**

