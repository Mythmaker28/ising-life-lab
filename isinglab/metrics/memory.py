"""
Memory and attractor detection for CA/Ising systems.

Quantifies memory-like behavior through:
- Attractor identification
- Cycle detection
- Return-time statistics
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


def detect_cycle(history: List[np.ndarray], max_period: int = 100) -> Optional[Tuple[int, int]]:
    """
    Detect periodic cycles in state history.
    
    Args:
        history: Sequence of states
        max_period: Maximum cycle period to check
        
    Returns:
        (transient_length, period) if cycle found, None otherwise
    """
    n = len(history)
    
    if n < 2:
        return None
    
    # Convert states to hashable tuples for comparison
    state_hashes = [tuple(state.flatten()) for state in history]
    
    # Check for cycles starting from the end
    for period in range(1, min(max_period, n // 2) + 1):
        # Check if last 'period' states repeat
        is_cycle = True
        for offset in range(period):
            if n - 1 - offset < period:
                is_cycle = False
                break
            
            idx1 = n - 1 - offset
            idx2 = n - 1 - offset - period
            
            if state_hashes[idx1] != state_hashes[idx2]:
                is_cycle = False
                break
        
        if is_cycle:
            # Found cycle, now find when it started (transient)
            transient = n - 2 * period
            
            # Verify cycle is stable
            for i in range(transient, n - period):
                if state_hashes[i] != state_hashes[i + period]:
                    break
            else:
                return (transient, period)
    
    return None


def attractor_analysis(history: List[np.ndarray], max_period: int = 100) -> Dict:
    """
    Comprehensive attractor analysis.
    
    Identifies:
    - Fixed points (period 1)
    - Limit cycles (period > 1)
    - Chaotic attractors (no clear period)
    
    Args:
        history: Sequence of states
        max_period: Maximum cycle period to check
        
    Returns:
        Dictionary with attractor properties:
        - type: "fixed", "cycle", "chaotic", "transient"
        - period: Cycle period (or 0 if no cycle)
        - transient: Length of transient behavior
        - stability: Measure of attractor stability
    """
    result = {
        "type": "unknown",
        "period": 0,
        "transient": len(history),
        "stability": 0.0,
        "n_unique_states": 0
    }
    
    if len(history) < 2:
        return result
    
    # Count unique states
    state_hashes = [tuple(state.flatten()) for state in history]
    unique_states = len(set(state_hashes))
    result["n_unique_states"] = unique_states
    
    # Detect cycle
    cycle_info = detect_cycle(history, max_period)
    
    if cycle_info is not None:
        transient, period = cycle_info
        result["transient"] = transient
        result["period"] = period
        
        if period == 1:
            result["type"] = "fixed"
        else:
            result["type"] = "cycle"
        
        # Stability: how much of trajectory is in attractor
        result["stability"] = 1.0 - (transient / len(history))
    else:
        # No cycle detected
        if unique_states == 1:
            result["type"] = "fixed"
            result["period"] = 1
            result["stability"] = 1.0
        elif unique_states < len(history) * 0.5:
            # Many repeated states but no clear cycle
            result["type"] = "quasi-periodic"
            result["stability"] = 0.5
        else:
            # High diversity, likely chaotic or transient
            result["type"] = "chaotic"
            result["stability"] = 0.0
    
    return result


def memory_score(history: List[np.ndarray], max_period: int = 100) -> float:
    """
    Compute memory score: quantifies memory-like behavior.
    
    Memory score is high when:
    - System has stable attractors (fixed points or cycles)
    - Low period attractors (easier to "remember")
    - Quick convergence to attractor (low transient)
    
    Formula:
        memory_score = stability * (1 - period_penalty) * convergence_factor
    
    Where:
        - stability: fraction in attractor vs transient
        - period_penalty: normalized by max_period (long cycles score lower)
        - convergence_factor: how quickly system reaches attractor
    
    Returns:
        Memory score in [0, 1], where 1 = perfect memory (fixed point)
    """
    if len(history) < 2:
        return 0.0
    
    analysis = attractor_analysis(history, max_period)
    
    # Base score from stability
    stability = analysis["stability"]
    
    # Penalize long periods (harder to "remember")
    period = analysis["period"]
    if period > 0:
        period_penalty = min(period / max_period, 1.0)
    else:
        period_penalty = 1.0  # No attractor = max penalty
    
    # Reward quick convergence
    transient = analysis["transient"]
    convergence_factor = 1.0 - min(transient / len(history), 1.0)
    
    # Composite score
    memory = stability * (1.0 - period_penalty * 0.5) * (0.5 + 0.5 * convergence_factor)
    
    return float(np.clip(memory, 0.0, 1.0))


def return_time_statistics(history: List[np.ndarray]) -> Dict:
    """
    Compute return time statistics (Poincaré recurrence).
    
    Measures how long it takes for system to return to a previously visited state.
    
    Args:
        history: Sequence of states
        
    Returns:
        Dictionary with:
        - mean_return_time: Average recurrence time
        - std_return_time: Standard deviation
        - recurrence_rate: Fraction of states that recur
    """
    if len(history) < 2:
        return {
            "mean_return_time": 0.0,
            "std_return_time": 0.0,
            "recurrence_rate": 0.0
        }
    
    # Hash states
    state_hashes = [tuple(state.flatten()) for state in history]
    
    # Track first occurrence of each state
    first_occurrence = {}
    return_times = []
    
    for t, state_hash in enumerate(state_hashes):
        if state_hash in first_occurrence:
            # Recurrence detected
            first_t = first_occurrence[state_hash]
            return_time = t - first_t
            return_times.append(return_time)
        else:
            first_occurrence[state_hash] = t
    
    if return_times:
        mean_rt = np.mean(return_times)
        std_rt = np.std(return_times)
        recurrence_rate = len(return_times) / len(history)
    else:
        mean_rt = float(len(history))  # Never recurs
        std_rt = 0.0
        recurrence_rate = 0.0
    
    return {
        "mean_return_time": float(mean_rt),
        "std_return_time": float(std_rt),
        "recurrence_rate": float(recurrence_rate)
    }

