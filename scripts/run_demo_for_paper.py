"""
Script pour générer les figures et résultats du notebook ATLAS_GEOMETRIC_CONTROL_DEMO
pour le papier arXiv.
"""

import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif
import matplotlib.pyplot as plt
from pathlib import Path

# Ising-Life-Lab modules
from isinglab.data_bridge import AtlasMapper
from isinglab.pipelines.holonomy_optimization import compare_geometric_vs_dynamic_robustness
from isinglab.data_bridge.cost_functions import compute_target_profile

# Configuration matplotlib
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10

print("[OK] Imports reussis")

# Charger l'Atlas Mapper
mapper = AtlasMapper(mode='mock')
SYSTEMS = ['NV-298K', 'C13-Pyruvate', 'RP-Cry4']

print("="*70)
print("CHARGEMENT DES SYSTÈMES")
print("="*70)

system_profiles = {}
for sys_id in SYSTEMS:
    profile = mapper.get_profile(sys_id)
    system_profiles[sys_id] = profile
    print(f"{sys_id}: T2={profile.t2_us:.1f}µs, T={profile.temperature_k:.0f}K")

# Paramètres baseline
BASELINE_RAMP_PARAMS = {
    'NV-298K': {
        'k_start': 0.5,
        'k_end': 0.85,
        'duration': 1.0,
        'annealing_start': 0.2,
        'annealing_end': 0.6
    },
    'C13-Pyruvate': {
        'k_start': 0.6,
        'k_end': 0.9,
        'duration': 1.0,
        'annealing_start': 0.15,
        'annealing_end': 0.5
    },
    'RP-Cry4': {
        'k_start': 0.3,
        'k_end': 0.7,
        'duration': 1.0,
        'annealing_start': 0.25,
        'annealing_end': 0.65
    }
}

# Exécuter comparaisons P3 vs P4
print("\n" + "="*70)
print("SIMULATIONS P3 vs P4")
print("="*70)

results = {}
for sys_id in SYSTEMS:
    print(f"\nProcessing {sys_id}...")
    
    result = compare_geometric_vs_dynamic_robustness(
        target_profile='uniform',
        atlas_profile=sys_id,
        best_ramp_params=BASELINE_RAMP_PARAMS[sys_id],
        noise_multiplier=2.0,
        n_trials=3,
        output_dir=f'results/atlas_geometric_demo/{sys_id}',
        seed=42,
        atlas_mapper=mapper
    )
    
    results[sys_id] = result
    print(f"[OK] {sys_id}: Winner={result['winner']}, Improvement={result['improvement']:.1f}%")

print("\n" + "="*70)
print("GÉNÉRATION DES FIGURES")
print("="*70)

# Créer le dossier figures
fig_dir = Path('figures/atlas_geometric_demo')
fig_dir.mkdir(parents=True, exist_ok=True)

# Figure 1: NV-298K P3 vs P4
sys_ref = 'NV-298K'
result_ref = results[sys_ref]

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

p3_cost = result_ref['p3_robustness_mean']
p4_cost = result_ref['p4_robustness_mean']
p3_std = result_ref['p3_robustness_std']
p4_std = result_ref['p4_robustness_std']

axes[0].bar(['P3 (Dynamic)', 'P4 (Geometric)'], [p3_cost, p4_cost], 
            yerr=[p3_std, p4_std], color=['#3498db', '#e74c3c'], 
            alpha=0.8, capsize=5, edgecolor='black')
axes[0].set_ylabel('Robustness Cost (lower = better)', fontsize=11)
axes[0].set_title(f'{sys_ref}: Noise Robustness', fontsize=12, fontweight='bold')
axes[0].grid(True, alpha=0.3, axis='y')
axes[0].set_ylim([0, max(p3_cost, p4_cost) * 1.3])

if result_ref['winner'] == 'P4':
    axes[0].text(1, p4_cost * 0.5, f"Winner\n+{result_ref['improvement']:.1f}%", 
                 ha='center', va='center', fontsize=11, fontweight='bold', color='white',
                 bbox=dict(boxstyle='round', facecolor='green', alpha=0.8))

var_p3 = result_ref['p3_stability_variance']
var_p4 = result_ref['p4_stability_variance']

axes[1].bar(['P3 (Dynamic)', 'P4 (Geometric)'], [var_p3, var_p4], 
            color=['#3498db', '#e74c3c'], alpha=0.8, edgecolor='black')
axes[1].set_ylabel('Var(r) final (lower = more stable)', fontsize=11)
axes[1].set_title(f'{sys_ref}: Stability under Noise', fontsize=12, fontweight='bold')
axes[1].grid(True, alpha=0.3, axis='y')
axes[1].set_ylim([0, max(var_p3, var_p4) * 1.3])

plt.tight_layout()
plt.savefig(fig_dir / 'figure1_nv298k_p3_vs_p4.png', dpi=300, bbox_inches='tight')
plt.close()
print("[OK] Figure 1 saved")

# Figure 2: Multi-system comparison
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

system_labels = []
p3_costs = []
p4_costs = []
p3_stds = []
p4_stds = []
improvements = []

for sys_id in SYSTEMS:
    res = results[sys_id]
    system_labels.append(sys_id)
    p3_costs.append(res['p3_robustness_mean'])
    p4_costs.append(res['p4_robustness_mean'])
    p3_stds.append(res['p3_robustness_std'])
    p4_stds.append(res['p4_robustness_std'])
    improvements.append(res['improvement'] if res['winner'] == 'P4' else -res['improvement'])

x = np.arange(len(SYSTEMS))
width = 0.35

bars1 = axes[0].bar(x - width/2, p3_costs, width, yerr=p3_stds, 
                     label='P3 (Dynamic)', color='#3498db', alpha=0.8, 
                     capsize=4, edgecolor='black')
bars2 = axes[0].bar(x + width/2, p4_costs, width, yerr=p4_stds, 
                     label='P4 (Geometric)', color='#e74c3c', alpha=0.8, 
                     capsize=4, edgecolor='black')

axes[0].set_ylabel('Robustness Cost', fontsize=11)
axes[0].set_title('Noise Robustness: P3 vs P4 by System', fontsize=12, fontweight='bold')
axes[0].set_xticks(x)
axes[0].set_xticklabels(system_labels, rotation=15, ha='right')
axes[0].legend(fontsize=10)
axes[0].grid(True, alpha=0.3, axis='y')

colors_improvement = ['green' if imp > 0 else 'orange' for imp in improvements]
axes[1].bar(system_labels, improvements, color=colors_improvement, alpha=0.8, edgecolor='black')
axes[1].axhline(0, color='black', linewidth=1, linestyle='--')
axes[1].set_ylabel('P4 Improvement over P3 (%)', fontsize=11)
axes[1].set_title('Robustness Gain with Geometric Control', fontsize=12, fontweight='bold')
axes[1].set_xticklabels(system_labels, rotation=15, ha='right')
axes[1].grid(True, alpha=0.3, axis='y')

for i, (sys, imp) in enumerate(zip(system_labels, improvements)):
    axes[1].text(i, imp + (2 if imp > 0 else -2), f"{imp:.1f}%", 
                 ha='center', va='bottom' if imp > 0 else 'top', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(fig_dir / 'figure2_multi_system_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
print("[OK] Figure 2 saved")

# Figure 3: System properties
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

t2_values = [system_profiles[sys].t2_us for sys in SYSTEMS]
axes[0, 0].barh(SYSTEMS, t2_values, color='#9b59b6', alpha=0.8, edgecolor='black')
axes[0, 0].set_xlabel('T2 (µs)', fontsize=11)
axes[0, 0].set_title('Coherence Time T2', fontsize=12, fontweight='bold')
axes[0, 0].grid(True, alpha=0.3, axis='x')
for i, val in enumerate(t2_values):
    axes[0, 0].text(val + max(t2_values)*0.02, i, f"{val:.1f} µs", 
                    va='center', fontsize=10, fontweight='bold')

temps = [system_profiles[sys].temperature_k for sys in SYSTEMS]
axes[0, 1].barh(SYSTEMS, temps, color='#e67e22', alpha=0.8, edgecolor='black')
axes[0, 1].set_xlabel('Temperature (K)', fontsize=11)
axes[0, 1].set_title('Operating Temperature', fontsize=12, fontweight='bold')
axes[0, 1].grid(True, alpha=0.3, axis='x')
for i, val in enumerate(temps):
    axes[0, 1].text(val + max(temps)*0.02, i, f"{val:.0f} K", 
                    va='center', fontsize=10, fontweight='bold')

noise_values = [system_profiles[sys].noise_level for sys in SYSTEMS]
axes[1, 0].barh(SYSTEMS, noise_values, color='#34495e', alpha=0.8, edgecolor='black')
axes[1, 0].set_xlabel('Noise Level', fontsize=11)
axes[1, 0].set_title('Intrinsic Noise', fontsize=12, fontweight='bold')
axes[1, 0].grid(True, alpha=0.3, axis='x')
for i, val in enumerate(noise_values):
    axes[1, 0].text(val + max(noise_values)*0.02, i, f"{val:.3f}", 
                    va='center', fontsize=10, fontweight='bold')

geometric_phases = [results[sys]['geometric_phase'] for sys in SYSTEMS]
axes[1, 1].barh(SYSTEMS, geometric_phases, color='#16a085', alpha=0.8, edgecolor='black')
axes[1, 1].set_xlabel('Geometric Phase (rad)', fontsize=11)
axes[1, 1].set_title('Berry Phase (P4 Trajectory)', fontsize=12, fontweight='bold')
axes[1, 1].grid(True, alpha=0.3, axis='x')
for i, val in enumerate(geometric_phases):
    axes[1, 1].text(val + max(geometric_phases)*0.02, i, f"{val:.3f} rad\n({val*180/np.pi:.1f}°)", 
                    va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(fig_dir / 'figure3_system_properties.png', dpi=300, bbox_inches='tight')
plt.close()
print("[OK] Figure 3 saved")

# Creer tableau CSV
table_data = []
for sys_id in SYSTEMS:
    res = results[sys_id]
    profile = system_profiles[sys_id]
    
    row = {
        'System': sys_id,
        'Type': profile.regime_notes.split(' - ')[0] if ' - ' in profile.regime_notes else 'Unknown',
        'T2_us': f"{profile.t2_us:.1f}",
        'Temperature_K': f"{profile.temperature_k:.0f}",
        'Noise': f"{profile.noise_level:.3f}",
        'P3_Robustness': f"{res['p3_robustness_mean']:.4f}",
        'P3_Robustness_Std': f"{res['p3_robustness_std']:.4f}",
        'P4_Robustness': f"{res['p4_robustness_mean']:.4f}",
        'P4_Robustness_Std': f"{res['p4_robustness_std']:.4f}",
        'Improvement_Percent': f"{res['improvement']:.1f}" if res['winner'] == 'P4' else f"-{res['improvement']:.1f}",
        'Winner': res['winner'],
        'Geometric_Phase_rad': f"{res['geometric_phase']:.3f}"
    }
    
    table_data.append(row)

df_results = pd.DataFrame(table_data)
csv_path = fig_dir / 'results_table.csv'
df_results.to_csv(csv_path, index=False)
print(f"[OK] Table saved: {csv_path}")

print("\n" + "="*70)
print("GENERATION TERMINEE")
print("="*70)
print(f"Figures: {fig_dir}")
print(f"  - figure1_nv298k_p3_vs_p4.png")
print(f"  - figure2_multi_system_comparison.png")
print(f"  - figure3_system_properties.png")
print(f"  - results_table.csv")

