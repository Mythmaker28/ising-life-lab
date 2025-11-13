"""
CA Vectorized — Implémentation vectorisée des automates cellulaires.

Remplace les boucles Python imbriquées par opérations NumPy + convolution.
Gain attendu : 10-50× plus rapide.
"""

import numpy as np
from scipy.signal import convolve2d
from typing import Set, Callable


def step_ca_vectorized(grid: np.ndarray, born: Set[int], survive: Set[int]) -> np.ndarray:
    """
    Évolution CA vectorisée (Life-like rules).
    
    Args:
        grid: Grille 2D (0/1)
        born: Ensemble valeurs naissance
        survive: Ensemble valeurs survie
    
    Returns:
        Nouvelle grille après 1 step
    
    Gain vs Python loops : ~10-20×
    """
    # Kernel Moore (8 voisins)
    kernel = np.array([[1, 1, 1],
                      [1, 0, 1],
                      [1, 1, 1]], dtype=int)
    
    # Compter voisins (mode='same' + boundary='wrap' pour toroïdal)
    neighbor_count = convolve2d(grid, kernel, mode='same', boundary='wrap')
    
    # Masques booléens
    alive = grid == 1
    dead = grid == 0
    
    # Conditions naissance/survie (vectorisées)
    born_mask = np.isin(neighbor_count, list(born))
    survive_mask = np.isin(neighbor_count, list(survive))
    
    # Nouvelle grille
    new_grid = np.zeros_like(grid, dtype=int)
    new_grid[alive & survive_mask] = 1
    new_grid[dead & born_mask] = 1
    
    return new_grid


def create_rule_function_vectorized(born: list, survive: list) -> Callable:
    """
    Crée fonction règle vectorisée.
    
    Args:
        born: Liste valeurs naissance [0-8]
        survive: Liste valeurs survie [0-8]
    
    Returns:
        Fonction grid -> new_grid (vectorisée)
    """
    born_set = set(born)
    survive_set = set(survive)
    
    def rule_func(grid):
        return step_ca_vectorized(grid, born_set, survive_set)
    
    return rule_func


def evolve_ca_vectorized(grid: np.ndarray, born: Set[int], survive: Set[int], 
                        steps: int) -> np.ndarray:
    """
    Évolution CA sur N steps (vectorisée).
    
    Args:
        grid: Grille initiale
        born: Ensemble naissance
        survive: Ensemble survie
        steps: Nombre de steps
    
    Returns:
        Grille finale
    """
    current_grid = grid.copy()
    for _ in range(steps):
        current_grid = step_ca_vectorized(current_grid, born, survive)
    return current_grid


# Benchmark : comparaison vs Python loops
def benchmark_ca_implementations(grid_size=(64,64), steps=100, seed=42):
    """
    Compare implémentations Python loops vs vectorisée.
    
    Returns:
        Dict avec temps d'exécution
    """
    import time
    from isinglab.memory_explorer import MemoryExplorer
    
    np.random.seed(seed)
    grid = (np.random.rand(*grid_size) < 0.3).astype(int)
    
    # Test Life (B3/S23)
    born, survive = [3], [2, 3]
    
    # Version Python loops (actuelle)
    explorer = MemoryExplorer()
    rule_func_python = explorer._create_rule_function(born, survive)
    
    start = time.time()
    grid_python = grid.copy()
    for _ in range(steps):
        grid_python = rule_func_python(grid_python)
    time_python = time.time() - start
    
    # Version vectorisée
    start = time.time()
    grid_vectorized = evolve_ca_vectorized(grid, set(born), set(survive), steps)
    time_vectorized = time.time() - start
    
    # Vérification cohérence
    assert np.array_equal(grid_python, grid_vectorized), "Résultats différents !"
    
    return {
        'grid_size': grid_size,
        'steps': steps,
        'time_python': time_python,
        'time_vectorized': time_vectorized,
        'speedup': time_python / time_vectorized,
        'coherent': True
    }


__all__ = [
    'step_ca_vectorized',
    'create_rule_function_vectorized',
    'evolve_ca_vectorized',
    'benchmark_ca_implementations'
]




