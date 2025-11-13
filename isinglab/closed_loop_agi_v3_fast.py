"""Closed Loop AGI v3 — Fast Mode + Anti-Trivial Filters

Changements vs v2.2 :
1. Mode fast par défaut (grilles 16×16, simulations réduites)
2. Filtres anti-trivialité (densité finale + richness)
3. Audit lourd seulement pour promus
"""
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import numpy as np

from isinglab.meta_learner.dynamic_memory import DynamicMemoryManager
from isinglab.meta_learner import train_meta_model, CandidateSelector
from isinglab.rules import load_hof_rules, add_or_update_rule, save_hof_rules
from isinglab.memory_explorer import MemoryExplorer, parse_notation
from isinglab.meta_learner.filters import apply_hard_filters


class ClosedLoopAGIv3:
    """AGI v3 avec fast mode + filtres anti-trivialité."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {
            'evaluation_seed': 42,
            'hof_max_size': 25,
            'adaptive_thresholds': True,
            'hof_percentiles': {
                'composite_min': 85,
                'memory_score_min_abs': 0.01,
                'edge_score_min_abs': 0.05,
                'entropy_min_abs': 0.0
            },
            'diversity_threshold': 2,
            # v3: Filtres anti-trivialité
            'density_min': 0.05,
            'density_max': 0.95,
            'richness_min': 0.05
        }
        self.aggregator = DynamicMemoryManager()
        self.meta_memory: List[Dict] = []
        self.meta_model = None
        self.selector = None
        self.explorer = MemoryExplorer(output_dir='results/scans')
        
        Path('logs').mkdir(parents=True, exist_ok=True)
        self.log_file = Path('logs') / f"agi_v3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    def _log(self, message: str):
        print(message)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(message + '\n')
    
    def _is_trivial_rule(self, metrics: Dict) -> tuple[bool, str]:
        """
        Détecte rules triviales (quasi-death, saturation, low richness).
        
        Returns: (is_trivial: bool, reason: str)
        """
        final_density = metrics.get('final_density', 0.5)
        
        # Filtre 1: Densité trop faible
        if final_density < self.config['density_min']:
            return True, f"Quasi-death (density={final_density:.3f})"
        
        # Filtre 2: Densité trop élevée
        if final_density > self.config['density_max']:
            return True, f"Saturation (density={final_density:.3f})"
        
        # Filtre 3: Richness (si disponible)
        richness = metrics.get('pattern_richness', None)
        if richness is not None and richness < self.config['richness_min']:
            return True, f"Low richness ({richness:.3f})"
        
        return False, "Valid"
    
    def evaluate_candidate_fast(self, rule: Dict) -> Dict:
        """
        Évaluation rapide d'un candidat.
        
        Mode fast :
        - grid_size = 16×16
        - steps = 50
        - n_patterns = 3, n_trials = 2, n_samples = 3
        
        + Capture grille finale pour richness
        """
        from isinglab.metrics.functional import (
            compute_memory_capacity,
            compute_robustness_to_noise,
            compute_basin_size,
            compute_functional_score
        )
        
        notation = rule.get('notation')
        born = rule.get('born')
        survive = rule.get('survive')
        if born is None or survive is None:
            born, survive = parse_notation(notation)
        
        try:
            # Métriques de base
            grid_size = (16, 16)
            steps = 50
            seed = self.config['evaluation_seed']
            
            metrics = self.explorer._evaluate_life_rule(notation, born, survive, grid_size, steps, seed)
            metrics['source'] = rule.get('source', 'unknown')
            metrics['timestamp'] = datetime.now().isoformat()
            
            # Métriques fonctionnelles (mode fast)
            rule_func = self.explorer._create_rule_function(born, survive)
            
            capacity_result = compute_memory_capacity(
                rule_func, grid_size=(16, 16), n_patterns=3, steps=20
            )
            robustness_result = compute_robustness_to_noise(
                rule_func, grid_size=(16, 16), noise_level=0.1, n_trials=2, steps=20
            )
            basin_result = compute_basin_size(
                rule_func, grid_size=(16, 16), n_samples=3, steps=15
            )
            
            metrics['capacity_score'] = capacity_result['capacity_score']
            metrics['robustness_score'] = robustness_result['robustness_score']
            metrics['basin_score'] = basin_result['basin_score']
            metrics['basin_diversity'] = basin_result['basin_diversity']
            metrics['functional_score'] = compute_functional_score(
                capacity_result, robustness_result, basin_result
            )
            
            # Capturer grille finale pour richness
            np.random.seed(seed)
            grid = (np.random.rand(*grid_size) < 0.3).astype(int)
            for _ in range(steps):
                grid = rule_func(grid)
            
            metrics['grid_final'] = grid
            metrics['pattern_richness'] = self._compute_pattern_richness(grid)
            
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
    
    def _compute_pattern_richness(self, grid, window_size=5):
        """Fraction motifs distincts dans grille."""
        h, w = grid.shape
        if h < window_size or w < window_size:
            return 0.0
        
        patterns = set()
        for i in range(0, h - window_size + 1, window_size):
            for j in range(0, w - window_size + 1, window_size):
                patch = grid[i:i+window_size, j:j+window_size]
                patterns.add(patch.tobytes())
        
        max_patterns = ((h // window_size) * (w // window_size))
        return len(patterns) / max_patterns if max_patterns > 0 else 0.0
    
    def discover_rules(self, num_iterations: int = 50, batch_size: int = 4,
                      strategy: str = 'mixed', grid_size=(16, 16), steps=50):
        """
        Boucle découverte v3 (fast mode).
        
        Changements :
        - evaluate_candidate_fast() par défaut
        - Filtres anti-trivialité avant promotion
        - Audit lourd seulement pour top promus
        """
        # Charger mémoire existante
        self.aggregator.aggregate_memory()
        self.meta_memory = self.aggregator.memory_rules
        
        # Initialiser selector
        if len(self.meta_memory) >= 10:
            self.meta_model = train_meta_model(self.meta_memory)
            self.selector = CandidateSelector(
                self.meta_model, self.meta_memory, use_bandit=True
            )
        else:
            self.selector = CandidateSelector(
                None, self.meta_memory, use_bandit=False
            )
        
        self._log("=" * 80)
        self._log(f"CLOSED LOOP AGI v3 — FAST MODE")
        self._log("=" * 80)
        self._log(f"Iterations : {num_iterations}")
        self._log(f"Batch size : {batch_size}")
        self._log(f"Strategy   : {strategy}")
        self._log(f"Grid       : {grid_size} (fast mode)")
        self._log("")
        
        for iter_idx in range(num_iterations):
            self._log(f"\n{'='*64}")
            self._log(f"ITERATION {iter_idx+1}/{num_iterations}")
            self._log(f"{'='*64}")
            
            # 1. Sélectionner candidats
            candidates = self.selector.recommend_next_batch(pool_size=200, batch_size=batch_size, strategy=strategy)
            self._log(f"  [SELECT] {len(candidates)} candidates")
            
            # 2. Évaluer (fast mode)
            results = []
            for cand in candidates:
                notation = cand.get('notation')
                
                # FILTRE DUR AVANT ÉVALUATION COMPLÈTE (filters.py)
                passed_hard_filters, filter_reason = apply_hard_filters(notation)
                
                if not passed_hard_filters:
                    self._log(f"  [HARD_FILTER] {notation} — BLOCKED: {filter_reason}")
                    # Skip évaluation complète, marqué comme rejeté
                    result = {
                        'notation': notation,
                        'born': cand.get('born'),
                        'survive': cand.get('survive'),
                        'source': cand.get('source', 'unknown'),
                        'trivial': True,
                        'trivial_reason': f"Hard filter: {filter_reason}",
                        'functional_score': 0.0,
                        'timestamp': datetime.now().isoformat()
                    }
                    results.append(result)
                    continue
                
                # Évaluation complète si filtres passés
                result = self.evaluate_candidate_fast(cand)
                
                # Appliquer filtres légers complémentaires (richness)
                is_trivial, reason = self._is_trivial_rule(result)
                result['trivial'] = is_trivial
                result['trivial_reason'] = reason
                
                if is_trivial:
                    self._log(f"  [SOFT_REJECT] {result['notation']} — {reason}")
                    # Pénalité sévère sur functional_score
                    result['functional_score'] *= 0.1
                else:
                    self._log(f"  [PASS] {result['notation']} — Valid (score={result.get('functional_score', 0):.3f})")
                
                results.append(result)
            
            # 3. Mettre à jour mémoire
            for result in results:
                if 'error' not in result:
                    self.aggregator.add_or_update_rule(result)
                    self.meta_memory.append(result)
            
            # 4. Promouvoir HoF
            self.aggregator.update_hof()
            
            self._log(f"  [MEMORY] {len(self.meta_memory)} rules total")
            self._log(f"  [HoF]    {len(self.aggregator.hof_rules)} rules")
        
        # 5. Sauvegarder
        self.aggregator.save_memory()
        self.aggregator.save_hof()
        
        self._log("\n" + "=" * 80)
        self._log("DISCOVERY COMPLETE")
        self._log("=" * 80)


__all__ = ['ClosedLoopAGIv3']

