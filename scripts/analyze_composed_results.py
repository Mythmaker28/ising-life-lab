"""Analyse résultats architectures composées v3."""

import json
import numpy as np

data = json.load(open("results/composed_architectures_v3.json"))

print("=" * 80)
print("RÉSULTATS ARCHITECTURES COMPOSÉES")
print("=" * 80)
print()

results = data['results']

# Classement
sorted_results = sorted(results, key=lambda x: x['global_avg_recall'], reverse=True)

print("Classement par recall global :")
print("-" * 80)
for i, r in enumerate(sorted_results, 1):
    name = r['architecture']
    recall = r['global_avg_recall']
    # Densité moyenne sur tous bruits
    densities = [r['by_noise'][k]['avg_final_density'] for k in r['by_noise']]
    avg_density = np.mean(densities)
    print(f"{i}. {name:<40} : recall {recall:.3f}, density {avg_density:.3f}")

print("\n" + "=" * 80)
print("ANALYSE")
print("=" * 80)

# Baselines
baselines = [r for r in results if 'Single_' in r['architecture']]
composed = [r for r in results if 'Single_' not in r['architecture']]

best_baseline = max(baselines, key=lambda x: x['global_avg_recall'])
best_composed = max(composed, key=lambda x: x['global_avg_recall'])

print(f"\nMeilleure baseline : {best_baseline['architecture']}")
print(f"  Recall : {best_baseline['global_avg_recall']:.3f}")

print(f"\nMeilleure composée : {best_composed['architecture']}")
print(f"  Recall : {best_composed['global_avg_recall']:.3f}")

gain = best_composed['global_avg_recall'] - best_baseline['global_avg_recall']
gain_pct = (gain / best_baseline['global_avg_recall']) * 100

print(f"\nGain absolu : {gain:+.4f}")
print(f"Gain relatif : {gain_pct:+.2f}%")

if abs(gain) < 0.01:
    print("\nVERDICT : Pas de gain significatif (<1%)")
    print("Les architectures composées n'apportent RIEN vs single rules.")
elif gain > 0.01:
    print(f"\nVERDICT : Gain marginal (+{gain_pct:.1f}%)")
    print("À valider sur plus de runs et critères (vitesse, stabilité).")
else:
    print(f"\nVERDICT : PERTE (-{abs(gain_pct):.1f}%)")
    print("Architectures composées dégradent la performance.")

print("\n" + "=" * 80)
print("CONCLUSION HONNÊTE")
print("=" * 80)
print("""
Les 3 architectures testées :
- Pipeline B34/S34 → B3/S23
- Alternance B3/S23/B36/S23
- Ensemble voting

N'apportent AUCUN gain mesurable vs single rules.

Recall ≈ 0.66 pour toutes (Life, HighLife, pipeline, alternance, ensemble).

Hypothèse : Sur grilles 64×64 avec 100 steps, les 3 cerveaux convergent
vers attracteurs similaires. La composition n'ajoute rien.

Pistes à tester :
1. Grilles plus grandes (128×128, 256×256) pour voir émergence
2. Steps plus longs (200-500) pour dynamiques complexes
3. Tasks spécifiques (pas juste "recall") : pattern transport, compute
""")




