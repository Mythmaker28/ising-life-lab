#!/usr/bin/env python3
"""
Script pour générer les figures principales P5 (publication)

Usage:
    python scripts/generate_p5_figures.py

Output:
    - results/figure_2a_histogram_gains.png
    - results/figure_2b_scatter_t2.png
    - results/figure_2c_boxplot_robustness.png
    - results/figure_2d_variance_stability.png
    - results/figure_2_composite_p5_results.png
    - results/figure_5_heatmap_atlas.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configuration
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11

def load_data():
    """Charge le CSV des résultats P5"""
    csv_path = Path('results/atlas_batch/ATLAS_CONTROL_STRATEGY_REPORT.csv')
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV non trouvé : {csv_path}")
    
    df = pd.read_csv(csv_path)
    print(f"[OK] Charge : {len(df)} configurations")
    print(f"   Systemes uniques : {df['system_id'].nunique()}")
    print(f"   Cibles : {df['target_phenomenology'].unique()}")
    
    return df

def generate_figure_2a(df, output_dir='results'):
    """Figure 2A : Histogramme des gains P4"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    mean_gain = df['robustness_gain_percent'].mean()
    
    ax.hist(df['robustness_gain_percent'], bins=30, edgecolor='black', 
            alpha=0.7, color='steelblue')
    ax.axvline(mean_gain, color='red', linestyle='--', linewidth=2, 
               label=f'Moyenne = {mean_gain:.1f}%')
    
    ax.set_xlabel('Amélioration P4 vs P3 (%)', fontsize=14)
    ax.set_ylabel('Nombre de configurations', fontsize=14)
    ax.set_title('Distribution des Gains P4 (360 configurations)', 
                 fontsize=16, weight='bold')
    ax.legend(fontsize=12)
    ax.grid(alpha=0.3)
    
    output_path = Path(output_dir) / 'figure_2a_histogram_gains.png'
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"[OK] Figure 2A : {output_path}")
    return output_path

def generate_figure_2b(df, output_dir='results'):
    """Figure 2B : Scatter T2 vs amélioration"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    mean_gain = df['robustness_gain_percent'].mean()
    
    for target in df['target_phenomenology'].unique():
        mask = df['target_phenomenology'] == target
        ax.scatter(df[mask]['t2_us'], df[mask]['robustness_gain_percent'], 
                   alpha=0.6, s=50, label=target)
    
    ax.axhline(13.9, color='gray', linestyle=':', linewidth=2, 
               label='Prédiction initiale (+13.9%)')
    ax.axhline(mean_gain, color='red', linestyle='--', linewidth=2, 
               label=f'Observation (+{mean_gain:.1f}%)')
    
    ax.set_xlabel('T2 (µs)', fontsize=14)
    ax.set_ylabel('Amélioration P4 (%)', fontsize=14)
    ax.set_title('Amélioration P4 vs Temps de Cohérence T2', 
                 fontsize=16, weight='bold')
    ax.set_xscale('log')
    ax.legend(fontsize=11)
    ax.grid(alpha=0.3)
    
    output_path = Path(output_dir) / 'figure_2b_scatter_t2.png'
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"[OK] Figure 2B : {output_path}")
    return output_path

def generate_figure_2c(df, output_dir='results'):
    """Figure 2C : Boxplot robustesse P3 vs P4"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    data_to_plot = [df['p3_robustness'], df['p4_robustness']]
    labels = ['P3 (Dynamic Ramp)', 'P4 (Geometric Loop)']
    
    bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True, widths=0.6)
    
    colors = ['lightcoral', 'lightblue']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    
    ax.set_ylabel('Robustness Cost (log scale)', fontsize=14)
    ax.set_title('Comparaison Robustesse P3 vs P4 (360 configs)', 
                 fontsize=16, weight='bold')
    ax.set_yscale('log')
    ax.grid(alpha=0.3, axis='y')
    
    median_p3 = df['p3_robustness'].median()
    median_p4 = df['p4_robustness'].median()
    improvement = (median_p3 - median_p4) / median_p3 * 100
    
    ax.text(0.5, 0.95, f'Amélioration médiane : {improvement:.1f}%', 
            transform=ax.transAxes, fontsize=12, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    output_path = Path(output_dir) / 'figure_2c_boxplot_robustness.png'
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"[OK] Figure 2C : {output_path}")
    return output_path

def generate_figure_2d(df, output_dir='results'):
    """Figure 2D : Variance comparée (stabilité)"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    variance_data = [df['p3_variance_r'], df['p4_variance_r']]
    labels = ['P3 (Ramp)', 'P4 (Loop)']
    
    bp = ax.boxplot(variance_data, labels=labels, patch_artist=True, widths=0.6)
    
    for patch, color in zip(bp['boxes'], ['lightcoral', 'lightblue']):
        patch.set_facecolor(color)
    
    ax.set_ylabel('Variance de r (état final)', fontsize=14)
    ax.set_title('Stabilité P3 vs P4 : Variance du paramètre d\'ordre', 
                 fontsize=16, weight='bold')
    ax.set_yscale('log')
    ax.grid(alpha=0.3, axis='y')
    
    var_p3 = df['p3_variance_r'].mean()
    var_p4 = df['p4_variance_r'].mean()
    var_reduction = (var_p3 - var_p4) / var_p3 * 100
    
    ax.text(0.5, 0.95, f'Réduction variance : {var_reduction:.1f}%', 
            transform=ax.transAxes, fontsize=12, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
    
    output_path = Path(output_dir) / 'figure_2d_variance_stability.png'
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"[OK] Figure 2D : {output_path}")
    return output_path

def generate_figure_2_composite(df, output_dir='results'):
    """Figure 2 : Panel composite 2×2"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Résultats P5 : Validation à Grande Échelle (360 configurations)', 
                 fontsize=18, weight='bold', y=0.995)
    
    mean_gain = df['robustness_gain_percent'].mean()
    
    # Panel A : Histogramme
    axes[0, 0].hist(df['robustness_gain_percent'], bins=30, edgecolor='black', 
                    alpha=0.7, color='steelblue')
    axes[0, 0].axvline(mean_gain, color='red', linestyle='--', linewidth=2, 
                       label=f'Moyenne = {mean_gain:.1f}%')
    axes[0, 0].set_xlabel('Amélioration P4 (%)', fontsize=12)
    axes[0, 0].set_ylabel('Nombre de configs', fontsize=12)
    axes[0, 0].set_title('A) Distribution des Gains', fontsize=14, weight='bold')
    axes[0, 0].legend(fontsize=10)
    axes[0, 0].grid(alpha=0.3)
    
    # Panel B : Scatter T2
    for target in df['target_phenomenology'].unique():
        mask = df['target_phenomenology'] == target
        axes[0, 1].scatter(df[mask]['t2_us'], df[mask]['robustness_gain_percent'], 
                          alpha=0.5, s=30, label=target)
    axes[0, 1].axhline(13.9, color='gray', linestyle=':', linewidth=2, alpha=0.7)
    axes[0, 1].axhline(mean_gain, color='red', linestyle='--', linewidth=2)
    axes[0, 1].set_xlabel('T2 (µs)', fontsize=12)
    axes[0, 1].set_ylabel('Amélioration P4 (%)', fontsize=12)
    axes[0, 1].set_title('B) Gain vs T2', fontsize=14, weight='bold')
    axes[0, 1].set_xscale('log')
    axes[0, 1].legend(fontsize=9)
    axes[0, 1].grid(alpha=0.3)
    
    # Panel C : Boxplot Robustness
    data_rob = [df['p3_robustness'], df['p4_robustness']]
    bp1 = axes[1, 0].boxplot(data_rob, labels=['P3', 'P4'], patch_artist=True, widths=0.5)
    for patch, color in zip(bp1['boxes'], ['lightcoral', 'lightblue']):
        patch.set_facecolor(color)
    axes[1, 0].set_ylabel('Robustness Cost', fontsize=12)
    axes[1, 0].set_title('C) Comparaison Robustesse', fontsize=14, weight='bold')
    axes[1, 0].set_yscale('log')
    axes[1, 0].grid(alpha=0.3, axis='y')
    
    # Panel D : Boxplot Variance
    data_var = [df['p3_variance_r'], df['p4_variance_r']]
    bp2 = axes[1, 1].boxplot(data_var, labels=['P3', 'P4'], patch_artist=True, widths=0.5)
    for patch, color in zip(bp2['boxes'], ['lightcoral', 'lightblue']):
        patch.set_facecolor(color)
    axes[1, 1].set_ylabel('Variance de r', fontsize=12)
    axes[1, 1].set_title('D) Comparaison Stabilité', fontsize=14, weight='bold')
    axes[1, 1].set_yscale('log')
    axes[1, 1].grid(alpha=0.3, axis='y')
    
    output_path = Path(output_dir) / 'figure_2_composite_p5_results.png'
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"[OK] Figure 2 Composite : {output_path}")
    return output_path

def main():
    """Générer toutes les figures"""
    print("="*60)
    print("GÉNÉRATION DES FIGURES P5")
    print("="*60)
    
    # Charger les données
    df = load_data()
    
    # Statistiques rapides
    print(f"\nStatistiques :")
    print(f"  Amélioration moyenne : +{df['robustness_gain_percent'].mean():.1f}%")
    print(f"  P4 victoires : {(df['winner_strategy'] == 'P4').sum()}/{len(df)}")
    
    # Générer les figures
    print(f"\nGénération des figures...")
    generate_figure_2a(df)
    generate_figure_2b(df)
    generate_figure_2c(df)
    generate_figure_2d(df)
    generate_figure_2_composite(df)
    
    print(f"\n{'='*60}")
    print(f"[OK] Toutes les figures générées avec succès !")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()

