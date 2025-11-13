"""
Stress-Testing Extrême pour Modules Mémoire CA.

Tests multi-grille (16 à 128) + multi-bruit (0.0 à 0.4) sur règles candidates.
Objectif : Valider robustesse et capacité réelles sous conditions variées.
"""

import numpy as np
from typing import Dict, List, Tuple, Callable
import json
from pathlib import Path


def create_test_patterns(grid_size: Tuple[int, int]) -> List[np.ndarray]:
    """Crée un set de patterns de test (pas seulement aléatoires)."""
    h, w = grid_size
    patterns = []
    
    # 1. Random (densité 0.3)
    patterns.append((np.random.rand(h, w) < 0.3).astype(int))
    
    # 2. Blocs compacts (4x4 blocs)
    blocks = np.zeros((h, w), dtype=int)
    for i in range(0, min(h, 12), 4):
        for j in range(0, min(w, 12), 4):
            blocks[i:i+2, j:j+2] = 1
    patterns.append(blocks)
    
    # 3. Lignes (alternées)
    lines = np.zeros((h, w), dtype=int)
    lines[::3, :] = 1
    patterns.append(lines)
    
    # 4. Damier
    checker = np.zeros((h, w), dtype=int)
    checker[::2, ::2] = 1
    checker[1::2, 1::2] = 1
    patterns.append(checker)
    
    # 5. Blob central
    blob = np.zeros((h, w), dtype=int)
    center_h, center_w = h // 2, w // 2
    blob[center_h-2:center_h+2, center_w-2:center_w+2] = 1
    patterns.append(blob)
    
    return patterns


def apply_noise(grid: np.ndarray, noise_prob: float) -> np.ndarray:
    """Applique du bruit (flips aléatoires) à une grille."""
    if noise_prob <= 0:
        return grid.copy()
    
    noisy = grid.copy()
    h, w = grid.shape
    n_flips = int(h * w * noise_prob)
    
    for _ in range(n_flips):
        i, j = np.random.randint(0, h), np.random.randint(0, w)
        noisy[i, j] = 1 - noisy[i, j]
    
    return noisy


def run_stress_test(rule_function: Callable, 
                   grid_sizes: List[Tuple[int, int]] = None,
                   noise_levels: List[float] = None,
                   steps: int = 50,
                   seed: int = 42) -> Dict:
    """
    Stress-test complet : multi-grille + multi-bruit.
    
    Args:
        rule_function: Fonction CA (grid -> new_grid)
        grid_sizes: Liste de tailles [(h,w), ...]
        noise_levels: Liste de niveaux de bruit [0.0, 0.1, ...]
        steps: Steps d'évolution
        seed: Random seed
    
    Returns:
        Dict structuré avec résultats par grille et par bruit
    """
    if grid_sizes is None:
        grid_sizes = [(16, 16), (32, 32), (64, 64), (128, 128)]
    
    if noise_levels is None:
        noise_levels = [0.0, 0.01, 0.05, 0.1, 0.2, 0.3, 0.4]
    
    np.random.seed(seed)
    
    results = {
        'config': {
            'grid_sizes': grid_sizes,
            'noise_levels': noise_levels,
            'steps': steps,
            'seed': seed
        },
        'by_grid_size': {},
        'by_noise_level': {},
        'summary': {}
    }
    
    # Tests par taille de grille
    for grid_size in grid_sizes:
        size_key = f"{grid_size[0]}x{grid_size[1]}"
        patterns = create_test_patterns(grid_size)
        
        # Tester avec bruit = 0 d'abord
        stable_count = 0
        avg_final_density = []
        
        for pattern in patterns:
            state = pattern.copy()
            for _ in range(steps):
                state = rule_function(state)
            
            # Vérifier stabilité (3 steps identiques)
            is_stable = True
            for _ in range(3):
                next_state = rule_function(state)
                if not np.array_equal(next_state, state):
                    is_stable = False
                    break
                state = next_state
            
            if is_stable:
                stable_count += 1
            
            avg_final_density.append(state.mean())
        
        results['by_grid_size'][size_key] = {
            'stable_patterns': stable_count,
            'total_patterns': len(patterns),
            'stability_rate': stable_count / len(patterns),
            'avg_final_density': float(np.mean(avg_final_density))
        }
    
    # Tests par niveau de bruit (sur grille 32x32)
    base_grid_size = (32, 32)
    patterns_base = create_test_patterns(base_grid_size)
    
    for noise_level in noise_levels:
        noise_key = f"noise_{noise_level:.2f}"
        recalls = []
        
        for pattern in patterns_base:
            # Ajouter bruit initial
            noisy = apply_noise(pattern, noise_level)
            
            # Évoluer
            state = noisy.copy()
            for _ in range(steps):
                state = rule_function(state)
            
            # Mesurer "recall" (similarité avec pattern original après évolution)
            # Note : recall parfait difficile, on mesure juste non-explosion
            final_density = state.mean()
            initial_density = pattern.mean()
            
            # Score simple : densité finale reste proche de l'initiale
            if initial_density > 0:
                recall = 1.0 - abs(final_density - initial_density) / initial_density
                recalls.append(max(0, recall))
            else:
                recalls.append(0)
        
        results['by_noise_level'][noise_key] = {
            'noise_level': noise_level,
            'avg_recall': float(np.mean(recalls)),
            'std_recall': float(np.std(recalls))
        }
    
    # Summary agrégé
    size_stabilities = [v['stability_rate'] for v in results['by_grid_size'].values()]
    noise_recalls = [v['avg_recall'] for v in results['by_noise_level'].values()]
    
    results['summary'] = {
        'avg_stability_across_sizes': float(np.mean(size_stabilities)),
        'avg_recall_across_noise': float(np.mean(noise_recalls)),
        'robustness_score': float(np.mean(noise_recalls))  # Score agrégé
    }
    
    return results


def stress_test_key_rules(rules: List[Dict], 
                          grid_sizes: List[Tuple[int, int]] = None,
                          noise_levels: List[float] = None,
                          output_file: str = 'results/functional_stress_summary.json'):
    """
    Stress-test un ensemble de règles clés et sauvegarde résultats.
    
    Args:
        rules: Liste de dicts avec notation, born, survive
        grid_sizes: Tailles de grille à tester
        noise_levels: Niveaux de bruit
        output_file: Fichier de sortie JSON
    """
    from isinglab.memory_explorer import parse_notation
    
    if grid_sizes is None:
        grid_sizes = [(16, 16), (32, 32), (64, 64)]  # 128 optionnel (lent)
    
    if noise_levels is None:
        noise_levels = [0.0, 0.01, 0.05, 0.1, 0.2, 0.3]
    
    results = {}
    
    for rule in rules:
        notation = rule.get('notation')
        born = rule.get('born')
        survive = rule.get('survive')
        
        if not born or not survive:
            try:
                born, survive = parse_notation(notation)
            except:
                continue
        
        print(f"Stress-testing {notation}...")
        
        # Créer rule_function
        born_set, survive_set = set(born), set(survive)
        
        def rule_func(grid):
            h, w = grid.shape
            new_grid = np.zeros_like(grid)
            for i in range(h):
                for j in range(w):
                    neighbors = 0
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if di == 0 and dj == 0:
                                continue
                            ni, nj = (i + di) % h, (j + dj) % w
                            neighbors += grid[ni, nj]
                    
                    if grid[i, j] == 1:
                        new_grid[i, j] = 1 if neighbors in survive_set else 0
                    else:
                        new_grid[i, j] = 1 if neighbors in born_set else 0
            return new_grid
        
        # Run stress-test
        stress_result = run_stress_test(
            rule_func,
            grid_sizes=grid_sizes,
            noise_levels=noise_levels,
            steps=50,
            seed=42
        )
        
        results[notation] = stress_result
    
    # Sauvegarder
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[OK] Stress-test results saved: {output_file}")
    
    return results


__all__ = [
    'run_stress_test',
    'stress_test_key_rules',
    'create_test_patterns',
    'apply_noise'
]

