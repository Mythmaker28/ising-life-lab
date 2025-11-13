"""
Optimisation de trajectoires holonomiques sous contraintes physiques.

Intégration complète :
    - P1 (Simulation) : Moteur Kuramoto/XY
    - P2 (Physique) : Contraintes Atlas (T1, T2, Température)
    - P3 (Contrôle) : HolonomyPath optimisation

Question centrale : "Quelle est la meilleure trajectoire pour atteindre
une cible phénoménologique, sous les contraintes d'un système quantique physique ?"
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
from tqdm import tqdm

from ..oscillators import KuramotoXYEngine, MultiKernelConfig
from ..analysis import detect_vortices
from ..control.holonomy import HolonomyPath, generate_linear_ramp_path, generate_smooth_sigmoid_path
from ..control.optimizers import GridSearchOptimizer, RandomSearchOptimizer, OptimizationResult
from ..data_bridge.atlas_map import AtlasMapper, AtlasProfile, PhenoParams
from ..data_bridge.physics_validator import PhysicsValidator
from ..data_bridge.cost_functions import PhenoState, phenomenology_distance, compute_target_profile
from .trajectory_cost import compute_trajectory_metrics, TrajectoryMetrics, rank_trajectories


def simulate_with_holonomy_path(
    path: HolonomyPath,
    grid_size: Tuple[int, int] = (64, 64),
    steps_per_unit_time: int = 50,
    record_interval: int = 5,
    seed: int = 42
) -> Tuple[List[PhenoState], List[Dict[str, float]]]:
    """
    Simule le moteur d'oscillateurs en suivant une trajectoire holonomique.
    
    Args:
        path: Trajectoire holonomique à suivre
        grid_size: Taille de la grille
        steps_per_unit_time: Nombre de steps de simulation par unité de temps du path
        record_interval: Intervalle d'enregistrement
        seed: Seed pour reproductibilité
        
    Returns:
        (state_history, params_history)
    """
    state_history = []
    params_history = []
    
    # Durée totale de la trajectoire
    if len(path.points) > 0:
        total_duration = path.points[-1].t
    else:
        total_duration = 1.0
    
    total_steps = int(total_duration * steps_per_unit_time)
    
    # Initialiser le moteur avec les paramètres initiaux
    initial_params = path.interpolate(0.0)
    
    engine = None
    
    for step in range(total_steps):
        # Temps normalisé actuel
        t_current = step / steps_per_unit_time
        
        # Interpoler les paramètres à ce moment
        current_params = path.interpolate(t_current)
        
        # Créer/mettre à jour le moteur
        if engine is None or step % 10 == 0:  # Reconfigurer périodiquement
            kernel_config = MultiKernelConfig(
                k1_strength=current_params.get('k1', 1.0),
                k1_range=1,
                k1_sign=1.0,
                k2_strength=abs(current_params.get('k2', 0.0)),
                k2_range=3,
                k2_sign=-1.0 if current_params.get('k2', 0.0) < 0 else 1.0,
                k3_strength=current_params.get('k3', 0.0),
                k3_range=7,
                k3_sign=1.0,
                dt=0.05,
                noise_amplitude=current_params.get('noise', 0.1),
                annealing_rate=current_params.get('annealing', 0.1)
            )
            
            if engine is None:
                engine = KuramotoXYEngine(shape=grid_size, config=kernel_config, seed=seed)
                engine.reset()
            else:
                engine.config = kernel_config
        
        # Step de simulation
        engine.step()
        
        # Enregistrer
        if step % record_interval == 0:
            phase_field = engine.get_phase_field()
            r, _ = engine.get_order_parameter()
            defect_metrics = detect_vortices(phase_field, threshold=0.5)
            
            state = PhenoState(
                order_parameter_r=r,
                defect_density=defect_metrics.defect_density,
                n_defects=defect_metrics.n_defects,
                annihilation_rate=0.0,  # Calculé plus tard
                mean_phase=float(np.mean(phase_field)),
                std_phase=float(np.std(phase_field))
            )
            
            state_history.append(state)
            params_history.append(current_params)
    
    # Calculer les taux d'annihilation
    if len(state_history) > 1:
        for i in range(1, len(state_history)):
            rate = (state_history[i-1].n_defects - state_history[i].n_defects) / record_interval
            state_history[i].annihilation_rate = rate
    
    return state_history, params_history


def optimize_holonomy_path(
    target_profile: str,
    atlas_profile: str,
    atlas_mapper: Optional[AtlasMapper] = None,
    optimizer_type: str = 'random',
    n_evaluations: int = 20,
    path_generator: str = 'linear_ramp',
    grid_size: Tuple[int, int] = (64, 64),
    steps_per_unit_time: int = 50,
    output_dir: Optional[str] = None,
    seed: int = 42
) -> Dict:
    """
    Optimise une trajectoire holonomique pour atteindre une cible phénoménologique
    sous les contraintes physiques de l'Atlas.
    
    INTÉGRATION COMPLÈTE P1-P2-P3.
    
    Args:
        target_profile: Profil phéno cible ('uniform', 'fragmented', 'balanced')
        atlas_profile: ID du système physique Atlas (ex: 'NV-298K')
        atlas_mapper: Mapper Atlas (créé si None)
        optimizer_type: 'random' ou 'grid'
        n_evaluations: Nombre d'évaluations (samples pour random, points par dim pour grid)
        path_generator: 'linear_ramp' ou 'smooth_sigmoid'
        grid_size: Taille de la grille de simulation
        steps_per_unit_time: Résolution temporelle
        output_dir: Répertoire de sortie
        seed: Seed
        
    Returns:
        Dict contenant :
            - 'best_path': Meilleur HolonomyPath trouvé
            - 'best_metrics': TrajectoryMetrics du meilleur
            - 'optimization_result': OptimizationResult complet
            - 'atlas_profile': Profil physique utilisé
            - 'target_state': État phéno cible
    """
    # 1. Initialisation
    if atlas_mapper is None:
        atlas_mapper = AtlasMapper()
    
    phys_profile = atlas_mapper.get_profile(atlas_profile)
    target_state = compute_target_profile(target_profile)
    
    print(f"📡 Atlas Profile: {phys_profile}")
    print(f"🎯 Target: {target_profile} (r={target_state.order_parameter_r:.2f}, density={target_state.defect_density:.3f})")
    
    # 2. Définir les ranges de paramètres basés sur l'Atlas
    k_max_safe = atlas_mapper._compute_k_max(phys_profile.t1_us, phys_profile.t2_us)
    noise_baseline = atlas_mapper._compute_noise(phys_profile.t2_us)
    
    if target_profile == 'uniform':
        # Pour uniformisation : K1 fort, annealing élevé
        param_ranges = {
            'k_start': (k_max_safe * 0.5, k_max_safe * 0.9),
            'k_end': (k_max_safe * 0.7, k_max_safe * 1.0),
            'duration': (0.8, 1.0),
            'annealing_start': (0.05, 0.15),
            'annealing_end': (0.3, 0.6)
        }
    elif target_profile == 'fragmented':
        # Pour fragmentation : K1 modéré, pas d'annealing
        param_ranges = {
            'k_start': (k_max_safe * 0.3, k_max_safe * 0.6),
            'k_end': (k_max_safe * 0.5, k_max_safe * 0.8),
            'duration': (0.8, 1.0),
            'annealing_start': (0.0, 0.1),
            'annealing_end': (0.0, 0.1)
        }
    else:  # balanced
        param_ranges = {
            'k_start': (k_max_safe * 0.4, k_max_safe * 0.7),
            'k_end': (k_max_safe * 0.6, k_max_safe * 0.9),
            'duration': (0.8, 1.0),
            'annealing_start': (0.1, 0.2),
            'annealing_end': (0.2, 0.4)
        }
    
    # 3. Définir la fonction de coût
    def cost_function(path: HolonomyPath) -> float:
        """Évalue le coût d'une trajectoire."""
        # Simuler
        state_history, params_history = simulate_with_holonomy_path(
            path,
            grid_size=grid_size,
            steps_per_unit_time=steps_per_unit_time,
            record_interval=5,
            seed=seed
        )
        
        # Calculer les métriques
        metrics = compute_trajectory_metrics(
            state_history,
            target_state,
            params_history,
            phys_profile
        )
        
        return metrics.composite_score
    
    # 4. Créer l'optimiseur
    print(f"\n🔧 Optimizer: {optimizer_type}, Generator: {path_generator}")
    
    if optimizer_type == 'random':
        optimizer = RandomSearchOptimizer(
            param_ranges=param_ranges,
            n_samples=n_evaluations,
            path_generator=path_generator,
            verbose=True,
            seed=seed
        )
    elif optimizer_type == 'grid':
        # Convertir ranges pour grid search
        param_ranges_grid = {
            k: (v[0], v[1], int(np.sqrt(n_evaluations)))
            for k, v in param_ranges.items()
        }
        optimizer = GridSearchOptimizer(
            param_ranges=param_ranges_grid,
            path_generator=path_generator,
            verbose=True
        )
    else:
        raise ValueError(f"Unknown optimizer: {optimizer_type}")
    
    # 5. Optimiser
    print(f"\n🚀 Starting optimization...")
    opt_result = optimizer.optimize(cost_function, atlas_profile=phys_profile)
    
    print(f"\n✅ Optimization complete!")
    print(f"   Best cost: {opt_result.best_cost:.4f}")
    print(f"   Best params: {opt_result.best_params}")
    
    # 6. Évaluer le meilleur en détail
    print(f"\n📊 Evaluating best trajectory in detail...")
    best_state_history, best_params_history = simulate_with_holonomy_path(
        opt_result.best_path,
        grid_size=grid_size,
        steps_per_unit_time=steps_per_unit_time,
        record_interval=5,
        seed=seed
    )
    
    best_metrics = compute_trajectory_metrics(
        best_state_history,
        target_state,
        best_params_history,
        phys_profile
    )
    
    print(f"\n   Final distance: {best_metrics.final_distance:.3f}")
    print(f"   Time to target: {best_metrics.time_to_target:.1f} steps")
    print(f"   Violations: {best_metrics.n_violations}")
    print(f"   Stability: {best_metrics.final_stability:.3f}")
    
    # 7. Sauvegarder
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder le path optimal
        with open(output_path / 'best_path.json', 'w') as f:
            json.dump(opt_result.best_path.to_dict(), f, indent=2)
        
        # Sauvegarder les métriques
        metrics_dict = {
            'composite_score': best_metrics.composite_score,
            'final_distance': best_metrics.final_distance,
            'time_to_target': best_metrics.time_to_target,
            'convergence_rate': best_metrics.convergence_rate,
            'final_stability': best_metrics.final_stability,
            'n_violations': best_metrics.n_violations,
            'max_violation_severity': best_metrics.max_violation_severity,
            'total_control_effort': best_metrics.total_control_effort
        }
        
        with open(output_path / 'best_metrics.json', 'w') as f:
            json.dump(metrics_dict, f, indent=2)
        
        # Sauvegarder l'historique
        history_data = []
        for i, (state, params) in enumerate(zip(best_state_history, best_params_history)):
            history_data.append({
                'step': i,
                'r': state.order_parameter_r,
                'defect_density': state.defect_density,
                'n_defects': state.n_defects,
                'k1': params.get('k1', 0),
                'annealing': params.get('annealing', 0)
            })
        
        df_history = pd.DataFrame(history_data)
        df_history.to_csv(output_path / 'trajectory_history.csv', index=False)
        
        # Sauvegarder tous les résultats d'optimisation
        all_results_data = []
        for params, cost in opt_result.all_evaluated:
            all_results_data.append({**params, 'cost': cost})
        
        df_all = pd.DataFrame(all_results_data)
        df_all = df_all.sort_values('cost')
        df_all.to_csv(output_path / 'all_evaluations.csv', index=False)
    
    # 8. Retour
    return {
        'best_path': opt_result.best_path,
        'best_metrics': best_metrics,
        'best_state_history': best_state_history,
        'best_params_history': best_params_history,
        'optimization_result': opt_result,
        'atlas_profile': phys_profile,
        'target_state': target_state
    }


def compare_trajectory_strategies(
    target_profile: str,
    atlas_profile: str,
    strategies: List[str] = ['linear_ramp', 'smooth_sigmoid'],
    n_evaluations_per_strategy: int = 15,
    output_dir: Optional[str] = None
) -> Dict:
    """
    Compare différentes stratégies de génération de trajectoire.
    
    Args:
        target_profile: Cible phéno
        atlas_profile: Système physique
        strategies: Liste de générateurs à comparer
        n_evaluations_per_strategy: Nombre d'évaluations par stratégie
        output_dir: Répertoire de sortie
        
    Returns:
        Dict avec résultats de comparaison
    """
    results = {}
    
    print(f"🔬 Comparing {len(strategies)} trajectory strategies...")
    
    for strategy in strategies:
        print(f"\n{'='*60}")
        print(f"Strategy: {strategy}")
        print(f"{'='*60}")
        
        result = optimize_holonomy_path(
            target_profile=target_profile,
            atlas_profile=atlas_profile,
            optimizer_type='random',
            n_evaluations=n_evaluations_per_strategy,
            path_generator=strategy,
            output_dir=str(Path(output_dir) / strategy) if output_dir else None
        )
        
        results[strategy] = result
    
    # Classement
    ranking = []
    for strategy, result in results.items():
        ranking.append({
            'strategy': strategy,
            'best_cost': result['best_metrics'].composite_score,
            'final_distance': result['best_metrics'].final_distance,
            'time_to_target': result['best_metrics'].time_to_target
        })
    
    ranking.sort(key=lambda x: x['best_cost'])
    
    print(f"\n{'='*60}")
    print(f"RANKING:")
    print(f"{'='*60}")
    for i, entry in enumerate(ranking, 1):
        print(f"{i}. {entry['strategy']:20s} | cost={entry['best_cost']:.4f} | distance={entry['final_distance']:.3f}")
    
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        with open(output_path / 'strategy_ranking.json', 'w') as f:
            json.dump({'ranking': ranking}, f, indent=2)
    
    return {
        'results': results,
        'ranking': ranking
    }

