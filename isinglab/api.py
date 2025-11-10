"""
Main API for Ising Life Lab.

Provides simple, stateless interface for evaluating CA/Ising rules.
Designed for use by AI agents and reproducible experiments.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from .core import CAEngine, IsingEngine
from .metrics.edge_score import composite_edge_metric


def evaluate_rule(
    rule: Union[int, Dict],
    grid_size: Union[int, Tuple[int, ...]] = (100, 100),
    steps: int = 200,
    seed: int = 42,
    ca_type: str = "elementary",
    boundary: str = "periodic",
    return_history: bool = False
) -> Dict:
    """
    Evaluate a CA or Ising rule comprehensively.
    
    This is the main entry point for rule evaluation. It:
    1. Initializes the system deterministically (with seed)
    2. Evolves it for 'steps' time steps
    3. Computes all relevant metrics
    4. Returns a comprehensive metric dictionary
    
    Args:
        rule: Rule number (int) or Ising parameters (dict)
        grid_size: Grid dimensions. Single int for 1D, tuple for 2D
        steps: Number of evolution steps
        seed: Random seed for reproducibility
        ca_type: Type of CA ("elementary", "life", "totalistic")
        boundary: Boundary conditions ("periodic", "fixed")
        return_history: If True, include full history in results
        
    Returns:
        Dictionary with metrics:
        - entropy: Shannon entropy
        - spatial_entropy: Spatial pattern complexity
        - sensitivity: Hamming sensitivity to perturbations
        - memory_score: Memory-like behavior score
        - edge_score: Composite edge-of-chaos score
        - activity: Activity level (density of 1s)
        - attractor_type: Type of attractor ("fixed", "cycle", "chaotic")
        - attractor_period: Period of limit cycle (0 if not cyclic)
        - lambda_estimate: Langton's λ parameter estimate
        - history: Full state history (if return_history=True)
        
    Example:
        >>> from isinglab.api import evaluate_rule
        >>> metrics = evaluate_rule(rule=30, grid_size=100, steps=200, seed=42)
        >>> print(f"Edge score: {metrics['edge_score']:.3f}")
        >>> print(f"Memory: {metrics['memory_score']:.3f}")
    """
    # Normalize grid_size
    if isinstance(grid_size, int):
        grid_size = (grid_size,)
    
    # Initialize engine based on rule type
    if isinstance(rule, dict):
        # Ising model
        engine = IsingEngine(
            grid_size=grid_size if len(grid_size) == 2 else (grid_size[0], grid_size[0]),
            J=rule.get("J", 1.0),
            h=rule.get("h", 0.0),
            temperature=rule.get("T", 1.0),
            dynamics=rule.get("dynamics", "glauber"),
            boundary=boundary,
            seed=seed
        )
    else:
        # CA model
        engine = CAEngine(
            grid_size=grid_size,
            rule=rule,
            ca_type=ca_type,
            boundary=boundary,
            seed=seed
        )
    
    # Run evolution
    history = engine.run(steps)
    
    # Create evolution function for sensitivity analysis
    def evolve_func(state, n_steps):
        if isinstance(rule, dict):
            # Ising model - create temp engine with Ising params
            temp_engine = IsingEngine(
                grid_size=grid_size if len(grid_size) == 2 else (grid_size[0], grid_size[0]),
                J=rule.get("J", 1.0),
                h=rule.get("h", 0.0),
                temperature=rule.get("T", 1.0),
                dynamics=rule.get("dynamics", "glauber"),
                boundary=boundary,
                seed=None
            )
            temp_engine.spins = state.copy()
        else:
            # CA model
            temp_engine = CAEngine(
                grid_size=grid_size,
                rule=rule,
                ca_type=ca_type,
                boundary=boundary,
                seed=None
            )
            temp_engine.grid = state.copy()
        
        temp_engine.history = [state.copy()]
        temp_engine.run(n_steps)
        
        return temp_engine.spins if isinstance(rule, dict) else temp_engine.grid
    
    # Compute comprehensive metrics
    metrics = composite_edge_metric(
        history=history,
        evolution_func=evolve_func,
        initial_state=history[0],
        steps=min(50, steps // 4),
        seed=seed
    )
    
    # Add lambda estimate
    from .metrics.edge_score import lambda_parameter_estimate
    metrics["lambda_estimate"] = lambda_parameter_estimate(history)
    
    # Add metadata
    metrics["rule"] = rule
    metrics["grid_size"] = grid_size
    metrics["steps"] = steps
    metrics["seed"] = seed
    
    # Optionally include history
    if return_history:
        metrics["history"] = history
    
    return metrics


def evaluate_batch(
    rules: List[Union[int, Dict]],
    grid_size: Union[int, Tuple[int, ...]] = (100, 100),
    steps: int = 200,
    seed: int = 42,
    ca_type: str = "elementary",
    boundary: str = "periodic",
    n_seeds: int = 1
) -> List[Dict]:
    """
    Evaluate multiple rules in batch.
    
    For each rule, optionally runs with multiple seeds and averages metrics.
    
    Args:
        rules: List of rule numbers or Ising parameter dicts
        grid_size: Grid dimensions
        steps: Evolution steps per run
        seed: Base random seed
        ca_type: CA type
        boundary: Boundary conditions
        n_seeds: Number of different initial conditions per rule
        
    Returns:
        List of metric dictionaries (one per rule)
    """
    results = []
    
    for rule in rules:
        if n_seeds == 1:
            # Single seed
            metrics = evaluate_rule(
                rule=rule,
                grid_size=grid_size,
                steps=steps,
                seed=seed,
                ca_type=ca_type,
                boundary=boundary
            )
            results.append(metrics)
        else:
            # Multiple seeds: average metrics
            all_metrics = []
            for i in range(n_seeds):
                metrics = evaluate_rule(
                    rule=rule,
                    grid_size=grid_size,
                    steps=steps,
                    seed=seed + i,
                    ca_type=ca_type,
                    boundary=boundary
                )
                all_metrics.append(metrics)
            
            # Average numerical metrics
            avg_metrics = {
                "rule": rule,
                "grid_size": grid_size,
                "steps": steps,
                "seeds": list(range(seed, seed + n_seeds))
            }
            
            numeric_keys = [
                "entropy", "spatial_entropy", "sensitivity", 
                "memory_score", "edge_score", "activity", 
                "lambda_estimate", "attractor_period", "attractor_stability"
            ]
            
            for key in numeric_keys:
                values = [m[key] for m in all_metrics if key in m]
                if values:
                    avg_metrics[key] = np.mean(values)
                    avg_metrics[f"{key}_std"] = np.std(values)
            
            # Most common attractor type
            attractor_types = [m["attractor_type"] for m in all_metrics]
            from collections import Counter
            avg_metrics["attractor_type"] = Counter(attractor_types).most_common(1)[0][0]
            
            results.append(avg_metrics)
    
    return results


def quick_scan(
    rule_range: Tuple[int, int],
    grid_size: Union[int, Tuple[int, ...]] = (50, 50),
    steps: int = 100,
    seed: int = 42,
    ca_type: str = "elementary"
) -> List[Dict]:
    """
    Quick scan of rule space.
    
    Useful for rapid exploration. Uses smaller grids and fewer steps.
    
    Args:
        rule_range: (min_rule, max_rule) inclusive
        grid_size: Grid size (smaller = faster)
        steps: Evolution steps (fewer = faster)
        seed: Random seed
        ca_type: CA type
        
    Returns:
        List of metrics for all rules in range
    """
    rules = list(range(rule_range[0], rule_range[1] + 1))
    return evaluate_batch(rules, grid_size, steps, seed, ca_type)

