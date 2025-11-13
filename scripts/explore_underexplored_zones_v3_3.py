"""Phase B : Exploration Zones Sous-Explorées v3.3

CONSTAT :
- AGI v3 et voisinage cerveaux biaisés vers born moyens (B3, B36)
- Peu de règles testées avec born minimal (B0, B1, B2)
- Peu de règles high-sensitivity (born élevé + survive sélectif)

CAMPAGNES :
1. Minimal Birth : born ∈ {[], [0], [1], [2]}, survive autour 2-3-4
2. High Sensitivity : born ⊃ {5,6,7}, survive petits ensembles

HYPOTHÈSES :
- Minimal birth + survive strict = cerveaux parcimonieux stables
- High sensitivity = comportements riches sans collapse
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
    """Convertit types NumPy."""
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


def evaluate_candidate(notation, born, survive):
    """Évaluation rapide d'une candidate."""
    # Filtres durs
    passed, reason = apply_hard_filters(notation)
    if not passed:
        return None
    
    rule_func = create_rule_function_vectorized(born, survive)
    
    # Métriques clés (grille 32×32)
    capacity_result = compute_memory_capacity(rule_func, grid_size=(32, 32), n_patterns=5, steps=50)
    robustness_result = compute_robustness_to_noise(rule_func, grid_size=(32, 32), noise_level=0.2, n_trials=3, steps=50)
    basin_result = compute_basin_size(rule_func, grid_size=(32, 32), n_samples=5, steps=30)
    life_capacity_result = compute_life_pattern_capacity(rule_func, grid_size=(32, 32))
    
    functional = compute_functional_score(capacity_result, robustness_result, basin_result)
    
    return {
        'notation': notation,
        'born': born,
        'survive': survive,
        'capacity_score': capacity_result['capacity_score'],
        'robustness_score': robustness_result['robustness_score'],
        'basin_score': basin_result['basin_score'],
        'functional_score': functional,
        'life_capacity_score': life_capacity_result['life_capacity_score'],
        'life_patterns': {
            name: {'survived': p['survived'], 'score': p['score']}
            for name, p in life_capacity_result['patterns'].items()
        }
    }


def campaign_minimal_birth():
    """Campagne 1 : Minimal Birth / Selective Survive."""
    print("\n" + "="*80)
    print("CAMPAIGN 1: MINIMAL BIRTH")
    print("="*80)
    
    # Générer candidats
    born_sets = [[], [0], [1], [2]]
    survive_combinations = [
        [2, 3], [2], [3], [2, 3, 4], [3, 4], [2, 4], [1, 2, 3], [2, 3, 5]
    ]
    
    candidates = []
    for born in born_sets:
        for survive in survive_combinations:
            notation = f"B{''.join(map(str, born))}/S{''.join(map(str, survive))}"
            candidates.append((notation, born, survive))
    
    print(f"Generated {len(candidates)} candidates\n")
    
    results = []
    rejected = 0
    
    for i, (notation, born, survive) in enumerate(candidates):
        print(f"  [{i+1}/{len(candidates)}] {notation:15s}...", end=' ')
        
        result = evaluate_candidate(notation, born, survive)
        
        if result is None:
            print("REJECTED")
            rejected += 1
        else:
            func = result['functional_score']
            life = result['life_capacity_score']
            print(f"func={func:.3f}, life={life:.3f}")
            results.append(result)
    
    print(f"\n[SUMMARY]")
    print(f"  Evaluated: {len(candidates)}")
    print(f"  Rejected: {rejected}")
    print(f"  Valid: {len(results)}")
    
    return {'campaign': 'minimal_birth', 'candidates': candidates, 'results': results}


def campaign_high_sensitivity():
    """Campagne 2 : High Sensitivity (born élevé)."""
    print("\n" + "="*80)
    print("CAMPAIGN 2: HIGH SENSITIVITY")
    print("="*80)
    
    # Born avec au moins 1 valeur dans {5,6,7}
    born_sets = [
        [5], [6], [7],
        [3, 5], [3, 6], [3, 7],
        [5, 6], [5, 7], [6, 7],
        [3, 5, 6], [3, 5, 7], [3, 6, 7],
        [5, 6, 7]
    ]
    
    # Survive restreints (2-4 valeurs max)
    survive_combinations = [
        [2], [3], [2, 3], [3, 4], [2, 3, 4], [1, 2], [4, 5]
    ]
    
    candidates = []
    for born in born_sets:
        for survive in survive_combinations:
            notation = f"B{''.join(map(str, born))}/S{''.join(map(str, survive))}"
            candidates.append((notation, born, survive))
    
    print(f"Generated {len(candidates)} candidates\n")
    
    results = []
    rejected = 0
    
    for i, (notation, born, survive) in enumerate(candidates):
        print(f"  [{i+1}/{len(candidates)}] {notation:15s}...", end=' ')
        
        result = evaluate_candidate(notation, born, survive)
        
        if result is None:
            print("REJECTED")
            rejected += 1
        else:
            func = result['functional_score']
            life = result['life_capacity_score']
            print(f"func={func:.3f}, life={life:.3f}")
            results.append(result)
    
    print(f"\n[SUMMARY]")
    print(f"  Evaluated: {len(candidates)}")
    print(f"  Rejected: {rejected}")
    print(f"  Valid: {len(results)}")
    
    return {'campaign': 'high_sensitivity', 'candidates': candidates, 'results': results}


def main():
    """Lance les 2 campagnes."""
    print("="*80)
    print("PHASE B — UNDEREXPLORED ZONES v3.3")
    print("="*80)
    
    start_total = time.time()
    
    # Campaign 1
    campaign1_results = campaign_minimal_birth()
    
    # Campaign 2
    campaign2_results = campaign_high_sensitivity()
    
    elapsed_total = time.time() - start_total
    
    # Analyse globale
    all_results = campaign1_results['results'] + campaign2_results['results']
    
    print(f"\n{'='*80}")
    print("GLOBAL ANALYSIS")
    print(f"{'='*80}")
    print(f"Total evaluated: {len(all_results)}")
    
    # Top par functional
    top_functional = sorted(all_results, key=lambda r: r['functional_score'], reverse=True)[:10]
    
    print(f"\nTOP 10 BY FUNCTIONAL:")
    for i, res in enumerate(top_functional):
        notation = res['notation']
        func = res['functional_score']
        life = res['life_capacity_score']
        rob = res['robustness_score']
        print(f"  {i+1:2d}. {notation:15s}  func={func:.3f}  life={life:.3f}  rob={rob:.3f}")
    
    # Sauvegarder
    output = {
        'meta': {
            'timestamp': datetime.now().isoformat(),
            'version': 'v3.3_phase_b',
            'total_elapsed': elapsed_total
        },
        'campaigns': [campaign1_results, campaign2_results],
        'global_analysis': {
            'total_evaluated': len(all_results),
            'top_10_functional': top_functional[:10]
        }
    }
    
    output_converted = convert_numpy_types(output)
    
    output_file = Path('results/underexplored_zones_v3_3.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_converted, f, indent=2)
    
    print(f"\nResults saved: {output_file}")
    print("="*80)


if __name__ == '__main__':
    main()




