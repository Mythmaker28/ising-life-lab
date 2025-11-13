"""
Last Brain Hunt v7.0 — Dernière recherche structurée avec kill switch.

Ce script implémente la campagne finale de recherche de règles CA "cerveau".
Si aucune règle ne passe les critères stricts, la branche CA-réservoir est close.
"""

import json
import time
from pathlib import Path
from datetime import datetime
import numpy as np
from typing import List, Dict, Tuple
from itertools import combinations

from isinglab.brain_modules import BRAIN_MODULES
from isinglab.core.ca_vectorized import create_rule_function_vectorized
from isinglab.core.ca3d_vectorized import create_rule_function_3d
from isinglab.metrics.functional import (
    compute_life_pattern_capacity,
    compute_robustness_to_noise,
    compute_memory_capacity
)


def generate_local_mutations(born: List[int], survive: List[int], 
                             max_distance: int = 2) -> List[Tuple[List[int], List[int]]]:
    """
    Génère mutations locales (distance Hamming 1-2) d'une règle CA.
    
    Args:
        born: Liste valeurs naissance
        survive: Liste valeurs survie
        max_distance: Distance Hamming max (1 ou 2)
    
    Returns:
        Liste de (born_mut, survive_mut)
    """
    mutations = []
    born_set = set(born)
    survive_set = set(survive)
    
    # Mutations sur born
    for val in range(9):  # 0-8 voisins
        if val in born_set:
            # Retirer
            born_mut = [b for b in born if b != val]
            mutations.append((born_mut, survive))
        else:
            # Ajouter
            born_mut = sorted(born + [val])
            mutations.append((born_mut, survive))
    
    # Mutations sur survive
    for val in range(9):
        if val in survive_set:
            # Retirer
            survive_mut = [s for s in survive if s != val]
            mutations.append((born, survive_mut))
        else:
            # Ajouter
            survive_mut = sorted(survive + [val])
            mutations.append((born, survive_mut))
    
    # Si max_distance == 2, ajouter mutations doubles
    if max_distance >= 2:
        # Mutations doubles sur born
        for v1, v2 in combinations(range(9), 2):
            if v1 not in born_set and v2 not in born_set:
                born_mut = sorted(born + [v1, v2])
                mutations.append((born_mut, survive))
        
        # Mutations doubles sur survive
        for v1, v2 in combinations(range(9), 2):
            if v1 not in survive_set and v2 not in survive_set:
                survive_mut = sorted(survive + [v1, v2])
                mutations.append((born, survive_mut))
    
    # Dédupliquer
    unique_mutations = []
    seen = set()
    for b, s in mutations:
        key = (tuple(b), tuple(s))
        if key not in seen and len(b) > 0:  # Exclure born vide
            seen.add(key)
            unique_mutations.append((b, s))
    
    return unique_mutations


def hard_filter_rule(rule_func, grid_size: Tuple[int, int] = (32, 32), 
                     n_trials: int = 10, steps: int = 50) -> Dict:
    """
    Filtre dur : rejette règles triviales (death, explosion, sink).
    
    Returns:
        Dict avec {'pass': bool, 'reason': str, 'stats': dict}
    """
    densities = []
    entropies = []
    
    for trial in range(n_trials):
        # Pattern aléatoire (densité 0.3)
        grid = (np.random.rand(*grid_size) < 0.3).astype(int)
        
        # Évoluer
        for _ in range(steps):
            grid = rule_func(grid)
        
        # Mesures
        density = grid.mean()
        densities.append(density)
        
        # Entropie (approximation)
        if density > 0 and density < 1:
            entropy = -density * np.log2(density) - (1 - density) * np.log2(1 - density)
        else:
            entropy = 0.0
        entropies.append(entropy)
    
    avg_density = np.mean(densities)
    avg_entropy = np.mean(entropies)
    
    # Critères de rejet
    if avg_density < 0.05:
        return {'pass': False, 'reason': 'quasi-death', 'stats': {'density': avg_density, 'entropy': avg_entropy}}
    
    if avg_density > 0.98:
        return {'pass': False, 'reason': 'explosion', 'stats': {'density': avg_density, 'entropy': avg_entropy}}
    
    if avg_entropy < 0.1:
        return {'pass': False, 'reason': 'sink', 'stats': {'density': avg_density, 'entropy': avg_entropy}}
    
    return {'pass': True, 'reason': 'ok', 'stats': {'density': avg_density, 'entropy': avg_entropy}}


def evaluate_rule_candidate(born: List[int], survive: List[int], 
                            grid_size: Tuple[int, int] = (32, 32)) -> Dict:
    """
    Évaluation complète d'une règle candidate.
    
    Returns:
        Dict avec toutes les métriques + verdict
    """
    notation = f"B{''.join(map(str, born))}/S{''.join(map(str, survive))}"
    
    # Créer fonction règle
    rule_func = create_rule_function_vectorized(born, survive)
    
    # Filtre dur
    filter_result = hard_filter_rule(rule_func, grid_size)
    if not filter_result['pass']:
        return {
            'notation': notation,
            'born': born,
            'survive': survive,
            'passed_filter': False,
            'filter_reason': filter_result['reason'],
            'filter_stats': filter_result['stats']
        }
    
    # Métriques de capacité
    life_capacity_result = compute_life_pattern_capacity(rule_func, grid_size)
    robustness_10 = compute_robustness_to_noise(rule_func, grid_size, noise_level=0.10, n_trials=5)
    robustness_15 = compute_robustness_to_noise(rule_func, grid_size, noise_level=0.15, n_trials=5)
    robustness_20 = compute_robustness_to_noise(rule_func, grid_size, noise_level=0.20, n_trials=5)
    memory_capacity_result = compute_memory_capacity(rule_func, grid_size, n_patterns=10)
    
    # Scores
    life_capacity_score = life_capacity_result['life_capacity_score']
    robustness_score = robustness_15['robustness_score']  # On prend 15% comme référence
    memory_score = memory_capacity_result['capacity_score']
    
    # Critères de succès (STRICTS)
    criteria = {
        'life_capacity': life_capacity_score >= 0.50,  # Au moins 50%
        'robustness': robustness_score >= 0.40,  # Au moins 40%
        'non_trivial': filter_result['stats']['density'] > 0.05 and filter_result['stats']['density'] < 0.98
    }
    
    passed_all = all(criteria.values())
    
    return {
        'notation': notation,
        'born': born,
        'survive': survive,
        'passed_filter': True,
        'filter_stats': filter_result['stats'],
        'life_capacity_score': life_capacity_score,
        'life_capacity_patterns': life_capacity_result['patterns'],
        'robustness_10': robustness_10['robustness_score'],
        'robustness_15': robustness_15['robustness_score'],
        'robustness_20': robustness_20['robustness_score'],
        'memory_capacity_score': memory_score,
        'memory_capacity_details': memory_capacity_result,
        'criteria': criteria,
        'passed_all_criteria': passed_all
    }


def evaluate_rule_3d_candidate(born: List[int], survive: List[int], 
                               grid_size: Tuple[int, int, int] = (16, 16, 16)) -> Dict:
    """
    Évaluation d'une règle 3D candidate (simplifié).
    
    Note: Pas de life_pattern_capacity en 3D (patterns Life sont 2D).
    """
    notation = f"B{''.join(map(str, born))}/S{''.join(map(str, survive))}"
    
    # Créer fonction règle 3D
    rule_func = create_rule_function_3d(born, survive)
    
    # Filtre dur (adapté 3D)
    densities = []
    n_trials = 5
    steps = 30
    
    for trial in range(n_trials):
        grid = (np.random.rand(*grid_size) < 0.3).astype(int)
        for _ in range(steps):
            grid = rule_func(grid)
        densities.append(grid.mean())
    
    avg_density = np.mean(densities)
    
    # Critères 3D (plus laxistes, exploration)
    if avg_density < 0.05 or avg_density > 0.98:
        return {
            'notation': notation,
            'born': born,
            'survive': survive,
            'dimension': '3D',
            'passed_filter': False,
            'filter_reason': 'trivial',
            'avg_density': avg_density
        }
    
    return {
        'notation': notation,
        'born': born,
        'survive': survive,
        'dimension': '3D',
        'passed_filter': True,
        'avg_density': avg_density,
        'note': 'Règle 3D explorée, mais pas de critères stricts (patterns Life 2D incompatibles)'
    }


def main():
    """
    Lance la campagne finale v7.0.
    """
    print("=" * 80)
    print("LAST BRAIN HUNT v7.0 — DERNIÈRE CHASSE SÉRIEUSE")
    print("=" * 80)
    print()
    print("Objectif : Trouver des regles CA 'cerveau' qui passent criteres STRICTS")
    print("Kill Switch : Si aucune regle ne passe -> Cloture branche CA-reservoir")
    print()
    
    start_time = time.time()
    np.random.seed(42)
    
    # Configuration
    grid_size_2d = (32, 32)
    grid_size_3d = (16, 16, 16)
    
    # Etape 1 : Generer candidats 2D (mutations locales)
    print("[ETAPE 1] Generation candidats 2D (mutations locales)")
    print("-" * 80)
    
    candidates_2d = []
    seen_2d = set()
    
    for brain_name, brain_config in BRAIN_MODULES.items():
        born_seed = brain_config['born']
        survive_seed = brain_config['survive']
        
        print(f"  Seed: {brain_name:12s} ({brain_config['notation']})")
        
        # Générer mutations distance 1-2
        mutations = generate_local_mutations(born_seed, survive_seed, max_distance=2)
        
        for born_mut, survive_mut in mutations:
            key = (tuple(born_mut), tuple(survive_mut))
            if key not in seen_2d:
                seen_2d.add(key)
                candidates_2d.append({'born': born_mut, 'survive': survive_mut})
        
        print(f"    -> {len(mutations)} mutations generees")
    
    # Limiter a 30 candidats max (budget)
    if len(candidates_2d) > 30:
        print(f"\n  WARNING: Trop de candidats ({len(candidates_2d)}), echantillonnage aleatoire a 30")
        np.random.shuffle(candidates_2d)
        candidates_2d = candidates_2d[:30]
    
    print(f"\n  Total candidats 2D : {len(candidates_2d)}")
    
    # Etape 2 : Generer candidats 3D
    print("\n[ETAPE 2] Generation candidats 3D (regles inspirees physiquement)")
    print("-" * 80)
    
    candidates_3d = [
        {'born': [4], 'survive': [3, 4], 'name': 'life3d'},
        {'born': [4], 'survive': [4, 5], 'name': '445'},
        {'born': [5, 6, 7], 'survive': [5, 6, 7], 'name': '567'}
    ]
    
    print(f"  Total candidats 3D : {len(candidates_3d)}")
    
    # Etape 3 : Evaluer candidats 2D
    print("\n[ETAPE 3] Evaluation candidats 2D")
    print("-" * 80)
    
    results_2d = []
    passed_count = 0
    
    for i, candidate in enumerate(candidates_2d, 1):
        born = candidate['born']
        survive = candidate['survive']
        notation = f"B{''.join(map(str, born))}/S{''.join(map(str, survive))}"
        
        print(f"  [{i:2d}/{len(candidates_2d)}] {notation:15s}...", end=' ', flush=True)
        
        try:
            result = evaluate_rule_candidate(born, survive, grid_size_2d)
            results_2d.append(result)
            
            if result.get('passed_all_criteria', False):
                passed_count += 1
                print(f"[OK] PASSED (life_cap={result['life_capacity_score']:.2f}, rob={result['robustness_15']:.2f})")
            elif result.get('passed_filter', False):
                print(f"[WARN] FILTERED (life_cap={result['life_capacity_score']:.2f}, rob={result['robustness_15']:.2f})")
            else:
                print(f"[FAIL] REJECTED ({result['filter_reason']})")
        
        except Exception as e:
            print(f"[ERROR] ({str(e)[:50]})")
            results_2d.append({
                'notation': notation,
                'born': born,
                'survive': survive,
                'error': str(e)
            })
    
    print(f"\n  Candidats passant TOUS les criteres : {passed_count}/{len(candidates_2d)}")
    
    # Etape 4 : Evaluer candidats 3D
    print("\n[ETAPE 4] Evaluation candidats 3D")
    print("-" * 80)
    
    results_3d = []
    
    for i, candidate in enumerate(candidates_3d, 1):
        born = candidate['born']
        survive = candidate['survive']
        name = candidate.get('name', 'unknown')
        notation = f"B{''.join(map(str, born))}/S{''.join(map(str, survive))}"
        
        print(f"  [{i}/{len(candidates_3d)}] {name:12s} ({notation})...", end=' ', flush=True)
        
        try:
            result = evaluate_rule_3d_candidate(born, survive, grid_size_3d)
            results_3d.append(result)
            
            if result.get('passed_filter', False):
                print(f"[OK] NON-TRIVIAL (density={result['avg_density']:.2f})")
            else:
                print(f"[FAIL] REJECTED ({result['filter_reason']})")
        
        except Exception as e:
            print(f"[ERROR] ({str(e)[:50]})")
            results_3d.append({
                'notation': notation,
                'born': born,
                'survive': survive,
                'dimension': '3D',
                'error': str(e)
            })
    
    # Etape 5 : Sauvegarder resultats
    print("\n[ETAPE 5] Sauvegarde resultats")
    print("-" * 80)
    
    elapsed_time = time.time() - start_time
    
    output = {
        'timestamp': datetime.now().isoformat(),
        'version': 'v7.0',
        'config': {
            'grid_size_2d': grid_size_2d,
            'grid_size_3d': grid_size_3d,
            'n_candidates_2d': len(candidates_2d),
            'n_candidates_3d': len(candidates_3d),
            'seed': 42
        },
        'results_2d': results_2d,
        'results_3d': results_3d,
        'summary': {
            'total_candidates_2d': len(candidates_2d),
            'total_candidates_3d': len(candidates_3d),
            'passed_all_criteria_2d': passed_count,
            'elapsed_time_seconds': elapsed_time
        }
    }
    
    # Convertir numpy types
    def convert_numpy(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_numpy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy(item) for item in obj]
        else:
            return obj
    
    output = convert_numpy(output)
    
    # Sauvegarder
    output_file = Path('results/last_brain_hunt_v7_results.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"  Resultats sauvegardes : {output_file}")
    
    # Verdict final
    print("\n" + "=" * 80)
    print("VERDICT FINAL")
    print("=" * 80)
    
    if passed_count > 0:
        print(f"\n[SUCCESS] DECOUVERTE SIGNIFICATIVE : {passed_count} regle(s) passent TOUS les criteres")
        print("\nRegles candidates :")
        for result in results_2d:
            if result.get('passed_all_criteria', False):
                print(f"  - {result['notation']} : life_cap={result['life_capacity_score']:.2f}, rob={result['robustness_15']:.2f}")
        print("\n[WARNING] Ces regles necessitent validation supplementaire sur tache concrete (pattern completion, etc.)")
    else:
        print(f"\n[FAIL] AUCUNE REGLE NE PASSE LES CRITERES STRICTS")
        print(f"\nResume :")
        print(f"  - {len(candidates_2d)} candidats 2D testes")
        print(f"  - {len(candidates_3d)} candidats 3D testes")
        print(f"  - 0 regle passant tous les criteres")
        print(f"\n[KILL SWITCH] ACTIVE")
        print(f"\n-> Recommandation : CLOTURER la branche CA-reservoir pour IA pratique")
        print(f"-> Creer MISSION_v7_CA_BRANCH_CLOSED.md")
    
    print(f"\nTemps total : {elapsed_time:.1f}s")
    print("=" * 80)


if __name__ == '__main__':
    main()

