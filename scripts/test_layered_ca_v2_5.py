"""
Test expérimental des Layered CA v0.1.

Objectif : Tester si combiner 2 règles CA complémentaires donne :
- Meilleure robustesse que règles isolées
- Stabilité équivalente ou supérieure
- Patterns émergents intéressants

Paires testées :
1. B3/S23 (stable, fragile) + B34/S34 (robuste) → Cerveau hybride stable+robuste ?
2. B36/S23 (replication) + B018/S1236 (robuste instable) → Backup + sonde ?
"""

import sys
import json
import numpy as np
from pathlib import Path

# Import layered CA
sys.path.insert(0, str(Path(__file__).parent.parent))
from isinglab.experimental.layered_ca import test_layered_combination

# Configurations de test
PAIRS = [
    ("B3/S23", "B34/S34", ["none", "density_mask"]),
    ("B36/S23", "B018/S1236", ["none", "density_mask"]),
    ("B34/S34", "B018/S1236", ["none"])  # Bonus : 2 robustes
]

GRID_SIZE = (64, 64)
STEPS = 200
RUNS_PER_CONFIG = 3  # Répétitions pour stats

results = []

print("=" * 80)
print("LAYERED CA EXPERIMENTS v2.5")
print("=" * 80)
print(f"Config : grid {GRID_SIZE}, steps {STEPS}, runs {RUNS_PER_CONFIG}")
print()

for rule_a, rule_b, couplings in PAIRS:
    print(f"\n### Pair : {rule_a} + {rule_b}")
    print("-" * 60)
    
    for coupling in couplings:
        print(f"  Coupling : {coupling}")
        
        run_results = []
        for run_idx in range(RUNS_PER_CONFIG):
            seed = 42 + run_idx
            result = test_layered_combination(
                rule_a, rule_b,
                grid_size=GRID_SIZE,
                steps=STEPS,
                coupling=coupling,
                seed=seed
            )
            run_results.append(result)
            print(f"    Run {run_idx+1} : density_a={result['final_density_a']:.3f}, "
                  f"density_b={result['final_density_b']:.3f}, "
                  f"corr={result['correlation']:.3f}")
        
        # Agréger stats
        avg_density_a = np.mean([r['final_density_a'] for r in run_results])
        avg_density_b = np.mean([r['final_density_b'] for r in run_results])
        avg_corr = np.mean([r['correlation'] for r in run_results])
        
        agg_result = {
            'rule_a': rule_a,
            'rule_b': rule_b,
            'coupling': coupling,
            'avg_density_a': float(avg_density_a),
            'avg_density_b': float(avg_density_b),
            'avg_correlation': float(avg_corr),
            'runs': run_results
        }
        
        results.append(agg_result)
        
        print(f"    Moyenne : density_a={avg_density_a:.3f}, "
              f"density_b={avg_density_b:.3f}, corr={avg_corr:.3f}")

# Sauvegarder résultats
output_file = Path("results") / "layered_ca_experiments_v2_5.json"
with open(output_file, 'w') as f:
    json.dump({
        'meta': {
            'grid_size': GRID_SIZE,
            'steps': STEPS,
            'runs_per_config': RUNS_PER_CONFIG,
            'pairs_tested': len(PAIRS)
        },
        'results': results
    }, f, indent=2)

print("\n" + "=" * 80)
print("ANALYSE DES RÉSULTATS")
print("=" * 80)

# Critères d'évaluation heuristiques
print("\nCritères d'évaluation :")
print("- Densité stable (0.05-0.50) : ni mort ni explosion")
print("- Corrélation faible/modérée (0.0-0.6) : couches distinctes")
print("- Densité_A > Densité_B : couche A domine (souhaité)")

for res in results:
    rule_a = res['rule_a']
    rule_b = res['rule_b']
    coupling = res['coupling']
    dens_a = res['avg_density_a']
    dens_b = res['avg_density_b']
    corr = res['avg_correlation']
    
    print(f"\n{rule_a} + {rule_b} ({coupling})")
    
    # Évaluation heuristique
    stable_a = 0.05 <= dens_a <= 0.50
    stable_b = 0.05 <= dens_b <= 0.50
    distinct = corr < 0.6
    a_dominates = dens_a > dens_b * 1.2
    
    score = sum([stable_a, stable_b, distinct, a_dominates])
    
    print(f"  Stable A : {'[OK]' if stable_a else '[NO]'} (density {dens_a:.3f})")
    print(f"  Stable B : {'[OK]' if stable_b else '[NO]'} (density {dens_b:.3f})")
    print(f"  Distinct : {'[OK]' if distinct else '[NO]'} (corr {corr:.3f})")
    print(f"  A domine : {'[OK]' if a_dominates else '[NO]'}")
    print(f"  Score    : {score}/4")
    
    # Verdict
    if score >= 3:
        verdict = "PROMETTEUR - mérite validation approfondie"
    elif score == 2:
        verdict = "INTÉRESSANT - comportement stable mais pas optimal"
    else:
        verdict = "NON-CONCLUSIF - instable ou redondant"
    
    print(f"  Verdict  : {verdict}")

print("\n" + "=" * 80)
print(f"Résultats sauvegardés : {output_file}")
print("=" * 80)

