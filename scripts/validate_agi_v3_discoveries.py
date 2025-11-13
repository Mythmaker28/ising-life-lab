"""
Validation découvertes AGI v3 (20 itérations vectorisées).

Vérifier si les nouveaux promus sont des quasi-death rules.
"""

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from isinglab.rules import load_hof_rules
from isinglab.core.ca_vectorized import evolve_ca_vectorized
from isinglab.core.rule_ops import parse_notation

# Nouveaux promus (session v3)
NEW_RULES = [
    "B8/S0268",
    "B8/S136",
    "B45/S34",
    "B8/S0568",
    "B456/S3",
    "B45/S37",
    "B018/S1236",  # Déjà connue
    "B38/S068",
    "B8/S3"
]

print("=" * 80)
print("VALIDATION DÉCOUVERTES AGI v3 (VECTORISÉ)")
print("=" * 80)
print()

for notation in NEW_RULES:
    print(f"### {notation}")
    print("-" * 60)
    
    born, survive = parse_notation(notation)
    
    # Test simple : 2 runs, grid 32×32, 100 steps
    densities = []
    
    for seed in [42, 123]:
        np.random.seed(seed)
        grid = (np.random.rand(32, 32) < 0.3).astype(int)
        
        grid_final = evolve_ca_vectorized(grid, set(born), set(survive), 100)
        density = grid_final.mean()
        densities.append(density)
    
    avg_density = np.mean(densities)
    std_density = np.std(densities)
    
    # Verdict
    if avg_density < 0.05:
        verdict = "ARTEFACT : Quasi-death (density < 0.05)"
    elif avg_density > 0.95:
        verdict = "ARTEFACT : Saturation (density > 0.95)"
    elif avg_density < 0.10:
        verdict = "SUSPECT : Convergence sparse (verifier structures)"
    elif avg_density > 0.90:
        verdict = "SUSPECT : Convergence dense"
    else:
        verdict = "VALIDE : Densité non-triviale"
    
    print(f"  Densities : {densities[0]:.3f}, {densities[1]:.3f}")
    print(f"  Moyenne   : {avg_density:.3f} ± {std_density:.3f}")
    print(f"  Verdict   : {verdict}")
    print()

print("=" * 80)
print("COMPARAISON AVEC 3 CERVEAUX")
print("=" * 80)

benchmarks = {
    'B3/S23': 0.03,
    'B36/S23': 0.03,
    'B34/S34': 0.10
}

for name, density in benchmarks.items():
    print(f"  {name:<10} : density {density:.3f} (structures riches connues)")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print("Si majorité < 0.05 => quasi-death rules persistent")
print("Si majorité 0.05-0.50 => découvertes légitimes")
print("=" * 80)




