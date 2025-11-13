"""Investigation Approfondie Top Candidats v3.3

CIBLES: B6/S23 et B3/S2345

Ces 2 règles ont les meilleurs functional_scores trouvés dans le voisinage.
Investigation: multi-grilles étendues, multi-bruits, patterns détaillés.
"""

import json
import time
from pathlib import Path
from datetime import datetime
import numpy as np

from isinglab.core.ca_vectorized import create_rule_function_vectorized
from isinglab.metrics.functional import (
    compute_memory_capacity,
    compute_robustness_to_noise,
    compute_basin_size,
    compute_functional_score,
    compute_life_pattern_capacity
)


def deep_investigate(notation, born, survive):
    """Investigation complète d'une règle candidate."""
    print(f"\n{'='*80}")
    print(f"DEEP INVESTIGATION: {notation}")
    print(f"{'='*80}")
    
    rule_func = create_rule_function_vectorized(born, survive)
    
    report = {
        'notation': notation,
        'born': born,
        'survive': survive,
        'timestamp': datetime.now().isoformat(),
        'tests': {}
    }
    
    # Test 1: Multi-grilles étendues
    print("\n[TEST 1] Multi-Grids Performance")
    grids = [(16,16), (32,32), (64,64), (128,128), (256,256)]
    
    for grid_size in grids:
        print(f"  Grid {grid_size[0]}x{grid_size[1]}...", end=' ')
        start = time.time()
        
        capacity_result = compute_memory_capacity(
            rule_func, grid_size=grid_size, n_patterns=10, steps=100
        )
        robustness_result = compute_robustness_to_noise(
            rule_func, grid_size=grid_size, noise_level=0.2, n_trials=5, steps=100
        )
        basin_result = compute_basin_size(
            rule_func, grid_size=grid_size, n_samples=10, steps=50
        )
        
        functional = compute_functional_score(capacity_result, robustness_result, basin_result)
        elapsed = time.time() - start
        
        print(f"func={functional:.3f}, time={elapsed:.2f}s")
        
        report['tests'][f'grid_{grid_size[0]}x{grid_size[1]}'] = {
            'capacity_score': capacity_result['capacity_score'],
            'robustness_score': robustness_result['robustness_score'],
            'basin_score': basin_result['basin_score'],
            'basin_diversity': basin_result['basin_diversity'],
            'functional_score': functional,
            'elapsed_time': elapsed
        }
    
    # Test 2: Multi-bruits étendus (grille 64×64)
    print("\n[TEST 2] Noise Resilience (64x64)")
    noise_levels = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
    
    noise_results = []
    for noise_level in noise_levels:
        robustness_result = compute_robustness_to_noise(
            rule_func, grid_size=(64, 64), noise_level=noise_level, n_trials=5, steps=100
        )
        rob_score = robustness_result['robustness_score']
        noise_results.append({'noise_level': noise_level, 'robustness_score': rob_score})
        print(f"  Noise {int(noise_level*100):3d}%: robustness={rob_score:.3f}")
    
    report['tests']['noise_resilience'] = noise_results
    
    # Test 3: Life patterns détaillés (64×64)
    print("\n[TEST 3] Life Patterns Capacity (64x64)")
    life_capacity_result = compute_life_pattern_capacity(rule_func, grid_size=(64, 64))
    
    report['tests']['life_patterns_64x64'] = life_capacity_result
    
    print(f"  Global life_capacity: {life_capacity_result['life_capacity_score']:.3f}")
    for name, pinfo in life_capacity_result['patterns'].items():
        status = "ALIVE" if pinfo['survived'] else "DEAD"
        period = "OK" if pinfo['found_period'] else "NO"
        print(f"    {name:10s}: {status:5s}, period={period:3s}, score={pinfo['score']:.2f}")
    
    # Test 4: Échantillonnage dynamique (observer évolution sur temps long)
    print("\n[TEST 4] Long-Term Dynamics (64x64, 500 steps)")
    grid_size = (64, 64)
    np.random.seed(42)
    grid = (np.random.rand(*grid_size) < 0.3).astype(int)
    
    densities = []
    entropies = []
    
    for step in range(0, 500, 10):
        for _ in range(10):
            grid = rule_func(grid)
        
        density = grid.mean()
        densities.append(density)
        
        # Entropie simple (diversité locale 3×3)
        local_patterns = set()
        for i in range(0, grid_size[0]-2):
            for j in range(0, grid_size[1]-2):
                patch = grid[i:i+3, j:j+3]
                local_patterns.add(patch.tobytes())
        entropy = len(local_patterns) / ((grid_size[0]-2) * (grid_size[1]-2))
        entropies.append(entropy)
    
    report['tests']['long_term_dynamics'] = {
        'steps': 500,
        'densities': densities,
        'entropies': entropies,
        'final_density': densities[-1],
        'avg_density': np.mean(densities),
        'std_density': np.std(densities),
        'final_entropy': entropies[-1],
        'avg_entropy': np.mean(entropies)
    }
    
    print(f"  Final density: {densities[-1]:.3f}")
    print(f"  Avg density: {np.mean(densities):.3f} ± {np.std(densities):.3f}")
    print(f"  Final entropy: {entropies[-1]:.3f}")
    print(f"  Avg entropy: {np.mean(entropies):.3f}")
    
    # Summary
    avg_functional = np.mean([
        report['tests'][f'grid_{gs}x{gs}']['functional_score']
        for gs in [16, 32, 64, 128]
    ])
    
    print(f"\n[SUMMARY]")
    print(f"  Avg functional (multi-grid): {avg_functional:.3f}")
    print(f"  Life capacity (64x64): {life_capacity_result['life_capacity_score']:.3f}")
    print(f"  Long-term stable: {'YES' if np.std(densities) < 0.05 else 'NO'}")
    
    report['summary'] = {
        'avg_functional_multiGrid': avg_functional,
        'life_capacity_64x64': life_capacity_result['life_capacity_score'],
        'long_term_stable': np.std(densities) < 0.05
    }
    
    return report


def main():
    """Investigate top 2 candidates."""
    print("="*80)
    print("DEEP INVESTIGATION — TOP CANDIDATES v3.3")
    print("="*80)
    
    candidates = [
        ('B6/S23', [6], [2, 3]),
        ('B3/S2345', [3], [2, 3, 4, 5])
    ]
    
    reports = []
    
    for notation, born, survive in candidates:
        report = deep_investigate(notation, born, survive)
        reports.append(report)
    
    # Sauvegarder
    output = {
        'meta': {
            'timestamp': datetime.now().isoformat(),
            'version': 'v3.3_deep',
            'candidates_investigated': len(candidates)
        },
        'investigations': reports
    }
    
    output_file = Path('results/deep_investigation_v3_3.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"INVESTIGATION COMPLETE")
    print(f"{'='*80}")
    print(f"Results saved: {output_file}")
    print("="*80)


if __name__ == '__main__':
    main()




