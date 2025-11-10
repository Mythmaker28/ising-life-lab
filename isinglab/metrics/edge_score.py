"""
Edge-of-Chaos Score - Composite metric for criticality.

The edge-of-chaos is characterized by:
- Moderate entropy (neither ordered nor fully random)
- Some sensitivity to initial conditions (but not extreme)
- Presence of memory/attractors (but not fixed points)
- Balance between activity and inactivity

This module provides transparent, quantitative scoring.
"""

import numpy as np
from typing import List, Dict
from .entropy import shannon_entropy, spatial_entropy, activity_level
from .sensitivity import hamming_sensitivity
from .memory import memory_score, attractor_analysis


def edge_of_chaos_score(
    history: List[np.ndarray],
    sensitivity: float,
    memory: float,
    target_entropy: float = 0.5,
    target_activity: float = 0.3
) -> float:
    """
    Compute edge-of-chaos score from pre-computed metrics.
    
    Edge-of-chaos is characterized by:
    1. Moderate entropy (not too ordered, not too random)
    2. Moderate sensitivity (some chaos, but not extreme)
    3. Memory-like behavior (attractors, but not trivial fixed points)
    4. Balanced activity (not frozen, not fully active)
    
    Formula:
        edge_score = entropy_term * sensitivity_term * memory_term * activity_term
    
    Where each term is a bell-shaped function peaked at "optimal" values.
    
    Args:
        history: State history
        sensitivity: Pre-computed sensitivity metric (e.g., Hamming distance)
        memory: Pre-computed memory score
        target_entropy: Target normalized entropy (default 0.5)
        target_activity: Target activity level (default 0.3)
        
    Returns:
        Edge score in [0, 1], where 1 = perfect edge-of-chaos
    """
    if not history or len(history) < 2:
        return 0.0
    
    # 1. Entropy term: peaked at target_entropy
    entropy = shannon_entropy(history[-1])
    max_entropy = 1.0  # For binary states
    norm_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
    
    # sigma=0.2 allows more variability (was 0.1, too restrictive for chaotic rules)
    entropy_term = np.exp(-((norm_entropy - target_entropy) ** 2) / (2 * 0.2 ** 2))
    
    # 2. Sensitivity term: moderate sensitivity preferred
    # Too low = ordered, too high = chaotic
    # Optimal around 0.2-0.4 (empirical)
    target_sensitivity = 0.3
    sensitivity_term = np.exp(-((sensitivity - target_sensitivity) ** 2) / (2 * 0.15 ** 2))
    
    # 3. Memory term: some memory, but not trivial
    # Optimal around 0.4-0.6 (has attractors but not just fixed point)
    # Using Gaussian to avoid annihilating chaotic rules (memory=0)
    target_memory = 0.5
    memory_term = np.exp(-((memory - target_memory) ** 2) / (2 * 0.25 ** 2))
    
    # 4. Activity term: balanced activity
    activity = activity_level(history[-1])
    activity_term = np.exp(-((activity - target_activity) ** 2) / (2 * 0.2 ** 2))
    
    # Composite score (geometric mean for balanced criteria)
    edge_score = (entropy_term * sensitivity_term * memory_term * activity_term) ** 0.25
    
    return float(np.clip(edge_score, 0.0, 1.0))


def composite_edge_metric(
    history: List[np.ndarray],
    evolution_func=None,
    initial_state=None,
    steps: int = 50,
    seed: int = 42
) -> Dict:
    """
    Compute comprehensive edge-of-chaos metrics.
    
    This is the main API for evaluating a CA/Ising rule.
    
    Args:
        history: Complete state history
        evolution_func: Optional evolution function for sensitivity calculation
        initial_state: Initial state for sensitivity
        steps: Steps for sensitivity measurement
        seed: Random seed
        
    Returns:
        Dictionary with all metrics:
        - entropy: Shannon entropy
        - spatial_entropy: Spatial pattern complexity
        - sensitivity: Hamming sensitivity
        - memory_score: Memory quantification
        - edge_score: Composite edge-of-chaos score
        - activity: Activity level
        - attractor_type: Type of attractor
        - attractor_period: Period if cyclic
    """
    if not history or len(history) < 2:
        return {
            "entropy": 0.0,
            "spatial_entropy": 0.0,
            "sensitivity": 0.0,
            "memory_score": 0.0,
            "edge_score": 0.0,
            "activity": 0.0,
            "attractor_type": "unknown",
            "attractor_period": 0
        }
    
    # Compute individual metrics
    entropy = shannon_entropy(history[-1])
    spatial_ent = spatial_entropy(history[-1])
    memory = memory_score(history)
    activity = activity_level(history[-1])
    
    # Attractor analysis
    attractor_info = attractor_analysis(history)
    
    # Sensitivity (if evolution function provided)
    if evolution_func is not None and initial_state is not None:
        sensitivity = hamming_sensitivity(
            evolution_func,
            initial_state,
            steps=steps,
            seed=seed
        )
    else:
        # Estimate from history variability
        if len(history) > 1:
            diffs = [np.mean(history[i] != history[i+1]) for i in range(len(history)-1)]
            sensitivity = np.mean(diffs)
        else:
            sensitivity = 0.0
    
    # Compute edge score
    edge = edge_of_chaos_score(
        history,
        sensitivity=sensitivity,
        memory=memory
    )
    
    return {
        "entropy": float(entropy),
        "spatial_entropy": float(spatial_ent),
        "sensitivity": float(sensitivity),
        "memory_score": float(memory),
        "edge_score": float(edge),
        "activity": float(activity),
        "attractor_type": attractor_info["type"],
        "attractor_period": attractor_info["period"],
        "attractor_stability": attractor_info["stability"]
    }


def lambda_parameter_estimate(history: List[np.ndarray]) -> float:
    """
    Estimate Langton's λ parameter for CA rules.
    
    λ is defined as the fraction of non-quiescent transitions in the rule table.
    
    For actual dynamics, we estimate it from activity patterns:
        λ ≈ activity × (1 + variability)
    
    Edge-of-chaos occurs around λ ≈ 0.45 - 0.55 (empirically).
    
    ⚠️ EXPERIMENTAL: This is a HEURISTIC APPROXIMATION.
    True λ requires analyzing the complete rule table (exact calculation possible
    for elementary CA with 2^8 = 256 configurations, but not implemented yet).
    
    Args:
        history: State history
        
    Returns:
        Estimated λ in [0, 1]
    """
    # Convert to list if numpy array
    if isinstance(history, np.ndarray):
        if history.ndim == 2:
            # Single state passed, wrap in list
            history = [history]
        elif history.ndim == 3:
            # 3D array: (timesteps, height, width)
            history = [history[i] for i in range(len(history))]
    
    if len(history) < 2:
        return 0.0
    
    # Activity level
    activity = activity_level(history[-1])
    
    # Variability (how much activity changes)
    activities = [activity_level(state) for state in history]
    variability = np.std(activities)
    
    # Estimate λ
    lambda_est = activity * (1.0 + variability)
    
    return float(np.clip(lambda_est, 0.0, 1.0))

