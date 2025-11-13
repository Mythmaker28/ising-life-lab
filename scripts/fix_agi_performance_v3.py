"""
Fix AGI Performance v3 — Mode Fast + Filtres Anti-Trivialité

Objectif : Passer de 4h/itération à ~3 min/itération.

Méthode :
1. Mode fast : Réduction simulations (340 → 120/candidat)
2. Filtres anti-trivialité : Rejeter quasi-death rules
3. Audit lourd : Seulement pour top promus
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from isinglab.memory_explorer import MemoryExplorer
import numpy as np

# === NIVEAU 1 : MODE FAST ===

def evaluate_candidate_fast(explorer, rule, seed=42):
    """
    Version fast de evaluate_candidate avec réductions :
    - grid_size : 16×16 (vs 32×32)
    - steps : 50 (vs 120)
    - n_patterns : 3 (vs 5)
    - n_trials : 2 (vs 3)
    - n_samples : 3 (vs 5)
    
    Réduction : ~340 → ~120 simulations/candidat
    """
    from isinglab.memory_explorer import parse_notation
    from isinglab.metrics.functional import (
        compute_memory_capacity,
        compute_robustness_to_noise,
        compute_basin_size,
        compute_functional_score
    )
    from datetime import datetime
    
    notation = rule.get('notation')
    born = rule.get('born')
    survive = rule.get('survive')
    if born is None or survive is None:
        born, survive = parse_notation(notation)
    
    try:
        # Métriques de base (légères)
        grid_size = (16, 16)
        steps = 50
        
        metrics = explorer._evaluate_life_rule(notation, born, survive, grid_size, steps, seed)
        metrics['source'] = rule.get('source', 'unknown')
        metrics['timestamp'] = datetime.now().isoformat()
        
        # Métriques fonctionnelles (mode fast)
        rule_func = explorer._create_rule_function(born, survive)
        
        capacity_result = compute_memory_capacity(
            rule_func, grid_size=(16, 16), n_patterns=3, steps=20  # 3×20 = 60
        )
        robustness_result = compute_robustness_to_noise(
            rule_func, grid_size=(16, 16), noise_level=0.1, n_trials=2, steps=20  # 2×20 = 40
        )
        basin_result = compute_basin_size(
            rule_func, grid_size=(16, 16), n_samples=3, steps=15  # 3×15 = 45
        )
        
        # Stocker
        metrics['capacity_score'] = capacity_result['capacity_score']
        metrics['robustness_score'] = robustness_result['robustness_score']
        metrics['basin_score'] = basin_result['basin_score']
        metrics['basin_diversity'] = basin_result['basin_diversity']
        metrics['functional_score'] = compute_functional_score(
            capacity_result, robustness_result, basin_result
        )
        
        # Calcul densité finale pour filtres
        # (déjà dans metrics via _evaluate_life_rule)
        
        return metrics
    
    except Exception as exc:
        return {
            'notation': notation,
            'born': born,
            'survive': survive,
            'source': rule.get('source', 'unknown'),
            'error': str(exc),
            'timestamp': datetime.now().isoformat()
        }


# === NIVEAU 2 : FILTRES ANTI-TRIVIALITÉ ===

def is_quasi_death_rule(metrics, threshold=0.05):
    """Détecte rules convergent vers vide."""
    final_density = metrics.get('final_density', 0.5)
    return final_density < threshold


def is_saturation_rule(metrics, threshold=0.95):
    """Détecte rules saturant la grille."""
    final_density = metrics.get('final_density', 0.5)
    return final_density > threshold


def compute_pattern_richness(grid, window_size=5):
    """
    Compte motifs distincts dans grille finale.
    
    Retourne : fraction motifs uniques (0.0 = tout identique, 1.0 = tout unique)
    """
    h, w = grid.shape
    if h < window_size or w < window_size:
        return 0.0
    
    patterns = set()
    for i in range(0, h - window_size + 1, window_size):
        for j in range(0, w - window_size + 1, window_size):
            patch = grid[i:i+window_size, j:j+window_size]
            patterns.add(patch.tobytes())
    
    max_patterns = ((h // window_size) * (w // window_size))
    if max_patterns == 0:
        return 0.0
    
    return len(patterns) / max_patterns


def apply_anti_trivial_filters(metrics, grid_final=None):
    """
    Applique filtres anti-trivialité.
    
    Returns:
        (pass_filters: bool, reason: str, penalty: float)
    """
    # Filtre 1 : Densité finale
    if is_quasi_death_rule(metrics):
        return False, "Quasi-death rule (density < 0.05)", 0.1
    
    if is_saturation_rule(metrics):
        return False, "Saturation rule (density > 0.95)", 0.1
    
    # Filtre 2 : Richness (si grille fournie)
    if grid_final is not None:
        richness = compute_pattern_richness(grid_final)
        if richness < 0.05:
            return False, f"Low pattern richness ({richness:.3f})", 0.3
    
    # Passe tous les filtres
    return True, "Valid", 1.0


# === PATCH : Intégration dans MemoryExplorer ===

def patch_memory_explorer():
    """Patch MemoryExplorer avec mode fast."""
    
    # Sauvegarder ancienne méthode
    original_evaluate = MemoryExplorer.evaluate_candidate
    
    def evaluate_candidate_patched(self, rule, grid_size=(32,32), steps=100, seed=42, 
                                   compute_functional=True, fast_mode=False):
        """Version patchée avec fast_mode."""
        if fast_mode:
            return evaluate_candidate_fast(self, rule, seed)
        else:
            return original_evaluate(self, rule, grid_size, steps, seed, compute_functional)
    
    MemoryExplorer.evaluate_candidate = evaluate_candidate_patched
    print("[PATCH] MemoryExplorer.evaluate_candidate patched with fast_mode")


# === TEST RAPIDE ===

if __name__ == "__main__":
    print("=" * 80)
    print("FIX AGI PERFORMANCE v3 — TEST")
    print("=" * 80)
    print()
    
    # Patch
    patch_memory_explorer()
    
    # Test sur 3 règles
    explorer = MemoryExplorer()
    
    test_rules = [
        {'notation': 'B3/S23', 'born': [3], 'survive': [2, 3], 'source': 'test'},
        {'notation': 'B34/S34', 'born': [3,4], 'survive': [3,4], 'source': 'test'},
        {'notation': 'B38/S06', 'born': [3,8], 'survive': [0,6], 'source': 'test'}  # Quasi-death
    ]
    
    import time
    
    for rule in test_rules:
        print(f"\n### {rule['notation']}")
        print("-" * 60)
        
        # Mode normal (baseline)
        start = time.time()
        result_normal = explorer.evaluate_candidate(rule, grid_size=(16,16), steps=50, 
                                                    fast_mode=False, compute_functional=True)
        time_normal = time.time() - start
        
        # Mode fast
        start = time.time()
        result_fast = explorer.evaluate_candidate(rule, grid_size=(16,16), steps=50, 
                                                  fast_mode=True, compute_functional=True)
        time_fast = time.time() - start
        
        print(f"  Normal mode : {time_normal:.2f}s")
        print(f"  Fast mode   : {time_fast:.2f}s")
        print(f"  Speedup     : {time_normal/time_fast:.1f}×")
        
        # Filtres
        pass_filters, reason, penalty = apply_anti_trivial_filters(result_fast)
        print(f"  Filters     : {'PASS' if pass_filters else 'REJECT'} ({reason})")
        if not pass_filters:
            print(f"  Penalty     : {penalty:.1f}× (functional score multiplied)")
    
    print("\n" + "=" * 80)
    print("TEST TERMINÉ")
    print("=" * 80)
    print("\nProchaine étape : Intégrer fast_mode dans closed_loop_agi.py")
    print("  - run_one_iteration(..., fast_mode=True)")
    print("  - Appliquer filtres dans _update_memory_and_hof()")

