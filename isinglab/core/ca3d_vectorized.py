"""
CA 3D Vectorized — Implémentation vectorisée des automates cellulaires 3D.

Extension du moteur 2D vers 3D avec vectorisation NumPy.
"""

import numpy as np
from scipy.ndimage import convolve
from typing import Set, Callable


def step_ca3d_vectorized(grid: np.ndarray, born: Set[int], survive: Set[int]) -> np.ndarray:
    """
    Évolution CA 3D vectorisée (Life-like rules 3D).
    
    Args:
        grid: Grille 3D (0/1) de shape (depth, height, width)
        born: Ensemble valeurs naissance
        survive: Ensemble valeurs survie
    
    Returns:
        Nouvelle grille après 1 step
    
    Note: Voisinage de Moore 3D = 26 voisins
    """
    # Kernel Moore 3D (26 voisins)
    kernel = np.ones((3, 3, 3), dtype=int)
    kernel[1, 1, 1] = 0  # Centre exclu
    
    # Compter voisins (mode='wrap' pour conditions périodiques)
    neighbor_count = convolve(grid.astype(int), kernel, mode='wrap')
    
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


def create_rule_function_3d(born: list, survive: list) -> Callable:
    """
    Crée fonction règle 3D vectorisée.
    
    Args:
        born: Liste valeurs naissance [0-26]
        survive: Liste valeurs survie [0-26]
    
    Returns:
        Fonction grid3d -> new_grid3d (vectorisée)
    """
    born_set = set(born)
    survive_set = set(survive)
    
    def rule_func(grid):
        return step_ca3d_vectorized(grid, born_set, survive_set)
    
    return rule_func


def evolve_ca3d_vectorized(grid: np.ndarray, born: Set[int], survive: Set[int], 
                          steps: int) -> np.ndarray:
    """
    Évolution CA 3D sur N steps (vectorisée).
    
    Args:
        grid: Grille initiale 3D
        born: Ensemble naissance
        survive: Ensemble survie
        steps: Nombre de steps
    
    Returns:
        Grille finale
    """
    current_grid = grid.copy()
    for _ in range(steps):
        current_grid = step_ca3d_vectorized(current_grid, born, survive)
    return current_grid


# Règles 3D connues
RULES_3D_KNOWN = {
    "life3d": {
        "born": [4],  # Naissance avec 4 voisins (analogue 3D de B3)
        "survive": [3, 4],  # Survie avec 3-4 voisins (analogue de S23)
        "description": "Life 3D standard"
    },
    "445": {
        "born": [4],
        "survive": [4, 5],
        "description": "Stable structures 3D"
    },
    "567": {
        "born": [5, 6, 7],
        "survive": [5, 6, 7],
        "description": "Dense 3D"
    }
}


__all__ = [
    'step_ca3d_vectorized',
    'create_rule_function_3d',
    'evolve_ca3d_vectorized',
    'RULES_3D_KNOWN'
]


