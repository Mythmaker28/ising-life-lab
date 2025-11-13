"""
Generate markdown reports for v3.5 results.
"""

import json
from pathlib import Path
from datetime import datetime


def generate_catalog(modules_data):
    """Generate BRAIN_MODULES_v3_5_CATALOG.md"""
    
    md = "# Brain Modules v3.5 — Catalog\n\n"
    md += f"**Date**: {datetime.now().date()}\n\n"
    md += "---\n\n"
    
    md += "## Overview\n\n"
    md += f"Total modules tested: {len(modules_data)}\n\n"
    
    brain_modules = [m for m in modules_data if m.get('classification', {}).get('category') == 'brain_module']
    stable_modules = [m for m in modules_data if m.get('stable', False)]
    
    md += f"- Brain modules: {len(brain_modules)}\n"
    md += f"- Stable (std < 0.15): {len(stable_modules)}\n\n"
    
    md += "---\n\n"
    md += "## Modules\n\n"
    
    # Sort by tier then life_capacity
    modules_sorted = sorted(modules_data, key=lambda x: (
        x.get('tier', 999),
        -x.get('metrics', {}).get('life_capacity', {}).get('mean', 0)
    ))
    
    for module in modules_sorted:
        notation = module['notation']
        tier = module.get('tier', '?')
        role = module.get('suggested_role', 'N/A')
        
        md += f"### {notation} (Tier {tier})\n\n"
        md += f"**Role**: {role}\n\n"
        
        metrics = module.get('metrics', {})
        classification = module.get('classification', {})
        
        md += "**Metrics** (mean ± std):\n"
        md += f"- Life capacity: {metrics.get('life_capacity', {}).get('mean', 0):.3f} ± "
        md += f"{metrics.get('life_capacity', {}).get('std', 0):.3f}\n"
        md += f"- Robustness: {metrics.get('robustness', {}).get('mean', 0):.3f} ± "
        md += f"{metrics.get('robustness', {}).get('std', 0):.3f}\n"
        md += f"- Basin diversity: {metrics.get('basin_diversity', {}).get('mean', 0):.3f} ± "
        md += f"{metrics.get('basin_diversity', {}).get('std', 0):.3f}\n"
        md += f"- Density: {metrics.get('density', {}).get('mean', 0):.3f} ± "
        md += f"{metrics.get('density', {}).get('std', 0):.3f}\n\n"
        
        md += f"**Classification**: {classification.get('category', 'N/A')}\n"
        md += f"**Reason**: {classification.get('reason', 'N/A')}\n"
        md += f"**Stable**: {'✓' if module.get('stable', False) else '✗'}\n\n"
        
        md += "---\n\n"
    
    return md


def generate_reservoir_results(reservoirs_data):
    """Generate BRAIN_RESERVOIR_RESULTS_v3_5.md"""
    
    md = "# Brain Reservoir Computation Results v3.5\n\n"
    md += f"**Date**: {datetime.now().date()}\n\n"
    md += "---\n\n"
    
    md += "## Tasks\n\n"
    md += "1. **N-bit memory**: Memorize and recall bit sequences (sequential task)\n"
    md += "2. **Pattern denoising**: Reconstruct clean pattern from noisy input (spatial task)\n\n"
    
    md += "**Readout**: Linear models (Logistic Regression for classification, Ridge for regression)\n\n"
    
    md += "---\n\n"
    
    results = reservoirs_data.get('results', [])
    
    # N-bit memory results
    md += "## Task 1: N-bit Memory\n\n"
    md += "| Notation | Train Acc | Test Acc | Status |\n"
    md += "|----------|-----------|----------|--------|\n"
    
    memory_results = []
    for r in results:
        if 'error' in r or 'error' in r.get('n_bit_memory', {}):
            continue
        
        notation = r['notation']
        mem = r.get('n_bit_memory', {})
        train_acc = mem.get('train_accuracy', 0)
        test_acc = mem.get('test_accuracy', 0)
        
        memory_results.append((notation, train_acc, test_acc))
        
        status = "✓" if test_acc > 0.6 else "⚠️" if test_acc > 0.5 else "✗"
        md += f"| {notation} | {train_acc:.3f} | {test_acc:.3f} | {status} |\n"
    
    # Best performer
    if memory_results:
        best = max(memory_results, key=lambda x: x[2])
        md += f"\n**Best**: {best[0]} (test_acc={best[2]:.3f})\n\n"
    
    md += "---\n\n"
    
    # Pattern denoising results
    md += "## Task 2: Pattern Denoising\n\n"
    md += "| Notation | Train R² | Test R² | Test MAE | Status |\n"
    md += "|----------|----------|---------|----------|--------|\n"
    
    denoising_results = []
    for r in results:
        if 'error' in r or 'error' in r.get('pattern_denoising', {}):
            continue
        
        notation = r['notation']
        denoise = r.get('pattern_denoising', {})
        train_r2 = denoise.get('train_r2', 0)
        test_r2 = denoise.get('test_r2', 0)
        test_mae = denoise.get('test_mae', 0)
        
        denoising_results.append((notation, train_r2, test_r2, test_mae))
        
        status = "✓" if test_r2 > 0.5 else "⚠️" if test_r2 > 0.3 else "✗"
        md += f"| {notation} | {train_r2:.3f} | {test_r2:.3f} | {test_mae:.3f} | {status} |\n"
    
    # Best performer
    if denoising_results:
        best = max(denoising_results, key=lambda x: x[2])
        md += f"\n**Best**: {best[0]} (test_r2={best[2]:.3f})\n\n"
    
    md += "---\n\n"
    
    md += "## Interpretation\n\n"
    md += "**Baselines**:\n"
    md += "- Random guess (N-bit memory): 0.50\n"
    md += "- Trivial predictor (Pattern denoising): R²=0.0\n\n"
    
    md += "**Useful modules** should significantly exceed baselines.\n\n"
    
    # Summary
    md += "## Summary\n\n"
    
    good_memory = [r for r in memory_results if r[2] > 0.6]
    good_denoising = [r for r in denoising_results if r[2] > 0.5]
    
    md += f"- Modules with good memory performance (acc > 0.6): {len(good_memory)}\n"
    md += f"- Modules with good denoising performance (R² > 0.5): {len(good_denoising)}\n\n"
    
    if good_memory:
        md += "**Good memory modules**: " + ", ".join([r[0] for r in good_memory]) + "\n\n"
    
    if good_denoising:
        md += "**Good denoising modules**: " + ", ".join([r[0] for r in good_denoising]) + "\n\n"
    
    return md


def generate_physical_mapping(mapping_data):
    """Generate BRAIN_TO_PHYSICAL_MAPPING_v3_5.md"""
    
    md = "# Brain to Physical Systems Mapping v3.5\n\n"
    md += f"**Date**: {datetime.now().date()}\n\n"
    md += "**DISCLAIMER**: Speculative mappings based on dynamic metrics. Not experimental validation.\n\n"
    md += "---\n\n"
    
    md += "## Physical Systems (Hypothetical Profiles)\n\n"
    
    phys_systems = mapping_data.get('physical_systems', {})
    for name, info in phys_systems.items():
        md += f"### {name}\n\n"
        md += f"**Description**: {info['description']}\n\n"
        md += "**Desired profile**:\n"
        profile = info['desired_profile']
        for key, value in profile.items():
            md += f"- {key}: {value:.2f}\n"
        md += "\n"
    
    md += "---\n\n"
    md += "## Mappings\n\n"
    
    mappings = mapping_data.get('mappings', [])
    
    for mapping in mappings:
        notation = mapping['notation']
        closest = mapping['closest_match']
        distance = mapping['closest_match_distance']
        description = mapping['closest_match_description']
        
        md += f"### {notation}\n\n"
        md += f"**Closest match**: {closest} ({description})\n"
        md += f"**Distance**: {distance:.3f}\n\n"
        
        md += "**CA profile**:\n"
        ca_prof = mapping['ca_profile']
        for key, value in ca_prof.items():
            md += f"- {key}: {value:.2f}\n"
        md += "\n"
    
    md += "---\n\n"
    md += "## Hypotheses\n\n"
    
    hypotheses = mapping_data.get('hypotheses', [])
    
    for i, hyp in enumerate(hypotheses, 1):
        md += f"### {i}. {hyp['physical_system']}\n\n"
        md += f"**Description**: {hyp['description']}\n\n"
        md += f"**Candidate CA rules**: {', '.join(hyp['candidate_ca_rules'])}\n\n"
        md += f"**Hypothesis**: {hyp['hypothesis']}\n\n"
        md += f"**Status**: {hyp['status']}\n\n"
        md += "**Suggested tests**:\n"
        for test in hyp.get('suggested_tests', []):
            md += f"- {test}\n"
        md += "\n"
    
    return md


def main():
    output_dir = Path("docs")
    output_dir.mkdir(exist_ok=True)
    
    # Generate catalog
    modules_path = Path("results/brain_modules_v3_5.json")
    if modules_path.exists():
        with open(modules_path) as f:
            modules_data = json.load(f)
        
        catalog_md = generate_catalog(modules_data['modules'])
        with open(output_dir / "BRAIN_MODULES_v3_5_CATALOG.md", 'w', encoding='utf-8') as f:
            f.write(catalog_md)
        
        print(f"Generated: docs/BRAIN_MODULES_v3_5_CATALOG.md")
    
    # Generate reservoir results
    reservoirs_path = Path("results/brain_reservoirs_v3_5.json")
    if reservoirs_path.exists():
        with open(reservoirs_path) as f:
            reservoirs_data = json.load(f)
        
        reservoir_md = generate_reservoir_results(reservoirs_data)
        with open(output_dir / "BRAIN_RESERVOIR_RESULTS_v3_5.md", 'w', encoding='utf-8') as f:
            f.write(reservoir_md)
        
        print(f"Generated: docs/BRAIN_RESERVOIR_RESULTS_v3_5.md")
    
    # Generate physical mapping
    mapping_path = Path("results/brain_physical_mapping_v3_5.json")
    if mapping_path.exists():
        with open(mapping_path) as f:
            mapping_data = json.load(f)
        
        mapping_md = generate_physical_mapping(mapping_data)
        with open(output_dir / "BRAIN_TO_PHYSICAL_MAPPING_v3_5.md", 'w', encoding='utf-8') as f:
            f.write(mapping_md)
        
        print(f"Generated: docs/BRAIN_TO_PHYSICAL_MAPPING_v3_5.md")


if __name__ == "__main__":
    main()

