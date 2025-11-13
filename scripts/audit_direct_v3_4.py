"""
Direct Audit v3.4 - Writes results directly to files, no console output.
Bypasses the broken print() issue.
"""

import sys
from pathlib import Path
import numpy as np
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from isinglab.core.rule_ops import parse_notation
from isinglab.core.ca_vectorized import evolve_ca_vectorized
from isinglab.metrics.functional import (
    compute_life_pattern_capacity,
    compute_robustness_to_noise,
    compute_basin_size
)


def create_rule_function(born_set, survive_set):
    """Create vectorized rule function."""
    def rule_func(grid):
        return evolve_ca_vectorized(grid, born_set, survive_set, steps=1)
    return rule_func


def audit_rule(notation, log_file):
    """Audit single rule, write to log file."""
    log_file.write(f"\n{'='*70}\n")
    log_file.write(f"AUDIT: {notation}\n")
    log_file.write(f"{'='*70}\n")
    log_file.flush()
    
    born, survive = parse_notation(notation)
    born_set, survive_set = set(born), set(survive)
    
    result = {
        'notation': notation,
        'born': born,
        'survive': survive,
        'timestamp': datetime.now().isoformat()
    }
    
    # Sanity check
    log_file.write(f"Structure: B={born}, S={survive}\n")
    
    if not born:
        result['category'] = 'stabilizer'
        result['reason'] = 'No birth rules'
        log_file.write("VERDICT: STABILIZER (no birth)\n")
        return result
    
    if not survive:
        result['category'] = 'chaotic'
        result['reason'] = 'No survival rules'
        log_file.write("VERDICT: CHAOTIC (no survival)\n")
        return result
    
    # Density tests
    log_file.write("\nDensity tests (3 seeds × 3 grids)...\n")
    densities = []
    
    for grid_size in [(32, 32), (64, 64), (128, 128)]:
        for seed in range(3):
            np.random.seed(42 + seed)
            grid = (np.random.rand(*grid_size) < 0.3).astype(int)
            grid_final = evolve_ca_vectorized(grid, born_set, survive_set, steps=100)
            density = grid_final.mean()
            densities.append(density)
    
    avg_density = np.mean(densities)
    std_density = np.std(densities)
    
    result['density_mean'] = float(avg_density)
    result['density_std'] = float(std_density)
    
    log_file.write(f"  Density: {avg_density:.3f} ± {std_density:.3f}\n")
    
    if avg_density < 0.05:
        result['category'] = 'sink'
        result['reason'] = f'Quasi-death (density={avg_density:.3f})'
        log_file.write("  VERDICT: SINK (quasi-death)\n")
        return result
    
    if avg_density > 0.95:
        result['category'] = 'sink'
        result['reason'] = f'Saturation (density={avg_density:.3f})'
        log_file.write("  VERDICT: SINK (saturation)\n")
        return result
    
    # Life pattern capacity
    log_file.write("\nLife pattern capacity...\n")
    rule_func = create_rule_function(born_set, survive_set)
    
    life_result = compute_life_pattern_capacity(rule_func, grid_size=(64, 64))
    life_score = life_result['life_capacity_score']
    
    result['life_capacity_score'] = float(life_score)
    result['life_patterns'] = life_result['patterns']
    
    log_file.write(f"  Life capacity: {life_score:.3f}\n")
    for pname, pres in life_result['patterns'].items():
        log_file.write(f"    {pname}: {pres['score']:.2f}\n")
    
    # Robustness
    log_file.write("\nRobustness tests...\n")
    robustness_scores = []
    
    for noise in [0.1, 0.2, 0.3]:
        rob_result = compute_robustness_to_noise(
            rule_func, grid_size=(32, 32), noise_level=noise, n_trials=3, steps=50
        )
        robustness_scores.append(rob_result['robustness_score'])
        log_file.write(f"  Noise {int(noise*100)}%: {rob_result['robustness_score']:.3f}\n")
    
    avg_robustness = np.mean(robustness_scores)
    result['avg_robustness'] = float(avg_robustness)
    
    # Basin diversity
    log_file.write("\nBasin diversity...\n")
    basin_result = compute_basin_size(rule_func, grid_size=(32, 32), n_samples=10, steps=50)
    basin_diversity = basin_result['basin_diversity']
    
    result['basin_diversity'] = float(basin_diversity)
    log_file.write(f"  Diversity: {basin_diversity:.3f}\n")
    
    # Classification
    if robustness > 0.9 and life_score < 0.3:
        category = 'stabilizer'
        reason = f'High robustness ({avg_robustness:.2f}) but low capacity ({life_score:.2f})'
    elif life_score > 0.4 and basin_diversity > 0.3:
        category = 'brain_module'
        reason = f'Good capacity ({life_score:.2f}) + diversity ({basin_diversity:.2f})'
    elif life_score > 0.5:
        category = 'brain_module'
        reason = f'High capacity ({life_score:.2f})'
    elif robustness > 0.8 and basin_diversity < 0.15:
        category = 'stabilizer'
        reason = f'Single attractor stabilizer'
    else:
        category = 'unclassified'
        reason = f'Mixed metrics'
    
    result['category'] = category
    result['reason'] = reason
    
    log_file.write(f"\nVERDICT: {category.upper()}\n")
    log_file.write(f"Reason: {reason}\n")
    log_file.flush()
    
    return result


def generate_neighbors(notation):
    """Generate ±1 neighbors of a rule."""
    born, survive = parse_notation(notation)
    neighbors = set()
    
    # Add/remove from born
    for b in range(9):
        if b not in born:
            new_born = sorted(born + [b])
            neighbors.add(f"B{''.join(map(str, new_born))}/S{''.join(map(str, survive))}")
        if b in born and len(born) > 1:
            new_born = [x for x in born if x != b]
            neighbors.add(f"B{''.join(map(str, new_born))}/S{''.join(map(str, survive))}")
    
    # Add/remove from survive
    for s in range(9):
        if s not in survive:
            new_survive = sorted(survive + [s])
            neighbors.add(f"B{''.join(map(str, born))}/S{''.join(map(str, new_survive))}")
        if s in survive and len(survive) > 1:
            new_survive = [x for x in survive if x != s]
            neighbors.add(f"B{''.join(map(str, born))}/S{''.join(map(str, new_survive))}")
    
    neighbors.discard(notation)
    return sorted(list(neighbors))


def main():
    # Setup output
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    
    log_path = output_dir / "audit_log_v3_4.txt"
    
    with open(log_path, 'w', encoding='utf-8') as log:
        log.write("="*80 + "\n")
        log.write("DEEP BRAIN HUNT v3.4 - DIRECT AUDIT\n")
        log.write("="*80 + "\n")
        log.write(f"Started: {datetime.now().isoformat()}\n\n")
        log.flush()
        
        all_results = []
        
        # PARTIE A: Audit suspects
        log.write("\n" + "="*80 + "\n")
        log.write("PARTIE A: AUDIT SUSPECTS\n")
        log.write("="*80 + "\n")
        log.flush()
        
        suspects = ["B/S234", "B/S123", "B6/S23"]
        
        for suspect in suspects:
            try:
                result = audit_rule(suspect, log)
                all_results.append(result)
            except Exception as e:
                log.write(f"ERROR auditing {suspect}: {e}\n")
                log.flush()
        
        # PARTIE B: Validate known brains
        log.write("\n" + "="*80 + "\n")
        log.write("PARTIE B: VALIDATE KNOWN BRAINS\n")
        log.write("="*80 + "\n")
        log.flush()
        
        known_brains = ["B3/S23", "B36/S23", "B34/S34", "B3/S234"]
        
        for brain in known_brains:
            try:
                result = audit_rule(brain, log)
                all_results.append(result)
            except Exception as e:
                log.write(f"ERROR auditing {brain}: {e}\n")
                log.flush()
        
        # PARTIE C: Scan neighborhoods (sample - just B3/S23 for now due to time)
        log.write("\n" + "="*80 + "\n")
        log.write("PARTIE C: NEIGHBORHOOD SCAN (B3/S23 only)\n")
        log.write("="*80 + "\n")
        log.flush()
        
        neighbors = generate_neighbors("B3/S23")
        log.write(f"Generated {len(neighbors)} neighbors\n\n")
        log.flush()
        
        # Sample 10 neighbors to keep runtime reasonable
        import random
        random.seed(42)
        sampled_neighbors = random.sample(neighbors, min(10, len(neighbors)))
        
        for i, neighbor in enumerate(sampled_neighbors, 1):
            log.write(f"\n[{i}/{len(sampled_neighbors)}] {neighbor}\n")
            log.flush()
            try:
                result = audit_rule(neighbor, log)
                all_results.append(result)
            except Exception as e:
                log.write(f"ERROR: {e}\n")
                log.flush()
        
        # Summary
        log.write("\n" + "="*80 + "\n")
        log.write("SUMMARY\n")
        log.write("="*80 + "\n")
        
        categories = {}
        for r in all_results:
            cat = r.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        log.write("\nCategory distribution:\n")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            log.write(f"  {cat}: {count}\n")
        
        brain_modules = [r for r in all_results if r.get('category') == 'brain_module']
        log.write(f"\nBrain modules found: {len(brain_modules)}\n")
        
        if brain_modules:
            log.write("\nTop brain modules:\n")
            brain_modules_sorted = sorted(
                brain_modules,
                key=lambda x: x.get('life_capacity_score', 0),
                reverse=True
            )
            for bm in brain_modules_sorted[:5]:
                log.write(f"  {bm['notation']}: life_cap={bm.get('life_capacity_score', 0):.3f}\n")
        
        log.write(f"\nCompleted: {datetime.now().isoformat()}\n")
        log.flush()
    
    # Save JSON
    output_json = output_dir / "audit_results_v3_4.json"
    with open(output_json, 'w') as f:
        json.dump({
            'meta': {
                'version': '3.4',
                'date': datetime.now().isoformat(),
                'suspects_audited': suspects,
                'known_brains_validated': known_brains
            },
            'results': all_results,
            'summary': {
                'total_tested': len(all_results),
                'categories': categories,
                'brain_modules_found': len(brain_modules)
            }
        }, f, indent=2, default=str)
    
    # Generate markdown report
    md_path = output_dir / "AUDIT_REPORT_v3_4.md"
    with open(md_path, 'w', encoding='utf-8') as md:
        md.write("# Audit Report v3.4\n\n")
        md.write(f"**Date**: {datetime.now().date()}\n\n")
        md.write("---\n\n")
        
        md.write("## Suspects Audited\n\n")
        md.write("| Rule | Category | Life Capacity | Density | Reason |\n")
        md.write("|------|----------|---------------|---------|--------|\n")
        
        for r in all_results:
            if r['notation'] in suspects:
                md.write(f"| {r['notation']} | {r.get('category', 'N/A')} | ")
                md.write(f"{r.get('life_capacity_score', 0):.3f} | ")
                md.write(f"{r.get('density_mean', 0):.3f} | ")
                md.write(f"{r.get('reason', 'N/A')[:40]} |\n")
        
        md.write("\n## Known Brains Validated\n\n")
        md.write("| Rule | Category | Life Capacity | Robustness | Diversity |\n")
        md.write("|------|----------|---------------|------------|----------|\n")
        
        for r in all_results:
            if r['notation'] in known_brains:
                md.write(f"| {r['notation']} | {r.get('category', 'N/A')} | ")
                md.write(f"{r.get('life_capacity_score', 0):.3f} | ")
                md.write(f"{r.get('avg_robustness', 0):.3f} | ")
                md.write(f"{r.get('basin_diversity', 0):.3f} |\n")
        
        md.write("\n## Summary\n\n")
        md.write(f"Total rules tested: {len(all_results)}\n\n")
        md.write("Category distribution:\n")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            md.write(f"- **{cat}**: {count}\n")
        
        if brain_modules:
            md.write(f"\n### Brain Modules ({len(brain_modules)})\n\n")
            md.write("| Rule | Life Capacity | Robustness | Diversity |\n")
            md.write("|------|---------------|------------|----------|\n")
            
            for bm in brain_modules_sorted[:10]:
                md.write(f"| {bm['notation']} | ")
                md.write(f"{bm.get('life_capacity_score', 0):.3f} | ")
                md.write(f"{bm.get('avg_robustness', 0):.3f} | ")
                md.write(f"{bm.get('basin_diversity', 0):.3f} |\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Write error to file since print doesn't work
        with open("results/audit_error.txt", 'w') as f:
            f.write(f"ERROR: {e}\n")
            import traceback
            f.write(traceback.format_exc())
        raise


