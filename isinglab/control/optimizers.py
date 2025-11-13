"""
Optimiseurs pour les trajectoires holonomiques.

Implémente des algorithmes d'optimisation pour trouver les meilleurs
paramètres de HolonomyPath (k_start, k_end, duration, etc.) qui minimisent
un coût tout en respectant les contraintes physiques.
"""

import numpy as np
from typing import Dict, List, Tuple, Callable, Optional
from dataclasses import dataclass
from tqdm import tqdm

from .holonomy import HolonomyPath, generate_linear_ramp_path, generate_smooth_sigmoid_path
from ..data_bridge.atlas_map import AtlasProfile


@dataclass
class OptimizationResult:
    """Résultat d'une optimisation de trajectoire."""
    
    best_path: HolonomyPath
    best_params: Dict[str, float]
    best_cost: float
    all_evaluated: List[Tuple[Dict[str, float], float]]  # (params, cost)
    n_evaluations: int
    
    def __repr__(self):
        return (f"OptimizationResult(best_cost={self.best_cost:.4f}, "
                f"n_evaluations={self.n_evaluations}, "
                f"best_params={self.best_params})")


class GridSearchOptimizer:
    """
    Optimiseur par recherche sur grille (Grid Search).
    
    Simple mais efficace pour espaces de faible dimension.
    """
    
    def __init__(
        self,
        param_ranges: Dict[str, Tuple[float, float, int]],
        path_generator: str = "linear_ramp",
        verbose: bool = True
    ):
        """
        Args:
            param_ranges: Dict de {param_name: (min, max, n_points)}
                Ex: {'k_start': (0.5, 2.0, 5), 'k_end': (1.0, 3.0, 5)}
            path_generator: Type de générateur ('linear_ramp', 'smooth_sigmoid')
            verbose: Affichage de la progression
        """
        self.param_ranges = param_ranges
        self.path_generator = path_generator
        self.verbose = verbose
        
    def optimize(
        self,
        cost_function: Callable[[HolonomyPath], float],
        atlas_profile: Optional[AtlasProfile] = None
    ) -> OptimizationResult:
        """
        Exécute l'optimisation par grid search.
        
        Args:
            cost_function: Fonction qui prend un HolonomyPath et retourne un coût
            atlas_profile: Profil Atlas pour valider les contraintes
            
        Returns:
            OptimizationResult avec le meilleur path trouvé
        """
        # Générer la grille
        param_grids = {}
        for param_name, (min_val, max_val, n_points) in self.param_ranges.items():
            param_grids[param_name] = np.linspace(min_val, max_val, n_points)
        
        # Produit cartésien
        param_names = list(param_grids.keys())
        param_values_list = list(param_grids.values())
        
        # Générer toutes les combinaisons
        import itertools
        all_combinations = list(itertools.product(*param_values_list))
        
        # Évaluer chaque combinaison
        results = []
        best_cost = float('inf')
        best_path = None
        best_params = None
        
        iterator = tqdm(all_combinations, desc="Grid Search") if self.verbose else all_combinations
        
        for combination in iterator:
            params = dict(zip(param_names, combination))
            
            # Générer le path
            try:
                if self.path_generator == "linear_ramp":
                    path = generate_linear_ramp_path(
                        k_start=params.get('k_start', 1.0),
                        k_end=params.get('k_end', 2.0),
                        duration=params.get('duration', 1.0),
                        annealing_start=params.get('annealing_start', 0.1),
                        annealing_end=params.get('annealing_end', 0.5)
                    )
                elif self.path_generator == "smooth_sigmoid":
                    path = generate_smooth_sigmoid_path(
                        k_start=params.get('k_start', 1.0),
                        k_end=params.get('k_end', 2.0),
                        duration=params.get('duration', 1.0),
                        steepness=params.get('steepness', 5.0)
                    )
                else:
                    raise ValueError(f"Unknown path generator: {self.path_generator}")
                
                # Valider contraintes si atlas_profile fourni
                if atlas_profile:
                    from ..data_bridge.atlas_map import AtlasMapper
                    mapper = AtlasMapper()
                    k_max_safe = mapper._compute_k_max(atlas_profile.t1_us, atlas_profile.t2_us)
                    
                    # Skip si K1 trop élevé
                    if params.get('k_end', 0) > k_max_safe * 1.2:
                        continue
                
                # Évaluer le coût
                cost = cost_function(path)
                results.append((params, cost))
                
                # Mettre à jour le meilleur
                if cost < best_cost:
                    best_cost = cost
                    best_path = path
                    best_params = params
                    
            except Exception as e:
                if self.verbose:
                    print(f"Warning: Failed to evaluate {params}: {e}")
                continue
        
        return OptimizationResult(
            best_path=best_path,
            best_params=best_params,
            best_cost=best_cost,
            all_evaluated=results,
            n_evaluations=len(results)
        )


class RandomSearchOptimizer:
    """
    Optimiseur par recherche aléatoire.
    
    Plus rapide que grid search pour espaces de haute dimension.
    """
    
    def __init__(
        self,
        param_ranges: Dict[str, Tuple[float, float]],
        n_samples: int = 50,
        path_generator: str = "linear_ramp",
        verbose: bool = True,
        seed: Optional[int] = None
    ):
        """
        Args:
            param_ranges: Dict de {param_name: (min, max)}
            n_samples: Nombre d'échantillons aléatoires
            path_generator: Type de générateur
            verbose: Affichage
            seed: Seed pour reproductibilité
        """
        self.param_ranges = param_ranges
        self.n_samples = n_samples
        self.path_generator = path_generator
        self.verbose = verbose
        self.rng = np.random.default_rng(seed)
        
    def optimize(
        self,
        cost_function: Callable[[HolonomyPath], float],
        atlas_profile: Optional[AtlasProfile] = None
    ) -> OptimizationResult:
        """
        Exécute l'optimisation par random search.
        
        Args:
            cost_function: Fonction de coût
            atlas_profile: Profil Atlas pour contraintes
            
        Returns:
            OptimizationResult
        """
        results = []
        best_cost = float('inf')
        best_path = None
        best_params = None
        
        iterator = tqdm(range(self.n_samples), desc="Random Search") if self.verbose else range(self.n_samples)
        
        for _ in iterator:
            # Échantillonner des paramètres aléatoires
            params = {}
            for param_name, (min_val, max_val) in self.param_ranges.items():
                params[param_name] = self.rng.uniform(min_val, max_val)
            
            # Générer le path
            try:
                if self.path_generator == "linear_ramp":
                    path = generate_linear_ramp_path(
                        k_start=params.get('k_start', 1.0),
                        k_end=params.get('k_end', 2.0),
                        duration=params.get('duration', 1.0),
                        annealing_start=params.get('annealing_start', 0.1),
                        annealing_end=params.get('annealing_end', 0.5)
                    )
                elif self.path_generator == "smooth_sigmoid":
                    path = generate_smooth_sigmoid_path(
                        k_start=params.get('k_start', 1.0),
                        k_end=params.get('k_end', 2.0),
                        duration=params.get('duration', 1.0),
                        steepness=params.get('steepness', 5.0)
                    )
                else:
                    raise ValueError(f"Unknown path generator: {self.path_generator}")
                
                # Valider contraintes
                if atlas_profile:
                    from ..data_bridge.atlas_map import AtlasMapper
                    mapper = AtlasMapper()
                    k_max_safe = mapper._compute_k_max(atlas_profile.t1_us, atlas_profile.t2_us)
                    
                    if params.get('k_end', 0) > k_max_safe * 1.2:
                        continue
                
                # Évaluer
                cost = cost_function(path)
                results.append((params, cost))
                
                # Mettre à jour
                if cost < best_cost:
                    best_cost = cost
                    best_path = path
                    best_params = params
                    
            except Exception as e:
                if self.verbose:
                    print(f"Warning: Failed to evaluate {params}: {e}")
                continue
        
        return OptimizationResult(
            best_path=best_path,
            best_params=best_params,
            best_cost=best_cost,
            all_evaluated=results,
            n_evaluations=len(results)
        )


def compare_path_generators(
    param_sets: List[Dict[str, float]],
    generators: List[str],
    cost_function: Callable[[HolonomyPath], float]
) -> Dict[str, List[float]]:
    """
    Compare différents générateurs de trajectoire.
    
    Args:
        param_sets: Liste de paramètres à tester
        generators: Liste de noms de générateurs
        cost_function: Fonction de coût
        
    Returns:
        Dict de {generator_name: [costs]}
    """
    results = {gen: [] for gen in generators}
    
    for params in param_sets:
        for gen_name in generators:
            try:
                if gen_name == "linear_ramp":
                    path = generate_linear_ramp_path(**params)
                elif gen_name == "smooth_sigmoid":
                    path = generate_smooth_sigmoid_path(**params)
                else:
                    continue
                
                cost = cost_function(path)
                results[gen_name].append(cost)
            except:
                results[gen_name].append(float('inf'))
    
    return results

