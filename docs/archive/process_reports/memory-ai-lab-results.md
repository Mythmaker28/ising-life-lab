# Memory AI Lab - Résultats

Ce fichier contient les résultats des tests automatiques du Hall of Fame.

## Comment générer les résultats

1. **Démarrer le serveur**:
```bash
cd C:\Users\tommy\Documents\ising-v2-final
python -m http.server 8001
```

2. **Ouvrir Memory AI Lab**:
```
http://localhost:8001/experiments/memory-ai-lab/index.html
```

3. **Créer des patterns de test** (onglet Memory Lab):
   - Dessiner 2-3 patterns simples (32×32):
     - Glider (petit pattern mobile)
     - Blinker (oscillateur période 2)
     - Block (structure stable 2×2)
   - Cliquer "Add Pattern" après chaque

4. **Ouvrir la console** (F12) et exécuter:

```javascript
// Test automatique de toutes les règles Hall of Fame
const batch = await MemoryLab.runBatchForHallOfFame({ 
  noiseLevel: 0.05,  // 5% de bruit
  steps: 80,         // 80 étapes d'évolution
  runs: 50           // 50 runs par pattern
});

// Comparaison avec Hopfield
const comp = await HopfieldLab.compareWithHallOfFame({
  noiseLevel: 0.05,
  runs: 50
});

// Générer le rapport Markdown
const report = Reports.generateMarkdownReport(batch, comp);

// Afficher et copier le rapport
console.log(report);
```

**Note**: Si aucun pattern n'est dessiné dans l'UI, le système utilise automatiquement 4 patterns par défaut (block, blinker, glider-like, random sparse).

5. **Coller les résultats ci-dessous**

---

## Final Memory Hall of Fame

**Date de validation**: 08/11/2025  
**Méthode**: AutoScan multi-noise avec patterns reproductibles

### 7 Règles Mémoire Validées

| Règle | Notation | Recall Min (%) | Recall Max (%) | Status | Notes |
|-------|----------|----------------|----------------|--------|-------|
| B01/S3 | B01/S3 | 95 | 99.9 | ✅ Champion | Mythmaker_2, recall ~96-99% |
| B01/S23 | B01/S23 | 71 | 95 | ✅ Excellent | Variant Conway survive |
| B01/S34 | B01/S34 | 77 | 100 | ✅ Excellent | Extended survive |
| B01/S2 | B01/S2 | 95 | 100 | ✅ Excellent | Minimal survive |
| B01/S4 | B01/S4 | 99 | 100 | ✅ Excellent | Single survive |
| B01/S13 | B01/S13 | 66 | 100 | ✅ Good | Low survive |
| B46/S58 | B46/S58 | 84 | 100 | ✅ Excellent | High-birth variant |

**Critères de validation:**
- Recall ≥70% sur au moins 2 niveaux de bruit (0.01, 0.03, 0.05)
- Coverage ≥40%
- Attracteurs ≥0.5
- Recall ≥40% à bruit élevé (0.08)
- Distance de Hamming ≤10% pour succès

---

## Résultats (tests utilisateur)

### Méthodologie

- **Patterns testés**: 3-4 (glider, blinker, block, random sparse)
- **Runs par pattern**: 50
- **Noise level**: 0.05 (5%)
- **Steps**: 80
- **Critère de succès**: Distance de Hamming ≤ 10% de la taille du pattern
- **Date**: [À remplir après tests]

### Hall of Fame - Résultats CA

| Règle | Notation | Recall Rate | Coverage | Attracteurs | Status |
|-------|----------|-------------|----------|-------------|--------|
| Seed_1.88a | B2456/S078 | [À tester] | [À tester] | [À tester] | ? |
| Seed_1.88b | B2456/S068 | [À tester] | [À tester] | [À tester] | ? |
| Evo B246/S58 | B246/S58 | [À tester] | [À tester] | [À tester] | ? |
| Evo B2456/S07 | B2456/S07 | [À tester] | [À tester] | [À tester] | ? |
| Evo B246/S5 | B246/S5 | [À tester] | [À tester] | [À tester] | ? |
| Mythmaker_1 | B2456/S5 | [À tester] | [À tester] | [À tester] | ? |
| Mythmaker_2 | B01/S3 | [À tester] | [À tester] | [À tester] | ? |

### Comparaison CA vs Hopfield

| Règle | CA Recall | Hopfield Recall | Δ | Gagnant |
|-------|-----------|-----------------|---|---------|
| B2456/S078 | [À tester] | [À tester] | [À tester] | ? |
| B2456/S068 | [À tester] | [À tester] | [À tester] | ? |
| B246/S58 | [À tester] | [À tester] | [À tester] | ? |
| B2456/S07 | [À tester] | [À tester] | [À tester] | ? |
| B246/S5 | [À tester] | [À tester] | [À tester] | ? |
| B2456/S5 | [À tester] | [À tester] | [À tester] | ? |
| B01/S3 | [À tester] | [À tester] | [À tester] | ? |

### Conclusion

**Règle recommandée**: [À déterminer après tests]

**Meilleur recall rate**: [À tester]

**CA vs Hopfield**: [À déterminer]

---

## Notes

- **Critère de succès réaliste**: Distance de Hamming ≤ 10% permet de considérer qu'un pattern est "retrouvé" même avec de légères variations
- Les résultats peuvent varier de ±5% entre les runs (seeds aléatoires non fixées)
- Les patterns de test influencent fortement les résultats
- Pour des résultats plus robustes, augmenter le nombre de runs (100+)
- **Classification**:
  - Recall rate < 40% : "Fail" (mémoire faible)
  - Recall rate 40-70% : "Weak" (mémoire modérée)
  - Recall rate ≥70% : "OK" (bonne mémoire)
- **Patterns par défaut**: Si aucun pattern n'est dessiné, le système utilise automatiquement 4 patterns de test standard

## Historique des tests

### [Date] - Test initial
- Patterns: [description]
- Résultats: [lien vers commit avec résultats]

