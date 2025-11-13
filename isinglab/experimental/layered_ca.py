"""
Layered CA v0.1 — Superposition de Règles CA Multi-Couches.

Expérimental : Test si combiner 2 règles CA donne profils "cerveau" améliorés.
Version 0.1 : Couplage minimal, pas de réseau complexe.
"""

import numpy as np
from typing import Tuple, Callable, List, Dict


class LayeredCA:
    """
    Automate cellulaire à 2 couches avec couplage minimal.
    
    Couche A : Règle primaire
    Couche B : Règle secondaire
    Couplage : B voit densité locale de A (optionnel)
    """
    
    def __init__(self, rule_a: Callable, rule_b: Callable, coupling: str = 'none'):
        """
        Args:
            rule_a: Fonction règle couche A (grid -> new_grid)
            rule_b: Fonction règle couche B
            coupling: 'none', 'density_mask', 'xor'
        """
        self.rule_a = rule_a
        self.rule_b = rule_b
        self.coupling = coupling
    
    def step(self, grid_a: np.ndarray, grid_b: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Évolution d'un step pour les 2 couches.
        
        Returns:
            (new_grid_a, new_grid_b)
        """
        # Évolution couche A (indépendante)
        new_a = self.rule_a(grid_a)
        
        # Évolution couche B selon couplage
        if self.coupling == 'none':
            new_b = self.rule_b(grid_b)
        
        elif self.coupling == 'density_mask':
            # B modulé par densité locale de A
            # Si A est dense localement, B activé; sinon B inhibé
            # Simple : masque binaire basé sur A
            mask = (grid_a > 0).astype(int)
            intermediate_b = self.rule_b(grid_b)
            new_b = intermediate_b * mask  # B actif seulement où A est vivant
        
        elif self.coupling == 'xor':
            # Couplage XOR : B voit A XOR B
            combined = np.logical_xor(grid_a, grid_b).astype(int)
            new_b = self.rule_b(combined)
        
        else:
            new_b = self.rule_b(grid_b)
        
        return new_a, new_b
    
    def evolve(self, grid_a: np.ndarray, grid_b: np.ndarray, steps: int) -> Tuple[np.ndarray, np.ndarray]:
        """Évolution sur N steps."""
        for _ in range(steps):
            grid_a, grid_b = self.step(grid_a, grid_b)
        return grid_a, grid_b


def test_layered_combination(rule_a_notation: str, rule_b_notation: str,
                            grid_size: Tuple[int, int] = (32, 32),
                            steps: int = 100,
                            coupling: str = 'none',
                            seed: int = 42) -> Dict:
    """
    Teste une combinaison de 2 règles en mode layered.
    
    Args:
        rule_a_notation: Notation règle A (ex: 'B3/S23')
        rule_b_notation: Notation règle B (ex: 'B018/S1236')
        grid_size: Taille grille
        steps: Steps d'évolution
        coupling: Type de couplage
        seed: Random seed
    
    Returns:
        Dict avec métriques combinées
    """
    from ..core.rule_ops import parse_notation
    
    np.random.seed(seed)
    
    # Parser règles
    born_a, survive_a = parse_notation(rule_a_notation)
    born_b, survive_b = parse_notation(rule_b_notation)
    
    born_a_set, survive_a_set = set(born_a), set(survive_a)
    born_b_set, survive_b_set = set(born_b), set(survive_b)
    
    # Créer fonctions règles
    def rule_func_a(grid):
        h, w = grid.shape
        new_grid = np.zeros_like(grid)
        for i in range(h):
            for j in range(w):
                neighbors = sum(grid[(i+di)%h, (j+dj)%w] for di in [-1,0,1] for dj in [-1,0,1] if not (di==0 and dj==0))
                if grid[i,j] == 1:
                    new_grid[i,j] = 1 if neighbors in survive_a_set else 0
                else:
                    new_grid[i,j] = 1 if neighbors in born_a_set else 0
        return new_grid
    
    def rule_func_b(grid):
        h, w = grid.shape
        new_grid = np.zeros_like(grid)
        for i in range(h):
            for j in range(w):
                neighbors = sum(grid[(i+di)%h, (j+dj)%w] for di in [-1,0,1] for dj in [-1,0,1] if not (di==0 and dj==0))
                if grid[i,j] == 1:
                    new_grid[i,j] = 1 if neighbors in survive_b_set else 0
                else:
                    new_grid[i,j] = 1 if neighbors in born_b_set else 0
        return new_grid
    
    # Créer LayeredCA
    layered = LayeredCA(rule_func_a, rule_func_b, coupling=coupling)
    
    # Init grilles
    h, w = grid_size
    grid_a = (np.random.rand(h, w) < 0.3).astype(int)
    grid_b = (np.random.rand(h, w) < 0.3).astype(int)
    
    # Évoluer
    final_a, final_b = layered.evolve(grid_a, grid_b, steps)
    
    # Métriques simples
    density_a = final_a.mean()
    density_b = final_b.mean()
    
    # Correlation entre couches
    correlation = np.corrcoef(final_a.flatten(), final_b.flatten())[0, 1]
    
    result = {
        'rule_a': rule_a_notation,
        'rule_b': rule_b_notation,
        'coupling': coupling,
        'grid_size': grid_size,
        'steps': steps,
        'final_density_a': float(density_a),
        'final_density_b': float(density_b),
        'correlation': float(correlation) if not np.isnan(correlation) else 0.0
    }
    
    return result


__all__ = ['LayeredCA', 'test_layered_combination']

