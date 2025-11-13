# ISING META-INTELLIGENCE — SUGGESTIONS POUR LA SUITE

**Date :** 2025-11-11  
**Version actuelle :** v2.1 (validée)  
**Statut :** ✅ Système opérationnel

---

## ✅ ÉTAT ACTUEL VALIDÉ

- **57 tests passent** (6 v1 + 12 v2 + 10 v2.1 + intégration)
- **Export fonctionnel** avec module_id, profile, suggested_use
- **Métriques fonctionnelles** : capacity, robustness, basin calculées
- **Sélection Pareto** : implémentée et testée
- **143 règles en mémoire**, 1 en HoF

---

## 💡 5 SUGGESTIONS CONCRÈTES

### 1. **Activer Pareto complet** (Priorité: HAUTE)

**Problème :** `use_pareto: False` (ligne 235 de closed_loop_agi.py) car refonte incomplète

**Solution :**
```python
# Dans _update_memory_and_hof, remplacer la boucle adaptative par :
if use_pareto:
    candidates_for_pareto = [... préparer avec tous les scores ...]
    promoted, removed = select_pareto_hof(candidates_for_pareto, current_hof, objectives, ...)
    for rule in promoted:
        profile, use = infer_module_profile(...)
        rule['module_profile'] = profile
        add_or_update_rule(rule)
```

**Bénéfice :** HoF devient vraiment un ensemble Pareto de stratégies non-dominées

---

### 2. **Tests fonctionnels configurables** (Priorité: MOYENNE)

**Problème :** Métriques fonctionnelles lentes sur grands batchs (grid 16x16, 5 patterns)

**Solution :**
```python
config = {
    'functional_tests_mode': 'lite',  # ou 'full'
    'functional_tests_params': {
        'lite': {'grid': (16,16), 'n_patterns': 5, 'steps': 30},
        'full': {'grid': (32,32), 'n_patterns': 20, 'steps': 100}
    }
}
```

**Bénéfice :** Équilibre vitesse/précision selon contexte

---

### 3. **Tracking profils dans HoF** (Priorité: MOYENNE)

**Manque :** Pas de stats sur distribution des profils dans HoF

**Solution :**
```python
# Dans run_one_iteration, après promotion :
profile_counts = defaultdict(int)
for rule in load_hof_rules():
    profile = rule.get('module_profile', 'unknown')
    profile_counts[profile] += 1

self._log(f"  [HoF PROFILES] {dict(profile_counts)}")
# → [HoF PROFILES] {'stable_memory': 3, 'robust_memory': 2, 'generic': 1}
```

**Bénéfice :** Visibilité sur diversité fonctionnelle du HoF

---

### 4. **Reward bandit enrichi** (Priorité: BASSE)

**Actuellement :** `reward = promotions + avg_composite`

**Amélioration :**
```python
# Ajouter bonus pour diversité et qualité fonctionnelle
bonus_diversity = len(set(r.get('module_profile') for r in promoted)) / max(len(promoted), 1)
bonus_functional = np.mean([r.get('functional_score', 0) for r in promoted])

reward = promotions + avg_composite + bonus_diversity + bonus_functional
```

**Bénéfice :** Bandit favorise les bras qui trouvent des modules réellement utiles

---

### 5. **Validation croisée des profils** (Priorité: BASSE)

**Problème :** Profil attribué sur 1 seed seulement

**Solution :**
```python
# Évaluer sur 3 seeds différents
profiles_votes = []
for seed in [42, 123, 456]:
    metrics = evaluate_with_seed(rule, seed)
    profile, _ = infer_module_profile(metrics['capacity'], ...)
    profiles_votes.append(profile)

# Consensus majoritaire
final_profile = max(set(profiles_votes), key=profiles_votes.count)
confidence = profiles_votes.count(final_profile) / len(profiles_votes)
```

**Bénéfice :** Profils plus robustes, moins de faux positifs

---

## 🎯 ROADMAP SUGGÉRÉE

### Court terme (1-2 sessions)
1. ✅ Activer Pareto complet dans ClosedLoopAGI
2. ✅ Tracking profils HoF dans logs

### Moyen terme (3-5 sessions)
3. ✅ Tests fonctionnels configurables (lite/full)
4. ✅ Reward bandit enrichi avec bonus_diversity

### Long terme (6+ sessions)
5. ✅ Validation croisée profils (multi-seed)
6. Clustering automatique de profils (au lieu de heuristiques)
7. Métriques fonctionnelles avancées (patterns spécifiques, dynamiques temporelles)
8. Intégration Atlas : mapper profils → régimes physiques

---

## ⚠️ NOTES IMPORTANTES

### Ce qui fonctionne maintenant :
- ✅ Métriques fonctionnelles calculées et stockées
- ✅ Profils inférés et exportés
- ✅ Export enrichi conforme v2.1
- ✅ 57 tests passent

### Ce qui est partiellement implémenté :
- ⚠️ Pareto codé mais `use_pareto: False` (à activer)
- ⚠️ Logging diversité commenté (en attente Pareto actif)

### Ce qui est à prouver expérimentalement :
- ⚠️ Corrélation functional_score ↔ utilité réelle (validation externe)
- ⚠️ Profils stables sur différents seeds
- ⚠️ HoF Pareto > 1 règle après 20+ itérations

---

## 📋 COMMANDES UTILES

```bash
# Valider système
pytest tests/ -q  # 57 tests

# Export avec profils
python -m isinglab.export_memory_library

# Vérifier profils
python -c "import json; hof=json.load(open('results/agi_export_hof.json'))['hall_of_fame']; [print(f'{r[\"notation\"]}: {r[\"module_profile\"]}') for r in hof]"

# Logs détaillés
tail -n 100 logs/agi_*.log | grep -E "ADAPTIVE|BANDIT|PROMOTED|HoF"
```

---

**FIN — v2.1 VALIDÉ, SUGGESTIONS DOCUMENTÉES**

