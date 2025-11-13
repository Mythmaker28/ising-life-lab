"""
Benchmark Coût v5.0 — Mesure du coût computationnel 2D vs 3D.

Quantifie le coût pour établir un budget réaliste avant campagnes lourdes.
"""

import time
import json
from pathlib import Path
from datetime import datetime
import numpy as np

from isinglab.core.ca_vectorized import step_ca_vectorized, create_rule_function_vectorized
from isinglab.core.ca3d_vectorized import step_ca3d_vectorized, create_rule_function_3d


def benchmark_2d(grid_sizes, steps_list, rule_born, rule_survive, n_trials=3):
    """
    Benchmark CA 2D sur différentes tailles.
    
    Returns:
        Liste de résultats {grid_size, steps, time_per_update, n_cells}
    """
    results = []
    
    for grid_size in grid_sizes:
        h, w = grid_size
        n_cells = h * w
        
        for steps in steps_list:
            print(f"  2D {h}×{w}, {steps} steps...", end=' ', flush=True)
            
            # Moyenne sur n_trials
            times = []
            for trial in range(n_trials):
                grid = np.random.randint(0, 2, (h, w))
                
                start = time.time()
                current = grid.copy()
                for _ in range(steps):
                    current = step_ca_vectorized(current, set(rule_born), set(rule_survive))
                elapsed = time.time() - start
                
                times.append(elapsed)
            
            avg_time = np.mean(times)
            time_per_update = avg_time / steps
            
            results.append({
                'dimension': '2D',
                'grid_size': grid_size,
                'steps': steps,
                'n_cells': n_cells,
                'total_time': avg_time,
                'time_per_update': time_per_update,
                'n_trials': n_trials
            })
            
            print(f"OK (t={avg_time:.3f}s, {time_per_update*1000:.2f}ms/update)")
    
    return results


def benchmark_3d(grid_sizes, steps_list, rule_born, rule_survive, n_trials=3):
    """
    Benchmark CA 3D sur différentes tailles.
    
    Returns:
        Liste de résultats {grid_size, steps, time_per_update, n_cells}
    """
    results = []
    
    for grid_size in grid_sizes:
        d, h, w = grid_size
        n_cells = d * h * w
        
        for steps in steps_list:
            print(f"  3D {d}×{h}×{w}, {steps} steps...", end=' ', flush=True)
            
            # Moyenne sur n_trials
            times = []
            for trial in range(n_trials):
                grid = np.random.randint(0, 2, (d, h, w))
                
                start = time.time()
                current = grid.copy()
                for _ in range(steps):
                    current = step_ca3d_vectorized(current, set(rule_born), set(rule_survive))
                elapsed = time.time() - start
                
                times.append(elapsed)
            
            avg_time = np.mean(times)
            time_per_update = avg_time / steps
            
            results.append({
                'dimension': '3D',
                'grid_size': grid_size,
                'n_cells': n_cells,
                'steps': steps,
                'total_time': avg_time,
                'time_per_update': time_per_update,
                'n_trials': n_trials
            })
            
            print(f"OK (t={avg_time:.3f}s, {time_per_update*1000:.2f}ms/update)")
    
    return results


def fit_cost_model(results):
    """
    Fit modèle de coût : time_per_update = alpha * n_cells + beta
    
    Returns:
        Dict avec coefficients et prédictions
    """
    # Séparer 2D et 3D
    results_2d = [r for r in results if r['dimension'] == '2D']
    results_3d = [r for r in results if r['dimension'] == '3D']
    
    model = {}
    
    for dim, data in [('2D', results_2d), ('3D', results_3d)]:
        if not data:
            continue
        
        X = np.array([r['n_cells'] for r in data])
        y = np.array([r['time_per_update'] for r in data])
        
        # Régression linéaire simple
        A = np.vstack([X, np.ones(len(X))]).T
        alpha, beta = np.linalg.lstsq(A, y, rcond=None)[0]
        
        # Prédictions
        y_pred = alpha * X + beta
        mse = np.mean((y - y_pred) ** 2)
        
        model[dim] = {
            'alpha': float(alpha),
            'beta': float(beta),
            'mse': float(mse),
            'formula': f't = {alpha:.2e} * n_cells + {beta:.2e}'
        }
    
    return model


def estimate_budget(model, max_total_time=60.0):
    """
    Estime budget en nombre d'updates pour un temps max donné.
    
    Args:
        model: Modèle de coût
        max_total_time: Temps max en secondes (default: 60s = 1 min)
    
    Returns:
        Budget dict
    """
    budget = {}
    
    for dim in ['2D', '3D']:
        if dim not in model:
            continue
        
        alpha = model[dim]['alpha']
        beta = model[dim]['beta']
        
        # Pour différentes tailles
        sizes_examples = {
            '2D': [(64, 64), (128, 128), (256, 256)],
            '3D': [(16, 16, 16), (32, 32, 32), (48, 48, 48)]
        }
        
        if dim not in sizes_examples:
            continue
        
        budget[dim] = {}
        for size in sizes_examples[dim]:
            n_cells = np.prod(size)
            time_per_update = alpha * n_cells + beta
            max_updates = int(max_total_time / time_per_update) if time_per_update > 0 else 0
            
            budget[dim][str(size)] = {
                'n_cells': int(n_cells),
                'time_per_update_ms': float(time_per_update * 1000),
                'max_updates_in_60s': max_updates
            }
    
    return budget


def main():
    """
    Lance le benchmark complet et sauve résultats.
    """
    print("=" * 80)
    print("BENCHMARK COÛT v5.0 — 2D vs 3D")
    print("=" * 80)
    
    # Configuration
    rule_born_2d = [3]
    rule_survive_2d = [2, 3]
    
    rule_born_3d = [4]
    rule_survive_3d = [3, 4]
    
    # Tailles à tester
    grid_sizes_2d = [(64, 64), (128, 128), (256, 256)]
    grid_sizes_3d = [(16, 16, 16), (32, 32, 32)]  # Prudent pour 3D
    
    steps_list = [50, 100]
    n_trials = 3
    
    # Benchmark 2D
    print("\n[BENCHMARK 2D]")
    results_2d = benchmark_2d(grid_sizes_2d, steps_list, rule_born_2d, rule_survive_2d, n_trials)
    
    # Benchmark 3D
    print("\n[BENCHMARK 3D]")
    results_3d = benchmark_3d(grid_sizes_3d, steps_list, rule_born_3d, rule_survive_3d, n_trials)
    
    # Combiner
    all_results = results_2d + results_3d
    
    # Fit modèle
    print("\n[FITTING COST MODEL]")
    model = fit_cost_model(all_results)
    
    for dim, params in model.items():
        print(f"  {dim}: {params['formula']}")
        print(f"       MSE = {params['mse']:.2e}")
    
    # Estimer budget
    print("\n[ESTIMATING BUDGET]")
    budget = estimate_budget(model, max_total_time=60.0)
    
    for dim, sizes in budget.items():
        print(f"\n  {dim}:")
        for size, info in sizes.items():
            print(f"    {size}: {info['max_updates_in_60s']} updates/min "
                  f"({info['time_per_update_ms']:.2f}ms/update)")
    
    # Recommandation
    print("\n[RECOMMENDATION]")
    if '3D' in budget:
        max_3d_updates = max(v['max_updates_in_60s'] for v in budget['3D'].values())
        if max_3d_updates < 100:
            print("  WARNING: 3D est TRES COUTEUX (< 100 updates/min)")
            print("  -> Limiter 3D aux tests cibles uniquement")
        elif max_3d_updates < 500:
            print("  WARNING: 3D est COUTEUX (< 500 updates/min)")
            print("  -> Utiliser 3D avec parcimonie")
        else:
            print("  OK: 3D est ACCEPTABLE pour exploration moderee")
    
    # Sauvegarder
    output = {
        'timestamp': datetime.now().isoformat(),
        'rule_2d': {'born': rule_born_2d, 'survive': rule_survive_2d},
        'rule_3d': {'born': rule_born_3d, 'survive': rule_survive_3d},
        'results': all_results,
        'model': model,
        'budget': budget
    }
    
    output_file = Path('results/cost_model_v5.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n{'='*80}")
    print("BENCHMARK COMPLETE")
    print(f"{'='*80}")
    print(f"Results saved: {output_file}")


if __name__ == '__main__':
    main()

