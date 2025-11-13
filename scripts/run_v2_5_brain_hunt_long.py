"""
Campagne ClosedLoopAGI v2.5 - Brain Hunt Long Run

Objectif :
- 150 itérations (vs 50-100 habituelles)
- Strategy 'mixed' avec stable_bias activé
- Chercher si AGI découvre spontanément des cerveaux > classiques
- Comparer résultats finaux vs B3/S23, B36/S23, B34/S34

Config :
- Grilles 32×32 pour vitesse
- Seuil functional >= 0.30 (déjà en place)
- Percentile 85 (promotions raisonnables)
- Log détaillé every 10 iterations
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from isinglab.closed_loop_agi import ClosedLoopAGI

# Config
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
    'hof_max_size': 25,  # Augmenté légèrement
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
print("CLOSED LOOP AGI v2.5 - BRAIN HUNT LONG RUN")
print("=" * 80)
print(f"Start : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()
print("Config :")
print(f"  Iterations : 150")
print(f"  Strategy   : mixed (avec stable_bias)")
print(f"  Grid size  : 32x32")
print(f"  Percentile : {config['hof_percentiles']['composite_min']}")
print(f"  HoF max    : {config['hof_max_size']}")
print()

agi = ClosedLoopAGI(config=config)

# Lancer découverte
agi.discover_rules(
    num_iterations=150,
    batch_size=3,
    strategy='mixed',  # Utilise bandit avec stable_bias
    grid_size=(32, 32),
    steps=100
)

# Export final
hof = agi.aggregator.hof_rules
meta_memory = agi.meta_memory

print("\n" + "=" * 80)
print("RÉSULTATS FINAUX")
print("=" * 80)
print(f"HoF final : {len(hof)} règles")
print(f"Meta memory : {len(meta_memory)} règles évaluées")

# Analyse rapide
profiles_count = {}
for rule in hof:
    profile = rule.get('module_profile', 'unknown')
    profiles_count[profile] = profiles_count.get(profile, 0) + 1

print("\nDistribution profils HoF :")
for profile, count in sorted(profiles_count.items(), key=lambda x: -x[1]):
    print(f"  {profile:<25} : {count}")

# Chercher si découvertes AGI classées "cerveaux"
print("\nRègles cerveaux potentielles (stable_memory, robust_memory, diverse_memory) :")
brain_candidates = [r for r in hof if r.get('module_profile') in ['stable_memory', 'robust_memory', 'diverse_memory']]

for rule in brain_candidates[:10]:  # Top 10
    notation = rule['notation']
    profile = rule.get('module_profile', 'unknown')
    scores = rule.get('scores', {})
    functional = scores.get('functional_score', 0.0)
    composite = scores.get('composite', 0.0)
    print(f"  {notation:<15} | {profile:<20} | func {functional:.3f} | comp {composite:.3f}")

# Sauvegarder rapport
report = {
    'meta': {
        'date': datetime.now().isoformat(),
        'iterations': 150,
        'strategy': 'mixed',
        'hof_size': len(hof),
        'meta_memory_size': len(meta_memory)
    },
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

output_file = Path("results") / "brain_hunt_long_v2_5.json"
with open(output_file, 'w') as f:
    json.dump(report, f, indent=2)

print(f"\n{'-' * 80}")
print(f"Rapport sauvegardé : {output_file}")
print(f"End : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

