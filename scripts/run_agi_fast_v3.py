"""
AGI Fast Mode v3 — Réparation + Mode Rapide

Objectif : 50 itérations en <30 minutes avec filtres anti-trivialité.

Correctifs :
1. Implémente boucle manquante (discover_rules n'existait pas !)
2. Mode fast activé (16×16, steps=50, métriques réduites)
3. Filtres anti-trivialité appliqués
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from isinglab.closed_loop_agi import ClosedLoopAGI

# Config optimisée
config = {
    'evaluation_seed': 42,
    'use_pareto': False,
    'profile_stability_min': 0.67,
    'hof_profile_quotas': {
        'stable_memory': 4,
        'robust_memory': 4,
        'diverse_memory': 4,
        'chaotic_probe': 4,
        'sensitive_detector': 4,
        'attractor_dominant': 2,
        'generic': 2
    },
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

print("=" * 80)
print("AGI FAST MODE v3 — 50 Itérations Rapides")
print("=" * 80)
print(f"Start : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()
print("Config :")
print(f"  Iterations : 50")
print(f"  Batch size : 3")
print(f"  Grid size  : 16x16 (mode fast)")
print(f"  Steps      : 50 (mode fast)")
print(f"  Strategy   : mixed")
print()

agi = ClosedLoopAGI(config=config)

# === BOUCLE MANQUANTE (réparée) ===
num_iterations = 50
batch_size = 3
strategy = 'mixed'

import time

all_summaries = []

for iteration in range(1, num_iterations + 1):
    print(f"\n{'='*80}")
    print(f"ITERATION {iteration}/{num_iterations}")
    print(f"{'='*80}")
    
    iter_start = time.time()
    
    # Mode fast : grilles 16×16, steps 50
    summary = agi.run_one_iteration(
        batch_size=batch_size,
        strategy=strategy,
        grid_size=16,  # Mode fast
        steps=50       # Mode fast
    )
    
    iter_time = time.time() - iter_start
    
    summary['iteration'] = iteration
    summary['iteration_time_seconds'] = iter_time
    all_summaries.append(summary)
    
    print(f"\nIteration {iteration} completed in {iter_time:.1f}s")
    print(f"  Promotions : {summary['new_rules_added']}")
    print(f"  Total HoF  : {summary['total_hof_rules']}")
    print(f"  Memory size: {summary['total_memory_rules']}")
    
    # Break early si temps estimé > 1h
    if iteration >= 10:
        avg_time = sum(s['iteration_time_seconds'] for s in all_summaries) / len(all_summaries)
        estimated_total = avg_time * num_iterations
        if estimated_total > 3600:  # > 1h
            print(f"\n[WARNING] Estimated total time: {estimated_total/60:.1f} min (> 60 min)")
            print(f"Breaking early at iteration {iteration}")
            break

# Export final
hof = agi.aggregator.hof_rules
meta_memory = agi.meta_memory

print("\n" + "=" * 80)
print("RÉSULTATS FINAUX")
print("=" * 80)
print(f"Iterations completed : {len(all_summaries)}")
print(f"HoF final : {len(hof)} règles")
print(f"Meta memory : {len(meta_memory)} règles évaluées")

# Timing stats
total_time = sum(s['iteration_time_seconds'] for s in all_summaries)
avg_time = total_time / len(all_summaries)
print(f"\nTiming :")
print(f"  Total time   : {total_time/60:.1f} minutes")
print(f"  Avg/iteration: {avg_time:.1f} seconds")

# Analyse rapide
profiles_count = {}
for rule in hof:
    profile = rule.get('module_profile', 'unknown')
    profiles_count[profile] = profiles_count.get(profile, 0) + 1

print("\nDistribution profils HoF :")
for profile, count in sorted(profiles_count.items(), key=lambda x: -x[1]):
    print(f"  {profile:<25} : {count}")

# Chercher si découvertes intéressantes
print("\nRègles HoF avec functional >= 0.40 (cerveaux potentiels) :")
brain_candidates = []
for rule in hof:
    func = rule.get('scores', {}).get('functional_score', 0)
    if func >= 0.40:
        brain_candidates.append(rule)

if brain_candidates:
    for rule in sorted(brain_candidates, key=lambda r: r.get('scores', {}).get('functional_score', 0), reverse=True)[:10]:
        notation = rule['notation']
        scores = rule.get('scores', {})
        func = scores.get('functional_score', 0)
        rob = scores.get('robustness_score', 0)
        cap = scores.get('capacity_score', 0)
        print(f"  {notation:<15} | func {func:.3f} | rob {rob:.3f} | cap {cap:.3f}")
else:
    print("  Aucune règle avec functional >= 0.40")

# Sauvegarder rapport
report = {
    'meta': {
        'date': datetime.now().isoformat(),
        'iterations_completed': len(all_summaries),
        'iterations_planned': num_iterations,
        'total_time_seconds': total_time,
        'avg_time_per_iteration': avg_time,
        'mode': 'fast',
        'grid_size': 16,
        'steps': 50
    },
    'summaries': all_summaries,
    'profiles_distribution': profiles_count,
    'brain_candidates': [
        {
            'notation': r['notation'],
            'profile': r.get('module_profile'),
            'scores': r.get('scores')
        }
        for r in brain_candidates[:20]
    ]
}

output_file = Path("results") / "agi_fast_v3_report.json"
with open(output_file, 'w') as f:
    json.dump(report, f, indent=2)

print(f"\n{'-' * 80}")
print(f"Rapport sauvegardé : {output_file}")
print(f"End : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

