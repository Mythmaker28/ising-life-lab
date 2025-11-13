"""
Fonctions de coût pour l'optimisation de trajectoires holonomiques.

Permet d'évaluer et d'optimiser des HolonomyPath selon plusieurs critères :
- Efficacité : Vitesse d'atteinte de la cible
- Stabilité : Qualité de l'état final
- Violations : Respect des contraintes physiques
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from ..data_bridge.atlas_map import AtlasProfile
from ..data_bridge.cost_functions import PhenoState


@dataclass
class TrajectoryMetrics:
    """Métriques d'une trajectoire complète."""
    
    # Efficacité temporelle
    time_to_target: float  # Temps pour atteindre la cible (steps)
    convergence_rate: float  # Vitesse de convergence
    
    # Qualité finale
    final_distance: float  # Distance à la cible phénoménologique
    final_stability: float  # Stabilité de l'état final (variance sur derniers steps)
    
    # Contraintes physiques
    n_violations: int  # Nombre de violations de contraintes
    max_violation_severity: float  # Sévérité maximale [0, 1]
    
    # Efficacité énergétique (conceptuel)
    total_control_effort: float  # Intégrale de ||∂K/∂t||²
    
    # Score composite
    composite_score: float  # Score global combinant tous les critères


def cost_efficiency(
    state_history: List[PhenoState],
    target_state: PhenoState,
    distance_threshold: float = 0.5
) -> float:
    """
    Coût d'efficacité : Temps pour atteindre la cible.
    
    Plus le temps est court, meilleur est le score.
    
    Args:
        state_history: Historique des états phéno générés
        target_state: État cible
        distance_threshold: Seuil de distance pour considérer la cible atteinte
        
    Returns:
        Coût normalisé [0, 1] où 0 = très efficace, 1 = inefficace
    """
    from ..data_bridge.cost_functions import phenomenology_distance
    
    # Trouver le premier moment où on atteint la cible
    time_to_target = len(state_history)  # Par défaut : jamais atteint
    
    for i, state in enumerate(state_history):
        distance = phenomenology_distance(state, target_state)
        if distance < distance_threshold:
            time_to_target = i
            break
    
    # Normaliser : plus court = mieux
    efficiency_cost = time_to_target / len(state_history)
    
    return efficiency_cost


def cost_stability(
    state_history: List[PhenoState],
    window_size: int = 10
) -> float:
    """
    Coût de stabilité : Variance de l'état final.
    
    Un état stable présente peu de fluctuations en fin de trajectoire.
    
    Args:
        state_history: Historique des états
        window_size: Taille de la fenêtre pour mesurer la stabilité
        
    Returns:
        Coût [0, 1] où 0 = très stable, 1 = instable
    """
    if len(state_history) < window_size:
        return 1.0
    
    # Derniers états
    final_states = state_history[-window_size:]
    
    # Variance du paramètre d'ordre r
    r_values = [s.order_parameter_r for s in final_states]
    r_variance = np.var(r_values)
    
    # Variance de la densité de défauts
    density_values = [s.defect_density for s in final_states]
    density_variance = np.var(density_values)
    
    # Score composite (variances normalisées)
    stability_cost = np.clip(r_variance * 10 + density_variance * 100, 0, 1)
    
    return stability_cost


def cost_violation(
    path_params_history: List[Dict[str, float]],
    atlas_profile: AtlasProfile,
    k_max_margin: float = 0.1
) -> Tuple[float, int]:
    """
    Coût de violation des contraintes physiques.
    
    Pénalise les trajectoires qui dépassent K_max ou violent d'autres contraintes.
    
    Args:
        path_params_history: Historique des paramètres (K1, K2, noise, annealing)
        atlas_profile: Profil physique du système
        k_max_margin: Marge de sécurité pour K_max
        
    Returns:
        (violation_cost, n_violations)
    """
    from ..data_bridge.atlas_map import AtlasMapper
    
    mapper = AtlasMapper()
    k_max_safe = mapper._compute_k_max(atlas_profile.t1_us, atlas_profile.t2_us) * (1 - k_max_margin)
    noise_max_safe = 0.3
    
    violations = []
    
    for params in path_params_history:
        k1 = params.get('k1', 0.0)
        noise = params.get('noise', 0.0)
        
        # Violation K_max
        if k1 > k_max_safe:
            severity = (k1 - k_max_safe) / k_max_safe
            violations.append(severity)
        
        # Violation noise_max
        if noise > noise_max_safe:
            severity = (noise - noise_max_safe) / noise_max_safe
            violations.append(severity)
    
    n_violations = len(violations)
    
    if n_violations == 0:
        return 0.0, 0
    
    # Coût = moyenne des sévérités
    violation_cost = np.mean(violations)
    
    return np.clip(violation_cost, 0, 1), n_violations


def cost_control_effort(
    path_params_history: List[Dict[str, float]],
    dt: float = 0.1
) -> float:
    """
    Coût de l'effort de contrôle : intégrale de ||∂K/∂t||².
    
    Pénalise les changements brusques de paramètres (smoothness).
    
    Args:
        path_params_history: Historique des paramètres
        dt: Pas de temps
        
    Returns:
        Coût normalisé [0, 1]
    """
    if len(path_params_history) < 2:
        return 0.0
    
    total_effort = 0.0
    
    for i in range(1, len(path_params_history)):
        prev_params = path_params_history[i-1]
        curr_params = path_params_history[i]
        
        # Différences de K1, K2, annealing
        dk1 = curr_params.get('k1', 0) - prev_params.get('k1', 0)
        dk2 = curr_params.get('k2', 0) - prev_params.get('k2', 0)
        d_annealing = curr_params.get('annealing', 0) - prev_params.get('annealing', 0)
        
        # Norme L2 des dérivées
        norm_squared = dk1**2 + dk2**2 + d_annealing**2
        total_effort += norm_squared / (dt + 1e-6)
    
    # Normaliser par le nombre de steps
    avg_effort = total_effort / len(path_params_history)
    
    # Normaliser à [0, 1] (valeurs typiques < 10)
    return np.clip(avg_effort / 10.0, 0, 1)


def compute_trajectory_metrics(
    state_history: List[PhenoState],
    target_state: PhenoState,
    path_params_history: List[Dict[str, float]],
    atlas_profile: AtlasProfile,
    weights: Optional[Dict[str, float]] = None
) -> TrajectoryMetrics:
    """
    Calcule toutes les métriques d'une trajectoire et le score composite.
    
    Args:
        state_history: Historique des états phéno
        target_state: État cible
        path_params_history: Historique des paramètres de contrôle
        atlas_profile: Profil physique du système
        weights: Poids pour le score composite
            - 'efficiency': poids de l'efficacité temporelle
            - 'stability': poids de la stabilité
            - 'violation': poids des violations
            - 'effort': poids de l'effort de contrôle
            
    Returns:
        TrajectoryMetrics complet
    """
    from ..data_bridge.cost_functions import phenomenology_distance
    
    if weights is None:
        weights = {
            'efficiency': 2.0,
            'stability': 1.5,
            'violation': 3.0,  # Pénalité forte
            'effort': 0.5
        }
    
    # Coût d'efficacité
    efficiency_cost = cost_efficiency(state_history, target_state)
    
    # Coût de stabilité
    stability_cost = cost_stability(state_history)
    
    # Coût de violation
    violation_cost, n_violations = cost_violation(path_params_history, atlas_profile)
    
    # Coût d'effort
    effort_cost = cost_control_effort(path_params_history)
    
    # Distance finale
    final_distance = phenomenology_distance(state_history[-1], target_state)
    
    # Temps d'atteinte
    time_to_target = efficiency_cost * len(state_history)
    
    # Taux de convergence (pente moyenne de la distance)
    if len(state_history) > 1:
        distances = [phenomenology_distance(s, target_state) for s in state_history]
        convergence_rate = -(distances[-1] - distances[0]) / len(distances)
    else:
        convergence_rate = 0.0
    
    # Score composite (minimiser)
    composite_score = (
        weights['efficiency'] * efficiency_cost +
        weights['stability'] * stability_cost +
        weights['violation'] * violation_cost +
        weights['effort'] * effort_cost
    )
    
    # Normaliser par la somme des poids
    total_weight = sum(weights.values())
    composite_score /= total_weight
    
    # Sévérité maximale de violation
    if n_violations > 0:
        max_severity = violation_cost
    else:
        max_severity = 0.0
    
    return TrajectoryMetrics(
        time_to_target=time_to_target,
        convergence_rate=convergence_rate,
        final_distance=final_distance,
        final_stability=1 - stability_cost,  # Inverser : plus haut = plus stable
        n_violations=n_violations,
        max_violation_severity=max_severity,
        total_control_effort=effort_cost * len(path_params_history),
        composite_score=composite_score
    )


def rank_trajectories(
    trajectories_metrics: List[Tuple[str, TrajectoryMetrics]]
) -> List[Tuple[str, TrajectoryMetrics, float]]:
    """
    Classe des trajectoires par score composite.
    
    Args:
        trajectories_metrics: Liste de (nom_trajectoire, metrics)
        
    Returns:
        Liste triée de (nom, metrics, rank_score) du meilleur au pire
    """
    # Extraire les scores
    scores = [(name, metrics, metrics.composite_score) 
              for name, metrics in trajectories_metrics]
    
    # Trier par score (plus bas = meilleur)
    scores.sort(key=lambda x: x[2])
    
    return scores

