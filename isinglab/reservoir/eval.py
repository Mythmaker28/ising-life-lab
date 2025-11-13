"""
Reservoir Computing Evaluation — Tâches standard de RC.

Implémente les tâches canoniques de reservoir computing :
- NARMA10/NARMA20 (non-linéarité + mémoire)
- Prédiction série chaotique (Mackey-Glass simplifié)
- Denoising patterns (débruitage spatial)
"""

import numpy as np
from typing import Dict, Tuple, Optional
from .core import CAReservoir


def generate_narma10(n_samples: int = 1000, seed: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Génère données NARMA10 (Nonlinear AutoRegressive Moving Average order 10).
    
    Équation : y(t+1) = 0.3*y(t) + 0.05*y(t)*sum(y(t-k)) + 1.5*u(t)*u(t-9) + 0.1
    
    Args:
        n_samples: Nombre d'échantillons
        seed: Seed pour reproductibilité
    
    Returns:
        (u, y) : Input et target séquences
    """
    if seed is not None:
        np.random.seed(seed)
    
    u = np.random.uniform(0, 0.5, n_samples)
    y = np.zeros(n_samples)
    
    # Initialisation
    for t in range(10):
        y[t] = 0.1
    
    # Génération
    for t in range(9, n_samples - 1):
        sum_y = np.sum(y[t-9:t+1])
        y[t+1] = 0.3 * y[t] + 0.05 * y[t] * sum_y + 1.5 * u[t] * u[t-9] + 0.1
    
    return u, y


def generate_narma20(n_samples: int = 1000, seed: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Génère données NARMA20 (mémoire plus longue).
    
    Args:
        n_samples: Nombre d'échantillons
        seed: Seed pour reproductibilité
    
    Returns:
        (u, y) : Input et target séquences
    """
    if seed is not None:
        np.random.seed(seed)
    
    u = np.random.uniform(0, 0.5, n_samples)
    y = np.zeros(n_samples)
    
    # Initialisation
    for t in range(20):
        y[t] = 0.1
    
    # Génération
    for t in range(19, n_samples - 1):
        sum_y = np.sum(y[t-19:t+1])
        y[t+1] = 0.3 * y[t] + 0.05 * y[t] * sum_y + 1.5 * u[t] * u[t-19] + 0.1
    
    return u, y


def generate_mackey_glass(n_samples: int = 1000, tau: int = 17, seed: Optional[int] = None) -> np.ndarray:
    """
    Génère série temporelle Mackey-Glass simplifiée (série chaotique).
    
    Args:
        n_samples: Nombre d'échantillons
        tau: Délai (paramètre de chaos)
        seed: Seed pour reproductibilité
    
    Returns:
        Série temporelle y
    """
    if seed is not None:
        np.random.seed(seed)
    
    dt = 0.1
    a, b, c = 0.2, 0.1, 10.0
    
    # Initialisation
    y = np.zeros(n_samples)
    y[0] = 1.0
    
    # Génération (Euler simplifié)
    for t in range(n_samples - 1):
        if t < tau:
            y_delayed = y[0]
        else:
            y_delayed = y[t - tau]
        
        dy_dt = -b * y[t] + a * y_delayed / (1 + y_delayed ** c)
        y[t+1] = y[t] + dt * dy_dt
    
    return y


def generate_denoising_data(n_samples: int = 100, grid_size: Tuple[int, int] = (32, 32),
                           noise_level: float = 0.2, seed: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Génère données pour tâche de débruitage.
    
    Args:
        n_samples: Nombre d'échantillons
        grid_size: Taille des grilles
        noise_level: Niveau de bruit (0-1)
        seed: Seed pour reproductibilité
    
    Returns:
        (X_noisy, y_clean) : Patterns bruités et patterns propres
    """
    if seed is not None:
        np.random.seed(seed)
    
    height, width = grid_size
    X_noisy = []
    y_clean = []
    
    # Patterns simples : blocs, lignes, damiers
    patterns = [
        lambda h, w: np.zeros((h, w), dtype=int),  # Vide
        lambda h, w: np.ones((h, w), dtype=int),   # Plein
        lambda h, w: np.tile((np.arange(h)[:, None] % 2 == 0).astype(int), (1, w)),  # Lignes horizontales
        lambda h, w: np.tile((np.arange(w)[None, :] % 2 == 0).astype(int), (h, 1)),  # Lignes verticales
        lambda h, w: ((np.arange(h)[:, None] + np.arange(w)[None, :]) % 2 == 0).astype(int),  # Damier
    ]
    
    for _ in range(n_samples):
        # Pattern propre
        pattern_idx = np.random.randint(0, len(patterns))
        pattern_func = patterns[pattern_idx]
        clean = pattern_func(height, width)
        y_clean.append(clean)
        
        # Ajouter bruit
        noisy = clean.copy()
        n_flips = int(height * width * noise_level)
        for _ in range(n_flips):
            i, j = np.random.randint(0, height), np.random.randint(0, width)
            noisy[i, j] = 1 - noisy[i, j]
        X_noisy.append(noisy)
    
    return np.array(X_noisy), np.array(y_clean)


def evaluate_narma(reservoir: CAReservoir, u: np.ndarray, y: np.ndarray,
                   train_ratio: float = 0.7) -> Dict:
    """
    Évalue un réservoir sur tâche NARMA.
    
    Args:
        reservoir: Instance CAReservoir
        u: Input séquence
        y: Target séquence
        train_ratio: Ratio train/test
    
    Returns:
        Dict avec métriques (NMSE, MSE, etc.)
    """
    n_train = int(len(u) * train_ratio)
    
    # Train
    X_train = []
    y_train = []
    for i in range(10, n_train - 1):
        input_seq = u[max(0, i-9):i+1]  # Fenêtre de 10
        features = reservoir.extract_features(reservoir.evolve(reservoir.encode_input(input_seq)))
        X_train.append(features)
        y_train.append(y[i+1])
    
    X_train = np.array(X_train)
    y_train = np.array(y_train)
    
    # Entraîner
    reservoir.train_readout(X_train, y_train)
    
    # Test
    X_test = []
    y_test = []
    for i in range(n_train, len(u) - 1):
        input_seq = u[max(0, i-9):i+1]
        features = reservoir.extract_features(reservoir.evolve(reservoir.encode_input(input_seq)))
        X_test.append(features)
        y_test.append(y[i+1])
    
    X_test = np.array(X_test)
    y_test = np.array(y_test)
    
    # Prédire
    y_pred = []
    for i in range(n_train, len(u) - 1):
        input_seq = u[max(0, i-9):i+1]
        pred = reservoir.predict(input_seq)
        y_pred.append(pred[0])
    
    y_pred = np.array(y_pred)
    
    # Métriques
    mse = np.mean((y_test - y_pred) ** 2)
    var_y = np.var(y_test)
    nmse = mse / var_y if var_y > 0 else float('inf')
    
    return {
        'mse': mse,
        'nmse': nmse,
        'rmse': np.sqrt(mse),
        'mae': np.mean(np.abs(y_test - y_pred)),
        'correlation': np.corrcoef(y_test, y_pred)[0, 1] if len(y_test) > 1 else 0.0
    }


def evaluate_mackey_glass(reservoir: CAReservoir, y: np.ndarray, lookahead: int = 1,
                         train_ratio: float = 0.7) -> Dict:
    """
    Évalue un réservoir sur prédiction Mackey-Glass.
    
    Args:
        reservoir: Instance CAReservoir
        y: Série temporelle
        lookahead: Nombre de steps à prédire en avance
        train_ratio: Ratio train/test
    
    Returns:
        Dict avec métriques
    """
    n_train = int(len(y) * train_ratio)
    
    # Train
    X_train = []
    y_train = []
    window_size = 10
    for i in range(window_size, n_train - lookahead):
        input_seq = y[i-window_size:i]
        features = reservoir.extract_features(reservoir.evolve(reservoir.encode_input(input_seq)))
        X_train.append(features)
        y_train.append(y[i + lookahead])
    
    X_train = np.array(X_train)
    y_train = np.array(y_train)
    
    # Entraîner
    reservoir.train_readout(X_train, y_train)
    
    # Test
    X_test = []
    y_test = []
    for i in range(n_train, len(y) - lookahead):
        input_seq = y[i-window_size:i]
        features = reservoir.extract_features(reservoir.evolve(reservoir.encode_input(input_seq)))
        X_test.append(features)
        y_test.append(y[i + lookahead])
    
    y_test = np.array(y_test)
    
    # Prédire
    y_pred = []
    for i in range(n_train, len(y) - lookahead):
        input_seq = y[i-window_size:i]
        pred = reservoir.predict(input_seq)
        y_pred.append(pred[0])
    
    y_pred = np.array(y_pred)
    
    # Métriques
    mse = np.mean((y_test - y_pred) ** 2)
    var_y = np.var(y_test)
    nmse = mse / var_y if var_y > 0 else float('inf')
    
    return {
        'mse': mse,
        'nmse': nmse,
        'rmse': np.sqrt(mse),
        'mae': np.mean(np.abs(y_test - y_pred)),
        'correlation': np.corrcoef(y_test, y_pred)[0, 1] if len(y_test) > 1 else 0.0
    }


def evaluate_denoising(reservoir: CAReservoir, X_noisy: np.ndarray, y_clean: np.ndarray,
                     train_ratio: float = 0.7) -> Dict:
    """
    Évalue un réservoir sur tâche de débruitage.
    
    Args:
        reservoir: Instance CAReservoir
        X_noisy: Patterns bruités
        y_clean: Patterns propres
        train_ratio: Ratio train/test
    
    Returns:
        Dict avec métriques (accuracy, MSE, etc.)
    """
    n_train = int(len(X_noisy) * train_ratio)
    
    # Train
    X_train_features = []
    y_train_flat = []
    for i in range(n_train):
        features = reservoir.extract_features(reservoir.evolve(X_noisy[i]))
        X_train_features.append(features)
        y_train_flat.append(y_clean[i].flatten())
    
    X_train_features = np.array(X_train_features)
    y_train_flat = np.array(y_train_flat)
    
    # Entraîner
    reservoir.train_readout(X_train_features, y_train_flat)
    
    # Test
    X_test_features = []
    y_test_flat = []
    for i in range(n_train, len(X_noisy)):
        features = reservoir.extract_features(reservoir.evolve(X_noisy[i]))
        X_test_features.append(features)
        y_test_flat.append(y_clean[i].flatten())
    
    y_test_flat = np.array(y_test_flat)
    
    # Prédire
    y_pred_flat = []
    for i in range(n_train, len(X_noisy)):
        pred = reservoir.predict(X_noisy[i])
        y_pred_flat.append(pred)
    
    y_pred_flat = np.array(y_pred_flat)
    
    # Binariser prédictions
    y_pred_binary = (y_pred_flat > 0.5).astype(int)
    
    # Métriques
    mse = np.mean((y_test_flat - y_pred_flat) ** 2)
    accuracy = np.mean(y_test_flat == y_pred_binary)
    
    return {
        'mse': mse,
        'rmse': np.sqrt(mse),
        'accuracy': accuracy,
        'mae': np.mean(np.abs(y_test_flat - y_pred_flat))
    }


__all__ = [
    'generate_narma10',
    'generate_narma20',
    'generate_mackey_glass',
    'generate_denoising_data',
    'evaluate_narma',
    'evaluate_mackey_glass',
    'evaluate_denoising'
]


