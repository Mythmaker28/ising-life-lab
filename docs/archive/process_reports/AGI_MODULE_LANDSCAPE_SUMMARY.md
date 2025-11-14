# AGI MODULE LANDSCAPE SUMMARY — Ising-Life-Lab v2.1

**Date :** 2025-11-11  
**Source :** `results/agi_export_hof.json`  
**Statut :** 168 règles en mémoire, 1 en HoF

---

## RÉSUMÉ FACTUEL

**Hall of Fame :** 1 règle  
**Memory Library :** 100 règles (top composite)  
**Distribution profils :** 1 generic (HoF), profils fonctionnels en cours d'évaluation

---

## DISTRIBUTION DES LABELS (Memory Library)

| Label | Count | Signification |
|-------|-------|---------------|
| `closed_loop` | 100 | Découvert par AGI closed-loop |
| `dynamic` | 100 | High entropy (>0.7) |
| `evaluated` | 100 | Évalué avec métriques complètes |
| `high_entropy` | 100 | Entropie élevée |
| `low_memory` | 99 | Memory score < 0.1 |
| `robust` | 81 | Edge score > 0.3 |
| `moderate_edge` | 19 | Edge score 0.15-0.3 |

**Interprétation :**  
La bibliothèque actuelle contient principalement des règles **dynamiques/chaotiques** (entropy élevée) avec **faible capacité mémoire** mais **robustes au bruit** (edge score élevé).

---

## TOP 10 MODULES PAR SCORE COMPOSITE

| # | Notation | Composite | Profil suggéré | Usage |
|---|----------|-----------|----------------|-------|
| 1 | B08/S068 | 0.389 | chaotic_probe | Haute entropie, low memory → exploration/hashing |
| 2 | B016/S8 | 0.324 | chaotic_probe | Similar, dynamiques complexes |
| 3 | B18/S1268 | 0.309 | chaotic_probe | Robuste, dynamique |
| 4 | B18/S126 | 0.308 | chaotic_probe | Robuste, entropie élevée |
| 5 | B08/S06 | 0.308 | chaotic_probe | Robuste, dynamique |
| 6 | B18/S1267 | 0.308 | chaotic_probe | Robuste, dynamique |
| 7 | B067/S08 | 0.304 | chaotic_probe | Robuste, entropie élevée |
| 8 | B18/S0126 | 0.299 | chaotic_probe | Robuste, dynamique |
| 9 | B016/S08 | 0.298 | chaotic_probe | Robuste, dynamique |
| 10 | B18/S1256 | 0.297 | chaotic_probe | Robuste, entropie élevée |

---

## MODULES EXEMPLAIRES PAR PROFIL

### chaotic_probe (dominante)

**B08/S068** (composite: 0.389)
- Memory: 0.14, Edge: 0.48, Entropy: 0.87
- **Usage :** Dynamiques complexes, exploration d'espace ou génération de hashing
- **Justification :** Entropie élevée (0.87) + robustesse modérée (0.48) → bon pour exploration structurée

**B18/S126** (composite: 0.308)
- Memory: 0.03, Edge: 0.34, Entropy: 0.95
- **Usage :** Sondes chaotiques, amplification de bruit
- **Justification :** Entropie maximale (0.95) mais low memory → détection plutôt que stockage

### robust (81 règles)

**B016/S8** (composite: 0.324)
- Memory: 0.07, Edge: 0.35, Entropy: 0.92
- **Usage :** Contextes bruités, exploration robuste
- **Justification :** Edge score > 0.3 → résiste au bruit

---

## PROFILS MANQUANTS OU RARES

**Profils absents dans l'export actuel :**
- `stable_memory` : capacity > 0.6, robustness > 0.6
- `diverse_memory` : capacity > 0.5, basin_diversity > 0.5
- `attractor_dominant` : basin_diversity < 0.2

**Raison :** Les métriques fonctionnelles v2.1 (capacity, robustness, basin) ne sont pas encore dans l'export visible. Elles sont calculées mais pas présentes dans les scores visibles.

**Action requise :** Les prochaines itérations avec métriques fonctionnelles actives devraient découvrir ces profils.

---

## LIMITATIONS ACTUELLES

### 1. Profils fonctionnels incomplets
**État :** memory_library contient `functional_score`, mais pas dans les scores affichés  
**Cause :** Export basé sur ancien format  
**Solution :** Ré-exporter après quelques itérations v2.1 complètes

### 2. Biais vers chaotic_probe
**État :** 99/100 règles sont low_memory + high_entropy  
**Cause :** Sélection AGI favorise l'exploration (bras "curiosity" et "diversity" du bandit)  
**Solution :** Forcer quelques itérations avec bras "exploitation" pour règles stables

### 3. HoF minimale
**État :** 1 règle seulement  
**Cause :** Seuils adaptatifs stricts (percentile 90) + `use_pareto: False`  
**Solution :** Activer Pareto + baisser percentile à 85

---

## CONCLUSION HONNÊTE

**Ce qui existe :**
- ✅ 168 règles en mémoire
- ✅ 100 règles exportées
- ✅ Distribution : 99% chaotic_probe / dynamiques
- ✅ Top règles robustes (edge > 0.3)

**Ce qui manque :**
- ⚠️ Profils stable_memory / diverse_memory (non découverts)
- ⚠️ functional_score visible dans export
- ⚠️ HoF diversifié (1 règle uniquement)

**Prochaine étape :**
Lancer 20+ itérations avec :
- `use_pareto: True`
- Forcer bras "exploitation" pour trouver règles stables
- Vérifier émergence de profils stable_memory

---

**FIN — LANDSCAPE ACTUEL DOCUMENTÉ SANS BULLSHIT**

