# Memory Capacity Results V1.0

**Date**: 08/11/2025  
**Protocol**: Memory AI Lab V1.0

## Protocole

- **Pattern size**: 32×32
- **Pattern counts tested**: 3, 5, 10
- **Noise levels**: 0.01, 0.03, 0.05, 0.08
- **Steps**: 80 (CA), 100 (Hopfield)
- **Runs**: 40 par configuration
- **Success criterion**: Hamming distance ≤ 10%

## Résultats

| Règle | Modèle | Max Capacity | Avg Recall (%) |
|-------|--------|--------------|----------------|
| B01/S3 | CA | 10 | 100 |
| B01/S23 | CA | 10 | 100 |
| B01/S34 | CA | 10 | 100 |
| B01/S2 | CA | 10 | 100 |
| B01/S4 | CA | 10 | 100 |
| B01/S13 | CA | 10 | 100 |
| B46/S58 | CA | 10 | 100 |
| Hopfield | Hopfield | 10 | 100 |

## Conclusion

**Sur ce protocole, les 7 règles CA matchent Hopfield (10 patterns, noise jusqu'à 0.08).**

Toutes les règles du MEMORY_HALL_OF_FAME atteignent 100% de recall sur l'ensemble des configurations testées, démontrant leur robustesse exceptionnelle.

## Dataset

Résultats complets: `data/memory_capacity_v1.json`

## Reproduction

```javascript
const capacity = await MemoryCapacity.runFullSuite({
  rules: ['B01/S3', 'B01/S23', 'B01/S34', 'B01/S2', 'B01/S4', 'B01/S13', 'B46/S58'],
  patternConfigs: [
    { size: 32, count: 3 },
    { size: 32, count: 5 },
    { size: 32, count: 10 }
  ],
  noiseLevels: [0.01, 0.03, 0.05, 0.08],
  steps: 80,
  runs: 40
});
```

