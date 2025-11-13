"""Validation Cerveaux v3.1 — Stress-Tests Vectorisés

Teste les 3 cerveaux validés + B3/S234 :
- Multi-grilles (32×32, 64×64, 128×128)
- Multi-bruits (0%, 10%, 20%, 30%, 40%)
- Vectorisation activée
- Métriques complètes + life_pattern_capacity

Objectif : Confirmer robustesse + classifier B3/S234
"""

import json
import time
from pathlib import Path
from datetime import datetime
import numpy as np

from isinglab.memory_explorer import MemoryExplorer


def convert_numpy_types(obj):
    """Convertit récursivement les types NumPy en types Python natifs."""
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj
from isinglab.metrics.functional import (
    compute_memory_capacity,
    compute_robustness_to_noise,
    compute_basin_size,
    compute_functional_score,
    compute_life_pattern_capacity
)
from isinglab.core.ca_vectorized import create_rule_function_vectorized


def validate_brain(notation, born, survive, grid_sizes, noise_levels, vectorized=True):
    """
    Valide un cerveau CA sur plusieurs configurations.
    
    Returns:
        Dict avec résultats détaillés
    """
    print(f"\n{'='*64}")
    print(f"BRAIN: {notation}")
    print(f"{'='*64}")
    
    explorer = MemoryExplorer()
    
    if vectorized:
        rule_func = create_rule_function_vectorized(born, survive)
    else:
        rule_func = explorer._create_rule_function(born, survive)
    
    results = {
        'notation': notation,
        'born': born,
        'survive': survive,
        'vectorized': vectorized,
        'timestamp': datetime.now().isoformat(),
        'grid_tests': [],
        'noise_tests': [],
        'life_capacity': None,
        'summary': {}
    }
    
    # Test 1 : Multi-grilles (sans bruit)
    print(f"\n[GRID TESTS]")
    for grid_size in grid_sizes:
        print(f"  Grid {grid_size[0]}×{grid_size[1]}...", end=' ')
        start = time.time()
        
        # Métriques fonctionnelles
        capacity_result = compute_memory_capacity(
            rule_func, grid_size=grid_size, n_patterns=5, steps=50
        )
        robustness_result = compute_robustness_to_noise(
            rule_func, grid_size=grid_size, noise_level=0.1, n_trials=3, steps=50
        )
        basin_result = compute_basin_size(
            rule_func, grid_size=grid_size, n_samples=5, steps=30
        )
        
        functional = compute_functional_score(capacity_result, robustness_result, basin_result)
        elapsed = time.time() - start
        
        results['grid_tests'].append({
            'grid_size': grid_size,
            'capacity_score': capacity_result['capacity_score'],
            'robustness_score': robustness_result['robustness_score'],
            'basin_score': basin_result['basin_score'],
            'functional_score': functional,
            'elapsed_time': elapsed
        })
        
        print(f"OK (functional={functional:.3f}, t={elapsed:.2f}s)")
    
    # Test 2 : Multi-bruits (grille 32×32)
    print(f"\n[NOISE TESTS]")
    for noise_level in noise_levels:
        print(f"  Noise {int(noise_level*100)}%...", end=' ')
        start = time.time()
        
        robustness_result = compute_robustness_to_noise(
            rule_func, grid_size=(32, 32), noise_level=noise_level, n_trials=5, steps=50
        )
        elapsed = time.time() - start
        
        results['noise_tests'].append({
            'noise_level': noise_level,
            'robustness_score': robustness_result['robustness_score'],
            'elapsed_time': elapsed
        })
        
        print(f"OK (robustness={robustness_result['robustness_score']:.3f}, t={elapsed:.2f}s)")
    
    # Test 3 : Life Pattern Capacity (grille 32×32)
    print(f"\n[LIFE CAPACITY TEST]")
    start = time.time()
    life_capacity_result = compute_life_pattern_capacity(rule_func, grid_size=(32, 32))
    elapsed = time.time() - start
    
    results['life_capacity'] = {
        'life_capacity_score': life_capacity_result['life_capacity_score'],
        'patterns': life_capacity_result['patterns'],
        'elapsed_time': elapsed
    }
    
    print(f"  Life capacity score: {life_capacity_result['life_capacity_score']:.3f} (t={elapsed:.2f}s)")
    print(f"  Patterns working:")
    for name, pinfo in life_capacity_result['patterns'].items():
        status = "OK" if pinfo['survived'] else "DEAD"
        print(f"    [{status:4s}] {name:10s}: score={pinfo['score']:.2f}")
    
    # Summary
    avg_functional = np.mean([t['functional_score'] for t in results['grid_tests']])
    avg_robustness = np.mean([t['robustness_score'] for t in results['noise_tests']])
    
    results['summary'] = {
        'avg_functional_score': avg_functional,
        'avg_robustness_to_noise': avg_robustness,
        'life_capacity_score': life_capacity_result['life_capacity_score'],
        'total_elapsed_time': sum(t['elapsed_time'] for t in results['grid_tests']) +
                             sum(t['elapsed_time'] for t in results['noise_tests']) +
                             results['life_capacity']['elapsed_time']
    }
    
    print(f"\n[SUMMARY]")
    print(f"  Avg functional:      {avg_functional:.3f}")
    print(f"  Avg robustness:      {avg_robustness:.3f}")
    print(f"  Life capacity:       {life_capacity_result['life_capacity_score']:.3f}")
    print(f"  Total time:          {results['summary']['total_elapsed_time']:.2f}s")
    
    return results


def main():
    """
    Valide les 4 cerveaux candidats.
    """
    print("=" * 80)
    print("BRAIN VALIDATION v3.1 — Stress-Tests Vectorisés")
    print("=" * 80)
    
    # Configuration
    brains = [
        ('B3/S23', [3], [2, 3]),         # Life
        ('B36/S23', [3, 6], [2, 3]),     # HighLife
        ('B34/S34', [3, 4], [3, 4]),     # 34 Life
        ('B3/S234', [3], [2, 3, 4])      # Candidate à valider
    ]
    
    grid_sizes = [(32, 32), (64, 64), (128, 128)]
    noise_levels = [0.0, 0.1, 0.2, 0.3, 0.4]
    
    # Validation
    all_results = []
    
    for notation, born, survive in brains:
        result = validate_brain(notation, born, survive, grid_sizes, noise_levels, vectorized=True)
        all_results.append(result)
    
    # Sauvegarder (convertir types NumPy)
    output_file = Path('results/brain_validation_v3.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    all_results_converted = convert_numpy_types(all_results)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results_converted, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"VALIDATION COMPLETE")
    print(f"{'='*80}")
    print(f"Results saved: {output_file}")
    
    # Tableau récapitulatif
    print(f"\n{'='*80}")
    print("BRAIN COMPARISON")
    print(f"{'='*80}")
    print(f"{'Brain':12s} | {'Functional':10s} | {'Robustness':10s} | {'Life Cap':10s} | {'Time (s)':8s}")
    print("-" * 80)
    
    for result in all_results:
        notation = result['notation']
        summary = result['summary']
        print(f"{notation:12s} | {summary['avg_functional_score']:10.3f} | "
              f"{summary['avg_robustness_to_noise']:10.3f} | "
              f"{summary['life_capacity_score']:10.3f} | "
              f"{summary['total_elapsed_time']:8.2f}")
    
    print("=" * 80)


if __name__ == '__main__':
    main()

