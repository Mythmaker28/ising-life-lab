"""
Test Tâches Temporelles v5.0 — Propagation/réparation temporelle.

Teste si CA aident à lisser/prolonger signaux spatio-temporels.
"""

import time
import json
from pathlib import Path
from datetime import datetime
import numpy as np
from sklearn.metrics import mean_squared_error

from isinglab.brain_modules import get_brain_rule_function


def generate_propagating_patterns(n_samples=50, grid_size=(64, 64), n_frames=10, seed=42):
    """
    Génère patterns qui se propagent dans le temps.
    
    Returns:
        sequences: (n_samples, n_frames, h, w)
    """
    np.random.seed(seed)
    h, w = grid_size
    sequences = []
    
    for _ in range(n_samples):
        seq = []
        # Point de départ
        pattern = np.zeros((h, w))
        cx, cy = h // 2, w // 2
        pattern[cx-2:cx+3, cy-2:cy+3] = 1
        seq.append(pattern.copy())
        
        # Propagation simple (diffusion)
        for frame in range(1, n_frames):
            # Dilater légèrement
            new_pattern = pattern.copy()
            for i in range(1, h-1):
                for j in range(1, w-1):
                    if pattern[i, j] == 0 and np.sum(pattern[i-1:i+2, j-1:j+2]) >= 3:
                        new_pattern[i, j] = 1
            pattern = new_pattern
            seq.append(pattern.copy())
        
        sequences.append(np.array(seq))
    
    return np.array(sequences)


def test_temporal_prediction(brain_name, sequences, steps=5):
    """
    Teste si CA aide à prédire frame suivante.
    
    Stratégie : CA + readout linéaire vs readout seul.
    """
    rule_func = get_brain_rule_function(brain_name)
    
    X = []
    y = []
    
    # Préparer données : frame t → frame t+1
    for seq in sequences:
        for t in range(len(seq) - 1):
            current_frame = seq[t]
            next_frame = seq[t + 1]
            
            # Feature : frame après évolution CA
            evolved = current_frame.copy()
            for _ in range(steps):
                evolved = rule_func(evolved)
            
            X.append(evolved.flatten())
            y.append(next_frame.flatten())
    
    X = np.array(X)
    y = np.array(y)
    
    # Split
    n_train = int(len(X) * 0.7)
    X_train, X_test = X[:n_train], X[n_train:]
    y_train, y_test = y[:n_train], y[n_train:]
    
    # Readout linéaire
    from sklearn.linear_model import Ridge
    model = Ridge(alpha=1.0)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    # Binariser
    y_pred_binary = (y_pred > 0.5).astype(int)
    
    # Métrique
    mse = mean_squared_error(y_test, y_pred)
    acc = np.mean(y_test == y_pred_binary)
    
    return {
        'mse': mse,
        'accuracy': acc,
        'method': f'CA_{brain_name}_readout'
    }


def test_temporal_baseline(sequences):
    """
    Baseline : readout linéaire direct (sans CA).
    """
    X = []
    y = []
    
    for seq in sequences:
        for t in range(len(seq) - 1):
            X.append(seq[t].flatten())
            y.append(seq[t + 1].flatten())
    
    X = np.array(X)
    y = np.array(y)
    
    # Split
    n_train = int(len(X) * 0.7)
    X_train, X_test = X[:n_train], X[n_train:]
    y_train, y_test = y[:n_train], y[n_train:]
    
    # Readout linéaire
    from sklearn.linear_model import Ridge
    model = Ridge(alpha=1.0)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    y_pred_binary = (y_pred > 0.5).astype(int)
    
    mse = mean_squared_error(y_test, y_pred)
    acc = np.mean(y_test == y_pred_binary)
    
    return {
        'mse': mse,
        'accuracy': acc,
        'method': 'Baseline_readout'
    }


def test_temporal_smoothing(brain_name, sequences, steps=3):
    """
    Teste si CA lisse bruit temporel.
    """
    rule_func = get_brain_rule_function(brain_name)
    
    # Ajouter bruit temporel
    noisy_sequences = []
    for seq in sequences:
        noisy_seq = []
        for frame in seq:
            # Flip 10% pixels aléatoirement
            noisy = frame.copy()
            noise_mask = np.random.rand(*frame.shape) < 0.1
            noisy[noise_mask] = 1 - noisy[noise_mask]
            noisy_seq.append(noisy)
        noisy_sequences.append(np.array(noisy_seq))
    noisy_sequences = np.array(noisy_sequences)
    
    # Lisser avec CA
    smoothed = []
    for seq in noisy_sequences:
        smoothed_seq = []
        for frame in seq:
            evolved = frame.copy()
            for _ in range(steps):
                evolved = rule_func(evolved)
            smoothed_seq.append(evolved)
        smoothed.append(np.array(smoothed_seq))
    smoothed = np.array(smoothed)
    
    # Métrique : similarité avec original
    mse = mean_squared_error(sequences.flatten(), smoothed.flatten())
    acc = np.mean(sequences.flatten() == smoothed.flatten())
    
    return {
        'mse': mse,
        'accuracy': acc,
        'method': f'CA_{brain_name}_smoothing'
    }


def test_baseline_smoothing(sequences):
    """
    Baseline : filtre médian temporel.
    """
    from scipy.ndimage import median_filter
    
    # Ajouter bruit
    noisy_sequences = []
    for seq in sequences:
        noisy_seq = []
        for frame in seq:
            noisy = frame.copy()
            noise_mask = np.random.rand(*frame.shape) < 0.1
            noisy[noise_mask] = 1 - noisy[noise_mask]
            noisy_seq.append(noisy)
        noisy_sequences.append(np.array(noisy_seq))
    noisy_sequences = np.array(noisy_sequences)
    
    # Lisser avec median
    smoothed = []
    for seq in noisy_sequences:
        smoothed_seq = []
        for frame in seq:
            smooth = median_filter(frame, size=3)
            smoothed_seq.append(smooth)
        smoothed.append(np.array(smoothed_seq))
    smoothed = np.array(smoothed)
    
    mse = mean_squared_error(sequences.flatten(), smoothed.flatten())
    acc = np.mean(sequences.flatten() == (smoothed > 0.5).astype(int).flatten())
    
    return {
        'mse': mse,
        'accuracy': acc,
        'method': 'Baseline_median_temporal'
    }


def main():
    """
    Lance tests temporels pour brain modules.
    """
    print("=" * 80)
    print("TEST TACHES TEMPORELLES v5.0")
    print("=" * 80)
    
    # Configuration
    grid_size = (64, 64)
    n_samples = 50
    n_frames = 10
    seed = 42
    np.random.seed(seed)
    
    # Générer données
    print("\n[GENERATING DATA]")
    print("  Propagating patterns...", end=' ', flush=True)
    sequences = generate_propagating_patterns(n_samples, grid_size, n_frames, seed)
    print(f"OK ({len(sequences)} sequences, {n_frames} frames each)")
    
    # Brain modules
    brain_names = ['life', 'highlife', 'life_dense', '34life']
    
    # Résultats
    all_results = {
        'timestamp': datetime.now().isoformat(),
        'config': {
            'grid_size': grid_size,
            'n_samples': n_samples,
            'n_frames': n_frames,
            'seed': seed
        },
        'prediction': [],
        'smoothing': []
    }
    
    # Test 1 : Prédiction temporelle
    print("\n[TEST 1: PREDICTION FRAME SUIVANTE]")
    
    for brain_name in brain_names:
        print(f"  CA {brain_name:12s} + readout...", end=' ', flush=True)
        start = time.time()
        result = test_temporal_prediction(brain_name, sequences, steps=5)
        result['elapsed'] = time.time() - start
        all_results['prediction'].append(result)
        print(f"acc={result['accuracy']:.3f}, mse={result['mse']:.4f} (t={result['elapsed']:.2f}s)")
    
    # Baseline
    print(f"  Baseline readout...", end=' ', flush=True)
    start = time.time()
    result = test_temporal_baseline(sequences)
    result['elapsed'] = time.time() - start
    all_results['prediction'].append(result)
    print(f"acc={result['accuracy']:.3f}, mse={result['mse']:.4f} (t={result['elapsed']:.2f}s)")
    
    # Test 2 : Lissage temporel
    print("\n[TEST 2: LISSAGE TEMPOREL]")
    
    for brain_name in brain_names:
        print(f"  CA {brain_name:12s}...", end=' ', flush=True)
        start = time.time()
        result = test_temporal_smoothing(brain_name, sequences, steps=3)
        result['elapsed'] = time.time() - start
        all_results['smoothing'].append(result)
        print(f"acc={result['accuracy']:.3f}, mse={result['mse']:.4f} (t={result['elapsed']:.2f}s)")
    
    # Baseline
    print(f"  Baseline median...", end=' ', flush=True)
    start = time.time()
    result = test_baseline_smoothing(sequences)
    result['elapsed'] = time.time() - start
    all_results['smoothing'].append(result)
    print(f"acc={result['accuracy']:.3f}, mse={result['mse']:.4f} (t={result['elapsed']:.2f}s)")
    
    # Sauvegarder
    output_dir = Path('results/brain_niches_v5')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'temporal_tasks.json'
    
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*80}")
    print("TEST TEMPOREL COMPLETE")
    print(f"{'='*80}")
    print(f"Results saved: {output_file}")
    
    # Analyse
    print("\n[ANALYSE]")
    print("\nPrediction:")
    for r in sorted(all_results['prediction'], key=lambda x: x['accuracy'], reverse=True):
        print(f"  {r['method']:30s}: Acc={r['accuracy']:.3f}")
    
    print("\nSmoothing:")
    for r in sorted(all_results['smoothing'], key=lambda x: x['accuracy'], reverse=True):
        print(f"  {r['method']:30s}: Acc={r['accuracy']:.3f}")


if __name__ == '__main__':
    main()

