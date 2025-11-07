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

// Copier le rapport (Ctrl+C)
copy(report);
```

5. **Coller les résultats ci-dessous**

---

## Résultats (à compléter après tests)

### Méthodologie

- **Patterns testés**: 3 (glider, blinker, block)
- **Runs par pattern**: 50
- **Noise level**: 0.05 (5%)
- **Steps**: 80
- **Date**: [À remplir]

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

- Les résultats peuvent varier de ±5% entre les runs (seeds aléatoires non fixées)
- Les patterns de test influencent fortement les résultats
- Pour des résultats plus robustes, augmenter le nombre de runs (100+)
- Les règles avec recall rate < 40% sont considérées comme "Fail" pour la mémoire
- Les règles avec recall rate 40-70% sont "Weak"
- Les règles avec recall rate ≥70% sont "OK"

## Historique des tests

### [Date] - Test initial
- Patterns: [description]
- Résultats: [lien vers commit avec résultats]

