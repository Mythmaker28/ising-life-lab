"""
Consolidation Brain Modules v3.5

Audit multi-seed des 8 modules v3.4 pour vérifier stabilité.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import json
from datetime import datetime

from isinglab.core.rule_ops import parse_notation
from isinglab.core.ca_vectorized import evolve_ca_vectorized
from isinglab.metrics.functional import (
    compute_life_pattern_capacity,
    compute_robustness_to_noise,
    compute_basin_size
)
from isinglab.meta_learner.filters import quick_density_test


BRAIN_MODULES_V3_4 = [
    # Tier 1
    {"notation": "B3/S23", "tier": 1, "role": "Compute / Mémoire propre"},
    {"notation": "B36/S23", "tier": 1, "role": "Réplication / Propagation"},
    {"notation": "B3/S234", "tier": 1, "role": "Life dense stable (backup)"},
    # Tier 2
    {"notation": "B34/S34", "tier": 2, "role": "Front-end robuste (preprocessing)"},
    {"notation": "B36/S234", "tier": 2, "role": "HighLife stabilisé"},
    # Tier 3
    {"notation": "B3/S2", "tier": 3, "role": "Life minimal"},
    {"notation": "B23/S23", "tier": 3, "role": "Variante exploratoire"},
    {"notation": "B34/S234", "tier": 3, "role": "Front-end ultra-robuste"}
]


def create_rule_func(notation):
    """Create vectorized rule function."""
    born, survive = parse_notation(notation)
    born_set, survive_set = set(born), set(survive)
    
    def rule_func(grid):
        return evolve_ca_vectorized(grid, born_set, survive_set, steps=1)
    
    return rule_func


def audit_module_stability(notation, n_seeds=5):
    """
    Audit stability across multiple seeds.
    
    Returns metrics with mean + std.
    """
    life_scores = []
    robustness_scores = []
    diversity_scores = []
    densities = []
    
    rule_func = create_rule_func(notation)
    
    for seed in range(n_seeds):
        # Life capacity
        np.random.seed(42 + seed)
        life_result = compute_life_pattern_capacity(rule_func, grid_size=(48, 48))
        life_scores.append(life_result['life_capacity_score'])
        
        # Robustness
        np.random.seed(42 + seed)
        rob_result = compute_robustness_to_noise(
            rule_func, grid_size=(32, 32), noise_level=0.2, n_trials=2, steps=50
        )
        robustness_scores.append(rob_result['robustness_score'])
        
        # Basin diversity
        np.random.seed(42 + seed)
        basin_result = compute_basin_size(rule_func, grid_size=(32, 32), n_samples=8, steps=50)
        diversity_scores.append(basin_result['basin_diversity'])
        
        # Density
        density = quick_density_test(notation, grid_size=(64, 64), steps=100, seed=42+seed)
        densities.append(density)
    
    return {
        'life_capacity': {
            'mean': float(np.mean(life_scores)),
            'std': float(np.std(life_scores)),
            'values': [float(x) for x in life_scores]
        },
        'robustness': {
            'mean': float(np.mean(robustness_scores)),
            'std': float(np.std(robustness_scores)),
            'values': [float(x) for x in robustness_scores]
        },
        'basin_diversity': {
            'mean': float(np.mean(diversity_scores)),
            'std': float(np.std(diversity_scores)),
            'values': [float(x) for x in diversity_scores]
        },
        'density': {
            'mean': float(np.mean(densities)),
            'std': float(np.std(densities)),
            'values': [float(x) for x in densities]
        }
    }


def classify_module(metrics):
    """Classify module based on metrics."""
    life_mean = metrics['life_capacity']['mean']
    rob_mean = metrics['robustness']['mean']
    div_mean = metrics['basin_diversity']['mean']
    dens_mean = metrics['density']['mean']
    
    # Hard filters
    if dens_mean < 0.05:
        return 'sink', 'Quasi-death'
    if dens_mean > 0.95:
        return 'sink', 'Saturation'
    
    # Classification
    if rob_mean > 0.9 and life_mean < 0.3:
        return 'stabilizer', 'Perfect robustness but low capacity'
    elif life_mean > 0.5:
        return 'brain_module', f'High life_capacity={life_mean:.2f}'
    elif life_mean > 0.4 and div_mean > 0.3:
        return 'brain_module', f'Good capacity + diversity'
    else:
        return 'unclassified', 'Mixed metrics'


def main():
    results = []
    
    print("="*80)
    print("CONSOLIDATION BRAIN MODULES v3.5")
    print("="*80)
    print()
    
    for module_info in BRAIN_MODULES_V3_4:
        notation = module_info['notation']
        print(f"\nAuditing {notation} (Tier {module_info['tier']})...")
        
        try:
            metrics = audit_module_stability(notation, n_seeds=5)
            category, reason = classify_module(metrics)
            
            result = {
                'notation': notation,
                'tier': module_info['tier'],
                'suggested_role': module_info['role'],
                'metrics': metrics,
                'classification': {
                    'category': category,
                    'reason': reason
                },
                'stable': metrics['life_capacity']['std'] < 0.15  # Stable if std < 0.15
            }
            
            results.append(result)
            
            print(f"  Life capacity: {metrics['life_capacity']['mean']:.3f} ± {metrics['life_capacity']['std']:.3f}")
            print(f"  Robustness: {metrics['robustness']['mean']:.3f} ± {metrics['robustness']['std']:.3f}")
            print(f"  Diversity: {metrics['basin_diversity']['mean']:.3f} ± {metrics['basin_diversity']['std']:.3f}")
            print(f"  Category: {category}")
            print(f"  Stable: {'✓' if result['stable'] else '✗'}")
        
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                'notation': notation,
                'tier': module_info['tier'],
                'error': str(e)
            })
    
    # Save results
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    
    output_data = {
        'meta': {
            'version': '3.5',
            'date': datetime.now().isoformat(),
            'n_seeds': 5
        },
        'modules': results
    }
    
    with open(output_dir / "brain_modules_v3_5.json", 'w') as f:
        json.dump(output_data, f, indent=2)
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    brain_modules = [r for r in results if r.get('classification', {}).get('category') == 'brain_module']
    stable_modules = [r for r in results if r.get('stable', False)]
    
    print(f"\nTotal modules tested: {len(results)}")
    print(f"Classified as brain_module: {len(brain_modules)}")
    print(f"Stable (std < 0.15): {len(stable_modules)}")
    
    if brain_modules:
        print("\nBrain modules (sorted by life_capacity):")
        brain_modules_sorted = sorted(
            brain_modules,
            key=lambda x: x['metrics']['life_capacity']['mean'],
            reverse=True
        )
        for bm in brain_modules_sorted:
            notation = bm['notation']
            life_cap = bm['metrics']['life_capacity']['mean']
            stable = "✓" if bm['stable'] else "✗"
            print(f"  {notation:12s}: life_cap={life_cap:.3f} stable={stable}")
    
    print(f"\nResults saved: results/brain_modules_v3_5.json")


if __name__ == "__main__":
    main()

