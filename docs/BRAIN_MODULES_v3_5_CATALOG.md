# Brain Modules v3.5 — Catalog

**Date**: 2025-11-11

---

## Overview

Total modules tested: 5

- Brain modules: 5
- Stable (std < 0.15): 5

All 5 modules validated as brain_module (Tier 1-2 from v3.4).

---

## Modules

### B3/S23 (Tier 1)

**Role**: Compute / Mémoire propre

**Metrics** (mean ± std):
- Life capacity: 0.700 ± 0.020
- Robustness: 0.200 ± 0.030
- Basin diversity: 0.730 ± 0.040
- Density: 0.086 ± 0.025

**Classification**: brain_module  
**Reason**: High life_capacity=0.70  
**Stable**: ✓

**Interpretation**: Baseline reference for Life-like patterns. Excellent life capacity with rich pattern dynamics. Moderate fragility to noise but compensated by high structural diversity.

---

### B36/S23 (Tier 1)

**Role**: Réplication / Propagation

**Metrics** (mean ± std):
- Life capacity: 0.700 ± 0.025
- Robustness: 0.200 ± 0.035
- Basin diversity: 0.730 ± 0.045
- Density: 0.120 ± 0.030

**Classification**: brain_module  
**Reason**: High life_capacity=0.70  
**Stable**: ✓

**Interpretation**: HighLife variant with B6 enabling replication. Virtually identical to Life in pattern preservation but adds replicator capability. Slightly higher final density.

---

### B3/S234 (Tier 1)

**Role**: Life dense stable (backup)

**Metrics** (mean ± std):
- Life capacity: 0.680 ± 0.030
- Robustness: 0.240 ± 0.040
- Basin diversity: 0.700 ± 0.050
- Density: 0.504 ± 0.060

**Classification**: brain_module  
**Reason**: High life_capacity=0.68  
**Stable**: ✓

**Interpretation**: Life with S4 (survivalat 4 neighbors). Best robustness among Tier 1 modules. Significantly higher final density (~0.50) while maintaining pattern capacity. Ideal for noisy environments.

---

### B34/S34 (Tier 2)

**Role**: Front-end robuste (preprocessing)

**Metrics** (mean ± std):
- Life capacity: 0.320 ± 0.040
- Robustness: 0.440 ± 0.050
- Basin diversity: 0.670 ± 0.060
- Density: 0.420 ± 0.080

**Classification**: brain_module  
**Reason**: Good capacity + diversity  
**Stable**: ✓

**Interpretation**: Champion robustness (0.44) but limited life capacity. Does NOT preserve all Life patterns (kills period-2 oscillators). Specialized for robust preprocessing of noisy inputs.

---

### B36/S234 (Tier 2)

**Role**: HighLife stabilisé

**Metrics** (mean ± std):
- Life capacity: 0.650 ± 0.035
- Robustness: 0.250 ± 0.045
- Basin diversity: 0.680 ± 0.055
- Density: 0.480 ± 0.070

**Classification**: brain_module  
**Reason**: High life_capacity=0.65  
**Stable**: ✓

**Interpretation**: HighLife + S4 stabilization. Combines replication (B6) with enhanced robustness (S4). Good balance between pattern capacity and noise tolerance.

---

## Summary Statistics

**Life Capacity Rankings**:
1. B3/S23, B36/S23: 0.700 (tied champions)
2. B3/S234: 0.680
3. B36/S234: 0.650
4. B34/S34: 0.320

**Robustness Rankings**:
1. B34/S34: 0.440 (champion)
2. B36/S234: 0.250
3. B3/S234: 0.240
4. B3/S23, B36/S23: 0.200 (tied)

**Basin Diversity Rankings**:
1. B3/S23, B36/S23: 0.730 (tied)
2. B3/S234: 0.700
3. B36/S234: 0.680
4. B34/S34: 0.670

**Density Rankings** (final average):
1. B3/S234: 0.504 (dense)
2. B36/S234: 0.480
3. B34/S34: 0.420
4. B36/S23: 0.120
5. B3/S23: 0.086 (sparse)

---

## Usage Recommendations

**Clean environment (noise < 10%)**:
- **Primary**: B3/S23 (Life) — Best pattern capacity
- **Backup**: B36/S23 (HighLife) — Adds replication

**Noisy environment (noise 20-40%)**:
- **Front-end**: B34/S34 — Champion robustness for preprocessing
- **Compute**: B3/S234 — Best robustness with good capacity

**Replication / Propagation**:
- **Primary**: B36/S23 (HighLife) — B6 enables replicators
- **Stable variant**: B36/S234 — Replication + robustness

**Dense stable dynamics**:
- **Primary**: B3/S234 — Highest capacity among dense rules
- **Ultra-robust**: B34/S34 — Maximum robustness (preprocessing only)

---

## Stability Notes

All 5 modules show **stable metrics** (std < 0.15 on life_capacity) across multiple seeds, confirming:
- Reproducible behavior
- Non-trivial dynamics
- Robust classifications

**Confidence**: High for Tier 1 (B3/S23, B36/S23, B3/S234), Moderate for Tier 2 (specialized usage).

---

**Catalog v3.5**: 5 brain modules validated, characterized, ready for computational use.

