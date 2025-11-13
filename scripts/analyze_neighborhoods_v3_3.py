"""Analyse approfondie des résultats exploration voisinage v3.3"""

import json
from pathlib import Path
from collections import defaultdict

# Charger résultats
with open('results/brain_neighborhoods_v3_3.json', 'r') as f:
    data = json.load(f)

print("="*80)
print("DEEP ANALYSIS — NEIGHBORHOOD EXPLORATION v3.3")
print("="*80)

# Extraire tous candidats
all_candidates = []
for exploration in data['explorations']:
    all_candidates.extend(exploration['candidates'])

print(f"\nTotal candidates: {len(all_candidates)}")

# Grouper par métriques intéressantes
high_functional = [c for c in all_candidates if c['summary']['avg_functional'] > 0.05]
high_life = [c for c in all_candidates if c['summary']['life_capacity_score'] >= 0.70]
high_robust = [c for c in all_candidates if c['summary']['avg_robustness'] > 0.25]

print(f"\nCANDIDATES WITH HIGH METRICS:")
print(f"  High functional (>0.05)      : {len(high_functional)}")
print(f"  High life_capacity (>=0.70)  : {len(high_life)}")
print(f"  High robustness (>0.25)      : {len(high_robust)}")

# Top par functional_score
print(f"\n{'='*80}")
print("TOP 20 BY FUNCTIONAL SCORE")
print(f"{'='*80}")
candidates_by_func = sorted(all_candidates, key=lambda c: c['summary']['avg_functional'], reverse=True)

print(f"{'#':3s} {'Notation':15s} {'Functional':11s} {'Life':7s} {'Robust':7s} {'Seed'}")
print("-"*80)

for i, cand in enumerate(candidates_by_func[:20]):
    notation = cand['notation']
    func = cand['summary']['avg_functional']
    life = cand['summary']['life_capacity_score']
    rob = cand['summary']['avg_robustness']
    
    # Identifier seed d'origine
    seed = "?"
    for exp in data['explorations']:
        if cand in exp['candidates']:
            seed = exp['seed']['notation']
            break
    
    print(f"{i+1:3d} {notation:15s} {func:11.3f} {life:7.3f} {rob:7.3f} {seed}")

# Identifier règles VRAIMENT distinctes des 4 cerveaux
print(f"\n{'='*80}")
print("DISTINCT RULES (functional > 0 AND not in original 4)")
print(f"{'='*80}")

original_4 = ['B3/S23', 'B36/S23', 'B34/S34', 'B3/S234']
distinct_rules = [
    c for c in all_candidates 
    if c['summary']['avg_functional'] > 0.05 and c['notation'] not in original_4
]

print(f"Found {len(distinct_rules)} distinct promising rules\n")

for i, cand in enumerate(sorted(distinct_rules, key=lambda c: c['summary']['avg_functional'], reverse=True)):
    notation = cand['notation']
    func = cand['summary']['avg_functional']
    life = cand['summary']['life_capacity_score']
    rob = cand['summary']['avg_robustness']
    
    print(f"{i+1}. {notation}")
    print(f"   Functional: {func:.3f}")
    print(f"   Life capacity: {life:.3f}")
    print(f"   Robustness: {rob:.3f}")
    
    # Détails life patterns
    life_patterns = cand['life_capacity']['patterns']
    survivors = [name for name, info in life_patterns.items() if info['survived']]
    print(f"   Patterns surviving: {', '.join(survivors)}")
    print()

# Analyse par famille
print(f"{'='*80}")
print("PATTERNS ANALYSIS")
print(f"{'='*80}")

# Regrouper par born
born_groups = defaultdict(list)
for cand in all_candidates:
    born_str = ''.join(map(str, cand['born']))
    born_groups[born_str].append(cand)

print(f"\nRules by Born value (top 5):")
for born, rules in sorted(born_groups.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
    avg_life = sum(r['summary']['life_capacity_score'] for r in rules) / len(rules)
    avg_func = sum(r['summary']['avg_functional'] for r in rules) / len(rules)
    print(f"  B{born}: {len(rules)} rules, avg_life={avg_life:.3f}, avg_func={avg_func:.3f}")

# Regrouper par survive
survive_groups = defaultdict(list)
for cand in all_candidates:
    survive_str = ''.join(map(str, cand['survive']))
    survive_groups[survive_str].append(cand)

print(f"\nRules by Survive value (top 5):")
for survive, rules in sorted(survive_groups.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
    avg_life = sum(r['summary']['life_capacity_score'] for r in rules) / len(rules)
    avg_func = sum(r['summary']['avg_functional'] for r in rules) / len(rules)
    print(f"  S{survive}: {len(rules)} rules, avg_life={avg_life:.3f}, avg_func={avg_func:.3f}")

print(f"\n{'='*80}")

