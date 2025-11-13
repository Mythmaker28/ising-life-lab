"""
Fonctions de coût pour mesurer la distance entre états phénoménologiques.

Permet de comparer un état généré par simulation avec un état cible,
afin d'optimiser les paramètres pour atteindre un profil phénoménologique désiré.
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class PhenoState:
    """État phénoménologique résumé."""
    
    order_parameter_r: float  # Paramètre d'ordre Kuramoto [0, 1]
    defect_density: float  # Densité de défauts topologiques
    n_defects: int  # Nombre absolu de défauts
    annihilation_rate: float  # Taux d'annihilation (si historique dispo)
    
    # Statistiques additionnelles
    mean_phase: float = 0.0
    std_phase: float = 0.0
    
    def to_vector(self) -> np.ndarray:
        """Convertit en vecteur pour calcul de distance."""
        return np.array([
            self.order_parameter_r,
            self.defect_density,
            self.annihilation_rate,
            self.std_phase
        ])


def phenomenology_distance(
    state_a: PhenoState,
    state_b: PhenoState,
    weights: Dict[str, float] = None
) -> float:
    """
    Distance euclidienne pondérée entre deux états phénoménologiques.
    
    Args:
        state_a: État 1
        state_b: État 2
        weights: Poids pour chaque métrique. Par défaut :
            {'r': 2.0, 'density': 3.0, 'annihilation': 1.0, 'std': 0.5}
            
    Returns:
        Distance [0, inf), où 0 = états identiques
    """
    if weights is None:
        weights = {
            'r': 2.0,  # Paramètre d'ordre très important
            'density': 3.0,  # Densité de défauts critique
            'annihilation': 1.0,
            'std': 0.5
        }
    
    # Différences normalisées
    delta_r = abs(state_a.order_parameter_r - state_b.order_parameter_r)
    delta_density = abs(state_a.defect_density - state_b.defect_density)
    delta_annihilation = abs(state_a.annihilation_rate - state_b.annihilation_rate)
    delta_std = abs(state_a.std_phase - state_b.std_phase) / (np.pi + 1e-6)
    
    # Distance pondérée
    distance = np.sqrt(
        weights['r'] * delta_r**2 +
        weights['density'] * delta_density**2 +
        weights['annihilation'] * delta_annihilation**2 +
        weights['std'] * delta_std**2
    )
    
    return distance


def phenomenology_score(
    state_generated: PhenoState,
    state_target: PhenoState,
    max_distance: float = 5.0
) -> float:
    """
    Score de similarité [0, 1] où 1 = parfaite correspondance.
    
    Args:
        state_generated: État généré par simulation
        state_target: État cible désiré
        max_distance: Distance maximale pour normalisation
        
    Returns:
        Score ∈ [0, 1]
    """
    distance = phenomenology_distance(state_generated, state_target)
    score = np.exp(-distance / max_distance)
    return score


def regime_classifier(state: PhenoState) -> str:
    """
    Classifie un état phénoménologique en régime.
    
    Returns:
        'uniform', 'fragmented', 'intermediate', ou 'chaotic'
    """
    r = state.order_parameter_r
    density = state.defect_density
    
    if r > 0.85 and density < 0.01:
        return 'uniform'  # Type 5-MeO-DMT
    elif r < 0.4 and density > 0.05:
        return 'fragmented'  # Type N,N-DMT
    elif density > 0.1 and state.annihilation_rate < 0:
        return 'chaotic'  # Instable
    else:
        return 'intermediate'


def compute_target_profile(regime: str) -> PhenoState:
    """
    Génère un profil phénoménologique cible selon le régime désiré.
    
    Args:
        regime: 'uniform', 'fragmented', 'balanced'
        
    Returns:
        PhenoState cible
    """
    if regime == 'uniform':
        # Profil 5-MeO-DMT : haute synchronie, peu de défauts
        return PhenoState(
            order_parameter_r=0.95,
            defect_density=0.002,
            n_defects=5,
            annihilation_rate=0.5,  # Positif = annihilation active
            mean_phase=np.pi,
            std_phase=0.3
        )
    
    elif regime == 'fragmented':
        # Profil N,N-DMT : basse synchronie, défauts persistants
        return PhenoState(
            order_parameter_r=0.25,
            defect_density=0.08,
            n_defects=200,
            annihilation_rate=0.02,  # Proche de zéro = défauts stables
            mean_phase=np.pi,
            std_phase=1.5
        )
    
    else:  # balanced
        return PhenoState(
            order_parameter_r=0.6,
            defect_density=0.02,
            n_defects=50,
            annihilation_rate=0.1,
            mean_phase=np.pi,
            std_phase=0.8
        )


def multi_objective_cost(
    state: PhenoState,
    target_r: float,
    target_density: float,
    lambda_r: float = 1.0,
    lambda_density: float = 1.0
) -> float:
    """
    Fonction de coût multi-objectif.
    
    Minimise : λ_r·(r - r_target)² + λ_density·(density - density_target)²
    
    Args:
        state: État actuel
        target_r: Paramètre d'ordre cible
        target_density: Densité de défauts cible
        lambda_r: Poids du paramètre d'ordre
        lambda_density: Poids de la densité
        
    Returns:
        Coût total (à minimiser)
    """
    cost_r = lambda_r * (state.order_parameter_r - target_r)**2
    cost_density = lambda_density * (state.defect_density - target_density)**2
    
    return cost_r + cost_density


