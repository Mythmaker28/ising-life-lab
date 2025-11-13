# POLITIQUE DE SEUILS AGI — v2.5

**Version :** v2.5  
**Date :** 2025-11-11  
**Objectif :** Sortir du biais pro-chaos SANS arbitraire

---

## PROBLÈME IDENTIFIÉ

**Feedback loop pro-chaos (v2.0-v2.4) :**
1. Bibliothèque biaisée (99% chaotic_probe)
2. Percentile 85 calculé sur cette bibliothèque → seuil 0.29
3. Règles stables (B3/S23, composite 0.05) < 0.29 → rejetées
4. Méta-modèle entraîné sur chaos → prédit chaos
5. Boucle se renforce

**Résultat :** Aucune règle stable_memory/robust_memory découverte malgré stable_bias.

---

## SOLUTION : DOUBLE VOIE DE PROMOTION

### Voie 1 : Chaotic/EP-Like (Percentile Adaptatif)

**Profils cibles :** chaotic_probe, sensitive_detector

**Critères :**
```python
composite_score >= percentile_adaptive(85)  # Top 15%
AND edge_score >= 0.05
AND entropy >= 0.0
```

**Justification :** Ces règles sont nombreuses, seuil strictement adaptatif.

---

### Voie 2 : Memory-Like (Seuils Absolus Fonctionnels)

**Profils cibles :** stable_memory, robust_memory, diverse_memory

**Critères :**
```python
functional_score >= 0.30  # Utilité mesurée
AND capacity_score >= 0.30  # Stockage patterns
AND stability >= 0.67  # Cohérent multi-échelles
AND (
    (robustness >= 0.60) OR  # Robuste bruit
    (memory_score >= 0.30)    # OU capacité brute
)
```

**Justification :**
- functional ≥ 0.30 : B018/S1236 (0.36), B34/S34 (0.44) passent
- capacity ≥ 0.30 : Stockage patterns (B3/S23 proxy 0.67)
- stability ≥ 0.67 : B3/S23, B36/S23, B34/S34 valident
- robustness ≥ 0.60 OU memory ≥ 0.30 : Flexibilité pour cerveaux spécialisés

**Bypass percentile :** Ces règles entrent même si composite faible.

---

### Quotas de Profils (Anti-Saturation)

**Config actuelle :**
```python
'hof_profile_quotas': {
    'stable_memory': 4,
    'robust_memory': 4,
    'diverse_memory': 4,
    'chaotic_probe': 4,
    'sensitive_detector': 4,
    'attractor_dominant': 2,
    'generic': 2
}
```

**Règle :** Si quota atteint, peut remplacer règle moins bonne du même profil.

---

### Bootstrap Profil Manquant

**Trigger :** Si `stable_memory` ou `robust_memory` absent après 30 itérations

**Action :**
```python
if iter > 30 and 'stable_memory' not in hof_profiles:
    candidates_stable = [r for r in memory if infer_profile(r) == 'stable_memory']
    if candidates_stable:
        best = max(candidates_stable, key=lambda r: r['functional_score'])
        bootstrap_rule(best)
        log("[BOOTSTRAP PROFILE] Forced stable_memory: {best['notation']}")
```

**Justification :** Garantit couverture minimale après exploration significative.

---

## IMPLÉMENTATION

**Fichier :** `isinglab/closed_loop_agi.py`

**Code actuel (v2.3) :**
```python
# Ligne 338
functional_ok = functional_score >= 0.30
if (composite_ok OR functional_ok) and memory_ok and edge_ok and entropy_ok:
```

**Améliorations v2.5 :**
```python
# Voie 1 : Chaotic (percentile adaptatif)
chaotic_path = composite_score >= adaptive_thresholds['composite_threshold']

# Voie 2 : Memory (seuils absolus fonctionnels)
memory_path = (
    functional_score >= 0.30 AND
    capacity_score >= 0.30 AND
    profile_stability >= 0.67 AND
    (robustness_score >= 0.60 OR memory_score >= 0.30)
)

if (chaotic_path OR memory_path) and diversity_ok and profile_quota_ok:
    promote = True
```

---

## CALIBRATION DES SEUILS

**Sources de calibration :**

### Functional Score
- B018/S1236 : 0.36 → Seuil 0.30 (10% marge)
- B34/S34 : 0.44 → Seuil 0.30 passe
- Règles < 0.30 : vraiment faibles (à rejeter)

### Capacity Score
- B3/S23 (proxy) : 0.67-0.73 → Seuil 0.30 inclusif
- B018/S1236 : 0.6 → Passe
- Règles 0.0 : aucune capacité

### Robustness Score
- B34/S34 : 0.44 → Seuil 0.60 strict (B34 échoue)
- B018/S1236 : 0.46 → Échoue aussi
- **Compromis :** Robustness 0.60 OU memory 0.30 (flexibilité)

### Stability
- B3/S23, B36/S23 : 0.73 → Seuil 0.67 (standard établi)
- B34/S34 : 0.67 → Passe juste
- B018/S1236 : 0.13 → Échoue (attendu)

---

## TESTS

**Fichier :** `tests/test_threshold_policy.py`

**Cas testés :**
1. Règle mémoire forte (functional 0.4, capacity 0.6, stability 0.7) → Passe voie 2
2. Règle chaotique (composite percentile 90, entropy 0.9) → Passe voie 1
3. Règle faible (functional 0.1, composite 0.1) → Rejetée
4. Quota saturé (chaotic_probe 4/4) → Nouveau chaotic rejeté sauf si meilleur

---

## VALIDATION

**Après implémentation :**
```bash
pytest tests/test_threshold_policy.py -v
pytest tests/ -q  # Tous tests doivent passer
```

**Après long run (200 iter) :**
- Vérifier HoF contient ≥ 1 stable_memory ou robust_memory
- Sinon, diagnostiquer dans rapport (données, pas excuses)

---

## CONCLUSION

**Politique explicite, calibrée sur données observées.**  
**Double voie : chaotic (adaptatif) + memory (absolu).**  
**Bootstrap contrôlé si manque après 30 iter.**  
**Quotas anti-saturation maintenus.**

**Pas de magie, tout traçable.**

