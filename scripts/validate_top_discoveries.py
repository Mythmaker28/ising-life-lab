"""
Validation rapide des "top discoveries" AGI.

Teste si les règles avec scores parfaits sont réelles ou artefacts.
"""

import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from isinglab.core.rule_ops import parse_notation
from isinglab.memory_explorer import MemoryExplorer

# Top 5 règles suspectes (scores parfaits)
SUSPECTS = [
    "B38/S06",
    "B8/S136",
    "B58/S06",
    "B4/S13",
    "B4/S03"
]

print("=" * 80)
print("VALIDATION RÈGLES SUSPECTES (SCORES PARFAITS)")
print("=" * 80)
print()

explorer = MemoryExplorer()

for notation in SUSPECTS:
    print(f"\n### {notation}")
    print("-" * 60)
    
    born, survive = parse_notation(notation)
    
    # Test simple : grille aléatoire 32×32, 100 steps
    np.random.seed(42)
    grid = (np.random.rand(32, 32) < 0.3).astype(int)
    
    initial_density = grid.mean()
    
    # Évolution
    for _ in range(100):
        new_grid = np.zeros_like(grid)
        h, w = grid.shape
        for i in range(h):
            for j in range(w):
                neighbors = sum(grid[(i+di)%h, (j+dj)%w] 
                              for di in [-1,0,1] for dj in [-1,0,1] 
                              if not (di==0 and dj==0))
                if grid[i,j] == 1:
                    new_grid[i,j] = 1 if neighbors in survive else 0
                else:
                    new_grid[i,j] = 1 if neighbors in born else 0
        grid = new_grid
    
    final_density = grid.mean()
    
    # Diagnostics
    print(f"  Initial density : {initial_density:.3f}")
    print(f"  Final density   : {final_density:.3f}")
    
    # Détection artefacts
    if final_density == 0.0:
        verdict = "ARTEFACT : Death rule (tout meurt)"
    elif final_density == 1.0:
        verdict = "ARTEFACT : Saturation rule (tout vivant)"
    elif abs(final_density - initial_density) < 0.01:
        verdict = "Suspect : Densité stable (potentiel identity rule)"
    elif final_density < 0.05:
        verdict = "Suspect : Convergence quasi-vide"
    elif final_density > 0.95:
        verdict = "Suspect : Convergence quasi-saturée"
    else:
        verdict = "VALIDE : Comportement non-trivial"
    
    print(f"  Verdict         : {verdict}")
    
    # Test stabilité : 2ème run avec seed différent
    np.random.seed(123)
    grid2 = (np.random.rand(32, 32) < 0.3).astype(int)
    for _ in range(100):
        new_grid = np.zeros_like(grid2)
        h, w = grid2.shape
        for i in range(h):
            for j in range(w):
                neighbors = sum(grid2[(i+di)%h, (j+dj)%w] 
                              for di in [-1,0,1] for dj in [-1,0,1] 
                              if not (di==0 and dj==0))
                if grid2[i,j] == 1:
                    new_grid[i,j] = 1 if neighbors in survive else 0
                else:
                    new_grid[i,j] = 1 if neighbors in born else 0
        grid2 = new_grid
    
    final_density2 = grid2.mean()
    print(f"  Run 2 density   : {final_density2:.3f}")
    
    if abs(final_density - final_density2) < 0.01:
        print(f"  Stabilité       : Convergence cohérente")
    else:
        print(f"  Stabilité       : Comportement variable")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print()
print("Si majorité = artefacts → scores parfaits invalides")
print("Si majorité = valides   → vraies découvertes intéressantes")
print()
print("À comparer avec B3/S23 (density finale ~0.03) et B34/S34 (~0.10)")
print("=" * 80)

