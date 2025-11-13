"""Run AGI v3 Clean — Pipeline Découverte avec Filtres Durs

Configuration :
- Vectorisation activée
- Filtres durs anti-trivialité (filters.py)
- Fast mode (grilles 16×16, évaluations réduites)
- Logs détaillés + JSON recap

Objectif :
- Montrer émergence candidats non-triviaux
- Pas de flood death-rules
- HoF propre avec profils exploitables
"""

import json
import sys
from pathlib import Path
from datetime import datetime

from isinglab.closed_loop_agi_v3_fast import ClosedLoopAGIv3


def main():
    """
    Lance AGI v3 avec configuration propre.
    """
    print("=" * 80)
    print("CLOSED LOOP AGI v3 — CLEAN RUN")
    print("=" * 80)
    print("Configuration :")
    print("  - Vectorisation : ON")
    print("  - Filtres durs  : ON (apply_hard_filters)")
    print("  - Mode          : Fast (16×16, éval réduite)")
    print("  - Iterations    : 20")
    print("  - Batch size    : 4")
    print("  - Strategy      : mixed (exploration + exploitation)")
    print("=" * 80)
    print()
    
    # Configuration
    config = {
        'evaluation_seed': 42,
        'hof_max_size': 25,
        'adaptive_thresholds': True,
        'hof_percentiles': {
            'composite_min': 80,        # Seuil HoF ajusté
            'memory_score_min_abs': 0.01,
            'edge_score_min_abs': 0.05,
            'entropy_min_abs': 0.0
        },
        'diversity_threshold': 2,
        # Filtres anti-trivialité (légers, complémentaires aux hard filters)
        'density_min': 0.05,
        'density_max': 0.95,
        'richness_min': 0.05
    }
    
    # Initialiser AGI v3
    agi = ClosedLoopAGIv3(config=config)
    
    # Lancer découverte
    try:
        agi.discover_rules(
            num_iterations=5,  # Réduit pour démo
            batch_size=4,
            strategy='mixed',
            grid_size=(16, 16),
            steps=50
        )
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Sauvegarde en cours...")
        agi.aggregator.save_memory()
        agi.aggregator.save_hof()
        print("[DONE] Sauvegarde complète.")
        sys.exit(0)
    
    # Analyse HoF
    print("\n" + "=" * 80)
    print("HALL OF FAME — ANALYSE")
    print("=" * 80)
    
    hof_rules = agi.aggregator.hof_rules
    
    if not hof_rules:
        print("HoF vide — Aucune règle promue.")
        return
    
    print(f"Nombre de règles promues : {len(hof_rules)}")
    print()
    
    # Trier par functional_score
    hof_sorted = sorted(
        hof_rules,
        key=lambda r: r.get('functional_score', 0),
        reverse=True
    )
    
    # Top 10
    print("TOP 10 RULES (functional_score)")
    print("-" * 80)
    print(f"{'#':3s} {'Notation':12s} {'Func':6s} {'Cap':6s} {'Rob':6s} {'Basin':6s} {'Trivial':8s}")
    print("-" * 80)
    
    for i, rule in enumerate(hof_sorted[:10]):
        notation = rule.get('notation', 'N/A')
        func = rule.get('functional_score', 0)
        cap = rule.get('capacity_score', 0)
        rob = rule.get('robustness_score', 0)
        basin = rule.get('basin_score', 0)
        trivial = "YES" if rule.get('trivial', False) else "NO"
        
        print(f"{i+1:3d} {notation:12s} {func:6.3f} {cap:6.3f} {rob:6.3f} {basin:6.3f} {trivial:8s}")
    
    # Statistiques trivialité
    n_trivial = sum(1 for r in hof_rules if r.get('trivial', False))
    n_hard_filtered = sum(1 for r in agi.meta_memory if 'Hard filter' in r.get('trivial_reason', ''))
    
    print()
    print("STATISTIQUES")
    print("-" * 80)
    print(f"  Total mémoire       : {len(agi.meta_memory)} rules")
    print(f"  HoF                 : {len(hof_rules)} rules")
    print(f"  Trivial (soft)      : {n_trivial} rules in HoF")
    print(f"  Hard filtered       : {n_hard_filtered} rules (bloquées avant éval complète)")
    
    # Profils
    from collections import Counter
    profiles = Counter(r.get('profile', 'unknown') for r in hof_rules if not r.get('trivial', False))
    
    if profiles:
        print()
        print("PROFILS (non-trivial HoF)")
        print("-" * 80)
        for profile, count in profiles.most_common():
            print(f"  {profile:20s} : {count} rules")
    
    # Sauvegarder récap JSON
    output_file = Path('results/agi_v3_clean_report.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    recap = {
        'timestamp': datetime.now().isoformat(),
        'config': config,
        'iterations': 20,
        'batch_size': 4,
        'strategy': 'mixed',
        'total_memory': len(agi.meta_memory),
        'hof_size': len(hof_rules),
        'n_trivial_in_hof': n_trivial,
        'n_hard_filtered': n_hard_filtered,
        'top_10_rules': [
            {
                'rank': i+1,
                'notation': r.get('notation'),
                'functional_score': r.get('functional_score', 0),
                'capacity_score': r.get('capacity_score', 0),
                'robustness_score': r.get('robustness_score', 0),
                'basin_score': r.get('basin_score', 0),
                'trivial': r.get('trivial', False),
                'trivial_reason': r.get('trivial_reason', '')
            }
            for i, r in enumerate(hof_sorted[:10])
        ],
        'profiles': dict(profiles)
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(recap, f, indent=2)
    
    print()
    print(f"Rapport sauvegardé : {output_file}")
    print("=" * 80)


if __name__ == '__main__':
    main()

