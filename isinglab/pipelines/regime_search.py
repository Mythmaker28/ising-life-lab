"""
Regime Search Pipeline

Stateless, deterministic pipeline for searching CA/Ising regimes
based on target profiles (from physical system properties).

NEW (2025): Constrained search using phase oscillators and Atlas bridge.

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
from tqdm import tqdm

from ..api import evaluate_rule, evaluate_batch
from ..mapping_profiles import get_target_profile_for_system, suggest_ca_rules_for_profile

# Nouveaux imports pour phase oscillators
from ..oscillators import KuramotoXYEngine, MultiKernelConfig
from ..analysis import detect_vortices
from ..control import HolonomyPath, StrokeLibrary
from ..data_bridge.atlas_map import AtlasMapper, AtlasProfile, PhenoParams
from ..data_bridge.physics_validator import PhysicsValidator
from ..data_bridge.cost_functions import (
    PhenoState, phenomenology_distance, compute_target_profile
)


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


# ============================================================================
# NOUVELLE SECTION : Recherche contrainte avec Atlas Bridge (2025)
# ============================================================================

def run_constrained_search(
    target_profile: str,
    atlas_profile: str,
    atlas_mapper: Optional[AtlasMapper] = None,
    n_iterations: int = 20,
    grid_size: Tuple[int, int] = (128, 128),
    steps_per_run: int = 500,
    record_interval: int = 10,
    use_strokes: bool = True,
    output_dir: Optional[str] = None,
    seed: int = 42
) -> Dict:
    """
    Recherche de régimes contrainte par la physique quantique.
    
    Cette fonction effectue une recherche dans l'espace des paramètres
    phénoménologiques (K, bruit, annealing) tout en respectant les
    contraintes imposées par un système quantique physique (T1, T2, etc.).
    
    Algorithme :
        1. Charge le profil physique depuis l'Atlas
        2. Génère des paramètres phéno candidats via mapping
        3. Valide la faisabilité physique
        4. Simule les oscillateurs de phase
        5. Mesure la distance à la cible phénoménologique
        6. Retourne les meilleurs paramètres
    
    Args:
        target_profile: Régime phénoménologique cible ('uniform', 'fragmented', 'balanced')
        atlas_profile: ID du système physique dans l'Atlas (ex: 'NV-298K')
        atlas_mapper: Mapper Atlas (si None, en crée un nouveau)
        n_iterations: Nombre de configurations à tester
        grid_size: Taille de la grille (H, W)
        steps_per_run: Nombre de steps de simulation
        record_interval: Intervalle d'enregistrement
        use_strokes: Si True, teste aussi les strokes holonomiques
        output_dir: Répertoire de sauvegarde (optionnel)
        seed: Seed pour reproductibilité
        
    Returns:
        Dict contenant :
            - 'best_params': Meilleurs PhenoParams trouvés
            - 'best_state': État phénoménologique généré
            - 'best_distance': Distance à la cible
            - 'atlas_profile': Profil physique utilisé
            - 'validation': Résultat de validation physique
            - 'all_results': Liste de tous les résultats
    """
    # 1. Initialisation
    if atlas_mapper is None:
        atlas_mapper = AtlasMapper()
    
    validator = PhysicsValidator(strict=False)
    rng = np.random.default_rng(seed)
    
    # 2. Charger le profil physique
    phys_profile = atlas_mapper.get_profile(atlas_profile)
    print(f"📡 Atlas Profile: {phys_profile}")
    
    # 3. Générer le profil phénoménologique cible
    target_state = compute_target_profile(target_profile)
    print(f"🎯 Target: {target_profile} (r={target_state.order_parameter_r:.2f}, density={target_state.defect_density:.3f})")
    
    # 4. Générer des paramètres candidats
    candidates = []
    
    # 4a. Mapping direct depuis l'Atlas
    for regime in ['uniform', 'fragmented', 'balanced']:
        params = atlas_mapper.map_to_pheno(phys_profile, regime=regime)
        candidates.append(('atlas_' + regime, params))
    
    # 4b. Variations autour des paramètres de base
    base_params = atlas_mapper.map_to_pheno(phys_profile, regime=target_profile)
    for i in range(n_iterations - 3):
        # Perturbation aléatoire
        k1_var = base_params.k1_strength * (1 + rng.normal(0, 0.2))
        k2_var = base_params.k2_strength * (1 + rng.normal(0, 0.3))
        noise_var = base_params.noise_amplitude * (1 + rng.normal(0, 0.15))
        annealing_var = base_params.annealing_rate * (1 + rng.normal(0, 0.1))
        
        varied_params = PhenoParams(
            k1_strength=np.clip(k1_var, 0.1, 5.0),
            k2_strength=np.clip(k2_var, 0.0, 3.0),
            k3_strength=base_params.k3_strength,
            dt=base_params.dt,
            noise_amplitude=np.clip(noise_var, 0.001, 0.5),
            annealing_rate=np.clip(annealing_var, 0.0, 1.0),
            source_system=phys_profile.system_id,
            physical_validity=0.0  # À recalculer
        )
        candidates.append((f'variation_{i}', varied_params))
    
    # 5. Évaluer tous les candidats
    results = []
    best_distance = float('inf')
    best_params = None
    best_state = None
    
    print(f"\n🔬 Testing {len(candidates)} parameter configurations...")
    
    for config_name, params in tqdm(candidates, desc="Simulating"):
        # 5a. Valider la faisabilité physique
        validation = validator.validate(params, phys_profile)
        
        if not validation.is_valid:
            # Skip si physiquement impossible
            continue
        
        # 5b. Créer le moteur avec ces paramètres
        kernel_config = MultiKernelConfig(
            k1_strength=params.k1_strength,
            k1_range=1,
            k1_sign=1.0,
            k2_strength=params.k2_strength,
            k2_range=3,
            k2_sign=-1.0 if target_profile == 'fragmented' else 1.0,
            k3_strength=params.k3_strength,
            k3_range=7,
            k3_sign=1.0,
            dt=params.dt,
            noise_amplitude=params.noise_amplitude,
            annealing_rate=params.annealing_rate
        )
        
        engine = KuramotoXYEngine(
            shape=grid_size,
            config=kernel_config,
            seed=seed + hash(config_name) % 1000
        )
        
        # 5c. Simuler
        engine.reset()
        
        phase_history = []
        for step in range(steps_per_run):
            engine.step()
            if step % record_interval == 0:
                phase_history.append(engine.get_phase_field())
        
        # 5d. Analyser l'état final
        final_phase = engine.get_phase_field()
        r_final, _ = engine.get_order_parameter()
        defect_metrics = detect_vortices(final_phase, threshold=0.5)
        
        # Calculer le taux d'annihilation
        if len(phase_history) > 1:
            defects_initial = detect_vortices(phase_history[0], threshold=0.5)
            annihilation_rate = (defects_initial.n_defects - defect_metrics.n_defects) / len(phase_history)
        else:
            annihilation_rate = 0.0
        
        generated_state = PhenoState(
            order_parameter_r=r_final,
            defect_density=defect_metrics.defect_density,
            n_defects=defect_metrics.n_defects,
            annihilation_rate=annihilation_rate,
            mean_phase=float(np.mean(final_phase)),
            std_phase=float(np.std(final_phase))
        )
        
        # 5e. Calculer la distance à la cible
        distance = phenomenology_distance(generated_state, target_state)
        
        # 5f. Enregistrer
        result = {
            'config_name': config_name,
            'params': params,
            'generated_state': generated_state,
            'distance': distance,
            'validation': validation,
            'r_final': r_final,
            'defect_density': defect_metrics.defect_density,
            'n_defects': defect_metrics.n_defects
        }
        results.append(result)
        
        # 5g. Mettre à jour le meilleur
        if distance < best_distance and validation.score > 0.6:
            best_distance = distance
            best_params = params
            best_state = generated_state
    
    # 6. Sauvegarder les résultats
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Résumé
        summary = {
            'target_profile': target_profile,
            'atlas_profile': atlas_profile,
            'physical_system': {
                'system_id': phys_profile.system_id,
                'temperature_k': phys_profile.temperature_k,
                't2_us': phys_profile.t2_us,
            },
            'target_state': {
                'r': target_state.order_parameter_r,
                'defect_density': target_state.defect_density,
            },
            'best_result': {
                'distance': best_distance,
                'r_achieved': best_state.order_parameter_r if best_state else None,
                'defect_density_achieved': best_state.defect_density if best_state else None,
            },
            'n_candidates_tested': len(results),
        }
        
        with open(output_path / 'search_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Résultats détaillés
        results_data = []
        for r in results:
            results_data.append({
                'config': r['config_name'],
                'distance': r['distance'],
                'r': r['r_final'],
                'defect_density': r['defect_density'],
                'n_defects': r['n_defects'],
                'k1': r['params'].k1_strength,
                'k2': r['params'].k2_strength,
                'noise': r['params'].noise_amplitude,
                'annealing': r['params'].annealing_rate,
                'validity_score': r['validation'].score
            })
        
        results_df = pd.DataFrame(results_data)
        results_df = results_df.sort_values('distance')
        results_df.to_csv(output_path / 'all_results.csv', index=False)
    
    # 7. Retour
    return {
        'best_params': best_params,
        'best_state': best_state,
        'best_distance': best_distance,
        'atlas_profile': phys_profile,
        'validation': validator.validate(best_params, phys_profile) if best_params else None,
        'all_results': results,
        'target_state': target_state
    }


def compare_systems_for_target(
    target_profile: str,
    system_ids: List[str],
    atlas_mapper: Optional[AtlasMapper] = None,
    n_iterations: int = 15,
    output_dir: Optional[str] = None
) -> Dict:
    """
    Compare plusieurs systèmes physiques pour atteindre une cible phénoménologique.
    
    Scénario typique :
        "Quel système quantique (NV-298K, SiC-VSi, RP-Cry4) peut le mieux
         reproduire un état de haute synchronie (5-MeO-DMT-like) ?"
    
    Args:
        target_profile: Profil phénoménologique cible
        system_ids: Liste d'IDs de systèmes à comparer
        atlas_mapper: Mapper Atlas
        n_iterations: Itérations par système
        output_dir: Répertoire de sortie
        
    Returns:
        Dict avec comparaisons et classement
    """
    if atlas_mapper is None:
        atlas_mapper = AtlasMapper()
    
    results_per_system = {}
    
    print(f"🔍 Comparing {len(system_ids)} systems for target: {target_profile}\n")
    
    for sys_id in system_ids:
        print(f"\n{'='*60}")
        print(f"System: {sys_id}")
        print(f"{'='*60}")
        
        sys_output_dir = None
        if output_dir:
            sys_output_dir = str(Path(output_dir) / sys_id)
        
        result = run_constrained_search(
            target_profile=target_profile,
            atlas_profile=sys_id,
            atlas_mapper=atlas_mapper,
            n_iterations=n_iterations,
            output_dir=sys_output_dir
        )
        
        results_per_system[sys_id] = result
        
        # Afficher résumé
        if result['best_params']:
            print(f"\n✓ Best distance: {result['best_distance']:.3f}")
            print(f"  r achieved: {result['best_state'].order_parameter_r:.3f}")
            print(f"  Defects: {result['best_state'].n_defects}")
        else:
            print(f"\n✗ No valid configuration found")
    
    # Classement
    ranking = []
    for sys_id, result in results_per_system.items():
        if result['best_params']:
            ranking.append({
                'system_id': sys_id,
                'distance': result['best_distance'],
                'r_achieved': result['best_state'].order_parameter_r,
                'validity': result['validation'].score if result['validation'] else 0.0
            })
    
    ranking.sort(key=lambda x: x['distance'])
    
    print(f"\n{'='*60}")
    print(f"FINAL RANKING for target '{target_profile}':")
    print(f"{'='*60}")
    for i, entry in enumerate(ranking, 1):
        print(f"{i}. {entry['system_id']:20s} | distance={entry['distance']:.3f} | r={entry['r_achieved']:.3f}")
    
    # Sauvegarder
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        with open(output_path / 'comparison_ranking.json', 'w') as f:
            json.dump({'ranking': ranking}, f, indent=2)
    
    return {
        'results_per_system': results_per_system,
        'ranking': ranking
    }
