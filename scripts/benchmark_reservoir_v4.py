"""
Benchmark Reservoir Computing v4.0 — Évaluation complète.

Évalue les 5 brain modules CA vs baselines ML standards sur tâches canoniques RC.
"""

import json
import time
from pathlib import Path
from datetime import datetime
import numpy as np

from isinglab.brain_modules import BRAIN_MODULES, get_brain_rule_function
from isinglab.reservoir import (
    CAReservoir,
    generate_narma10,
    generate_narma20,
    generate_mackey_glass,
    generate_denoising_data,
    evaluate_narma,
    evaluate_mackey_glass,
    evaluate_denoising
)
from isinglab.reservoir.baselines import SimpleESN, SimpleMLP, LinearBaseline


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


def benchmark_brain_module(brain_name: str, task_name: str, task_data: dict, 
                          grid_size: tuple = (32, 32), steps: int = 50) -> dict:
    """
    Benchmark un brain module sur une tâche.
    
    Args:
        brain_name: Nom du module ("life", "highlife", etc.)
        task_name: Nom de la tâche ("narma10", "mackey_glass", "denoising")
        task_data: Données de la tâche
        grid_size: Taille de la grille CA
        steps: Nombre de steps d'évolution
    
    Returns:
        Dict avec résultats
    """
    print(f"  [{brain_name:12s}] {task_name:15s}...", end=' ', flush=True)
    start_time = time.time()
    
    try:
        # Créer réservoir CA
        rule_func = get_brain_rule_function(brain_name)
        reservoir = CAReservoir(
            rule_function=rule_func,
            grid_size=grid_size,
            steps=steps,
            input_encoder='spatial' if task_name != 'mackey_glass' else 'temporal',
            readout_type='ridge',
            alpha=1.0
        )
        
        # Évaluer selon la tâche
        if task_name == 'narma10':
            u, y = task_data['u'], task_data['y']
            results = evaluate_narma(reservoir, u, y, train_ratio=0.7)
        elif task_name == 'narma20':
            u, y = task_data['u'], task_data['y']
            results = evaluate_narma(reservoir, u, y, train_ratio=0.7)
        elif task_name == 'mackey_glass':
            y = task_data['y']
            results = evaluate_mackey_glass(reservoir, y, lookahead=1, train_ratio=0.7)
        elif task_name == 'denoising':
            X_noisy, y_clean = task_data['X_noisy'], task_data['y_clean']
            results = evaluate_denoising(reservoir, X_noisy, y_clean, train_ratio=0.7)
        else:
            raise ValueError(f"Unknown task: {task_name}")
        
        elapsed = time.time() - start_time
        results['elapsed_time'] = elapsed
        results['success'] = True
        
        # Métrique principale selon tâche
        if task_name in ['narma10', 'narma20', 'mackey_glass']:
            main_metric = 'nmse'
            main_value = results.get('nmse', float('inf'))
        else:  # denoising
            main_metric = 'accuracy'
            main_value = results.get('accuracy', 0.0)
        
        print(f"OK ({main_metric}={main_value:.4f}, t={elapsed:.2f}s)")
        
        return {
            'brain_name': brain_name,
            'task_name': task_name,
            'success': True,
            'main_metric': main_metric,
            'main_value': main_value,
            'results': results
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"FAILED ({str(e)[:50]})")
        return {
            'brain_name': brain_name,
            'task_name': task_name,
            'success': False,
            'error': str(e),
            'elapsed_time': elapsed
        }


def benchmark_baseline(baseline_name: str, baseline_model, task_name: str, 
                       task_data: dict) -> dict:
    """
    Benchmark un baseline ML sur une tâche.
    
    Args:
        baseline_name: Nom du baseline ("esn", "mlp", "linear")
        baseline_model: Instance du modèle baseline
        task_name: Nom de la tâche
        task_data: Données de la tâche
    
    Returns:
        Dict avec résultats
    """
    print(f"  [{baseline_name:12s}] {task_name:15s}...", end=' ', flush=True)
    start_time = time.time()
    
    try:
        # Préparer données selon la tâche
        if task_name == 'narma10':
            u, y = task_data['u'], task_data['y']
            n_train = int(len(u) * 0.7)
            
            X_train = []
            y_train = []
            for i in range(10, n_train - 1):
                X_train.append(u[max(0, i-9):i+1])
                y_train.append(y[i+1])
            
            X_test = []
            y_test = []
            for i in range(n_train, len(u) - 1):
                X_test.append(u[max(0, i-9):i+1])
                y_test.append(y[i+1])
            
            X_train = np.array(X_train)
            y_train = np.array(y_train)
            X_test = np.array(X_test)
            y_test = np.array(y_test)
            
            baseline_model.train(X_train, y_train)
            y_pred = baseline_model.predict(X_test)
            
            mse = np.mean((y_test - y_pred) ** 2)
            var_y = np.var(y_test)
            nmse = mse / var_y if var_y > 0 else float('inf')
            
            results = {
                'mse': mse,
                'nmse': nmse,
                'rmse': np.sqrt(mse),
                'mae': np.mean(np.abs(y_test - y_pred)),
                'correlation': np.corrcoef(y_test.flatten(), y_pred.flatten())[0, 1] if len(y_test) > 1 else 0.0
            }
            main_metric = 'nmse'
            main_value = nmse
            
        elif task_name == 'mackey_glass':
            y = task_data['y']
            n_train = int(len(y) * 0.7)
            window_size = 10
            
            X_train = []
            y_train = []
            for i in range(window_size, n_train - 1):
                X_train.append(y[i-window_size:i])
                y_train.append(y[i+1])
            
            X_test = []
            y_test = []
            for i in range(n_train, len(y) - 1):
                X_test.append(y[i-window_size:i])
                y_test.append(y[i+1])
            
            X_train = np.array(X_train)
            y_train = np.array(y_train)
            X_test = np.array(X_test)
            y_test = np.array(y_test)
            
            baseline_model.train(X_train, y_train)
            y_pred = baseline_model.predict(X_test)
            
            mse = np.mean((y_test - y_pred) ** 2)
            var_y = np.var(y_test)
            nmse = mse / var_y if var_y > 0 else float('inf')
            
            results = {
                'mse': mse,
                'nmse': nmse,
                'rmse': np.sqrt(mse),
                'mae': np.mean(np.abs(y_test - y_pred)),
                'correlation': np.corrcoef(y_test.flatten(), y_pred.flatten())[0, 1] if len(y_test) > 1 else 0.0
            }
            main_metric = 'nmse'
            main_value = nmse
            
        elif task_name == 'denoising':
            X_noisy, y_clean = task_data['X_noisy'], task_data['y_clean']
            n_train = int(len(X_noisy) * 0.7)
            
            X_train = X_noisy[:n_train]
            y_train = y_clean[:n_train]
            X_test = X_noisy[n_train:]
            y_test = y_clean[n_train:]
            
            baseline_model.train(X_train, y_train.reshape(len(y_train), -1))
            y_pred = baseline_model.predict(X_test)
            
            y_test_flat = y_test.reshape(len(y_test), -1)
            y_pred_binary = (y_pred > 0.5).astype(int)
            
            mse = np.mean((y_test_flat - y_pred) ** 2)
            accuracy = np.mean(y_test_flat == y_pred_binary)
            
            results = {
                'mse': mse,
                'rmse': np.sqrt(mse),
                'accuracy': accuracy,
                'mae': np.mean(np.abs(y_test_flat - y_pred))
            }
            main_metric = 'accuracy'
            main_value = accuracy
            
        else:
            raise ValueError(f"Unknown task: {task_name}")
        
        elapsed = time.time() - start_time
        results['elapsed_time'] = elapsed
        
        print(f"OK ({main_metric}={main_value:.4f}, t={elapsed:.2f}s)")
        
        return {
            'baseline_name': baseline_name,
            'task_name': task_name,
            'success': True,
            'main_metric': main_metric,
            'main_value': main_value,
            'results': results
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"FAILED ({str(e)[:50]})")
        return {
            'baseline_name': baseline_name,
            'task_name': task_name,
            'success': False,
            'error': str(e),
            'elapsed_time': elapsed
        }


def main():
    """
    Lance le benchmark complet.
    """
    print("=" * 80)
    print("RESERVOIR COMPUTING BENCHMARK v4.0")
    print("=" * 80)
    
    # Configuration
    grid_size = (32, 32)
    steps = 50
    seed = 42
    np.random.seed(seed)
    
    # Générer données de tâches
    print("\n[GENERATING TASK DATA]")
    print("  NARMA10...", end=' ', flush=True)
    u_narma10, y_narma10 = generate_narma10(n_samples=500, seed=seed)
    print("OK")
    
    print("  NARMA20...", end=' ', flush=True)
    u_narma20, y_narma20 = generate_narma20(n_samples=500, seed=seed)
    print("OK")
    
    print("  Mackey-Glass...", end=' ', flush=True)
    y_mg = generate_mackey_glass(n_samples=500, seed=seed)
    print("OK")
    
    print("  Denoising...", end=' ', flush=True)
    X_noisy, y_clean = generate_denoising_data(n_samples=100, grid_size=grid_size, 
                                               noise_level=0.2, seed=seed)
    print("OK")
    
    tasks = {
        'narma10': {'u': u_narma10, 'y': y_narma10},
        'narma20': {'u': u_narma20, 'y': y_narma20},
        'mackey_glass': {'y': y_mg},
        'denoising': {'X_noisy': X_noisy, 'y_clean': y_clean}
    }
    
    # Brain modules à tester
    brain_names = list(BRAIN_MODULES.keys())
    
    # Baselines à tester
    baselines = {
        'esn': SimpleESN(reservoir_size=100, seed=seed),
        'mlp': SimpleMLP(hidden_size=50, random_state=seed),
        'linear': LinearBaseline(alpha=1.0)
    }
    
    # Résultats
    all_results = {
        'timestamp': datetime.now().isoformat(),
        'config': {
            'grid_size': grid_size,
            'steps': steps,
            'seed': seed
        },
        'brain_results': [],
        'baseline_results': []
    }
    
    # Benchmark brain modules
    print(f"\n[BENCHMARKING BRAIN MODULES] ({len(brain_names)} modules)")
    for brain_name in brain_names:
        for task_name, task_data in tasks.items():
            result = benchmark_brain_module(brain_name, task_name, task_data, 
                                           grid_size, steps)
            all_results['brain_results'].append(result)
    
    # Benchmark baselines
    print(f"\n[BENCHMARKING BASELINES] ({len(baselines)} baselines)")
    for baseline_name, baseline_model in baselines.items():
        for task_name, task_data in tasks.items():
            result = benchmark_baseline(baseline_name, baseline_model, task_name, task_data)
            all_results['baseline_results'].append(result)
    
    # Sauvegarder résultats
    output_file = Path('results/brain_reservoir_bench_v4.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    all_results_converted = convert_numpy_types(all_results)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results_converted, f, indent=2)
    
    print(f"\n{'='*80}")
    print("BENCHMARK COMPLETE")
    print(f"{'='*80}")
    print(f"Results saved: {output_file}")
    
    # Tableau récapitulatif
    print(f"\n{'='*80}")
    print("SUMMARY — Main Metrics")
    print(f"{'='*80}")
    
    # Par tâche
    for task_name in tasks.keys():
        print(f"\n[{task_name.upper()}]")
        print(f"{'Model':20s} | {'Main Metric':15s} | {'Value':10s}")
        print("-" * 50)
        
        # Brain modules
        for result in all_results['brain_results']:
            if result['task_name'] == task_name and result['success']:
                print(f"{result['brain_name']:20s} | {result['main_metric']:15s} | "
                      f"{result['main_value']:10.4f}")
        
        # Baselines
        for result in all_results['baseline_results']:
            if result['task_name'] == task_name and result['success']:
                print(f"{result['baseline_name']:20s} | {result['main_metric']:15s} | "
                      f"{result['main_value']:10.4f}")
    
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()



