"""
Regime Search Pipeline

Stateless, deterministic pipeline for searching CA/Ising regimes
based on target profiles (from physical system properties).

Design for AI agents:
    - Pure functions (no global state)
    - YAML/JSON config input
    - CSV/JSON output
    - Deterministic (seed control)
    - No external network calls
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

from ..api import evaluate_rule, evaluate_batch
from ..mapping_profiles import get_target_profile_for_system, suggest_ca_rules_for_profile


def run_regime_search(
    target_profile: Dict,
    rule_pool: Optional[List[int]] = None,
    ca_type: str = "elementary",
    grid_size: int = 100,
    steps: int = 200,
    seeds_per_rule: int = 3,
    base_seed: int = 42,
    output_dir: Optional[str] = None
) -> Tuple[pd.DataFrame, List[Dict]]:
    """
    Run a regime search based on a target profile.
    
    Stateless function:
        - Takes explicit parameters
        - Returns results (no side effects except optional file writes)
        - Deterministic given same seed
    
    Args:
        target_profile: Profile dict from get_target_profile_for_system()
        rule_pool: List of rules to evaluate (if None, uses profile suggestions)
        ca_type: CA type ("elementary", "life", "ising")
        grid_size: Grid size for simulations
        steps: Evolution steps per run
        seeds_per_rule: Number of random seeds per rule
        base_seed: Base random seed for reproducibility
        output_dir: If provided, save results to files
        
    Returns:
        (results_df, top_rules):
            - results_df: DataFrame with all evaluated rules and metrics
            - top_rules: List of top rules matching target profile
    """
    # 1. Determine rule pool
    if rule_pool is None:
        rule_pool = suggest_ca_rules_for_profile(target_profile, n_suggestions=50)
    
    # 2. Evaluate all rules
    results = evaluate_batch(
        rules=rule_pool,
        grid_size=grid_size,
        steps=steps,
        seed=base_seed,
        ca_type=ca_type,
        n_seeds=seeds_per_rule
    )
    
    # 3. Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    # 4. Filter by target profile
    target_metrics = target_profile.get("target_metrics", {})
    
    filtered_df = results_df.copy()
    for metric, (min_val, max_val) in target_metrics.items():
        if metric in filtered_df.columns:
            filtered_df = filtered_df[
                (filtered_df[metric] >= min_val) & 
                (filtered_df[metric] <= max_val)
            ]
    
    # 5. Rank by composite score
    # Simple ranking: distance from target midpoints
    filtered_df['match_score'] = 0.0
    
    for metric, (min_val, max_val) in target_metrics.items():
        if metric in filtered_df.columns:
            target_mid = (min_val + max_val) / 2.0
            target_range = max_val - min_val
            
            # Normalized distance from target midpoint
            distance = np.abs(filtered_df[metric] - target_mid) / (target_range + 1e-6)
            filtered_df['match_score'] += (1.0 - distance)
    
    filtered_df = filtered_df.sort_values('match_score', ascending=False)
    
    # 6. Extract top rules
    top_rules = filtered_df.head(10).to_dict('records')
    
    # 7. Optionally save results
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save full results
        results_csv = output_path / "regime_search_results.csv"
        results_df.to_csv(results_csv, index=False)
        
        # Save filtered + ranked results
        filtered_csv = output_path / "regime_search_filtered.csv"
        filtered_df.to_csv(filtered_csv, index=False)
        
        # Save top rules as JSON
        top_json = output_path / "top_rules.json"
        with open(top_json, 'w') as f:
            json.dump({
                "profile": target_profile,
                "top_rules": top_rules,
                "total_evaluated": len(results_df),
                "total_matching": len(filtered_df)
            }, f, indent=2)
    
    return results_df, top_rules


def batch_regime_search(
    systems_profiles: List[Dict],
    rule_pool: Optional[List[int]] = None,
    ca_type: str = "elementary",
    grid_size: int = 100,
    steps: int = 200,
    seeds_per_rule: int = 3,
    base_seed: int = 42,
    output_dir: Optional[str] = None
) -> Dict[str, Tuple[pd.DataFrame, List[Dict]]]:
    """
    Run regime search for multiple systems in batch.
    
    Useful for comparing multiple physical systems against CA/Ising regimes.
    
    Args:
        systems_profiles: List of target profiles (one per system)
        rule_pool: Shared rule pool (if None, each profile suggests its own)
        ca_type: CA type
        grid_size: Grid size
        steps: Evolution steps
        seeds_per_rule: Seeds per rule
        base_seed: Base seed
        output_dir: Output directory (creates subdir per system)
        
    Returns:
        Dictionary mapping system_id → (results_df, top_rules)
    """
    all_results = {}
    
    for i, profile in enumerate(systems_profiles):
        system_id = profile.get("modality", f"system_{i}")
        coherence = profile.get("coherence_class", "unknown")
        profile_key = f"{system_id}_{coherence}"
        
        # Unique output dir per system
        if output_dir:
            system_output_dir = Path(output_dir) / profile_key
        else:
            system_output_dir = None
        
        # Run search
        results_df, top_rules = run_regime_search(
            target_profile=profile,
            rule_pool=rule_pool,
            ca_type=ca_type,
            grid_size=grid_size,
            steps=steps,
            seeds_per_rule=seeds_per_rule,
            base_seed=base_seed + i,  # Different seed per system
            output_dir=system_output_dir
        )
        
        all_results[profile_key] = (results_df, top_rules)
    
    # Optionally save batch summary
    if output_dir:
        batch_summary = {
            "total_systems": len(systems_profiles),
            "systems": {}
        }
        
        for profile_key, (df, top_rules) in all_results.items():
            batch_summary["systems"][profile_key] = {
                "total_rules_evaluated": len(df),
                "top_rule": top_rules[0]["rule"] if top_rules else None,
                "top_edge_score": top_rules[0].get("edge_score", 0.0) if top_rules else 0.0
            }
        
        summary_path = Path(output_dir) / "batch_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(batch_summary, f, indent=2)
    
    return all_results


def filter_rules_by_criteria(
    results_df: pd.DataFrame,
    criteria: Dict[str, Tuple[float, float]]
) -> pd.DataFrame:
    """
    Filter rules by explicit metric criteria.
    
    Utility function for custom filtering.
    
    Args:
        results_df: DataFrame with rule metrics
        criteria: Dict of {metric_name: (min_val, max_val)}
        
    Returns:
        Filtered DataFrame
    """
    filtered = results_df.copy()
    
    for metric, (min_val, max_val) in criteria.items():
        if metric in filtered.columns:
            filtered = filtered[
                (filtered[metric] >= min_val) & 
                (filtered[metric] <= max_val)
            ]
    
    return filtered


def rank_rules_by_targets(
    results_df: pd.DataFrame,
    target_metrics: Dict[str, float],
    weights: Optional[Dict[str, float]] = None
) -> pd.DataFrame:
    """
    Rank rules by distance to target metric values.
    
    Args:
        results_df: DataFrame with rule metrics
        target_metrics: Dict of {metric_name: target_value}
        weights: Optional weights for each metric (default: equal)
        
    Returns:
        DataFrame with added 'rank_score' column, sorted by rank
    """
    if weights is None:
        weights = {metric: 1.0 for metric in target_metrics.keys()}
    
    ranked = results_df.copy()
    ranked['rank_score'] = 0.0
    
    for metric, target_val in target_metrics.items():
        if metric in ranked.columns:
            # Normalized distance
            distance = np.abs(ranked[metric] - target_val)
            max_distance = ranked[metric].std() + 1e-6
            normalized_dist = distance / max_distance
            
            # Add weighted score (closer = better)
            weight = weights.get(metric, 1.0)
            ranked['rank_score'] += weight * (1.0 - np.clip(normalized_dist, 0, 1))
    
    ranked = ranked.sort_values('rank_score', ascending=False)
    
    return ranked

