"""
Test Tâches Spatiales v5.0 — Segmentation & Denoising structuré.

Cherche si CA ont un avantage sur tâches spatiales 2D (leur domaine naturel).
"""

import time
import json
from pathlib import Path
from datetime import datetime
import numpy as np
from sklearn.metrics import accuracy_score, f1_score
from sklearn.neural_network import MLPClassifier
from scipy.ndimage import convolve

from isinglab.brain_modules import BRAIN_MODULES, get_brain_rule_function


def generate_geometric_patterns(n_samples=100, grid_size=(64, 64), seed=42):
    """
    Génère patterns géométriques simples (blobs, lignes, textures).
    
    Returns:
        X: Patterns (n_samples, h, w)
        y: Labels (n_samples,) - type de pattern
    """
    np.random.seed(seed)
    h, w = grid_size
    X = []
    y = []
    
    n_per_class = n_samples // 3
    
    # Classe 0 : Blobs centraux
    for _ in range(n_per_class):
        pattern = np.zeros((h, w))
        cx, cy = h // 2 + np.random.randint(-10, 10), w // 2 + np.random.randint(-10, 10)
        radius = np.random.randint(5, 15)
        for i in range(h):
            for j in range(w):
                if (i - cx)**2 + (j - cy)**2 < radius**2:
                    pattern[i, j] = 1
        X.append(pattern)
        y.append(0)
    
    # Classe 1 : Lignes diagonales
    for _ in range(n_per_class):
        pattern = np.zeros((h, w))
        angle = np.random.rand() * np.pi
        offset = np.random.randint(-20, 20)
        for i in range(h):
            for j in range(w):
                dist = abs(j * np.cos(angle) - i * np.sin(angle) + offset)
                if dist < 3:
                    pattern[i, j] = 1
        X.append(pattern)
        y.append(1)
    
    # Classe 2 : Damiers / Textures
    for _ in range(n_per_class):
        pattern = np.zeros((h, w))
        cell_size = np.random.randint(4, 12)
        for i in range(h):
            for j in range(w):
                if ((i // cell_size) + (j // cell_size)) % 2 == 0:
                    pattern[i, j] = 1
        X.append(pattern)
        y.append(2)
    
    X = np.array(X)
    y = np.array(y)
    
    # Shuffle
    indices = np.random.permutation(len(X))
    return X[indices], y[indices]


def generate_structured_noise(n_samples=100, grid_size=(64, 64), noise_level=0.2, seed=42):
    """
    Génère patterns bruités avec structure spatiale (domaines, cellules).
    
    Returns:
        X_noisy: Patterns bruités
        X_clean: Patterns propres
    """
    np.random.seed(seed)
    h, w = grid_size
    X_noisy = []
    X_clean = []
    
    for _ in range(n_samples):
        # Pattern propre : domaines aléatoires
        clean = np.zeros((h, w))
        n_domains = np.random.randint(3, 8)
        for _ in range(n_domains):
            cx, cy = np.random.randint(0, h), np.random.randint(0, w)
            radius = np.random.randint(5, 20)
            for i in range(max(0, cx-radius), min(h, cx+radius)):
                for j in range(max(0, cy-radius), min(w, cy+radius)):
                    if (i - cx)**2 + (j - cy)**2 < radius**2:
                        clean[i, j] = 1
        
        # Ajouter bruit structuré (par patches)
        noisy = clean.copy()
        n_patches = int(h * w * noise_level / 16)
        for _ in range(n_patches):
            i, j = np.random.randint(0, h-4), np.random.randint(0, w-4)
            noisy[i:i+4, j:j+4] = 1 - noisy[i:i+4, j:j+4]
        
        X_clean.append(clean)
        X_noisy.append(noisy)
    
    return np.array(X_noisy), np.array(X_clean)


def test_ca_segmentation(brain_name, X, y, steps=10):
    """
    Test CA pour segmentation de patterns.
    
    Stratégie : CA comme feature extractor, puis classifier simple sur densité finale.
    """
    rule_func = get_brain_rule_function(brain_name)
    
    # Features : densité finale après évolution CA
    features = []
    for pattern in X:
        final = pattern.copy()
        for _ in range(steps):
            final = rule_func(final)
        # Feature simple : densité
        density = final.mean()
        features.append([density])
    
    features = np.array(features)
    
    # Split train/test
    n_train = int(len(X) * 0.7)
    X_train, X_test = features[:n_train], features[n_train:]
    y_train, y_test = y[:n_train], y[n_train:]
    
    # Classifier simple (KNN basé sur densité)
    from sklearn.neighbors import KNeighborsClassifier
    clf = KNeighborsClassifier(n_neighbors=5)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='macro')
    
    return {'accuracy': acc, 'f1': f1, 'method': f'CA_{brain_name}'}


def test_baseline_segmentation(X, y):
    """
    Baseline : MLP direct sur patterns flatten.
    """
    # Flatten
    X_flat = X.reshape(len(X), -1)
    
    # Split
    n_train = int(len(X) * 0.7)
    X_train, X_test = X_flat[:n_train], X_flat[n_train:]
    y_train, y_test = y[:n_train], y[n_train:]
    
    # MLP simple
    clf = MLPClassifier(hidden_layer_sizes=(50,), max_iter=500, random_state=42)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='macro')
    
    return {'accuracy': acc, 'f1': f1, 'method': 'MLP_baseline'}


def test_conv_segmentation(X, y):
    """
    Baseline : Conv simple + pooling.
    """
    # Features : moyenne après filtre sobel-like
    kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
    features = []
    for pattern in X:
        filtered = convolve(pattern, kernel, mode='constant')
        # Feature : norme L2 du gradient
        feature = np.sqrt(np.mean(filtered**2))
        features.append([feature])
    
    features = np.array(features)
    
    # Split
    n_train = int(len(X) * 0.7)
    X_train, X_test = features[:n_train], features[n_train:]
    y_train, y_test = y[:n_train], y[n_train:]
    
    # Classifier
    from sklearn.neighbors import KNeighborsClassifier
    clf = KNeighborsClassifier(n_neighbors=5)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='macro')
    
    return {'accuracy': acc, 'f1': f1, 'method': 'Conv_baseline'}


def test_ca_denoising(brain_name, X_noisy, X_clean, steps=10):
    """
    Test CA pour denoising structuré.
    """
    rule_func = get_brain_rule_function(brain_name)
    
    # Débruitage : faire évoluer patterns bruités
    X_denoised = []
    for pattern in X_noisy:
        denoised = pattern.copy()
        for _ in range(steps):
            denoised = rule_func(denoised)
        X_denoised.append(denoised)
    
    X_denoised = np.array(X_denoised)
    
    # Métrique : accuracy pixel-wise
    acc = accuracy_score(X_clean.flatten(), X_denoised.flatten())
    
    # Métrique : MSE
    mse = np.mean((X_clean - X_denoised) ** 2)
    
    return {'accuracy': acc, 'mse': mse, 'method': f'CA_{brain_name}'}


def test_baseline_denoising(X_noisy, X_clean):
    """
    Baseline : filtre médian.
    """
    from scipy.ndimage import median_filter
    
    X_denoised = []
    for pattern in X_noisy:
        denoised = median_filter(pattern, size=3)
        X_denoised.append(denoised)
    
    X_denoised = np.array(X_denoised)
    
    acc = accuracy_score(X_clean.flatten(), (X_denoised > 0.5).astype(int).flatten())
    mse = np.mean((X_clean - X_denoised) ** 2)
    
    return {'accuracy': acc, 'mse': mse, 'method': 'Median_baseline'}


def main():
    """
    Lance tests tâches spatiales pour tous brain modules.
    """
    print("=" * 80)
    print("TEST TÂCHES SPATIALES v5.0")
    print("=" * 80)
    
    # Configuration
    grid_size = (64, 64)
    n_samples = 150
    steps = 10
    seed = 42
    
    # Générer données
    print("\n[GENERATING DATA]")
    print("  Geometric patterns...", end=' ', flush=True)
    X_geo, y_geo = generate_geometric_patterns(n_samples, grid_size, seed)
    print(f"OK ({len(X_geo)} samples)")
    
    print("  Structured noise...", end=' ', flush=True)
    X_noisy, X_clean = generate_structured_noise(n_samples, grid_size, noise_level=0.15, seed=seed)
    print(f"OK ({len(X_noisy)} samples)")
    
    # Brain modules à tester
    brain_names = ['life', 'highlife', 'life_dense', '34life']
    
    # Résultats
    all_results = {
        'timestamp': datetime.now().isoformat(),
        'config': {
            'grid_size': grid_size,
            'n_samples': n_samples,
            'steps': steps,
            'seed': seed
        },
        'segmentation': [],
        'denoising': []
    }
    
    # Test 1 : Segmentation
    print("\n[TEST 1: SEGMENTATION PATTERNS GEOMETRIQUES]")
    
    for brain_name in brain_names:
        print(f"  CA {brain_name:12s}...", end=' ', flush=True)
        start = time.time()
        result = test_ca_segmentation(brain_name, X_geo, y_geo, steps)
        result['elapsed'] = time.time() - start
        all_results['segmentation'].append(result)
        print(f"acc={result['accuracy']:.3f}, f1={result['f1']:.3f} (t={result['elapsed']:.2f}s)")
    
    # Baselines segmentation
    print(f"  Baseline MLP...", end=' ', flush=True)
    start = time.time()
    result = test_baseline_segmentation(X_geo, y_geo)
    result['elapsed'] = time.time() - start
    all_results['segmentation'].append(result)
    print(f"acc={result['accuracy']:.3f}, f1={result['f1']:.3f} (t={result['elapsed']:.2f}s)")
    
    print(f"  Baseline Conv...", end=' ', flush=True)
    start = time.time()
    result = test_conv_segmentation(X_geo, y_geo)
    result['elapsed'] = time.time() - start
    all_results['segmentation'].append(result)
    print(f"acc={result['accuracy']:.3f}, f1={result['f1']:.3f} (t={result['elapsed']:.2f}s)")
    
    # Test 2 : Denoising
    print("\n[TEST 2: DENOISING STRUCTURE]")
    
    for brain_name in brain_names:
        print(f"  CA {brain_name:12s}...", end=' ', flush=True)
        start = time.time()
        result = test_ca_denoising(brain_name, X_noisy, X_clean, steps)
        result['elapsed'] = time.time() - start
        all_results['denoising'].append(result)
        print(f"acc={result['accuracy']:.3f}, mse={result['mse']:.4f} (t={result['elapsed']:.2f}s)")
    
    # Baseline denoising
    print(f"  Baseline Median...", end=' ', flush=True)
    start = time.time()
    result = test_baseline_denoising(X_noisy, X_clean)
    result['elapsed'] = time.time() - start
    all_results['denoising'].append(result)
    print(f"acc={result['accuracy']:.3f}, mse={result['mse']:.4f} (t={result['elapsed']:.2f}s)")
    
    # Sauvegarder
    output_dir = Path('results/brain_niches_v5')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'spatial_tasks.json'
    
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*80}")
    print("TEST SPATIAL COMPLETE")
    print(f"{'='*80}")
    print(f"Results saved: {output_file}")
    
    # Analyse rapide
    print("\n[ANALYSE]")
    print("\nSegmentation:")
    seg_results = sorted(all_results['segmentation'], key=lambda x: x['f1'], reverse=True)
    for r in seg_results[:5]:
        print(f"  {r['method']:20s}: F1={r['f1']:.3f}")
    
    print("\nDenoising:")
    den_results = sorted(all_results['denoising'], key=lambda x: x['accuracy'], reverse=True)
    for r in den_results[:5]:
        print(f"  {r['method']:20s}: Acc={r['accuracy']:.3f}")


if __name__ == '__main__':
    main()


