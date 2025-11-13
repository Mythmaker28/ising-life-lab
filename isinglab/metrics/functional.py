"""
Métriques fonctionnelles task-based pour évaluer l'utilité réelle des règles CA.

Au lieu de mesurer des propriétés "esthétiques", on teste des capacités concrètes :
- Capacity : combien de patterns distincts peuvent être stabilisés ?
- Robustness : résistance au bruit
- Basin : taille des bassins d'attraction (équilibre nécessaire)
"""

import numpy as np
from typing import Dict, List, Tuple


def compute_memory_capacity(rule_function, grid_size: Tuple[int, int] = (32, 32), 
                            n_patterns: int = 10, steps: int = 50) -> Dict:
    """
    Test de capacité mémoire : combien de patterns distincts peuvent être stockés/rappelés ?
    
    Stratégie :
    - Générer n_patterns aléatoires
    - Pour chaque pattern : initialiser, faire évoluer, mesurer stabilité
    - Capacity score = fraction de patterns qui se stabilisent en états distincts
    """
    height, width = grid_size
    stable_patterns = 0
    distinct_finals = []
    
    for i in range(n_patterns):
        # Pattern aléatoire (densité 0.3)
        pattern = np.random.rand(height, width) < 0.3
        state = pattern.astype(int)
        
        # Évolution
        for step in range(steps):
            state = rule_function(state)
        
        # Vérifier stabilité (derniers 5 steps identiques)
        is_stable = True
        final_state = state.copy()
        for _ in range(5):
            next_state = rule_function(state)
            if not np.array_equal(next_state, state):
                is_stable = False
                break
            state = next_state
        
        if is_stable:
            # Vérifier que c'est distinct des autres
            is_distinct = True
            final_hash = hash(final_state.tobytes())
            if final_hash in distinct_finals:
                is_distinct = False
            else:
                distinct_finals.append(final_hash)
            
            if is_distinct:
                stable_patterns += 1
    
    capacity_score = stable_patterns / n_patterns if n_patterns > 0 else 0
    
    return {
        'capacity_score': capacity_score,
        'stable_patterns': stable_patterns,
        'total_patterns': n_patterns,
        'distinct_finals': len(distinct_finals)
    }


def compute_robustness_to_noise(rule_function, grid_size: Tuple[int, int] = (32, 32),
                                 noise_level: float = 0.1, n_trials: int = 5, 
                                 steps: int = 50) -> Dict:
    """
    Test de robustesse au bruit : le pattern se stabilise-t-il malgré du bruit initial ?
    
    Stratégie :
    - Pattern de référence stable
    - Ajouter noise_level% de bruit
    - Mesurer si le système revient vers un état stable
    """
    height, width = grid_size
    robustness_scores = []
    
    for trial in range(n_trials):
        # Pattern de base (damier ou autre structure)
        base_pattern = np.zeros((height, width), dtype=int)
        base_pattern[::2, ::2] = 1
        base_pattern[1::2, 1::2] = 1
        
        # Ajouter du bruit
        noisy = base_pattern.copy()
        n_flips = int(height * width * noise_level)
        for _ in range(n_flips):
            i, j = np.random.randint(0, height), np.random.randint(0, width)
            noisy[i, j] = 1 - noisy[i, j]
        
        # Évoluer
        state = noisy.copy()
        for step in range(steps):
            state = rule_function(state)
        
        # Mesurer similarité avec le pattern de base ou un état stable
        # Ici on mesure juste la stabilité atteinte
        stability = 0
        final_state = state.copy()
        for _ in range(5):
            next_state = rule_function(state)
            if np.array_equal(next_state, state):
                stability += 1
            state = next_state
        
        robustness = stability / 5  # 1.0 si parfaitement stable
        robustness_scores.append(robustness)
    
    avg_robustness = np.mean(robustness_scores)
    
    return {
        'robustness_score': avg_robustness,
        'noise_level': noise_level,
        'n_trials': n_trials
    }


def compute_basin_size(rule_function, grid_size: Tuple[int, int] = (32, 32),
                        n_samples: int = 10, steps: int = 30) -> Dict:
    """
    Test de taille des bassins d'attraction.
    
    Un bon équilibre :
    - Bassins trop petits → système fragile, peu de convergence
    - Bassins trop grands → comportement écrasant, pas de diversité
    
    Mesure : fraction de patterns aléatoires qui convergent vers le même attracteur.
    """
    height, width = grid_size
    attractors = []
    
    for sample in range(n_samples):
        # Pattern aléatoire
        pattern = np.random.rand(height, width) < 0.3
        state = pattern.astype(int)
        
        # Évoluer jusqu'à stabilité ou max steps
        for step in range(steps):
            next_state = rule_function(state)
            if np.array_equal(next_state, state):
                break
            state = next_state
        
        # Hash de l'attracteur final
        attractor_hash = hash(state.tobytes())
        attractors.append(attractor_hash)
    
    # Diversité des attracteurs
    unique_attractors = len(set(attractors))
    basin_diversity = unique_attractors / n_samples if n_samples > 0 else 0
    
    # Score : optimal autour de 0.3-0.7 (ni trop écrasant, ni trop fragmenté)
    if basin_diversity < 0.2:
        basin_score = basin_diversity * 2  # Pénaliser trop écrasant
    elif basin_diversity > 0.8:
        basin_score = (1.0 - basin_diversity) * 5  # Pénaliser trop fragmenté
    else:
        basin_score = basin_diversity  # Zone optimale
    
    return {
        'basin_score': basin_score,
        'basin_diversity': basin_diversity,
        'unique_attractors': unique_attractors,
        'n_samples': n_samples
    }


def compute_functional_score(capacity_result: Dict, robustness_result: Dict, 
                             basin_result: Dict) -> float:
    """
    Agrège les scores fonctionnels en un score composite.
    
    Pondération :
    - Capacity : 40% (le plus important)
    - Robustness : 35%
    - Basin : 25%
    """
    capacity = capacity_result.get('capacity_score', 0)
    robustness = robustness_result.get('robustness_score', 0)
    basin = basin_result.get('basin_score', 0)
    
    functional = (capacity * 0.4) + (robustness * 0.35) + (basin * 0.25)
    return functional


def infer_module_profile(capacity: float, robustness: float, basin_diversity: float,
                         entropy: float = 0.5) -> Tuple[str, str]:
    """
    Infère le profil/rôle d'une règle basé sur ses métriques fonctionnelles.
    
    Retourne (profile, suggested_use).
    """
    # Profil basé sur les métriques dominantes
    if capacity > 0.6 and robustness > 0.6:
        profile = "stable_memory"
        suggested_use = "Stockage d'états discrets robuste, idéal pour mémoire à long terme"
    
    elif robustness > 0.7 and capacity > 0.3:
        profile = "robust_memory"
        suggested_use = "Mémoire résistante au bruit, bon pour contextes bruités"
    
    elif capacity > 0.5 and basin_diversity > 0.5:
        profile = "diverse_memory"
        suggested_use = "Capacité de stockage avec bassins variés, bon pour patterns multiples"
    
    elif entropy > 0.7 and capacity < 0.3:
        profile = "chaotic_probe"
        suggested_use = "Dynamiques complexes, exploration ou génération de hashing"
    
    elif robustness < 0.3 and entropy > 0.5:
        profile = "sensitive_detector"
        suggested_use = "Sensible aux perturbations, capteur ou amplificateur de signaux"
    
    elif basin_diversity < 0.2 and robustness > 0.5:
        profile = "attractor_dominant"
        suggested_use = "Convergence forte vers attracteurs, bon pour classification"
    
    else:
        profile = "generic"
        suggested_use = "Usage général, profil mixte"
    
    return profile, suggested_use


def compute_life_pattern_capacity(rule_function, grid_size: Tuple[int, int] = (32, 32)) -> Dict:
    """
    Teste la capacité d'une règle à préserver/gérer des patterns Life canoniques.
    
    Patterns testés :
    - Block (still life)
    - Blinker (period 2)
    - Glider (moving spaceship)
    - Toad (period 2)
    - Beacon (period 2)
    
    Returns:
        Dict avec scores par pattern et score global
    """
    height, width = grid_size
    
    # Définir patterns canoniques Life (centrés)
    patterns = {}
    
    # Block (2×2 still life)
    block = np.zeros((height, width), dtype=int)
    cx, cy = height // 2, width // 2
    block[cx:cx+2, cy:cy+2] = 1
    patterns['block'] = {'grid': block, 'period': 1, 'type': 'still_life'}
    
    # Blinker (period 2 oscillator)
    blinker = np.zeros((height, width), dtype=int)
    blinker[cx, cy-1:cy+2] = 1  # Horizontal bar
    patterns['blinker'] = {'grid': blinker, 'period': 2, 'type': 'oscillator'}
    
    # Glider (moving spaceship)
    glider = np.zeros((height, width), dtype=int)
    glider[cx, cy+1] = 1
    glider[cx+1, cy+2] = 1
    glider[cx+2, cy:cy+3] = 1
    patterns['glider'] = {'grid': glider, 'period': 4, 'type': 'spaceship'}
    
    # Toad (period 2 oscillator)
    toad = np.zeros((height, width), dtype=int)
    toad[cx, cy:cy+3] = 1
    toad[cx+1, cy-1:cy+2] = 1
    patterns['toad'] = {'grid': toad, 'period': 2, 'type': 'oscillator'}
    
    # Beacon (period 2 oscillator)
    beacon = np.zeros((height, width), dtype=int)
    beacon[cx:cx+2, cy:cy+2] = 1
    beacon[cx+2:cx+4, cy+2:cy+4] = 1
    patterns['beacon'] = {'grid': beacon, 'period': 2, 'type': 'oscillator'}
    
    results = {}
    total_score = 0
    
    for name, pattern_info in patterns.items():
        grid = pattern_info['grid'].copy()
        period = pattern_info['period']
        
        # Évoluer sur 2-3 périodes complètes
        states = [grid.copy()]
        current = grid.copy()
        
        max_steps = period * 3 + 5  # Laisser temps de stabilisation
        for step in range(max_steps):
            current = rule_function(current)
            states.append(current.copy())
        
        # Vérifier si le pattern a la période attendue
        # (on compare l'état après n*period steps)
        found_period = False
        pattern_score = 0.0
        
        # Test 1 : Pattern persiste (pas mort)
        survived = current.sum() > 0
        if survived:
            pattern_score += 0.3
        
        # Test 2 : Périodicité correcte (seulement si le pattern survit)
        if survived and len(states) >= period + 5:
            # Comparer états séparés de 'period' steps
            state_at_start = states[5]  # Après warm-up
            state_after_period = states[5 + period] if 5 + period < len(states) else states[-1]
            
            # Vérifier périodicité ET que l'état n'est pas vide
            if np.array_equal(state_at_start, state_after_period) and state_at_start.sum() > 0:
                found_period = True
                pattern_score += 0.5
        
        # Test 3 : Structure cohérente (densité raisonnable)
        final_density = current.mean()
        if 0.01 < final_density < 0.5:
            pattern_score += 0.2
        
        results[name] = {
            'score': pattern_score,
            'survived': current.sum() > 0,
            'found_period': found_period,
            'final_density': final_density
        }
        total_score += pattern_score
    
    # Score global : moyenne sur tous les patterns
    global_score = total_score / len(patterns) if patterns else 0.0
    
    return {
        'life_capacity_score': global_score,
        'patterns': results,
        'n_patterns_tested': len(patterns)
    }


__all__ = [
    'compute_memory_capacity',
    'compute_robustness_to_noise',
    'compute_basin_size',
    'compute_functional_score',
    'infer_module_profile',
    'compute_life_pattern_capacity'
]

