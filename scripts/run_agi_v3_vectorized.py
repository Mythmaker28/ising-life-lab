"""
Run AGI v3 avec vectorisation NumPy intégrée.

Config :
- 20 itérations (validation performance)
- Fast mode : 16×16, 50 steps
- Filtres anti-trivialité : density [0.05, 0.95]
- Vectorisation : gain 29× attendu
"""

import sys
from pathlib import Path
import time
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from isinglab.closed_loop_agi import ClosedLoopAGI
from isinglab.rules import load_hof_rules

print("=" * 80)
print("AGI v3 VECTORIZED — VALIDATION PERFORMANCE")
print("=" * 80)
print()

config = {
    'evaluation_seed': 42,
    'hof_max_size': 25,
    'adaptive_thresholds': True,
    'hof_percentiles': {
        'composite_min': 85,
        'memory_score_min_abs': 0.01,
        'edge_score_min_abs': 0.05,
        'entropy_min_abs': 0.0
    },
    'diversity_threshold': 2
}

print("Config :")
print(f"  Iterations : 20")
print(f"  Grid size  : 16×16 (fast)")
print(f"  Steps      : 50 (fast)")
print(f"  Vectorized : ON (gain 29× attendu)")
print()

agi = ClosedLoopAGI(config=config)

# Filtrer quasi-death rules dans le pipeline
original_update = agi._update_memory_and_hof

def _update_filtered(evaluated):
    """Filtre quasi-death rules."""
    filtered = []
    rejected_count = 0
    
    for res in evaluated:
        final_density = res.get('final_density', 0.5)
        
        # Filtre : density hors [0.05, 0.95]
        if final_density < 0.05:
            res['functional_score'] = res.get('functional_score', 0) * 0.1
            rejected_count += 1
        elif final_density > 0.95:
            res['functional_score'] = res.get('functional_score', 0) * 0.1
            rejected_count += 1
        
        filtered.append(res)
    
    if rejected_count > 0:
        print(f"    [FILTER] {rejected_count} quasi-trivial rules penalized")
    
    return original_update(filtered)

agi._update_memory_and_hof = _update_filtered

start_time = time.time()

# 20 itérations
for i in range(20):
    agi.run_one_iteration(
        batch_size=4,
        strategy='mixed',
        grid_size=16,
        steps=50
    )
    
    if (i+1) % 5 == 0:
        elapsed = time.time() - start_time
        rate = elapsed / (i+1)
        eta = rate * (20 - i - 1)
        print(f"\n[{i+1}/20] {elapsed:.1f}s elapsed, {rate:.1f}s/iter, ETA {eta/60:.1f} min\n")

elapsed = time.time() - start_time

print("\n" + "=" * 80)
print("RÉSULTATS")
print("=" * 80)
print(f"Temps total      : {elapsed:.1f}s ({elapsed/60:.1f} min)")
print(f"Temps/iteration  : {elapsed/20:.1f}s")
print()

# Objectifs
if elapsed < 300:  # 5 minutes
    print("[OK] <5 min pour 20 iterations")
    print(f"     Gain vs baseline (4h/iter) : {4*3600/(elapsed/20):.0f}× plus rapide")
else:
    print(f"[FAIL] {elapsed/60:.1f} min pour 20 iterations")

# Stats
hof = load_hof_rules()
print(f"\nHoF final : {len(hof)} rules")

# Projection 50 iterations
time_50_iter = (elapsed/20) * 50
print(f"\nProjection 50 iterations : {time_50_iter/60:.1f} min")

# Sauvegarder rapport
report = {
    'meta': {
        'date': datetime.now().isoformat(),
        'iterations': 20,
        'vectorized': True,
        'fast_mode': True
    },
    'performance': {
        'total_time_seconds': elapsed,
        'time_per_iteration': elapsed/20,
        'projection_50_iter_minutes': time_50_iter/60,
        'speedup_vs_baseline': 4*3600/(elapsed/20)
    },
    'hof_size': len(hof)
}

output_file = Path("results") / "agi_v3_vectorized_report.json"
with open(output_file, 'w') as f:
    json.dump(report, f, indent=2)

print(f"\nRapport sauvegardé : {output_file}")
print("=" * 80)




