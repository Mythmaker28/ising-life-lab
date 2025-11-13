"""
Test Architectures Composées v3

Architecture 1 : Pipeline B34/S34 → B3/S23
  Hypothèse : B34/S34 filtre le bruit, Life traite proprement
  
Architecture 2 : Alternance temporelle Life/HighLife
  Hypothèse : Alternance apporte redondance/exploration

Architecture 3 : Ensemble voting (3 cerveaux)
  Hypothèse : Consensus majoritaire améliore robustesse
  
Protocole :
- Grilles 64×64
- Bruit 0%, 10%, 20%, 30%, 40%
- Patterns : random, gliders, blocks
- Métriques : recall, stability, final_density
"""

import sys
from pathlib import Path
import numpy as np
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from isinglab.core.rule_ops import parse_notation

# === ARCHITECTURES ===

def create_rule_func(notation):
    """Crée fonction CA depuis notation."""
    born, survive = parse_notation(notation)
    born_set, survive_set = set(born), set(survive)
    
    def rule_func(grid):
        h, w = grid.shape
        new_grid = np.zeros_like(grid)
        for i in range(h):
            for j in range(w):
                neighbors = sum(grid[(i+di)%h, (j+dj)%w] 
                              for di in [-1,0,1] for dj in [-1,0,1] 
                              if not (di==0 and dj==0))
                if grid[i,j] == 1:
                    new_grid[i,j] = 1 if neighbors in survive_set else 0
                else:
                    new_grid[i,j] = 1 if neighbors in born_set else 0
        return new_grid
    
    return rule_func


class Architecture:
    """Base class pour architectures composées."""
    
    def __init__(self, name):
        self.name = name
    
    def process(self, grid, steps):
        """Traite grille sur N steps."""
        raise NotImplementedError


class PipelineArchitecture(Architecture):
    """Pipeline : Rule A (N steps) → Rule B (M steps)."""
    
    def __init__(self, rule_a, rule_b, steps_a, steps_b):
        super().__init__(f"Pipeline_{rule_a}_to_{rule_b}")
        self.rule_a_func = create_rule_func(rule_a)
        self.rule_b_func = create_rule_func(rule_b)
        self.steps_a = steps_a
        self.steps_b = steps_b
        self.rule_a = rule_a
        self.rule_b = rule_b
    
    def process(self, grid, steps=None):
        """Phase 1: rule_a, Phase 2: rule_b."""
        # Phase 1
        grid_phase1 = grid.copy()
        for _ in range(self.steps_a):
            grid_phase1 = self.rule_a_func(grid_phase1)
        
        # Phase 2
        grid_phase2 = grid_phase1.copy()
        for _ in range(self.steps_b):
            grid_phase2 = self.rule_b_func(grid_phase2)
        
        return grid_phase2


class AlternatingArchitecture(Architecture):
    """Alternance : Rule A (1 step) → Rule B (1 step) → repeat."""
    
    def __init__(self, rule_a, rule_b, period_a=1, period_b=1):
        super().__init__(f"Alternating_{rule_a}_{rule_b}")
        self.rule_a_func = create_rule_func(rule_a)
        self.rule_b_func = create_rule_func(rule_b)
        self.period_a = period_a
        self.period_b = period_b
        self.rule_a = rule_a
        self.rule_b = rule_b
    
    def process(self, grid, steps):
        """Alterner A et B sur steps."""
        current_grid = grid.copy()
        cycle_length = self.period_a + self.period_b
        
        for step in range(steps):
            position_in_cycle = step % cycle_length
            
            if position_in_cycle < self.period_a:
                current_grid = self.rule_a_func(current_grid)
            else:
                current_grid = self.rule_b_func(current_grid)
        
        return current_grid


class EnsembleVotingArchitecture(Architecture):
    """Ensemble : 3 règles votent (majorité)."""
    
    def __init__(self, rules):
        super().__init__(f"Ensemble_Voting_{len(rules)}")
        self.rules = rules
        self.rule_funcs = [create_rule_func(r) for r in rules]
    
    def process(self, grid, steps):
        """Chaque règle évolue en parallèle, vote majoritaire."""
        grids = [grid.copy() for _ in self.rules]
        
        for _ in range(steps):
            # Évolution parallèle
            grids = [func(g) for func, g in zip(self.rule_funcs, grids)]
            
            # Vote majoritaire
            stacked = np.stack(grids, axis=0)
            voted_grid = (stacked.sum(axis=0) > len(self.rules) / 2).astype(int)
            
            # Synchroniser toutes les grilles au vote
            grids = [voted_grid.copy() for _ in self.rules]
        
        return grids[0]


# === BASELINE (Single Rules) ===

class SingleRuleArchitecture(Architecture):
    """Baseline : une seule règle."""
    
    def __init__(self, rule):
        super().__init__(f"Single_{rule}")
        self.rule_func = create_rule_func(rule)
        self.rule = rule
    
    def process(self, grid, steps):
        current_grid = grid.copy()
        for _ in range(steps):
            current_grid = self.rule_func(current_grid)
        return current_grid


# === PROTOCOLE DE TEST ===

def add_noise(grid, noise_level):
    """Ajoute bruit (flips aléatoires)."""
    noise_mask = np.random.rand(*grid.shape) < noise_level
    noisy_grid = grid.copy()
    noisy_grid[noise_mask] = 1 - noisy_grid[noise_mask]
    return noisy_grid


def compute_recall(grid_original, grid_final):
    """Recall = similarité entre original et final."""
    return np.mean(grid_original == grid_final)


def test_architecture(arch, grid_size=(64,64), noise_levels=[0, 0.1, 0.2, 0.3, 0.4], 
                      n_patterns=5, steps=100, seed=42):
    """
    Teste une architecture sur plusieurs patterns et niveaux de bruit.
    
    Returns: Dict avec métriques
    """
    np.random.seed(seed)
    
    results = {
        'architecture': arch.name,
        'grid_size': grid_size,
        'steps': steps,
        'by_noise': {}
    }
    
    for noise in noise_levels:
        recalls = []
        final_densities = []
        
        for pattern_idx in range(n_patterns):
            # Pattern original
            pattern_seed = seed + pattern_idx
            np.random.seed(pattern_seed)
            grid_original = (np.random.rand(*grid_size) < 0.3).astype(int)
            
            # Ajouter bruit
            grid_noisy = add_noise(grid_original, noise)
            
            # Traiter avec architecture
            grid_final = arch.process(grid_noisy, steps)
            
            # Métriques
            recall = compute_recall(grid_original, grid_final)
            final_density = grid_final.mean()
            
            recalls.append(recall)
            final_densities.append(final_density)
        
        # Agréger
        results['by_noise'][f'noise_{noise:.2f}'] = {
            'noise_level': noise,
            'avg_recall': float(np.mean(recalls)),
            'std_recall': float(np.std(recalls)),
            'avg_final_density': float(np.mean(final_densities)),
            'std_final_density': float(np.std(final_densities))
        }
    
    # Score global
    avg_recall_all = np.mean([r['avg_recall'] for r in results['by_noise'].values()])
    results['global_avg_recall'] = float(avg_recall_all)
    
    return results


# === MAIN ===

if __name__ == "__main__":
    print("=" * 80)
    print("TEST ARCHITECTURES COMPOSÉES v3")
    print("=" * 80)
    print()
    
    # Architectures à tester
    architectures = [
        # Baselines (single rules)
        SingleRuleArchitecture("B3/S23"),
        SingleRuleArchitecture("B36/S23"),
        SingleRuleArchitecture("B34/S34"),
        
        # Arch 1: Pipeline B34/S34 → B3/S23
        PipelineArchitecture("B34/S34", "B3/S23", steps_a=50, steps_b=50),
        
        # Arch 2: Alternance Life/HighLife
        AlternatingArchitecture("B3/S23", "B36/S23", period_a=5, period_b=5),
        
        # Arch 3: Ensemble voting
        EnsembleVotingArchitecture(["B3/S23", "B36/S23", "B34/S34"])
    ]
    
    all_results = []
    
    for arch in architectures:
        print(f"\n### {arch.name}")
        print("-" * 60)
        
        results = test_architecture(
            arch,
            grid_size=(64, 64),
            noise_levels=[0, 0.1, 0.2, 0.3, 0.4],
            n_patterns=5,
            steps=100,
            seed=42
        )
        
        # Afficher résumé
        print(f"  Global avg recall : {results['global_avg_recall']:.3f}")
        
        for noise_key, noise_data in results['by_noise'].items():
            noise = noise_data['noise_level']
            recall = noise_data['avg_recall']
            density = noise_data['avg_final_density']
            print(f"    Noise {noise*100:>3.0f}% : recall {recall:.3f}, density {density:.3f}")
        
        all_results.append(results)
    
    # Sauvegarder
    output_file = Path("results") / "composed_architectures_v3.json"
    with open(output_file, 'w') as f:
        json.dump({
            'meta': {
                'date': datetime.now().isoformat(),
                'test_config': {
                    'grid_size': [64, 64],
                    'steps': 100,
                    'n_patterns': 5,
                    'noise_levels': [0, 0.1, 0.2, 0.3, 0.4]
                }
            },
            'results': all_results
        }, f, indent=2)
    
    print("\n" + "=" * 80)
    print("COMPARAISON")
    print("=" * 80)
    
    # Trouver meilleure architecture
    sorted_results = sorted(all_results, key=lambda x: x['global_avg_recall'], reverse=True)
    
    print("\nClassement par recall global :")
    for i, res in enumerate(sorted_results, 1):
        name = res['architecture']
        recall = res['global_avg_recall']
        print(f"  {i}. {name:<40} : {recall:.3f}")
    
    # Baseline (best single rule)
    baseline_results = [r for r in all_results if 'Single_' in r['architecture']]
    best_baseline = max(baseline_results, key=lambda x: x['global_avg_recall'])
    
    # Architectures composées
    composed_results = [r for r in all_results if 'Single_' not in r['architecture']]
    
    print(f"\nMeilleure baseline : {best_baseline['architecture']} ({best_baseline['global_avg_recall']:.3f})")
    
    if composed_results:
        best_composed = max(composed_results, key=lambda x: x['global_avg_recall'])
        print(f"Meilleure composée : {best_composed['architecture']} ({best_composed['global_avg_recall']:.3f})")
        
        gain = best_composed['global_avg_recall'] - best_baseline['global_avg_recall']
        if gain > 0.01:
            print(f"\nGain réel : +{gain:.3f} ({gain/best_baseline['global_avg_recall']*100:.1f}%)")
        else:
            print(f"\nPas de gain significatif : {gain:+.3f}")
    
    print(f"\nRésultats sauvegardés : {output_file}")
    print("=" * 80)




