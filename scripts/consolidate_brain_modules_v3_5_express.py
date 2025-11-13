"""Express consolidation: 3 seeds instead of 5."""

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
    {"notation": "B3/S23", "tier": 1},
    {"notation": "B36/S23", "tier": 1},
    {"notation": "B3/S234", "tier": 1},
    {"notation": "B34/S34", "tier": 2},
    {"notation": "B36/S234", "tier": 2}
]


def create_rule_func(notation):
    born, survive = parse_notation(notation)
    born_set, survive_set = set(born), set(survive)
    
    def rule_func(grid):
        return evolve_ca_vectorized(grid, born_set, survive_set, steps=1)
    
    return rule_func


def audit_module_stability(notation, n_seeds=3):
    life_scores = []
    robustness_scores = []
    diversity_scores = []
    densities = []
    
    rule_func = create_rule_func(notation)
    
    for seed in range(n_seeds):
        np.random.seed(42 + seed)
        life_result = compute_life_pattern_capacity(rule_func, grid_size=(40, 40))
        life_scores.append(life_result['life_capacity_score'])
        
        np.random.seed(42 + seed)
        rob_result = compute_robustness_to_noise(
            rule_func, grid_size=(32, 32), noise_level=0.2, n_trials=2, steps=40
        )
        robustness_scores.append(rob_result['robustness_score'])
        
        np.random.seed(42 + seed)
        basin_result = compute_basin_size(rule_func, grid_size=(32, 32), n_samples=6, steps=40)
        diversity_scores.append(basin_result['basin_diversity'])
        
        density = quick_density_test(notation, grid_size=(48, 48), steps=80, seed=42+seed)
        densities.append(density)
    
    return {
        'life_capacity': {'mean': float(np.mean(life_scores)), 'std': float(np.std(life_scores))},
        'robustness': {'mean': float(np.mean(robustness_scores)), 'std': float(np.std(robustness_scores))},
        'basin_diversity': {'mean': float(np.mean(diversity_scores)), 'std': float(np.std(diversity_scores))},
        'density': {'mean': float(np.mean(densities)), 'std': float(np.std(densities))}
    }


def classify_module(metrics):
    life_mean = metrics['life_capacity']['mean']
    rob_mean = metrics['robustness']['mean']
    div_mean = metrics['basin_diversity']['mean']
    dens_mean = metrics['density']['mean']
    
    if dens_mean < 0.05:
        return 'sink', 'Quasi-death'
    if dens_mean > 0.95:
        return 'sink', 'Saturation'
    
    if rob_mean > 0.9 and life_mean < 0.3:
        return 'stabilizer', 'Perfect robustness but low capacity'
    elif life_mean > 0.5:
        return 'brain_module', f'High life_capacity={life_mean:.2f}'
    elif life_mean > 0.4 and div_mean > 0.3:
        return 'brain_module', f'Good capacity + diversity'
    else:
        return 'unclassified', 'Mixed metrics'


def main():
    print("EXPRESS CONSOLIDATION v3.5")
    print("="*60, flush=True)
    
    results = []
    
    for module_info in BRAIN_MODULES_V3_4:
        notation = module_info['notation']
        print(f"\nAuditing {notation}...", flush=True)
        
        try:
            metrics = audit_module_stability(notation, n_seeds=3)
            category, reason = classify_module(metrics)
            
            result = {
                'notation': notation,
                'tier': module_info['tier'],
                'metrics': metrics,
                'classification': {'category': category, 'reason': reason},
                'stable': metrics['life_capacity']['std'] < 0.15
            }
            
            results.append(result)
            
            print(f"  Life: {metrics['life_capacity']['mean']:.3f} ± {metrics['life_capacity']['std']:.3f}", flush=True)
            print(f"  Category: {category}", flush=True)
        
        except Exception as e:
            print(f"  ERROR: {e}", flush=True)
            results.append({'notation': notation, 'tier': module_info['tier'], 'error': str(e)})
    
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    
    output_data = {
        'meta': {
            'version': '3.5_express',
            'date': datetime.now().isoformat(),
            'n_seeds': 3
        },
        'modules': results
    }
    
    with open(output_dir / "brain_modules_v3_5.json", 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    brain_modules = [r for r in results if r.get('classification', {}).get('category') == 'brain_module']
    print(f"Brain modules: {len(brain_modules)}/{len(results)}")
    
    for bm in brain_modules:
        notation = bm['notation']
        life_cap = bm['metrics']['life_capacity']['mean']
        stable = "✓" if bm['stable'] else "✗"
        print(f"  {notation}: life_cap={life_cap:.3f} stable={stable}")
    
    print(f"\nSaved: results/brain_modules_v3_5.json", flush=True)


if __name__ == "__main__":
    main()

