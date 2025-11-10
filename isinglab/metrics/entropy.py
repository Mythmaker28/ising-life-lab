"""
Entropy measures for CA and Ising systems.

Provides:
- Shannon entropy of state distributions
- Spatial entropy (pattern complexity)
- Temporal entropy (time series)
"""

import numpy as np
from typing import List, Union


def shannon_entropy(states: Union[np.ndarray, List[np.ndarray]], base: int = 2) -> float:
    """
    Compute Shannon entropy of state distribution.
    
    For discrete states, computes:
        H = -sum_i p_i * log(p_i)
    
    Args:
        states: Single state or list of states (binary grids)
        base: Logarithm base (2 for bits, e for nats)
        
    Returns:
        Shannon entropy in specified units
    """
    if isinstance(states, list):
        # Flatten all states
        all_states = np.concatenate([s.flatten() for s in states])
    else:
        all_states = states.flatten()
    
    # Count frequencies
    unique, counts = np.unique(all_states, return_counts=True)
    probabilities = counts / len(all_states)
    
    # Compute entropy
    log_func = np.log2 if base == 2 else np.log
    entropy = -np.sum(probabilities * log_func(probabilities))
    
    return float(entropy)


def spatial_entropy(state: np.ndarray, block_size: int = 2) -> float:
    """
    Compute spatial entropy using block patterns.
    
    Measures complexity of spatial patterns by counting unique blocks.
    Higher values indicate more complex spatial structure.
    
    Args:
        state: 2D grid state
        block_size: Size of blocks to analyze (e.g., 2 for 2x2)
        
    Returns:
        Spatial entropy (normalized by max possible)
    """
    if state.ndim == 1:
        # 1D case: use sliding windows
        blocks = []
        for i in range(len(state) - block_size + 1):
            block = tuple(state[i:i+block_size])
            blocks.append(block)
    else:
        # 2D case: extract all blocks
        h, w = state.shape
        blocks = []
        for i in range(h - block_size + 1):
            for j in range(w - block_size + 1):
                block = tuple(state[i:i+block_size, j:j+block_size].flatten())
                blocks.append(block)
    
    if not blocks:
        return 0.0
    
    # Count unique blocks
    unique_blocks = len(set(blocks))
    max_blocks = 2 ** (block_size ** 2)  # Maximum possible distinct blocks
    
    # Normalized entropy
    if unique_blocks <= 1:
        return 0.0
    
    # Compute entropy of block distribution
    block_counts = {}
    for block in blocks:
        block_counts[block] = block_counts.get(block, 0) + 1
    
    total = len(blocks)
    probabilities = [count / total for count in block_counts.values()]
    entropy = -np.sum([p * np.log2(p) for p in probabilities])
    
    # Normalize by maximum entropy
    max_entropy = np.log2(min(max_blocks, len(blocks)))
    
    return entropy / max_entropy if max_entropy > 0 else 0.0


def temporal_entropy(history: List[np.ndarray], lag: int = 1) -> float:
    """
    Compute temporal entropy (predictability over time).
    
    Measures how predictable the next state is given current state.
    
    Args:
        history: Sequence of states
        lag: Time lag for conditional entropy
        
    Returns:
        Temporal entropy (bits)
    """
    if len(history) < lag + 1:
        return 0.0
    
    # Flatten states and create lag sequences
    transitions = []
    for i in range(len(history) - lag):
        current = tuple(history[i].flatten())
        next_state = tuple(history[i + lag].flatten())
        transitions.append((current, next_state))
    
    if not transitions:
        return 0.0
    
    # Count transitions
    transition_counts = {}
    for trans in transitions:
        transition_counts[trans] = transition_counts.get(trans, 0) + 1
    
    # Compute entropy
    total = len(transitions)
    probabilities = [count / total for count in transition_counts.values()]
    entropy = -np.sum([p * np.log2(p) for p in probabilities if p > 0])
    
    return float(entropy)


def activity_level(state: np.ndarray) -> float:
    """
    Compute activity level (density of 1s or +1 spins).
    
    Args:
        state: Grid state (binary or spin)
        
    Returns:
        Activity level in [0, 1]
    """
    # Handle both binary (0/1) and spin (-1/+1)
    if np.all((state == 0) | (state == 1)):
        return np.mean(state)
    else:
        # Spin case: map -1 to 0, +1 to 1
        return np.mean((state + 1) / 2)

