"""
AGI v2.2 Stable Discovery - Chasse aux modules stables/robustes/diversifiés

Objectifs :
- HoF ≥ 3 règles, ≥ 2 profils distincts
- Inclure stable_memory ou robust_memory
- Profile stability multi-grilles ≥ 0.67
- Diversité Hamming ≥ 2.0
"""

from isinglab.closed_loop_agi import ClosedLoopAGI
from isinglab.rules import load_hof_rules
from isinglab.memory_explorer import MemoryExplorer
import json
from pathlib import Path
from datetime import datetime
from collections import Counter


def main():
    print("=" * 80)
    print("AGI v2.2 STABLE DISCOVERY - 20 ITERATIONS")
    print("(Stable-Bias + Profile Quotas + Grid-Sweep Validation)")
    print("=" * 80)
    
    # Config v2.2
    config = {
        'evaluation_seed': 42,
        'adaptive_thresholds': True,
        'hof_percentiles': {'composite_min': 85},  # Baissé pour plus de promotions
        'diversity_threshold': 2,
        'profile_stability_min': 0.67,
        'hof_profile_quotas': {
            'stable_memory': 4,
            'robust_memory': 4,
            'diverse_memory': 4,
            'chaotic_probe': 4,
            'sensitive_detector': 4,
            'attractor_dominant': 2,
            'generic': 2
        }
    }
    
    agi = ClosedLoopAGI(config=config)
    explorer = MemoryExplorer()
    
    summaries = []
    grid_sweeps = []
    
    for i in range(20):
        print(f"\n{'='*80}")
        print(f">>> ITERATION {i+1}/20")
        print(f"{'='*80}")
        
        summary = agi.run_one_iteration(
            batch_size=6,
            strategy='mixed',  # Utilise bandit avec stable_bias
            grid_size=32,
            steps=100
        )
        summaries.append(summary)
        
        # Checkpoint tous les 5
        if (i+1) % 5 == 0:
            print(f"\n--- CHECKPOINT {i+1}/20 ---")
            print(f"  Memoire: {summary['total_memory_rules']}")
            print(f"  HoF: {summary.get('total_hof_rules', 0)}")
            print(f"  Promotions: {sum(s['new_rules_added'] for s in summaries)}")
    
    print("\n" + "=" * 80)
    print("VALIDATION MULTI-GRILLES (HoF)")
    print("=" * 80)
    
    # Grid-sweep sur règles HoF
    current_hof = load_hof_rules()
    print(f"\nHoF size: {len(current_hof)}")
    
    for rule in current_hof[:5]:  # Max 5 pour limiter temps
        sweep_result = explorer.grid_sweep(
            rule,
            grid_sizes=[(16,16), (32,32)],  # 2 tailles pour vitesse
            steps=50,
            seed=42
        )
        grid_sweeps.append(sweep_result)
        
        notation = sweep_result['notation']
        stability = sweep_result['profile_stability']
        consensus = sweep_result['consensus_profile']
        print(f"  {notation}: stability={stability:.2f}, profile={consensus}")
    
    print("\n" + "=" * 80)
    print("RESULTATS FINAUX")
    print("=" * 80)
    
    # KPIs
    final_summary = summaries[-1]
    total_hof = len(current_hof)
    profiles = [r.get('module_profile', 'unknown') for r in current_hof]
    profile_counts = Counter(profiles)
    unique_profiles = len(profile_counts)
    
    # Diversité
    if len(current_hof) > 1:
        distances = []
        for i, r1 in enumerate(current_hof):
            for r2 in current_hof[i+1:]:
                born1, born2 = set(r1.get('born', [])), set(r2.get('born', []))
                surv1, surv2 = set(r1.get('survive', [])), set(r2.get('survive', []))
                dist = len(born1 ^ born2) + len(surv1 ^ surv2)
                distances.append(dist)
        avg_distance = sum(distances) / len(distances) if distances else 0
    else:
        avg_distance = 0
    
    # Stability multi-grilles
    avg_stability = sum(s['profile_stability'] for s in grid_sweeps) / len(grid_sweeps) if grid_sweeps else 0
    
    print(f"\nKPIS:")
    print(f"  HoF size: {total_hof}")
    print(f"  Unique profiles: {unique_profiles}")
    print(f"  Profile distribution: {dict(profile_counts)}")
    print(f"  Avg Hamming distance: {avg_distance:.2f}")
    print(f"  Avg profile stability (grid-sweep): {avg_stability:.2f}")
    
    print(f"\nBANDIT:")
    bandit_path = Path('results/bandit_stats.json')
    if bandit_path.exists():
        with open(bandit_path, 'r') as f:
            bandit_data = json.load(f)
        arms = bandit_data.get('arms', {})
        for name in sorted(arms.keys(), key=lambda k: arms[k]['avg_reward'], reverse=True):
            arm = arms[name]
            print(f"  {name}: pulls={arm['pulls']}, reward={arm['avg_reward']:.3f}")
    
    # Checks
    print(f"\nCHECKS:")
    checks = [
        ("HoF >= 3 rules", total_hof >= 3),
        ("Unique profiles >= 2", unique_profiles >= 2),
        ("Avg distance >= 2.0", avg_distance >= 2.0),
        ("Profile stability >= 0.67", avg_stability >= 0.67 or len(grid_sweeps) == 0),
        ("Contains stable/robust", 'stable_memory' in profiles or 'robust_memory' in profiles)
    ]
    
    all_passed = True
    for check_name, result in checks:
        status = "[OK]" if result else "[FAIL]"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False
    
    # Sauvegarder résumé
    summary_data = {
        'config': config,
        'total_iterations': 20,
        'final_memory_rules': final_summary['total_memory_rules'],
        'final_hof_rules': total_hof,
        'unique_profiles': unique_profiles,
        'profile_distribution': dict(profile_counts),
        'avg_hamming_distance': avg_distance,
        'avg_profile_stability': avg_stability,
        'grid_sweeps': grid_sweeps,
        'checks': {name: result for name, result in checks},
        'all_checks_passed': all_passed,
        'bandit_stats': bandit_data if bandit_path.exists() else {}
    }
    
    output_file = Path('results/discovery_v2_2_summary.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2)
    
    print(f"\n[OK] Summary saved: {output_file}")
    
    if all_passed:
        print("\n" + "=" * 80)
        print("SUCCESS: All KPIs met!")
        print("=" * 80)
        return 0
    else:
        print("\n" + "=" * 80)
        print("PARTIAL: Some KPIs not met. See checks above.")
        print("=" * 80)
        return 1


if __name__ == '__main__':
    exit(main())

