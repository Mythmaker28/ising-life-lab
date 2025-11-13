"""
Hill-Climb v3 autour des 3 cerveaux validés.

Stratégie :
1. Seeds : B3/S23, B36/S23, B34/S34
2. Générer voisins (±1 digit born/survive)
3. Filtrer trivialités AVANT évaluation
4. Évaluer voisins (fast mode vectorisé)
5. Comparer vs seeds

Objectif : Trouver 1-2 variantes meilleures sur critères spécifiques.
"""

import sys
from pathlib import Path
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from isinglab.core.rule_ops import generate_neighbors
from isinglab.meta_learner.filters import apply_hard_filters
from isinglab.memory_explorer import MemoryExplorer

# Seeds
SEEDS = [
    ("B3/S23", "Life"),
    ("B36/S23", "HighLife"),
    ("B34/S34", "34 Life")
]

print("=" * 80)
print("HILL-CLIMB v3 AUTOUR DES 3 CERVEAUX")
print("=" * 80)
print()

explorer = MemoryExplorer()
results = []

for seed_notation, seed_name in SEEDS:
    print(f"\n### Seed : {seed_notation} ({seed_name})")
    print("-" * 60)
    
    # Générer voisins (distance 1)
    neighbors = generate_neighbors(seed_notation, radius=1)
    print(f"  Voisins générés : {len(neighbors)}")
    
    # Filtrer trivialités
    valid_neighbors = []
    rejected = []
    
    for neighbor in neighbors:
        pass_filter, reason = apply_hard_filters(neighbor)
        if pass_filter:
            valid_neighbors.append(neighbor)
        else:
            rejected.append((neighbor, reason))
    
    print(f"  Voisins valides : {len(valid_neighbors)}")
    print(f"  Rejetés         : {len(rejected)}")
    
    if rejected and len(rejected) <= 5:
        for notation, reason in rejected[:5]:
            print(f"    - {notation}: {reason}")
    
    # Évaluer voisins valides (fast mode, vectorisé)
    print(f"  Évaluation en cours...")
    
    candidates = [{'notation': n, 'source': f'hillclimb_{seed_notation}'} 
                  for n in valid_neighbors]
    
    # Batch eval
    neighbor_results = explorer.explore_batch(
        candidates,
        grid_size=(32, 32),
        steps=100,
        seed=42
    )
    
    # Évaluer seed aussi pour comparaison
    seed_result = explorer.evaluate_candidate(
        {'notation': seed_notation, 'source': 'seed'},
        grid_size=(32, 32),
        steps=100,
        seed=42
    )
    
    # Comparer
    seed_functional = seed_result.get('functional_score', 0)
    seed_robustness = seed_result.get('robustness_score', 0)
    seed_capacity = seed_result.get('capacity_score', 0)
    
    print(f"\n  Seed metrics :")
    print(f"    functional  : {seed_functional:.3f}")
    print(f"    robustness  : {seed_robustness:.3f}")
    print(f"    capacity    : {seed_capacity:.3f}")
    
    # Chercher meilleurs voisins
    better_functional = []
    better_robustness = []
    better_capacity = []
    
    for res in neighbor_results:
        if 'error' in res:
            continue
        
        func = res.get('functional_score', 0)
        rob = res.get('robustness_score', 0)
        cap = res.get('capacity_score', 0)
        notation = res['notation']
        
        if func > seed_functional:
            better_functional.append((notation, func))
        if rob > seed_robustness:
            better_robustness.append((notation, rob))
        if cap > seed_capacity:
            better_capacity.append((notation, cap))
    
    print(f"\n  Voisins supérieurs :")
    print(f"    Functional  : {len(better_functional)}")
    print(f"    Robustness  : {len(better_robustness)}")
    print(f"    Capacity    : {len(better_capacity)}")
    
    if better_functional:
        print(f"\n  Top 3 functional :")
        for notation, score in sorted(better_functional, key=lambda x: -x[1])[:3]:
            print(f"    {notation:<15} : {score:.3f} (vs {seed_functional:.3f})")
    
    if better_robustness:
        print(f"\n  Top 3 robustness :")
        for notation, score in sorted(better_robustness, key=lambda x: -x[1])[:3]:
            print(f"    {notation:<15} : {score:.3f} (vs {seed_robustness:.3f})")
    
    # Sauvegarder résultats
    results.append({
        'seed': seed_notation,
        'seed_name': seed_name,
        'neighbors_generated': len(neighbors),
        'neighbors_valid': len(valid_neighbors),
        'neighbors_rejected': len(rejected),
        'seed_metrics': {
            'functional': seed_functional,
            'robustness': seed_robustness,
            'capacity': seed_capacity
        },
        'better_functional': len(better_functional),
        'better_robustness': len(better_robustness),
        'better_capacity': len(better_capacity),
        'top_functional': better_functional[:3] if better_functional else [],
        'top_robustness': better_robustness[:3] if better_robustness else []
    })

# Sauvegarder rapport
output_file = Path("results") / "hillclimb_v3_report.json"
with open(output_file, 'w') as f:
    json.dump({
        'meta': {
            'date': datetime.now().isoformat(),
            'seeds': [s[0] for s in SEEDS],
            'strategy': 'local_mutations_radius_1'
        },
        'results': results
    }, f, indent=2)

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)

total_better = sum(r['better_functional'] + r['better_robustness'] + r['better_capacity'] 
                   for r in results)

if total_better == 0:
    print("\nAucune amélioration trouvée.")
    print("Les 3 cerveaux classiques sont des optimums locaux.")
else:
    print(f"\n{total_better} voisins supérieurs trouvés.")
    print("À valider sur stress-tests complets (multi-grilles, multi-bruits).")

print(f"\nRésultats sauvegardés : {output_file}")
print("=" * 80)




