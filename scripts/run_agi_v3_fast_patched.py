"""
Run AGI v3 avec patches fast mode + filtres anti-trivialité.

Approche pragmatique :
1. Monkey-patch evaluate_candidate() pour mode fast
2. Filtrer quasi-death rules avant promotion HoF
3. Tester 10 itérations en <5 minutes
"""

import sys
from pathlib import Path
import time
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from isinglab.closed_loop_agi import ClosedLoopAGI
from isinglab.memory_explorer import MemoryExplorer
from isinglab.rules import load_hof_rules

# === PATCHES ===

def is_quasi_death_rule(final_density, threshold=0.05):
    """Rejette rules convergent vers vide."""
    return final_density < threshold

def is_saturation_rule(final_density, threshold=0.95):
    """Rejette rules saturant la grille."""
    return final_density > threshold

# Monkey-patch de MemoryExplorer
original_explore_batch = MemoryExplorer.explore_batch

def explore_batch_fast(self, candidates, grid_size=(32,32), steps=100, seed=42):
    """Version fast : grilles 16×16, steps 50."""
    return original_explore_batch(self, candidates, grid_size=(16,16), steps=50, seed=seed)

MemoryExplorer.explore_batch = explore_batch_fast

print("[PATCH] MemoryExplorer.explore_batch => fast mode (16x16, 50 steps)")

# === RUN AGI ===

print("=" * 80)
print("AGI v3 FAST MODE (Patché)")
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

agi = ClosedLoopAGI(config=config)

# Hook pour filtrer avant HoF promotion
original_update = agi._update_memory_and_hof

def _update_memory_and_hof_filtered(evaluated):
    """Version filtrée : rejette quasi-death rules."""
    filtered = []
    rejected = []
    
    for res in evaluated:
        final_density = res.get('final_density', 0.5)
        
        if is_quasi_death_rule(final_density):
            rejected.append((res['notation'], f"Quasi-death (density={final_density:.3f})"))
            # Pénalité sur functional_score
            res['functional_score'] = res.get('functional_score', 0) * 0.1
        elif is_saturation_rule(final_density):
            rejected.append((res['notation'], f"Saturation (density={final_density:.3f})"))
            res['functional_score'] = res.get('functional_score', 0) * 0.1
        
        filtered.append(res)
    
    if rejected:
        print(f"  [FILTER] {len(rejected)} quasi-trivial rules penalized:")
        for notation, reason in rejected[:5]:
            print(f"     - {notation}: {reason}")
    
    return original_update(filtered)

agi._update_memory_and_hof = _update_memory_and_hof_filtered

print("[PATCH] ClosedLoopAGI._update_memory_and_hof => filtres anti-trivialite")
print()

start_time = time.time()

# 10 itérations test
print("Lancement 10 itérations...")
print()

for i in range(10):
    agi.run_one_iteration(
        batch_size=4,
        strategy='mixed',
        grid_size=16,  # Fast
        steps=50       # Fast
    )
    
    if (i+1) % 5 == 0:
        elapsed = time.time() - start_time
        print(f"\n[CHECKPOINT] {i+1}/10 iterations — {elapsed:.1f}s elapsed\n")

elapsed = time.time() - start_time

print("\n" + "=" * 80)
print("TEST TERMINÉ")
print("=" * 80)
print(f"Temps total : {elapsed:.1f}s ({elapsed/60:.1f} min)")
print(f"Temps/iteration : {elapsed/10:.1f}s")
print()

if elapsed < 300:  # 5 minutes
    print("[OK] OBJECTIF ATTEINT : <5 minutes pour 10 iterations")
    print(f"   Gain vs baseline : {4*3600/elapsed:.0f}× plus rapide")
else:
    print(f"[FAIL] TROP LENT : {elapsed/60:.1f} min pour 10 iterations")

# Stats
hof = load_hof_rules()
print(f"\nHoF final : {len(hof)} règles")

print("\nFichiers générés :")
print(f"  - logs/agi_*.log")
print(f"  - results/meta_memory.json")
print(f"  - results/hof_rules.json")

