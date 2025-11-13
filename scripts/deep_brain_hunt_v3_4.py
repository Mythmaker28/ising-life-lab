"""
Deep Brain Hunt v3.4 — Audit Profond + Scan Voisinages Ciblé

Objectifs :
1. Audit profond des règles "born-minimal" suspectes
2. Scan ciblé des voisinages des 4 vrais cerveaux
3. Classification rigoureuse : brains vs stabilizers vs sinks
4. Calibration des métriques contre artefacts

Autonomie : Ce script s'exécute sans intervention, génère rapports et données.
"""

import sys
from pathlib import Path
import numpy as np
import json
from datetime import datetime
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

from isinglab.core.rule_ops import parse_notation
from isinglab.core.ca_vectorized import evolve_ca_vectorized
from isinglab.metrics.functional import (
    compute_life_pattern_capacity,
    compute_memory_capacity,
    compute_robustness_to_noise,
    compute_basin_size,
    compute_functional_score
)
from isinglab.meta_learner.filters import quick_density_test


class BrainClassifier:
    """Classifie règles CA selon dynamique réelle."""
    
    CATEGORIES = {
        'brain_module': 'Dynamique riche exploitable cognitivevement',
        'stabilizer': 'Robuste mais trivial (converge uniformément)',
        'sink': 'Quasi-death ou saturation (à ignorer)',
        'chaotic': 'Explosion ou bruit non structuré'
    }
    
    def __init__(self):
        self.results = []
    
    def classify_rule(self, notation: str, verbose: bool = True) -> Dict:
        """
        Classification profonde d'une règle.
        
        Tests :
        1. Sanity check structurel (birth/survival non vides)
        2. Distribution densités multi-grilles
        3. Life pattern capacity (patterns canoniques)
        4. Robustesse au bruit (10-30%)
        5. Diversité attracteurs
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"AUDIT: {notation}")
            print(f"{'='*70}")
        
        born, survive = parse_notation(notation)
        born_set, survive_set = set(born), set(survive)
        
        result = {
            'notation': notation,
            'born': born,
            'survive': survive,
            'timestamp': datetime.now().isoformat()
        }
        
        # === 1. SANITY CHECK STRUCTUREL ===
        if verbose:
            print(f"  [1/5] Sanity check...")
        
        # Règle sans naissance = suspect
        if not born:
            result['category'] = 'stabilizer'
            result['reason'] = 'No birth rules (B empty)'
            result['pass_structural'] = False
            if verbose:
                print(f"    ❌ FAIL: No birth rules")
            return result
        
        # Règle sans survie = généralement chaotique/morte
        if not survive:
            result['category'] = 'chaotic'
            result['reason'] = 'No survival rules (S empty)'
            result['pass_structural'] = False
            if verbose:
                print(f"    ⚠️  No survival rules (likely chaotic)")
            return result
        
        result['pass_structural'] = True
        if verbose:
            print(f"    ✓ Structural OK (B={born}, S={survive})")
        
        # === 2. DISTRIBUTION DENSITÉS MULTI-ÉCHELLES ===
        if verbose:
            print(f"  [2/5] Multi-scale density test...")
        
        densities = []
        grid_sizes = [(32, 32), (64, 64), (128, 128)]
        
        for grid_size in grid_sizes:
            for seed in range(3):
                density = quick_density_test(notation, grid_size=grid_size, steps=100, seed=42+seed)
                densities.append(density)
        
        avg_density = np.mean(densities)
        std_density = np.std(densities)
        min_density = np.min(densities)
        max_density = np.max(densities)
        
        result['density_stats'] = {
            'mean': float(avg_density),
            'std': float(std_density),
            'min': float(min_density),
            'max': float(max_density),
            'samples': densities
        }
        
        # Détection sink (quasi-death ou saturation)
        if avg_density < 0.05:
            result['category'] = 'sink'
            result['reason'] = f'Quasi-death (avg_density={avg_density:.3f})'
            if verbose:
                print(f"    ❌ SINK: Quasi-death (density={avg_density:.3f})")
            return result
        
        if avg_density > 0.95:
            result['category'] = 'sink'
            result['reason'] = f'Saturation (avg_density={avg_density:.3f})'
            if verbose:
                print(f"    ❌ SINK: Saturation (density={avg_density:.3f})")
            return result
        
        if verbose:
            print(f"    ✓ Density OK: {avg_density:.3f} ± {std_density:.3f} (range: {min_density:.3f}-{max_density:.3f})")
        
        # === 3. LIFE PATTERN CAPACITY ===
        if verbose:
            print(f"  [3/5] Life pattern capacity...")
        
        rule_func = self._create_rule_function(born_set, survive_set)
        
        life_capacity_result = compute_life_pattern_capacity(rule_func, grid_size=(64, 64))
        life_capacity_score = life_capacity_result['life_capacity_score']
        
        result['life_capacity'] = life_capacity_result
        
        if verbose:
            print(f"    Life capacity: {life_capacity_score:.3f}")
            for pattern_name, pattern_res in life_capacity_result['patterns'].items():
                survived = "✓" if pattern_res['survived'] else "✗"
                period = "✓" if pattern_res['found_period'] else "✗"
                score = pattern_res['score']
                print(f"      {pattern_name:10s}: {score:.2f} (survive={survived}, period={period})")
        
        # === 4. ROBUSTESSE AU BRUIT ===
        if verbose:
            print(f"  [4/5] Robustness to noise...")
        
        robustness_tests = []
        for noise_level in [0.1, 0.2, 0.3]:
            rob_result = compute_robustness_to_noise(
                rule_func, 
                grid_size=(32, 32), 
                noise_level=noise_level, 
                n_trials=3, 
                steps=50
            )
            robustness_tests.append({
                'noise_level': noise_level,
                'robustness_score': rob_result['robustness_score']
            })
            if verbose:
                print(f"      Noise {int(noise_level*100):2d}%: {rob_result['robustness_score']:.3f}")
        
        result['robustness_tests'] = robustness_tests
        avg_robustness = np.mean([r['robustness_score'] for r in robustness_tests])
        result['avg_robustness'] = float(avg_robustness)
        
        # === 5. DIVERSITÉ ATTRACTEURS ===
        if verbose:
            print(f"  [5/5] Basin diversity...")
        
        basin_result = compute_basin_size(rule_func, grid_size=(32, 32), n_samples=10, steps=50)
        basin_diversity = basin_result['basin_diversity']
        unique_attractors = basin_result['unique_attractors']
        
        result['basin_diversity'] = float(basin_diversity)
        result['unique_attractors'] = int(unique_attractors)
        
        if verbose:
            print(f"    Diversity: {basin_diversity:.3f} ({unique_attractors}/10 attractors)")
        
        # === CLASSIFICATION FINALE ===
        result['category'], result['reason'], result['role'] = self._classify_from_metrics(
            life_capacity_score,
            avg_robustness,
            basin_diversity,
            avg_density
        )
        
        if verbose:
            print(f"\n  VERDICT: {result['category'].upper()}")
            print(f"  Reason:  {result['reason']}")
            print(f"  Role:    {result['role']}")
        
        return result
    
    def _classify_from_metrics(self, life_capacity: float, robustness: float, 
                               basin_diversity: float, density: float) -> Tuple[str, str, str]:
        """
        Logique de classification basée métriques.
        
        Returns: (category, reason, suggested_role)
        """
        # Règle parfaitement robuste mais capacity faible = stabilizer trivial
        if robustness > 0.9 and life_capacity < 0.3:
            return (
                'stabilizer',
                f'Perfect robustness ({robustness:.2f}) but low capacity ({life_capacity:.2f})',
                'Stabilizer/filter (not cognitive)'
            )
        
        # Capacity élevée + diversité = brain module
        if life_capacity > 0.4 and basin_diversity > 0.3:
            return (
                'brain_module',
                f'High capacity ({life_capacity:.2f}) + diversity ({basin_diversity:.2f})',
                'Cognitive module (memory/compute)'
            )
        
        # Robustesse et capacity décentes = brain potential
        if life_capacity > 0.5 and robustness > 0.2:
            return (
                'brain_module',
                f'Good capacity ({life_capacity:.2f}) + robustness ({robustness:.2f})',
                'Memory module with noise tolerance'
            )
        
        # Diversité très élevée mais capacity faible = chaotic
        if basin_diversity > 0.8 and life_capacity < 0.2:
            return (
                'chaotic',
                f'High diversity ({basin_diversity:.2f}) but no structure',
                'Exploratory/chaotic (not cognitive)'
            )
        
        # Robustesse parfaite + diversité nulle = stabilizer
        if robustness > 0.8 and basin_diversity < 0.15:
            return (
                'stabilizer',
                f'High robustness ({robustness:.2f}) but single attractor',
                'Stabilizer (converges uniformly)'
            )
        
        # Défaut : non classifié
        return (
            'unclassified',
            f'Mixed metrics (capacity={life_capacity:.2f}, robust={robustness:.2f}, div={basin_diversity:.2f})',
            'Requires further analysis'
        )
    
    def _create_rule_function(self, born_set, survive_set):
        """Crée fonction vectorisée pour règle CA."""
        def rule_func(grid):
            return evolve_ca_vectorized(grid, born_set, survive_set, steps=1)
        return rule_func


class NeighborhoodScanner:
    """Scan voisinages des cerveaux validés."""
    
    def __init__(self, classifier: BrainClassifier):
        self.classifier = classifier
    
    def generate_neighbors(self, notation: str, max_distance: int = 1) -> List[str]:
        """
        Génère voisins d'une règle (mutations ±1 sur B et S).
        
        Args:
            notation: Règle seed (ex: "B3/S23")
            max_distance: Distance de mutation (1 = ±1 voisin)
        
        Returns:
            Liste de notations voisines
        """
        born, survive = parse_notation(notation)
        neighbors = set()
        
        # Mutations sur B
        for b in range(9):
            # Ajouter b
            if b not in born:
                new_born = sorted(born + [b])
                new_notation = f"B{''.join(map(str, new_born))}/S{''.join(map(str, survive))}"
                neighbors.add(new_notation)
            
            # Retirer b
            if b in born and len(born) > 1:  # Garder au moins 1 birth
                new_born = [x for x in born if x != b]
                new_notation = f"B{''.join(map(str, new_born))}/S{''.join(map(str, survive))}"
                neighbors.add(new_notation)
        
        # Mutations sur S
        for s in range(9):
            # Ajouter s
            if s not in survive:
                new_survive = sorted(survive + [s])
                new_notation = f"B{''.join(map(str, born))}/S{''.join(map(str, new_survive))}"
                neighbors.add(new_notation)
            
            # Retirer s
            if s in survive and len(survive) > 1:  # Garder au moins 1 survive
                new_survive = [x for x in survive if x != s]
                new_notation = f"B{''.join(map(str, born))}/S{''.join(map(str, new_survive))}"
                neighbors.add(new_notation)
        
        # Exclure la règle originale
        neighbors.discard(notation)
        
        return sorted(list(neighbors))
    
    def scan_neighborhood(self, seed_notation: str, verbose: bool = True) -> List[Dict]:
        """Scan complet voisinage d'une règle seed."""
        if verbose:
            print(f"\n{'='*80}")
            print(f"NEIGHBORHOOD SCAN: {seed_notation}")
            print(f"{'='*80}")
        
        neighbors = self.generate_neighbors(seed_notation)
        
        if verbose:
            print(f"Generated {len(neighbors)} neighbors")
        
        results = []
        
        for i, neighbor in enumerate(neighbors, 1):
            if verbose:
                print(f"\n[{i}/{len(neighbors)}] Testing {neighbor}...")
            
            try:
                result = self.classifier.classify_rule(neighbor, verbose=False)
                results.append(result)
                
                if verbose:
                    category = result['category']
                    reason = result['reason'][:60]
                    print(f"  → {category.upper()}: {reason}")
            
            except Exception as exc:
                if verbose:
                    print(f"  ✗ ERROR: {exc}")
                results.append({
                    'notation': neighbor,
                    'error': str(exc),
                    'category': 'error'
                })
        
        return results


def main():
    print("=" * 80)
    print("DEEP BRAIN HUNT v3.4")
    print("=" * 80)
    print()
    
    classifier = BrainClassifier()
    scanner = NeighborhoodScanner(classifier)
    
    # === PARTIE A: AUDIT PROFOND DES SUSPECTS ===
    print("\n" + "="*80)
    print("PARTIE A: AUDIT SUSPECTS (born-minimal rules)")
    print("="*80)
    
    suspects = ["B/S234", "B/S123", "B6/S23"]
    audit_results = []
    
    for suspect in suspects:
        result = classifier.classify_rule(suspect, verbose=True)
        audit_results.append(result)
    
    # === PARTIE B: SCAN VOISINAGES CERVEAUX VALIDÉS ===
    print("\n" + "="*80)
    print("PARTIE B: SCAN VOISINAGES (validated brains)")
    print("="*80)
    
    validated_brains = ["B3/S23", "B36/S23", "B34/S34", "B3/S234"]
    neighborhood_results = {}
    
    for brain in validated_brains:
        neighbors_results = scanner.scan_neighborhood(brain, verbose=True)
        neighborhood_results[brain] = neighbors_results
    
    # === PARTIE C: SYNTHÈSE ET FILTRAGE ===
    print("\n" + "="*80)
    print("PARTIE C: SYNTHÈSE")
    print("="*80)
    
    # Compter par catégorie
    all_scanned = audit_results.copy()
    for brain_neighbors in neighborhood_results.values():
        all_scanned.extend(brain_neighbors)
    
    category_counts = {}
    for res in all_scanned:
        cat = res.get('category', 'unknown')
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    print("\nDistribution par catégorie:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat:20s}: {count:3d}")
    
    # Sélectionner les brain_modules
    brain_modules = [r for r in all_scanned if r.get('category') == 'brain_module']
    
    print(f"\n{'='*80}")
    print(f"BRAIN MODULES TROUVÉS: {len(brain_modules)}")
    print(f"{'='*80}")
    
    # Trier par life_capacity
    brain_modules_sorted = sorted(
        brain_modules, 
        key=lambda x: x.get('life_capacity', {}).get('life_capacity_score', 0),
        reverse=True
    )
    
    # Afficher top 10
    print("\nTop 10 Brain Modules (par life_capacity):")
    print("-" * 80)
    for i, brain in enumerate(brain_modules_sorted[:10], 1):
        notation = brain['notation']
        life_cap = brain.get('life_capacity', {}).get('life_capacity_score', 0)
        robustness = brain.get('avg_robustness', 0)
        diversity = brain.get('basin_diversity', 0)
        print(f"  {i:2d}. {notation:15s} | Life={life_cap:.3f} Rob={robustness:.3f} Div={diversity:.3f}")
    
    # === SAUVEGARDER RÉSULTATS ===
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    
    output_data = {
        'meta': {
            'version': '3.4',
            'date': datetime.now().isoformat(),
            'suspects_audited': suspects,
            'brains_scanned': validated_brains
        },
        'audit_suspects': audit_results,
        'neighborhood_scans': neighborhood_results,
        'summary': {
            'total_rules_tested': len(all_scanned),
            'brain_modules_found': len(brain_modules),
            'category_distribution': category_counts
        },
        'top_brain_modules': brain_modules_sorted[:10]
    }
    
    output_file = output_dir / "brain_hunt_v3_4.json"
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)
    
    print(f"\n{'='*80}")
    print(f"Résultats sauvegardés: {output_file}")
    print(f"{'='*80}")
    
    # === GÉNÉRER RAPPORT MARKDOWN ===
    generate_markdown_report(output_data, output_dir / "DEEP_BRAIN_HUNT_v3_4.md")
    
    return output_data


def generate_markdown_report(data: Dict, output_path: Path):
    """Génère rapport markdown lisible."""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Deep Brain Hunt v3.4 — Rapport Final\n\n")
        f.write(f"**Date**: {data['meta']['date'][:10]}\n\n")
        f.write("---\n\n")
        
        # PARTIE A: Audit suspects
        f.write("## Partie A: Audit des Suspects\n\n")
        f.write("Règles 'born-minimal' testées: " + ", ".join(data['meta']['suspects_audited']) + "\n\n")
        f.write("| Règle | Catégorie | Raison | Life Capacity |\n")
        f.write("|-------|-----------|--------|---------------|\n")
        
        for suspect in data['audit_suspects']:
            notation = suspect['notation']
            category = suspect.get('category', 'unknown')
            reason = suspect.get('reason', 'N/A')[:50]
            life_cap = suspect.get('life_capacity', {}).get('life_capacity_score', 0)
            f.write(f"| {notation} | {category} | {reason} | {life_cap:.3f} |\n")
        
        f.write("\n")
        
        # PARTIE B: Scan voisinages
        f.write("## Partie B: Scan Voisinages\n\n")
        
        for brain, neighbors in data['neighborhood_scans'].items():
            f.write(f"### {brain}\n\n")
            
            # Compter catégories
            cat_counts = {}
            for n in neighbors:
                cat = n.get('category', 'unknown')
                cat_counts[cat] = cat_counts.get(cat, 0) + 1
            
            f.write(f"Voisins testés: {len(neighbors)}\n\n")
            f.write("Distribution:\n")
            for cat, count in sorted(cat_counts.items()):
                f.write(f"- {cat}: {count}\n")
            
            # Brain modules trouvés
            brain_mods = [n for n in neighbors if n.get('category') == 'brain_module']
            if brain_mods:
                f.write(f"\n**Brain modules trouvés ({len(brain_mods)}):**\n\n")
                f.write("| Notation | Life Capacity | Robustness | Diversity |\n")
                f.write("|----------|---------------|------------|----------|\n")
                
                for bm in sorted(brain_mods, key=lambda x: x.get('life_capacity', {}).get('life_capacity_score', 0), reverse=True):
                    notation = bm['notation']
                    life_cap = bm.get('life_capacity', {}).get('life_capacity_score', 0)
                    robustness = bm.get('avg_robustness', 0)
                    diversity = bm.get('basin_diversity', 0)
                    f.write(f"| {notation} | {life_cap:.3f} | {robustness:.3f} | {diversity:.3f} |\n")
            
            f.write("\n")
        
        # PARTIE C: Top brain modules
        f.write("## Partie C: Top Brain Modules\n\n")
        f.write(f"Total brain modules identifiés: {data['summary']['brain_modules_found']}\n\n")
        f.write("### Top 10 (par Life Capacity)\n\n")
        f.write("| Rang | Notation | Life Cap | Robustness | Diversity | Rôle Suggéré |\n")
        f.write("|------|----------|----------|------------|-----------|---------------|\n")
        
        for i, brain in enumerate(data['top_brain_modules'][:10], 1):
            notation = brain['notation']
            life_cap = brain.get('life_capacity', {}).get('life_capacity_score', 0)
            robustness = brain.get('avg_robustness', 0)
            diversity = brain.get('basin_diversity', 0)
            role = brain.get('role', 'N/A')[:40]
            f.write(f"| {i} | {notation} | {life_cap:.3f} | {robustness:.3f} | {diversity:.3f} | {role} |\n")
        
        f.write("\n---\n\n")
        f.write("## Distribution Globale\n\n")
        
        for cat, count in sorted(data['summary']['category_distribution'].items(), key=lambda x: -x[1]):
            f.write(f"- **{cat}**: {count}\n")
        
        f.write("\n---\n\n")
        f.write("**Fichier de données**: `brain_hunt_v3_4.json`\n")
    
    print(f"Rapport markdown généré: {output_path}")


if __name__ == "__main__":
    main()


