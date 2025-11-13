"""
Benchmark Vectorisation NumPy vs Python Loops

Mesure gains réels sur règles CA.
"""

import sys
from pathlib import Path
import time
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from isinglab.core.ca_vectorized import benchmark_ca_implementations

print("=" * 80)
print("BENCHMARK VECTORISATION CA")
print("=" * 80)
print()

# Test sur plusieurs tailles
configs = [
    (32, 32, 100),
    (64, 64, 100),
    (128, 128, 50),
]

results = []

for h, w, steps in configs:
    print(f"### Grid {h}×{w}, {steps} steps")
    print("-" * 60)
    
    result = benchmark_ca_implementations(grid_size=(h, w), steps=steps)
    results.append(result)
    
    print(f"  Python loops : {result['time_python']:.3f}s")
    print(f"  Vectorized   : {result['time_vectorized']:.3f}s")
    print(f"  Speedup      : {result['speedup']:.1f}×")
    print(f"  Coherent     : {result['coherent']}")
    print()

# Moyenne
avg_speedup = np.mean([r['speedup'] for r in results])

print("=" * 80)
print("RÉSUMÉ")
print("=" * 80)
print(f"Speedup moyen : {avg_speedup:.1f}×")
print()

if avg_speedup > 10:
    print("[OK] Gain significatif (>10×)")
elif avg_speedup > 5:
    print("[OK] Gain acceptable (>5×)")
else:
    print("[WARNING] Gain faible (<5×)")

print("\nImpact sur AGI :")
print(f"  Temps/iteration (baseline 32×32, 100 steps) : {results[0]['time_python']*4:.1f}s")
print(f"  Temps/iteration (vectorized)                 : {results[0]['time_vectorized']*4:.1f}s")
print(f"  10 iterations (baseline)                     : {results[0]['time_python']*4*10/60:.1f} min")
print(f"  10 iterations (vectorized)                   : {results[0]['time_vectorized']*4*10/60:.1f} min")




