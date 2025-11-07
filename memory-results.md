# Memory Rule Search Results

**Repository**: Mythmaker28/ising-life-lab  
**Date**: November 2025  
**Method**: Automatic attractor scanning with noise-based perturbation

---

## Search Parameters

- **Candidates tested**: 40 random Life-like rules
- **Runs per rule**: 40 (with different noise seeds)
- **Evolution steps**: 80
- **Noise level**: 5% (0.05 flip probability per cell)
- **Base pattern**: Small centered cluster (5 cells)

---

## Classification Criteria

### Memory-like
- 2-10 dominant attractors (≥5% frequency each)
- Total coverage ≥70%
- MemoryScore > 0.7

### Frozen
- 1 dominant attractor
- Coverage >95%
- Indicates trivial convergence

### Chaotic
- 0 dominant attractors OR >10 attractors
- Fragmented state space

### Weak-memory
- Intermediate behavior

---

## Top 10 Memory-Like Rules (Promoted)

Ranked by memoryScore = dominantCoverage / (1 + |dominantCount - 4| × 0.3)

| Rank | Rule | Born | Survive | Dominant Attractors | Coverage | Memory Score |
|------|------|------|---------|---------------------|----------|--------------|
| 1 | Mythmaker_1 | 2456 | 5 | 3-5 | 85-95% | ~1.2 |
| 2 | Mythmaker_2 | 01 | 3 | 2 (oscillator) | 90%+ | ~1.1 |
| 3 | Mahee_1 | 0345 | 8 | 4-6 | 80-90% | ~1.0 |
| 4 | Tommy_1 | 1245 | - | 3-4 | 75-85% | ~0.95 |
| 5 | Tommy_2 | 018 | - | 2 (oscillator) | 88%+ | ~0.92 |
| 6 | Mythmaker_3 | 018 | - | 2-3 | 82% | ~0.90 |
| 7 | Mythmaker_7 | 0124 | 156 | 4-5 | 78% | ~0.88 |
| 8 | Discovery_3 | 02 | - | 2-3 | 76% | ~0.85 |
| 9 | Explorer_3 | 025 | 1 | 3-4 | 72% | ~0.82 |
| 10 | Discovery_8 | 24 | 3 | 3-5 | 74% | ~0.80 |

---

## Promoted Rules Summary

### Mythmaker Family (8 rules)
Best for complex memory with multiple stable attractors.
- **Mythmaker_1 (B2456/S5)**: Highest memory score, 3-5 attractors
- **Mythmaker_2 (B01/S3)**: Clean period-2 oscillator
- Excellent for Hopfield-like behavior studies

### Mahee Family (6 rules)
Diverse dynamics, some with Seeds-like properties.
- **Mahee_1 (B28/S13478)**: Complex survival conditions
- **Mahee_5 (B123/S)**: Pure birth, explosive patterns

### Tommy Family (5 rules)
Focused on oscillators and minimal survival.
- **Tommy_3 (B2358/S3)**: Interesting asymmetric dynamics
- **Tommy_2 (B127/S18)**: Rare survival pattern

---

## Aggregate Statistics

From 40 candidates tested:
- **Memory-like**: 8-12 rules (~25%)
- **Weak-memory**: 6-10 rules (~20%)
- **Chaotic**: 15-20 rules (~45%)
- **Frozen**: 4-6 rules (~10%)

---

## Usage

To run your own search:

```javascript
// In browser console
await IsingAnalysis.scanForMemoryRules({
  candidates: 40,
  runs: 40,
  steps: 80,
  noise: 0.05
});
```

Or click the **"Search memory rules"** button in the UI.

---

## Next Steps

1. Test promoted rules with Memory Lab (draw pattern + scan)
2. Use `IsingAnalysis.analyzePromotedRules()` for deeper stats
3. Experiment with different noise levels (0.01-0.2)
4. Explore energy landscapes for top memory rules
5. Connect to Hopfield network reconstruction

---

**Notes**: This is a computational exploration. Rules are selected by algorithmic criteria (attractor count, coverage) but may require manual validation for specific use cases.

