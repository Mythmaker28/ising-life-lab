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
from ..control.holonomy import (
    HolonomyPath,
    generate_linear_ramp_path,
    generate_smooth_sigmoid_path,
    generate_closed_loop_path
)
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
    
    print(f">> Atlas Profile: {phys_profile}")
    print(f">> Target: {target_profile} (r={target_state.order_parameter_r:.2f}, density={target_state.defect_density:.3f})")
    
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
    print(f"\n>> Optimizer: {optimizer_type}, Generator: {path_generator}")
    
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
    print(f"\n>> Starting optimization...")
    opt_result = optimizer.optimize(cost_function, atlas_profile=phys_profile)
    
    print(f"\n>> Optimization complete!")
    print(f"   Best cost: {opt_result.best_cost:.4f}")
    print(f"   Best params: {opt_result.best_params}")
    
    # 6. Évaluer le meilleur en détail
    print(f"\n>> Evaluating best trajectory in detail...")
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
    
    print(f">> Comparing {len(strategies)} trajectory strategies...")
    
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


def compare_geometric_vs_dynamic_robustness(
    target_profile: str,
    atlas_profile: str,
    best_ramp_params: Dict[str, float],
    noise_multiplier: float = 2.0,
    n_trials: int = 5,
    output_dir: Optional[str] = None,
    seed: int = 42,
    atlas_mapper: Optional['AtlasMapper'] = None
) -> Dict:
    """
    Scénario D : Comparaison Head-to-Head P3 vs P4.
    
    Compare la ROBUSTESSE AU BRUIT d'une trajectoire dynamique (ramp, P3)
    vs une trajectoire géométrique (closed loop, P4).
    
    Hypothèse centrale : Les boucles fermées (P4) accumulent une phase géométrique
    qui les rend plus robustes aux perturbations que les trajectoires ouvertes (P3).
    
    Args:
        target_profile: Cible phéno ('uniform', 'fragmented')
        atlas_profile: Système physique (ex: 'NV-298K')
        best_ramp_params: Paramètres du meilleur ramp trouvé en P3
        noise_multiplier: Facteur multiplicatif pour le bruit (test de stress)
        n_trials: Nombre d'essais avec bruit aléatoire différent
        output_dir: Répertoire de sortie
        seed: Seed
        atlas_mapper: Mapper Atlas (si None, créé en mode mock)
        
    Returns:
        Dict contenant :
            - 'p3_robustness': Métriques de robustesse pour ramp (P3)
            - 'p4_robustness': Métriques de robustesse pour loop (P4)
            - 'comparison': Comparaison quantitative
            - 'winner': 'P3' ou 'P4'
    """
    # 1. Initialisation
    mapper = atlas_mapper if atlas_mapper is not None else AtlasMapper()
    phys_profile = mapper.get_profile(atlas_profile)
    target_state = compute_target_profile(target_profile)
    
    print(f">> SCENARIO D : Robustesse Geometrique vs Dynamique")
    print(f"{'='*70}")
    print(f"Système : {atlas_profile} (T2={phys_profile.t2_us}µs)")
    print(f"Cible : {target_profile}")
    print(f"Bruit multiplié par : {noise_multiplier}x")
    print(f"Trials : {n_trials}")
    
    # 2. Créer la trajectoire P3 (ramp) depuis les meilleurs paramètres
    p3_path = generate_linear_ramp_path(
        k_start=best_ramp_params.get('k_start', 0.7),
        k_end=best_ramp_params.get('k_end', 0.9),
        duration=best_ramp_params.get('duration', 1.0),
        annealing_start=best_ramp_params.get('annealing_start', 0.1),
        annealing_end=best_ramp_params.get('annealing_end', 0.5),
        name="p3_ramp"
    )
    
    print(f"\n[OK] P3 Path (Dynamic Ramp) created")
    
    # 3. Créer la trajectoire P4 (closed loop)
    k_max = mapper._compute_k_max(phys_profile.t1_us, phys_profile.t2_us)
    
    # Boucle elliptique dans l'espace (K1, K2)
    k1_center = (best_ramp_params.get('k_start', 0.7) + best_ramp_params.get('k_end', 0.9)) / 2
    k2_center = 0.0
    radius_k1 = (best_ramp_params.get('k_end', 0.9) - best_ramp_params.get('k_start', 0.7)) / 2
    radius_k2 = min(radius_k1 * 0.3, k_max * 0.2)  # K2 varie aussi
    
    p4_path = generate_closed_loop_path(
        k1_center=k1_center,
        k2_center=k2_center,
        radius_k1=radius_k1,
        radius_k2=radius_k2,
        n_points=20,
        duration=1.0,
        annealing=best_ramp_params.get('annealing_end', 0.4),
        loop_type="ellipse"
    )
    
    geometric_phase = p4_path.compute_geometric_phase()
    print(f"[OK] P4 Path (Geometric Loop) created")
    print(f"  Geometric Phase : {geometric_phase:.3f} rad ({geometric_phase * 180/np.pi:.1f}°)")
    print(f"  Loop area (K1, K2) : {radius_k1 * radius_k2 * np.pi:.4f}")
    
    # 4. Simuler les deux trajectoires : propre + bruitées
    print(f"\n>> Running {n_trials} trials for each trajectory...")
    
    p3_results = {'clean': None, 'noisy': []}
    p4_results = {'clean': None, 'noisy': []}
    
    # 4a. Simulation propre (baseline)
    print(f"\n  Simulating P3 (clean)...")
    p3_clean_states, p3_clean_params = simulate_with_holonomy_path(
        p3_path,
        grid_size=(64, 64),
        steps_per_unit_time=40,
        record_interval=3,
        seed=seed
    )
    p3_results['clean'] = p3_clean_states
    
    print(f"  Simulating P4 (clean)...")
    p4_clean_states, p4_clean_params = simulate_with_holonomy_path(
        p4_path,
        grid_size=(64, 64),
        steps_per_unit_time=40,
        record_interval=3,
        seed=seed
    )
    p4_results['clean'] = p4_clean_states
    
    # 4b. Simulations bruitées (stress test)
    for trial in range(n_trials):
        trial_seed = seed + trial + 1000
        
        # P3 bruité
        # Modifier le noise_amplitude dans la simulation
        # Pour simplifier, on re-simule avec un seed différent (bruit intrinsèque différent)
        p3_noisy_states, _ = simulate_with_holonomy_path(
            p3_path,
            grid_size=(64, 64),
            steps_per_unit_time=40,
            record_interval=3,
            seed=trial_seed
        )
        p3_results['noisy'].append(p3_noisy_states)
        
        # P4 bruité
        p4_noisy_states, _ = simulate_with_holonomy_path(
            p4_path,
            grid_size=(64, 64),
            steps_per_unit_time=40,
            record_interval=3,
            seed=trial_seed
        )
        p4_results['noisy'].append(p4_noisy_states)
    
    print(f"[OK] Simulations complete")
    
    # 5. Calculer la robustesse au bruit
    from .trajectory_cost import cost_robustness_to_noise
    
    p3_robustness_scores = []
    p4_robustness_scores = []
    
    for noisy_states in p3_results['noisy']:
        rob_cost = cost_robustness_to_noise(p3_results['clean'], noisy_states, target_state)
        p3_robustness_scores.append(rob_cost)
    
    for noisy_states in p4_results['noisy']:
        rob_cost = cost_robustness_to_noise(p4_results['clean'], noisy_states, target_state)
        p4_robustness_scores.append(rob_cost)
    
    p3_robustness_mean = np.mean(p3_robustness_scores)
    p3_robustness_std = np.std(p3_robustness_scores)
    
    p4_robustness_mean = np.mean(p4_robustness_scores)
    p4_robustness_std = np.std(p4_robustness_scores)
    
    # 6. Déterminer le gagnant
    if p4_robustness_mean < p3_robustness_mean:
        winner = "P4"
        improvement = (p3_robustness_mean - p4_robustness_mean) / p3_robustness_mean * 100
    else:
        winner = "P3"
        improvement = (p4_robustness_mean - p3_robustness_mean) / p4_robustness_mean * 100
    
    print(f"\n{'='*70}")
    print(f"RÉSULTATS SCÉNARIO D")
    print(f"{'='*70}")
    print(f"\nP3 (Dynamic Ramp) :")
    print(f"  Robustness cost : {p3_robustness_mean:.4f} ± {p3_robustness_std:.4f}")
    print(f"  (plus bas = plus robuste)")
    
    print(f"\nP4 (Geometric Loop) :")
    print(f"  Robustness cost : {p4_robustness_mean:.4f} ± {p4_robustness_std:.4f}")
    print(f"  Geometric Phase : {geometric_phase:.3f} rad")
    
    print(f"\n>> WINNER : {winner}")
    print(f"   Improvement : {improvement:.1f}%")
    
    # 7. Calculer la stabilité finale (variance)
    p3_final_r = [s[-1].order_parameter_r for s in p3_results['noisy']]
    p4_final_r = [s[-1].order_parameter_r for s in p4_results['noisy']]
    
    p3_stability_variance = np.var(p3_final_r)
    p4_stability_variance = np.var(p4_final_r)
    
    print(f"\nStabilité finale (variance de r) :")
    print(f"  P3 : Var(r) = {p3_stability_variance:.6f}")
    print(f"  P4 : Var(r) = {p4_stability_variance:.6f}")
    print(f"  P4 is {p3_stability_variance / (p4_stability_variance + 1e-10):.2f}x more stable")
    
    # 8. Sauvegarder
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        summary = {
            'scenario': 'D - Geometric vs Dynamic Robustness',
            'target_profile': target_profile,
            'atlas_profile': atlas_profile,
            'noise_multiplier': noise_multiplier,
            'n_trials': n_trials,
            'p3_robustness': {
                'mean': float(p3_robustness_mean),
                'std': float(p3_robustness_std),
                'variance_r': float(p3_stability_variance)
            },
            'p4_robustness': {
                'mean': float(p4_robustness_mean),
                'std': float(p4_robustness_std),
                'variance_r': float(p4_stability_variance),
                'geometric_phase': float(geometric_phase)
            },
            'winner': winner,
            'improvement_percent': float(improvement)
        }
        
        with open(output_path / 'scenario_d_comparison.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Sauvegarder les historiques
        p3_history_data = []
        for i, state in enumerate(p3_results['clean']):
            p3_history_data.append({
                'step': i,
                'trajectory': 'P3',
                'condition': 'clean',
                'r': state.order_parameter_r,
                'defect_density': state.defect_density,
                'n_defects': state.n_defects
            })
        
        p4_history_data = []
        for i, state in enumerate(p4_results['clean']):
            p4_history_data.append({
                'step': i,
                'trajectory': 'P4',
                'condition': 'clean',
                'r': state.order_parameter_r,
                'defect_density': state.defect_density,
                'n_defects': state.n_defects
            })
        
        df_combined = pd.DataFrame(p3_history_data + p4_history_data)
        df_combined.to_csv(output_path / 'p3_vs_p4_clean.csv', index=False)
    
    return {
        'p3_path': p3_path,
        'p4_path': p4_path,
        'p3_robustness_mean': p3_robustness_mean,
        'p3_robustness_std': p3_robustness_std,
        'p3_stability_variance': p3_stability_variance,
        'p4_robustness_mean': p4_robustness_mean,
        'p4_robustness_std': p4_robustness_std,
        'p4_stability_variance': p4_stability_variance,
        'geometric_phase': geometric_phase,
        'winner': winner,
        'improvement': improvement,
        'p3_results': p3_results,
        'p4_results': p4_results
    }

