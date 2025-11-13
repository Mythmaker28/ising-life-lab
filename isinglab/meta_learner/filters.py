"""
Filtres Anti-Trivialité v3.1

Rejette rules triviales AVANT promotion HoF.
"""

import numpy as np
from typing import Tuple
from isinglab.core.rule_ops import parse_notation
from isinglab.core.ca_vectorized import evolve_ca_vectorized


def quick_density_test(notation: str, grid_size=(32, 32), steps=50, seed=42) -> float:
    """
    Test rapide densité finale d'une règle.
    
    Returns: final_density (0-1)
    """
    born, survive = parse_notation(notation)
    
    np.random.seed(seed)
    grid = (np.random.rand(*grid_size) < 0.3).astype(int)
    
    grid_final = evolve_ca_vectorized(grid, set(born), set(survive), steps)
    
    return grid_final.mean()


def is_quasi_death_rule(notation: str, threshold=0.05, n_tests=2) -> Tuple[bool, str]:
    """
    Détecte quasi-death rules (convergence vers vide).
    
    Args:
        notation: Règle à tester
        threshold: Densité minimale acceptable
        n_tests: Nombre de tests avec seeds différents
    
    Returns:
        (is_trivial, reason)
    """
    densities = []
    
    for i in range(n_tests):
        density = quick_density_test(notation, seed=42+i)
        densities.append(density)
    
    avg_density = np.mean(densities)
    
    if avg_density < threshold:
        return True, f"Quasi-death (avg_density={avg_density:.3f})"
    
    return False, "Pass"


def is_saturation_rule(notation: str, threshold=0.95, n_tests=2) -> Tuple[bool, str]:
    """
    Détecte saturation rules (convergence vers plein).
    
    Returns:
        (is_trivial, reason)
    """
    densities = []
    
    for i in range(n_tests):
        density = quick_density_test(notation, seed=42+i)
        densities.append(density)
    
    avg_density = np.mean(densities)
    
    if avg_density > threshold:
        return True, f"Saturation (avg_density={avg_density:.3f})"
    
    return False, "Pass"


def apply_hard_filters(notation: str) -> Tuple[bool, str]:
    """
    Applique tous les filtres durs.
    
    Returns:
        (pass_filters, reason)
        
    Usage dans selector AVANT évaluation complète.
    """
    # Filtre 1: Quasi-death
    is_death, reason = is_quasi_death_rule(notation, threshold=0.05, n_tests=2)
    if is_death:
        return False, reason
    
    # Filtre 2: Saturation
    is_sat, reason = is_saturation_rule(notation, threshold=0.95, n_tests=2)
    if is_sat:
        return False, reason
    
    # Tous filtres passés
    return True, "Valid"


__all__ = [
    'quick_density_test',
    'is_quasi_death_rule',
    'is_saturation_rule',
    'apply_hard_filters'
]




