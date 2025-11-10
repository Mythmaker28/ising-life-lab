"""
Sensitivity and Lyapunov exponent measures.

Quantifies sensitivity to initial conditions - a hallmark of chaos.
"""

import numpy as np
from typing import List, Callable, Optional


def hamming_distance(state1: np.ndarray, state2: np.ndarray) -> float:
    """
    Compute normalized Hamming distance between two states.
    
    Args:
        state1, state2: Binary or spin grids
        
    Returns:
        Hamming distance in [0, 1]
    """
    return np.mean(state1 != state2)


def hamming_sensitivity(
    evolution_func: Callable,
    initial_state: np.ndarray,
    steps: int,
    perturbation: float = 0.01,
    n_samples: int = 5,
    seed: Optional[int] = None
) -> float:
    """
    Compute sensitivity to initial conditions via Hamming distance.
    
    Perturbs initial state slightly and measures divergence over time.
    
    Args:
        evolution_func: Function that evolves a state for 'steps' steps
        initial_state: Reference initial condition
        steps: Number of evolution steps
        perturbation: Fraction of bits to flip (0.01 = 1%)
        n_samples: Number of perturbed trajectories to average
        seed: Random seed
        
    Returns:
        Mean Hamming distance at final time (proxy for sensitivity)
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Evolve reference trajectory
    reference_final = evolution_func(initial_state.copy(), steps)
    
    distances = []
    for _ in range(n_samples):
        # Create perturbed initial state
        perturbed = initial_state.copy()
        n_flips = max(1, int(perturbed.size * perturbation))
        flat_perturbed = perturbed.flatten()
        flip_indices = np.random.choice(len(flat_perturbed), n_flips, replace=False)
        
        for idx in flip_indices:
            flat_perturbed[idx] = 1 - flat_perturbed[idx]  # Flip bit
        
        perturbed = flat_perturbed.reshape(initial_state.shape)
        
        # Evolve perturbed trajectory
        perturbed_final = evolution_func(perturbed, steps)
        
        # Measure distance
        dist = hamming_distance(reference_final, perturbed_final)
        distances.append(dist)
    
    return np.mean(distances)


def lyapunov_exponent(
    evolution_func: Callable,
    initial_state: np.ndarray,
    steps: int,
    perturbation: float = 0.01,
    transient: int = 50,
    seed: Optional[int] = None
) -> float:
    """
    Estimate Lyapunov exponent for discrete systems.
    
    Measures exponential divergence rate:
        λ = lim_{t→∞} (1/t) * log(d(t) / d(0))
    
    Positive λ indicates chaos, zero indicates edge-of-chaos, negative is stable.
    
    Args:
        evolution_func: Function that evolves state one step
        initial_state: Initial condition
        steps: Number of steps to measure
        perturbation: Initial perturbation size
        transient: Steps to skip (transient behavior)
        seed: Random seed
        
    Returns:
        Estimated Lyapunov exponent
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Initial perturbation
    state1 = initial_state.copy()
    state2 = initial_state.copy()
    
    n_flips = max(1, int(state2.size * perturbation))
    flat_state2 = state2.flatten()
    flip_indices = np.random.choice(len(flat_state2), n_flips, replace=False)
    
    for idx in flip_indices:
        flat_state2[idx] = 1 - flat_state2[idx]
    
    state2 = flat_state2.reshape(initial_state.shape)
    
    d0 = hamming_distance(state1, state2)
    
    if d0 == 0:
        return 0.0
    
    # Skip transient
    for _ in range(transient):
        state1 = evolution_func(state1, 1)
        state2 = evolution_func(state2, 1)
    
    # Measure divergence
    log_divergences = []
    
    for t in range(1, steps + 1):
        state1 = evolution_func(state1, 1)
        state2 = evolution_func(state2, 1)
        
        dt = hamming_distance(state1, state2)
        
        if dt > 0:
            log_div = np.log(dt / d0)
            log_divergences.append(log_div / t)
    
    if not log_divergences:
        return 0.0
    
    # Average over time
    lyapunov = np.mean(log_divergences)
    
    return float(lyapunov)


def mutual_information(history: List[np.ndarray], lag: int = 1) -> float:
    """
    Compute mutual information between states at time t and t+lag.
    
    Measures predictability and memory in the dynamics.
    
    Args:
        history: Sequence of states
        lag: Time lag
        
    Returns:
        Mutual information (bits)
    """
    if len(history) < lag + 1:
        return 0.0
    
    # Discretize states (use spatial patterns as symbols)
    def state_to_symbol(state):
        return tuple(state.flatten())
    
    # Extract symbol sequences
    symbols_t = [state_to_symbol(history[i]) for i in range(len(history) - lag)]
    symbols_t_lag = [state_to_symbol(history[i + lag]) for i in range(len(history) - lag)]
    
    # Count joint and marginal probabilities
    from collections import Counter
    
    joint_counts = Counter(zip(symbols_t, symbols_t_lag))
    counts_t = Counter(symbols_t)
    counts_t_lag = Counter(symbols_t_lag)
    
    n_total = len(symbols_t)
    
    # Compute MI
    mi = 0.0
    for (sym_t, sym_t_lag), joint_count in joint_counts.items():
        p_joint = joint_count / n_total
        p_t = counts_t[sym_t] / n_total
        p_t_lag = counts_t_lag[sym_t_lag] / n_total
        
        if p_joint > 0 and p_t > 0 and p_t_lag > 0:
            mi += p_joint * np.log2(p_joint / (p_t * p_t_lag))
    
    return mi

