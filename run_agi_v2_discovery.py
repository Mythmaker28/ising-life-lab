"""
AGI v2.0 Discovery Script - 20 itérations avec seuils adaptatifs + diversité + bandit

Ce script démontre les capacités v2.0 :
- Seuils adaptatifs basés sur percentiles
- Filtre de diversité (distance de Hamming)
- Multi-armed bandit UCB1 pour exploration intelligente
- Export enrichi avec diversity_signature et tags

Résultats attendus après 20 itérations :
- HoF > 1 règle
- Plusieurs règles différentes (diversité)
- Bandit converge vers la meilleure stratégie
"""

from isinglab.closed_loop_agi import ClosedLoopAGI
from isinglab.rules import load_hof_rules
import json
from pathlib import Path


def main():
    print("\n" + "=" * 80)
    print("AGI v2.0 DISCOVERY - 20 ITERATIONS")
    print("(Adaptive Thresholds + Diversity + Multi-Armed Bandit)")
    print("=" * 80)
    
    # Configuration v2.0
    config = {
        'evaluation_seed': 42,
        'adaptive_thresholds': True,
        'hof_percentiles': {
            'composite_min': 85,  # Top 15% au lieu de 10% pour plus de promotions
            'memory_score_min_abs': 0.01,
            'edge_score_min_abs': 0.05,
            'entropy_min_abs': 0.0
        },
        'diversity_threshold': 2,  # Distance Hamming minimale
    }
    
    agi = ClosedLoopAGI(config=config)
    
    summaries = []
    hof_diversity = []
    
    for i in range(20):
        print(f"\n\n{'='*80}")
        print(f">>> ITERATION {i+1}/20")
        print(f"{'='*80}")
        
        summary = agi.run_one_iteration(
            batch_size=8,  # Augmenté pour plus de candidats
            strategy='mixed',  # Utilise le bandit
            grid_size=32,
            steps=100
        )
        summaries.append(summary)
        
        # Tracking de la diversité du HoF
        current_hof = load_hof_rules()
        hof_diversity.append({
            'iteration': i+1,
            'hof_size': len(current_hof),
            'unique_signatures': len(set([
                f"B{len(r.get('born', []))}/S{len(r.get('survive', []))}" 
                for r in current_hof
            ]))
        })
        
        # Afficher progression tous les 5 itérations
        if (i+1) % 5 == 0:
            print(f"\n--- CHECKPOINT ITERATION {i+1} ---")
            print(f"  Total mémoire: {summary['total_memory_rules']}")
            print(f"  Total HoF: {summary.get('total_hof_rules', 0)}")
            print(f"  Promotions totales: {sum(s['new_rules_added'] for s in summaries)}")
    
    print("\n" + "=" * 80)
    print("RECAPITULATIF FINAL (20 ITERATIONS)")
    print("=" * 80)
    
    # Stats globales
    total_promotions = sum(s['new_rules_added'] for s in summaries)
    total_bootstrap = sum(s.get('bootstrapped', 0) for s in summaries)
    final_memory = summaries[-1]['total_memory_rules']
    final_hof = summaries[-1].get('total_hof_rules', 0)
    
    print(f"\nMÉMOIRE & HoF:")
    print(f"  - Mémoire finale: {final_memory} règles")
    print(f"  - HoF final: {final_hof} règles")
    print(f"  - Promotions (non-bootstrap): {total_promotions}")
    print(f"  - Bootstrap: {total_bootstrap}")
    
    # Diversité
    print(f"\nDIVERSITÉ:")
    final_div = hof_diversity[-1]
    print(f"  - Signatures uniques: {final_div['unique_signatures']}/{final_div['hof_size']}")
    
    # Bandit stats
    if Path('results/bandit_stats.json').exists():
        with open('results/bandit_stats.json', 'r') as f:
            bandit_data = json.load(f)
        
        print(f"\nBANDIT (Multi-Armed):")
        print(f"  Total pulls: {bandit_data['total_pulls']}")
        arms = bandit_data.get('arms', {})
        for arm_name in sorted(arms.keys(), key=lambda k: arms[k]['avg_reward'], reverse=True):
            arm = arms[arm_name]
            print(f"  - {arm_name}: pulls={arm['pulls']}, avg_reward={arm['avg_reward']:.3f}")
    
    # Vérifications
    print(f"\nVÉRIFICATIONS:")
    checks = []
    checks.append(("Mémoire croissante", final_memory > summaries[0]['total_memory_rules']))
    checks.append(("HoF non vide", final_hof > 0))
    checks.append(("Au moins 1 promotion non-bootstrap", total_promotions > 0))
    checks.append(("Diversité > 50%", final_div['unique_signatures'] / max(final_div['hof_size'], 1) > 0.5))
    
    for check_name, result in checks:
        status = "[OK]" if result else "[FAIL]"
        print(f"  {status} {check_name}")
    
    # Export final
    print(f"\nEXPORT:")
    print(f"  Exécutez: python isinglab/export_memory_library.py")
    print(f"  Fichier généré: results/agi_export_hof.json")
    
    # Sauvegar der un récap
    recap_file = Path('results/agi_v2_discovery_recap.json')
    recap_file.parent.mkdir(parents=True, exist_ok=True)
    with open(recap_file, 'w', encoding='utf-8') as f:
        json.dump({
            'config': config,
            'total_iterations': 20,
            'final_memory_rules': final_memory,
            'final_hof_rules': final_hof,
            'total_promotions': total_promotions,
            'total_bootstrap': total_bootstrap,
            'diversity': hof_diversity[-1],
            'summaries': summaries[-5:]  # Dernières 5 itérations
        }, f, indent=2)
    
    print(f"  Récap sauvegardé: {recap_file}")
    
    print("\n" + "=" * 80)
    if all(check[1] for check in checks):
        print("SUCCESS: Tous les checks passent. AGI v2.0 opérationnel.")
    else:
        print("PARTIAL: Certains checks ont échoué. Voir ci-dessus.")
    print("=" * 80)


if __name__ == '__main__':
    main()

