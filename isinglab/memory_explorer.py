import json
import csv
import random
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

import pandas as pd
import numpy as np

from .api import evaluate_rule
from .rules import add_or_update_rule
from .metrics.functional import (
    compute_memory_capacity,
    compute_robustness_to_noise,
    compute_basin_size,
    compute_functional_score
)


def parse_notation(notation: str) -> Tuple[List[int], List[int]]:
    """Parse Life-like notation B../S.. into birth and survive lists."""
    if '/' not in notation:
        raise ValueError(f"Invalid Life-like notation: {notation}")
    born_part, survive_part = notation.split('/')
    born = [int(ch) for ch in born_part.replace('B', '') if ch.isdigit()]
    survive = [int(ch) for ch in survive_part.replace('S', '') if ch.isdigit()]
    return born, survive


def life_rule_to_int(born: List[int], survive: List[int]) -> int:
    """Convert birth/survive lists into integer encoding (bits 0-8 birth, 9-17 survive)."""
    rule_int = 0
    for b in born:
        rule_int |= (1 << b)
    for s in survive:
        rule_int |= (1 << (9 + s))
    return rule_int


class MemoryExplorer:
    """Helper class to explore CA rules and record metrics."""

    def __init__(self, output_dir: str = "results/scans"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _log(self, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def generate_random_candidates(
        self,
        count: int = 100,
        born_range: Tuple[int, int] = (0, 8),
        survive_range: Tuple[int, int] = (0, 8),
        seed: Optional[int] = None
    ) -> List[Dict]:
        if seed is not None:
            random.seed(seed)
        candidates = []
        seen = set()
        while len(candidates) < count:
            born_count = random.randint(1, 4)
            survive_count = random.randint(1, 4)
            born = sorted(random.sample(range(born_range[0], born_range[1] + 1), born_count))
            survive = sorted(random.sample(range(survive_range[0], survive_range[1] + 1), survive_count))
            notation = f"B{''.join(map(str, born))}/S{''.join(map(str, survive))}"
            if notation not in seen:
                candidates.append({'notation': notation, 'born': born, 'survive': survive, 'source': 'random_generation'})
                seen.add(notation)
        return candidates

    def generate_neighbors(self, base_rule: str, radius: int = 1) -> List[Dict]:
        born, survive = parse_notation(base_rule)
        neighbors: List[Dict] = []
        seen = {base_rule}

        def add_candidate(new_born, new_survive):
            notation = f"B{''.join(map(str, new_born))}/S{''.join(map(str, new_survive))}"
            if notation not in seen:
                neighbors.append({'notation': notation, 'born': new_born, 'survive': new_survive, 'source': f'neighbor_{base_rule}'})
                seen.add(notation)

        for b in range(9):
            if b not in born and len(neighbors) < radius * 20:
                add_candidate(sorted(born + [b]), survive)
            elif b in born and len(born) > 1 and len(neighbors) < radius * 20:
                add_candidate([x for x in born if x != b], survive)

        for s in range(9):
            if s not in survive and len(neighbors) < radius * 40:
                add_candidate(born, sorted(survive + [s]))
            elif s in survive and len(survive) > 0 and len(neighbors) < radius * 40:
                add_candidate(born, [x for x in survive if x != s])

        self._log(f"Generated {len(neighbors)} neighbors of {base_rule}")
        return neighbors

    def _evaluate_life_rule(self, notation: str, born: List[int], survive: List[int], grid_size: Tuple[int, int], steps: int, seed: int) -> Dict:
        rule_int = life_rule_to_int(born, survive)
        metrics = evaluate_rule(
            rule=rule_int,
            grid_size=grid_size,
            steps=steps,
            seed=seed,
            ca_type='life'
        )
        metrics['notation'] = notation
        metrics['born'] = born
        metrics['survive'] = survive
        return metrics

    def _create_rule_function(self, born: List[int], survive: List[int], vectorized=True):
        """Crée une fonction CA à partir de born/survive pour les tests fonctionnels."""
        born_set = set(born)
        survive_set = set(survive)
        
        if vectorized:
            # Version vectorisée (gain 29×)
            from isinglab.core.ca_vectorized import step_ca_vectorized
            
            def rule_func(grid: np.ndarray) -> np.ndarray:
                return step_ca_vectorized(grid, born_set, survive_set)
            
            return rule_func
        else:
            # Version Python loops (legacy)
            def rule_func(grid: np.ndarray) -> np.ndarray:
                """Applique la règle Life-like au grid."""
                height, width = grid.shape
                new_grid = np.zeros_like(grid)
                
                for i in range(height):
                    for j in range(width):
                        # Compter voisins (Moore neighborhood avec wrapping)
                        neighbors = 0
                        for di in [-1, 0, 1]:
                            for dj in [-1, 0, 1]:
                                if di == 0 and dj == 0:
                                    continue
                                ni = (i + di) % height
                                nj = (j + dj) % width
                                neighbors += grid[ni, nj]
                        
                        # Appliquer règle
                        if grid[i, j] == 1:
                            new_grid[i, j] = 1 if neighbors in survive_set else 0
                        else:
                            new_grid[i, j] = 1 if neighbors in born_set else 0
                
                return new_grid
            
            return rule_func

    def evaluate_candidate(
        self,
        rule: Dict,
        grid_size: Tuple[int, int] = (32, 32),
        steps: int = 100,
        seed: int = 42,
        compute_functional: bool = True
    ) -> Dict:
        notation = rule.get('notation')
        born = rule.get('born')
        survive = rule.get('survive')
        if born is None or survive is None:
            born, survive = parse_notation(notation)
        try:
            # Métriques de base
            metrics = self._evaluate_life_rule(notation, born, survive, grid_size, steps, seed)
            metrics['source'] = rule.get('source', 'unknown')
            metrics['timestamp'] = datetime.now().isoformat()
            
            # v2.1: Métriques fonctionnelles
            if compute_functional:
                rule_func = self._create_rule_function(born, survive)
                
                # Tests fonctionnels (plus légers que l'évaluation complète)
                capacity_result = compute_memory_capacity(rule_func, grid_size=(16, 16), n_patterns=5, steps=30)
                robustness_result = compute_robustness_to_noise(rule_func, grid_size=(16, 16), noise_level=0.1, n_trials=3, steps=30)
                basin_result = compute_basin_size(rule_func, grid_size=(16, 16), n_samples=5, steps=20)
                
                # Stocker résultats
                metrics['capacity_score'] = capacity_result['capacity_score']
                metrics['robustness_score'] = robustness_result['robustness_score']
                metrics['basin_score'] = basin_result['basin_score']
                metrics['basin_diversity'] = basin_result['basin_diversity']
                
                # Score fonctionnel agrégé
                metrics['functional_score'] = compute_functional_score(
                    capacity_result, robustness_result, basin_result
                )
            
            return metrics
        except Exception as exc:
            self._log(f"Error evaluating {notation}: {exc}")
            return {
                'notation': notation,
                'born': born,
                'survive': survive,
                'source': rule.get('source', 'unknown'),
                'error': str(exc),
                'timestamp': datetime.now().isoformat()
            }

    def grid_sweep(self, rule: Dict, grid_sizes: List[Tuple[int, int]] = None,
                   steps: int = 100, seed: int = 42) -> Dict:
        """
        v2.2: Évalue une règle sur plusieurs tailles de grille pour vérifier stabilité multi-échelle.
        
        Returns:
            {
                'notation': str,
                'sweeps': [{'grid_size': (h,w), 'metrics': {...}, 'profile': str}, ...],
                'profile_stability': float,  # Proportion d'accord entre tailles
                'consensus_profile': str
            }
        """
        if grid_sizes is None:
            grid_sizes = [(16, 16), (32, 32), (64, 64)]
        
        notation = rule.get('notation')
        self._log(f"Grid sweep: {notation} on {len(grid_sizes)} sizes")
        
        sweeps = []
        profiles = []
        
        for grid_size in grid_sizes:
            metrics = self.evaluate_candidate(rule, grid_size, steps, seed, compute_functional=True)
            
            # Inférer profil
            from .metrics.functional import infer_module_profile
            capacity = metrics.get('capacity_score', 0)
            robustness = metrics.get('robustness_score', 0)
            basin_div = metrics.get('basin_diversity', 0.5)
            entropy = metrics.get('entropy', 0.5)
            
            profile, _ = infer_module_profile(capacity, robustness, basin_div, entropy)
            profiles.append(profile)
            
            sweeps.append({
                'grid_size': grid_size,
                'metrics': {
                    'capacity_score': capacity,
                    'robustness_score': robustness,
                    'basin_diversity': basin_div,
                    'functional_score': metrics.get('functional_score', 0),
                    'entropy': entropy
                },
                'profile': profile
            })
        
        # Calculer stabilité du profil
        from collections import Counter
        profile_counts = Counter(profiles)
        most_common_profile, count = profile_counts.most_common(1)[0]
        profile_stability = count / len(profiles)
        
        result = {
            'notation': notation,
            'born': rule.get('born'),
            'survive': rule.get('survive'),
            'sweeps': sweeps,
            'profile_stability': profile_stability,
            'consensus_profile': most_common_profile,
            'profiles_by_size': profiles
        }
        
        return result

    def explore_batch(
        self,
        candidates: List[Dict],
        grid_size: Tuple[int, int] = (32, 32),
        steps: int = 100,
        seed: int = 42
    ) -> List[Dict]:
        self._log(f"Starting batch exploration: {len(candidates)} candidates")
        results = []
        for idx, candidate in enumerate(candidates, 1):
            self._log(f"[{idx}/{len(candidates)}] {candidate['notation']}")
            result = self.evaluate_candidate(candidate, grid_size, steps, seed)
            results.append(result)
        self._log(f"Batch exploration complete: {len(results)} results")
        return results

    def save_results(self, results: List[Dict], filename: str):
        if not results:
            self._log("No results to save")
            return
        output_path = self.output_dir / filename
        keys = sorted({k for r in results for k in r.keys()})
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
        self._log(f"Results saved to {output_path}")

    def save_results_json(self, results: List[Dict], filename: str):
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({'meta': {'timestamp': datetime.now().isoformat(), 'count': len(results)}, 'results': results}, f, indent=2)
        self._log(f"Results saved to {output_path}")

    def update_hall_of_fame(self, results: List[Dict], criteria: Optional[Dict] = None) -> List[Dict]:
        if criteria is None:
            criteria = {
                'memory_score_min': 0.70,
                'edge_score_min': 0.20,
                'entropy_min': 0.30
            }
        added = []
        for result in results:
            if 'error' in result:
                continue
            memory_score = result.get('memory_score', 0)
            edge_score = result.get('edge_score', 0)
            entropy = result.get('entropy', 0)
            if (memory_score >= criteria['memory_score_min'] and edge_score >= criteria['edge_score_min'] and entropy >= criteria['entropy_min']):
                rule_data = {
                    'notation': result['notation'],
                    'born': result.get('born', []),
                    'survive': result.get('survive', []),
                    'tier': 'candidate',
                    'avg_recall': memory_score * 100,
                    'edge_score': edge_score,
                    'entropy': entropy,
                    'discovered_by': 'memory_explorer',
                    'discovered_date': datetime.now().strftime('%Y-%m-%d'),
                    'tags': ['explorer', 'automated']
                }
                if add_or_update_rule(rule_data):
                    added.append(rule_data)
                    self._log(f"Added {result['notation']} to Hall of Fame")
        self._log(f"Hall of Fame updated: {len(added)} rules added")
        return added


def quick_explore(count: int = 50, seed: Optional[int] = None, output_dir: str = "results/scans") -> List[Dict]:
    explorer = MemoryExplorer(output_dir=output_dir)
    candidates = explorer.generate_random_candidates(count=count, seed=seed)
    results = explorer.explore_batch(candidates)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    explorer.save_results(results, f"quick_explore_{timestamp}.csv")
    explorer.save_results_json(results, f"quick_explore_{timestamp}.json")
    explorer.update_hall_of_fame(results)
    return results


__all__ = [
    'MemoryExplorer',
    'quick_explore',
    'parse_notation',
    'life_rule_to_int'
]
