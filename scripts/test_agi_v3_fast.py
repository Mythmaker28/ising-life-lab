"""
Test AGI v3 Fast Mode

Objectif : Vérifier que 10 itérations tournent en <5 minutes.
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from isinglab.closed_loop_agi_v3_fast import ClosedLoopAGIv3

print("=" * 80)
print("TEST AGI v3 FAST MODE")
print("=" * 80)
print()

config = {
    'evaluation_seed': 42,
    'hof_max_size': 25,
    'adaptive_thresholds': True,
    'hof_percentiles': {
        'composite_min': 85,
    },
    'diversity_threshold': 2,
    # Filtres anti-trivialité
    'density_min': 0.05,
    'density_max': 0.95,
    'richness_min': 0.05
}

agi = ClosedLoopAGIv3(config=config)

start_time = time.time()

# 10 itérations test
agi.discover_rules(
    num_iterations=10,
    batch_size=4,
    strategy='mixed',
    grid_size=(16, 16),
    steps=50
)

elapsed = time.time() - start_time

print("\n" + "=" * 80)
print("TEST TERMINÉ")
print("=" * 80)
print(f"Temps total : {elapsed:.1f}s ({elapsed/60:.1f} min)")
print(f"Temps/iteration : {elapsed/10:.1f}s")
print()

if elapsed < 300:  # 5 minutes
    print("✅ OBJECTIF ATTEINT : <5 minutes pour 10 itérations")
else:
    print(f"❌ TROP LENT : {elapsed/60:.1f} min pour 10 itérations")
    print("   Recommendation : Implémenter vectorisation NumPy (niveau 2)")

print("\nFichiers générés :")
print("  - logs/agi_v3_*.log")
print("  - results/meta_memory.json")
print("  - results/hof_rules.json")

