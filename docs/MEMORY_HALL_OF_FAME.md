# Memory Hall of Fame

**Version**: 1.0  
**Date de validation**: 08/11/2025  
**Méthode**: AutoScan multi-noise avec Memory AI Lab

---

## 🏆 7 Règles Mémoire Validées

Ces règles ont été identifiées comme excellentes pour la mémoire associative à travers des tests rigoureux multi-noise.

### 1. B01/S3 - CHAMPION 🥇

**Notation**: B01/S3  
**Famille**: Mythmaker_2  
**Recall moyen**: 96-99%  
**Coverage**: 91-95%  
**Attracteurs**: ~1-2 (très stable)

**Performance:**
- Noise 0.01: 99.9% recall
- Noise 0.03: 99.1% recall
- Noise 0.05: 96.7% recall
- Noise 0.08: 95% recall

**Notes:** Meilleure règle mémoire découverte. Performance proche de Hopfield (voire supérieure sur certains patterns). Born minimal (0,1) + survive unique (3) crée un bassin d'attraction très robuste.

---

### 2. B01/S23

**Notation**: B01/S23  
**Recall moyen**: 80-95%  
**Coverage**: 85-92%

**Performance:**
- Compatible avec survive de Conway (2,3)
- Bon équilibre stabilité/dynamique
- Robuste au bruit jusqu'à 0.08

---

### 3. B01/S34

**Notation**: B01/S34  
**Recall moyen**: 85-100%  
**Coverage**: 90-98%

**Performance:**
- Extended survive range (3,4)
- Excellente robustesse
- Convergence rapide

---

### 4. B01/S2

**Notation**: B01/S2  
**Recall moyen**: 95-100%  
**Coverage**: 92-99%

**Performance:**
- Minimal survive (2 uniquement)
- Très bon recall
- Bassin d'attraction simple

---

### 5. B01/S4

**Notation**: B01/S4  
**Recall moyen**: 99-100%  
**Coverage**: 95-100%

**Performance:**
- Single survive (4)
- Quasi-parfait recall
- Très stable

---

### 6. B01/S13

**Notation**: B01/S13  
**Recall moyen**: 70-100%  
**Coverage**: 75-95%

**Performance:**
- Low survive (1,3)
- Bon recall malgré simplicity
- Variance plus élevée selon patterns

---

### 7. B46/S58

**Notation**: B46/S58  
**Famille**: High-birth variant  
**Recall moyen**: 85-100%  
**Coverage**: 88-98%

**Performance:**
- Born élevé (4,6)
- Survive double (5,8)
- Excellent pour patterns complexes
- Seule règle "high-birth" de la liste

---

## 📊 Synthèse

### Famille Dominante

**B01/S*** représente 6/7 règles (85.7%)

**Caractéristiques communes:**
- Born minimal: 0 et/ou 1 (naissance rare)
- Survive simple: 1-3 valeurs max
- Bassin d'attraction robuste
- Convergence rapide (<80 steps)

### Comparaison avec Hopfield

Sur le protocole standard (4 patterns par défaut, noise 0.05):

| Règle | CA Recall | Hopfield Recall | Δ |
|-------|-----------|-----------------|---|
| B01/S3 | 96.7% | 84-88% | **+8 à +12%** ✅ |
| B01/S4 | 99% | 84-88% | **+11 à +15%** ✅ |
| B46/S58 | 100% | 84-88% | **+12 à +16%** ✅ |

**Conclusion:** Ces règles CA peuvent **surpasser** Hopfield sur certains types de patterns (simples, compacts).

---

## 🔬 Protocole de Validation

**Patterns testés:** 4 patterns par défaut reproductibles
- Block 2×2 (stable)
- Blinker période 2 (oscillateur)
- Glider-like (mobile)
- Random sparse (30 cellules, positions fixes)

**Critères de sélection:**
- Recall ≥70% sur au moins 2 niveaux de bruit bas (≤0.05)
- Coverage ≥40%
- Attracteurs ≥0.5 (bassin d'attraction existant)
- Recall ≥40% même à bruit élevé (0.08)

**Critère de succès:** Distance de Hamming ≤ 10% de la taille du pattern

**Runs:** 60 par configuration  
**Steps:** 160 (évolution CA)

---

## 💡 Utilisation

### Pour Tester une Règle

```javascript
// Dans Memory AI Lab console (F12)
const batch = await MemoryLab.runBatchForHallOfFame({ 
  noiseLevel: 0.05, 
  steps: 80, 
  runs: 50 
});

// B01/S3 devrait montrer recall ~96%
```

### Pour Découvrir d'Autres Candidates

```javascript
const scan = await MemoryScanner.scanMemoryCandidates({ 
  noiseLevels: [0.01, 0.03, 0.05, 0.08],
  steps: 160,
  runs: 60
});

// Devrait identifier les 7 règles ci-dessus
console.table(scan.candidates);
```

---

## 📚 Références

**Découverte initiale:**
- Seeds 1.88 (B2456/S078, B2456/S068): Identifiées via extreme search (10k+ règles)
- Voir `memory-results-extreme.md`

**Validation AutoScan:**
- 25 règles testées sur multi-noise
- Voir `experiments/memory-ai-lab/autoScan.js`

**Méthodologie complète:**
- Voir `docs/QUICK_START_MEMORY_AI_LAB.md`
- Voir `docs/PRD_MEMORY_AI_LAB.md`

---

## ⚠️ Notes Importantes

**Ces résultats sont spécifiques au protocole Memory AI Lab v1.0:**
- Grilles 32×32 (pas 64×64)
- Patterns dessinés/simples (pas patterns aléatoires complexes)
- Critère Hamming ≤10%
- Steps 80-160

**Pour d'autres contextes**, les performances peuvent varier. Les Seeds 1.88 par exemple sont optimales pour:
- Grilles 64×64
- Patterns aléatoires denses
- Critères plus stricts

**La famille B01/S*** semble particulièrement adaptée aux petits patterns compacts.**

---

**Version**: 1.0  
**Statut**: Validé et figé  
**Prochaine étape**: Exploiter ces 7 règles comme briques d'un système de stockage/retrieval

