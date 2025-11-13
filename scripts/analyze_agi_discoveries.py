"""
Analyse rapide des découvertes AGI (session interrompue).

Extrait et classe les règles intéressantes trouvées.
"""

import json
from pathlib import Path

# Charger meta_memory
meta_memory = json.load(open("results/meta_memory.json"))
rules = meta_memory["rules"]

print("=" * 80)
print("ANALYSE DÉCOUVERTES AGI (SESSION INTERROMPUE)")
print("=" * 80)
print(f"Total règles évaluées : {len(rules)}")
print()

# Filtrer règles intéressantes
# Critères : functional_score >= 0.40 OU robustness >= 0.60
interesting = []
for rule in rules:
    scores = rule.get('scores', {})
    functional = scores.get('functional_score', 0.0)
    robustness = scores.get('robustness_score', 0.0)
    capacity = scores.get('capacity_score', 0.0)
    
    # Critères cerveau potentiel
    if functional >= 0.40 or robustness >= 0.60 or capacity >= 0.50:
        interesting.append({
            'notation': rule['notation'],
            'functional': functional,
            'robustness': robustness,
            'capacity': capacity,
            'labels': rule.get('labels', [])
        })

print(f"Règles intéressantes (functional >= 0.40 OU robustness >= 0.60 OU capacity >= 0.50) : {len(interesting)}")
print()

# Trier par functional_score
interesting_sorted = sorted(interesting, key=lambda x: x['functional'], reverse=True)

print("TOP 20 PAR FUNCTIONAL SCORE :")
print("-" * 80)
for i, r in enumerate(interesting_sorted[:20], 1):
    hof = "[HoF]" if 'hof' in r['labels'] else "     "
    print(f"{i:>2}. {hof} {r['notation']:<15} | func {r['functional']:.3f} | rob {r['robustness']:.3f} | cap {r['capacity']:.3f}")

print("\n" + "=" * 80)
print("TOP 10 PAR ROBUSTNESS :")
print("-" * 80)
robust_sorted = sorted(interesting, key=lambda x: x['robustness'], reverse=True)
for i, r in enumerate(robust_sorted[:10], 1):
    hof = "[HoF]" if 'hof' in r['labels'] else "     "
    print(f"{i:>2}. {hof} {r['notation']:<15} | rob {r['robustness']:.3f} | func {r['functional']:.3f} | cap {r['capacity']:.3f}")

print("\n" + "=" * 80)
print("RÈGLES AVEC CAPACITY >= 0.50 :")
print("-" * 80)
high_capacity = [r for r in interesting if r['capacity'] >= 0.50]
if high_capacity:
    for r in sorted(high_capacity, key=lambda x: x['capacity'], reverse=True):
        hof = "[HoF]" if 'hof' in r['labels'] else "     "
        print(f"  {hof} {r['notation']:<15} | cap {r['capacity']:.3f} | func {r['functional']:.3f} | rob {r['robustness']:.3f}")
else:
    print("  Aucune règle avec capacity >= 0.50")

# HoF actuel
print("\n" + "=" * 80)
print("HALL OF FAME ACTUEL :")
print("-" * 80)
hof_rules = [r for r in rules if 'hof' in r.get('labels', [])]
print(f"Total HoF : {len(hof_rules)}")
for r in sorted(hof_rules, key=lambda x: x['scores'].get('functional_score', 0), reverse=True)[:15]:
    notation = r['notation']
    scores = r['scores']
    func = scores.get('functional_score', 0.0)
    rob = scores.get('robustness_score', 0.0)
    cap = scores.get('capacity_score', 0.0)
    print(f"  {notation:<15} | func {func:.3f} | rob {rob:.3f} | cap {cap:.3f}")

print("\n" + "=" * 80)
print("VERDICT RAPIDE")
print("=" * 80)

# Comparer avec les 3 cerveaux connus
B3S23_bench = {'functional': 0.289, 'robustness': 0.289, 'capacity': 0.733}
B34S34_bench = {'functional': 0.439, 'robustness': 0.439, 'capacity': 0.667}

best_func = interesting_sorted[0] if interesting_sorted else None
best_rob = robust_sorted[0] if robust_sorted else None

print("\nMeilleures découvertes AGI :")
if best_func:
    print(f"  Functional : {best_func['notation']} ({best_func['functional']:.3f})")
    if best_func['functional'] > B34S34_bench['functional']:
        print(f"    -> SURPASSE B34/S34 ({B34S34_bench['functional']:.3f}) !")
    else:
        print(f"    -> Inférieur à B34/S34 ({B34S34_bench['functional']:.3f})")

if best_rob:
    print(f"  Robustness : {best_rob['notation']} ({best_rob['robustness']:.3f})")
    if best_rob['robustness'] > B34S34_bench['robustness']:
        print(f"    -> SURPASSE B34/S34 ({B34S34_bench['robustness']:.3f}) !")
    else:
        print(f"    -> Inférieur à B34/S34 ({B34S34_bench['robustness']:.3f})")

if not high_capacity:
    print(f"  Capacity : Aucune règle >= 0.50 (B3/S23 = {B3S23_bench['capacity']:.3f})")

print("\n" + "=" * 80)
print("FIN ANALYSE")
print("=" * 80)

