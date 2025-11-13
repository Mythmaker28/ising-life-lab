"""
Script d'analyse approfondie des 3 cerveaux validés.

Objectif : Caractériser précisément B3/S23, B36/S23, B34/S34
avec données brain_scan_v2_4.json + tests complémentaires ciblés.
"""

import json
import numpy as np
from pathlib import Path

# Charger données brain scan
results_dir = Path("results")
data = json.load(open(results_dir / "brain_scan_v2_4.json"))
analysis = json.load(open(results_dir / "brain_scan_v2_4_analysis.json"))

# Les 3 vrais cerveaux (après retrait Replicator)
BRAINS = ["B3/S23", "B36/S23", "B34/S34"]

print("=" * 80)
print("ANALYSE APPROFONDIE DES 3 CERVEAUX VALIDÉS")
print("=" * 80)
print()

for rule in BRAINS:
    print(f"\n### {rule}")
    print("-" * 60)
    
    # Données stress-test
    stress = data[rule]
    
    # Stabilité multi-échelles
    by_size = stress["by_grid_size"]
    print(f"Stabilité multi-échelles :")
    for size_key in ["32x32", "64x64", "128x128"]:
        s = by_size[size_key]
        print(f"  {size_key:>7} : stability {s['stability_rate']:.2f}, density {s['avg_final_density']:.4f}")
    
    # Robustesse au bruit
    by_noise = stress["by_noise_level"]
    print(f"\nRobustesse au bruit (avg_recall) :")
    for noise_key in ["noise_0.00", "noise_0.10", "noise_0.20", "noise_0.30", "noise_0.40"]:
        n = by_noise[noise_key]
        print(f"  Bruit {n['noise_level']*100:>3.0f}% : recall {n['avg_recall']:.3f} ± {n['std_recall']:.3f}")
    
    # Métriques agrégées
    summary = stress["summary"]
    print(f"\nMétriques agrégées :")
    print(f"  Stability avg sizes : {summary['avg_stability_across_sizes']:.3f}")
    print(f"  Robustness score    : {summary['robustness_score']:.3f}")
    
    # Score cerveau
    brain_profile = analysis["brain_analysis"][rule]
    print(f"\nScore cerveau : {brain_profile['score']}/{brain_profile['max_score']}")
    print(f"Criteres valides :")
    for k, v in brain_profile['criteria'].items():
        print(f"  {k:>12} : {'[OK]' if v else '[NO]'}")
    print(f"Spécialisation : {brain_profile['specialization']}")

print("\n" + "=" * 80)
print("COMPARAISON DIRECTE")
print("=" * 80)

# Tableau comparatif
print(f"\n{'Métrique':<25} | {'B3/S23':>10} | {'B36/S23':>10} | {'B34/S34':>10}")
print("-" * 75)

for metric_name, metric_key in [
    ("Stability (multi-scale)", "stability"),
    ("Robustness (bruit 40%)", "robustness"),
    ("Capacity proxy", "capacity_proxy"),
    ("Functional score", "functional")
]:
    vals = [analysis["brain_analysis"][r]["metrics"][metric_key] for r in BRAINS]
    print(f"{metric_name:<25} | {vals[0]:>10.3f} | {vals[1]:>10.3f} | {vals[2]:>10.3f}")

# Identifier champion par métrique
print("\n" + "=" * 80)
print("CHAMPIONS PAR MÉTRIQUE")
print("=" * 80)

metrics = ["stability", "robustness", "capacity_proxy", "functional"]
for metric in metrics:
    vals = [(r, analysis["brain_analysis"][r]["metrics"][metric]) for r in BRAINS]
    champion = max(vals, key=lambda x: x[1])
    print(f"{metric:>15} : {champion[0]} ({champion[1]:.3f})")

# Détecter profils spécialisés
print("\n" + "=" * 80)
print("RÔLES INFÉRÉS")
print("=" * 80)

for rule in BRAINS:
    metrics = analysis["brain_analysis"][rule]["metrics"]
    stab = metrics["stability"]
    rob = metrics["robustness"]
    cap = metrics["capacity_proxy"]
    
    # Inférence rôle
    if stab >= 0.70 and rob < 0.35:
        role = "Structure & Compute (stable, fragile au bruit)"
    elif rob >= 0.40 and stab >= 0.60:
        role = "Robust Front-End (résiste bruit, stable)"
    elif stab >= 0.70 and rob >= 0.30:
        role = "Replication / Backup (stable, propagation)"
    else:
        role = "Generic (profil mixte)"
    
    print(f"{rule:>10} => {role}")
    print(f"           (stability {stab:.2f}, robustness {rob:.2f}, capacity {cap:.2f})")

print("\n" + "=" * 80)
print("ANALYSE TERMINÉE")
print("=" * 80)

