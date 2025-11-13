"""Deep Brain Hunt v3.3 — Exploration Voisinage Cerveaux

HYPOTHÈSE :
Les 4 cerveaux validés (B3/S23, B36/S23, B34/S34, B3/S234) sont peut-être
des optimaux locaux, mais leur voisinage immédiat n'a PAS été exploré systématiquement.

OBJECTIF :
Explorer toutes les mutations ±1 autour de ces cerveaux pour :
1. Confirmer qu'ils sont effectivement optimaux locaux
2. Identifier d'éventuels cerveaux cachés proches
3. Cartographier le gradient de qualité dans l'espace des règles

MÉTHODE :
- Mutations contrôlées : ±1 chiffre sur born/survive
- Variantes structurées (ex: B3/S2X avec X ∈ {0-8})
- Évaluation complète : multi-grilles, multi-bruits, life_capacity, filtres durs
- Vectorisation activée

CRITÈRES DE REJET (DURS) :
- Quasi-death (density < 0.05)
- Saturation (density > 0.95)
- Life capacity < 0.1 (aucun pattern Life ne survit)

CRITÈRES DE PROMOTION :
- Life capacity ≥ 0.4 (au moins 2/5 patterns OK)
- Robustness ≥ 0.15 (mieux que trivial)
- Functional ≥ 0.1 (capacité mesurable)
"""

import json
import time
from pathlib import Path
from datetime import datetime
from itertools import combinations
import numpy as np

from isinglab.core.ca_vectorized import create_rule_function_vectorized
from isinglab.meta_learner.filters import apply_hard_filters
from isinglab.metrics.functional import (
    compute_memory_capacity,
    compute_robustness_to_noise,
    compute_basin_size,
    compute_functional_score,
    compute_life_pattern_capacity
)


def convert_numpy_types(obj):
    """Convertit types NumPy en types Python natifs."""
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


def generate_neighbors(born, survive, strategy='mutations'):
    """
    Génère voisins d'une règle.
    
    Stratégies :
    - 'mutations' : ±1 chiffre sur born/survive
    - 'families' : variantes systématiques (ex: B3/S2X)
    """
    neighbors = set()
    
    if strategy == 'mutations':
        # Born mutations : ajouter/retirer 1 chiffre
        for val in range(9):
            if val not in born and val not in [0, 8]:  # éviter extremes
                new_born = sorted(born + [val])
                neighbors.add((tuple(new_born), tuple(survive)))
            
            if val in born and len(born) > 1:
                new_born = sorted([x for x in born if x != val])
                neighbors.add((tuple(new_born), tuple(survive)))
        
        # Survive mutations
        for val in range(9):
            if val not in survive and val not in [0, 8]:
                new_survive = sorted(survive + [val])
                neighbors.add((tuple(born), tuple(new_survive)))
            
            if val in survive and len(survive) > 1:
                new_survive = sorted([x for x in survive if x != val])
                neighbors.add((tuple(born), tuple(new_survive)))
    
    elif strategy == 'families':
        # Variantes B3/S2X (X variable)
        for val in range(9):
            if val not in survive:
                new_survive = sorted(survive + [val])
                neighbors.add((tuple(born), tuple(new_survive)))
        
        # Variantes B3X/S23 (X variable)
        for val in range(9):
            if val not in born:
                new_born = sorted(born + [val])
                neighbors.add((tuple(new_born), tuple(survive)))
    
    return list(neighbors)


def evaluate_rule_deep(notation, born, survive, grids=[(32,32), (64,64)], noise_levels=[0.0, 0.1, 0.2, 0.3]):
    """
    Évaluation profonde d'une règle (vectorisée).
    
    Returns:
        Dict avec métriques complètes ou None si rejet dur
    """
    # Filtres durs AVANT évaluation complète
    passed_filters, filter_reason = apply_hard_filters(notation)
    if not passed_filters:
        return None  # Rejet dur
    
    rule_func = create_rule_function_vectorized(born, survive)
    
    metrics = {
        'notation': notation,
        'born': born,
        'survive': survive,
        'timestamp': datetime.now().isoformat(),
        'grid_results': [],
        'noise_results': [],
        'life_capacity': None,
        'summary': {}
    }
    
    # Test 1 : Multi-grilles (sans bruit)
    for grid_size in grids:
        capacity_result = compute_memory_capacity(
            rule_func, grid_size=grid_size, n_patterns=3, steps=50
        )
        robustness_result = compute_robustness_to_noise(
            rule_func, grid_size=grid_size, noise_level=0.1, n_trials=2, steps=50
        )
        basin_result = compute_basin_size(
            rule_func, grid_size=grid_size, n_samples=3, steps=30
        )
        
        functional = compute_functional_score(capacity_result, robustness_result, basin_result)
        
        metrics['grid_results'].append({
            'grid_size': grid_size,
            'capacity_score': capacity_result['capacity_score'],
            'robustness_score': robustness_result['robustness_score'],
            'basin_score': basin_result['basin_score'],
            'functional_score': functional
        })
    
    # Test 2 : Multi-bruits (grille 32×32)
    for noise_level in noise_levels:
        robustness_result = compute_robustness_to_noise(
            rule_func, grid_size=(32, 32), noise_level=noise_level, n_trials=3, steps=50
        )
        
        metrics['noise_results'].append({
            'noise_level': noise_level,
            'robustness_score': robustness_result['robustness_score']
        })
    
    # Test 3 : Life pattern capacity
    life_capacity_result = compute_life_pattern_capacity(rule_func, grid_size=(32, 32))
    metrics['life_capacity'] = life_capacity_result
    
    # Summary
    avg_functional = np.mean([r['functional_score'] for r in metrics['grid_results']])
    avg_robustness = np.mean([r['robustness_score'] for r in metrics['noise_results']])
    life_score = life_capacity_result['life_capacity_score']
    
    metrics['summary'] = {
        'avg_functional': avg_functional,
        'avg_robustness': avg_robustness,
        'life_capacity_score': life_score,
        'is_candidate': (life_score >= 0.4 and avg_robustness >= 0.15) or avg_functional >= 0.1
    }
    
    return metrics


def explore_neighborhood(seed_notation, seed_born, seed_survive, strategy='mutations'):
    """
    Explore le voisinage d'un cerveau seed.
    """
    print(f"\n{'='*80}")
    print(f"EXPLORING NEIGHBORHOOD: {seed_notation}")
    print(f"{'='*80}")
    
    neighbors = generate_neighbors(seed_born, seed_survive, strategy=strategy)
    print(f"Generated {len(neighbors)} neighbors (strategy={strategy})")
    
    results = []
    candidates = []
    rejected_hard = 0
    rejected_soft = 0
    
    for i, (born_tuple, survive_tuple) in enumerate(neighbors):
        born = list(born_tuple)
        survive = list(survive_tuple)
        notation = f"B{''.join(map(str, born))}/S{''.join(map(str, survive))}"
        
        # Skip seed lui-même
        if notation == seed_notation:
            continue
        
        print(f"  [{i+1}/{len(neighbors)}] {notation}...", end=' ')
        
        result = evaluate_rule_deep(notation, born, survive)
        
        if result is None:
            print("REJECTED (hard filter)")
            rejected_hard += 1
            continue
        
        results.append(result)
        
        is_candidate = result['summary']['is_candidate']
        life_score = result['summary']['life_capacity_score']
        functional = result['summary']['avg_functional']
        
        if is_candidate:
            print(f"CANDIDATE (life={life_score:.2f}, func={functional:.3f})")
            candidates.append(result)
        else:
            print(f"WEAK (life={life_score:.2f}, func={functional:.3f})")
            rejected_soft += 1
    
    print(f"\n[SUMMARY]")
    print(f"  Total neighbors   : {len(neighbors)}")
    print(f"  Hard rejected     : {rejected_hard}")
    print(f"  Soft rejected     : {rejected_soft}")
    print(f"  Valid candidates  : {len(candidates)}")
    
    return {
        'seed': {
            'notation': seed_notation,
            'born': seed_born,
            'survive': seed_survive
        },
        'strategy': strategy,
        'total_neighbors': len(neighbors),
        'rejected_hard': rejected_hard,
        'rejected_soft': rejected_soft,
        'candidates': candidates,
        'all_results': results
    }


def main():
    """
    Explore le voisinage des 4 cerveaux validés.
    """
    print("="*80)
    print("DEEP BRAIN HUNT v3.3 — NEIGHBORHOOD EXPLORATION")
    print("="*80)
    
    # Seeds = 4 cerveaux validés
    seeds = [
        ('B3/S23', [3], [2, 3]),
        ('B36/S23', [3, 6], [2, 3]),
        ('B34/S34', [3, 4], [3, 4]),
        ('B3/S234', [3], [2, 3, 4])
    ]
    
    all_explorations = []
    
    start_total = time.time()
    
    # Explore chaque voisinage
    for seed_notation, seed_born, seed_survive in seeds:
        start = time.time()
        
        # Strategy 1 : Mutations ±1
        exploration_mut = explore_neighborhood(seed_notation, seed_born, seed_survive, strategy='mutations')
        exploration_mut['elapsed_time'] = time.time() - start
        all_explorations.append(exploration_mut)
        
        # Strategy 2 : Families (si pertinent)
        if seed_notation in ['B3/S23', 'B36/S23']:  # Seulement pour Life-like stricts
            start = time.time()
            exploration_fam = explore_neighborhood(seed_notation, seed_born, seed_survive, strategy='families')
            exploration_fam['elapsed_time'] = time.time() - start
            all_explorations.append(exploration_fam)
    
    elapsed_total = time.time() - start_total
    
    # Sauvegarder résultats
    output = {
        'meta': {
            'timestamp': datetime.now().isoformat(),
            'version': 'v3.3',
            'total_elapsed_time': elapsed_total,
            'total_explorations': len(all_explorations)
        },
        'explorations': all_explorations
    }
    
    output_file = Path('results/brain_neighborhoods_v3_3.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Convertir types NumPy
    output_converted = convert_numpy_types(output)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_converted, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"NEIGHBORHOOD EXPLORATION COMPLETE")
    print(f"{'='*80}")
    print(f"Total time: {elapsed_total:.1f}s")
    print(f"Results saved: {output_file}")
    
    # Analyse globale
    all_candidates = []
    for exp in all_explorations:
        all_candidates.extend(exp['candidates'])
    
    print(f"\n[GLOBAL ANALYSIS]")
    print(f"  Total candidates across all neighborhoods: {len(all_candidates)}")
    
    if all_candidates:
        print(f"\n  TOP 10 CANDIDATES (by life_capacity_score):")
        candidates_sorted = sorted(
            all_candidates,
            key=lambda c: c['summary']['life_capacity_score'],
            reverse=True
        )
        
        for i, cand in enumerate(candidates_sorted[:10]):
            notation = cand['notation']
            life_score = cand['summary']['life_capacity_score']
            func = cand['summary']['avg_functional']
            rob = cand['summary']['avg_robustness']
            print(f"    {i+1:2d}. {notation:12s}  life={life_score:.3f}  func={func:.3f}  rob={rob:.3f}")
    else:
        print("  No strong candidates found. Seeds remain optimal locals.")
    
    print("="*80)


if __name__ == '__main__':
    main()

