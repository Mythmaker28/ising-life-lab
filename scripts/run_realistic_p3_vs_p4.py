"""
Script principal : Comparaison P3 vs P4 avec modèles physiques réalistes.

Ce script remplace le pipeline jouet Kuramoto-XY par des modèles physiques
réalistes pour NV centers, 13C hyperpolarisés, et radical pairs.

Génère:
- Résultats numériques (CSV)
- Figures publication-ready (PNG)
- Données pour mise à jour du paper

Usage:
    python scripts/run_realistic_p3_vs_p4.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import json

from isinglab.data_bridge import AtlasMapper
from isinglab.control.realistic_models import (
    NVCenterModel, Hyperpolarized13CModel, RadicalPairModel,
    SystemType, initial_state, create_model
)
from isinglab.control.realistic_noise import AdaptiveNoiseGenerator

# Configuration matplotlib
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10


def infer_system_type(system_id: str) -> SystemType:
    """Infère le type de système depuis l'ID."""
    if system_id.startswith('NV'):
        return SystemType.NV_CENTER
    elif system_id.startswith('C13'):
        return SystemType.HYPERPOLARIZED_13C
    elif system_id.startswith('RP'):
        return SystemType.RADICAL_PAIR
    else:
        raise ValueError(f"Cannot infer system type from ID: {system_id}")


def simulate_control_trajectory_realistic(
    model,
    system_type: SystemType,
    control_sequence: list,
    dt_ns_or_us: float,
    noise_generator,
    n_trials: int = 3
) -> dict:
    """
    Simule une trajectoire de contrôle avec un modèle physique réaliste.
    
    Args:
        model: Instance du modèle (NVCenterModel, etc.)
        system_type: Type de système
        control_sequence: Liste de paramètres de contrôle à chaque step
        dt_ns_or_us: Pas de temps (ns pour NV, µs pour 13C/RP)
        noise_generator: Générateur de bruit
        n_trials: Nombre de trials avec bruit
        
    Returns:
        Dict avec:
            - 'signals': Signaux mesurés pour chaque trial
            - 'final_signal_mean': Signal final moyen
            - 'final_signal_std': Écart-type du signal final
            - 'robustness_cost': Coût de robustesse (variance du signal final)
    """
    all_signals = []
    
    for trial in range(n_trials):
        # Reset noise
        noise_generator.reset()
        
        # État initial
        state = initial_state(system_type)
        
        # Liste des signaux au cours du temps
        signals = []
        
        # Évolution
        for control_params in control_sequence:
            # Générer bruit
            noise = noise_generator.generate(dt_ns_or_us)
            noise_strength = control_params.get('noise_strength', 0.1)
            
            # Évolution selon le type de système
            if system_type == SystemType.NV_CENTER:
                omega_rabi = control_params.get('omega_rabi', 0.0)
                state = model.evolve(state, dt_ns_or_us, omega_rabi, noise_strength)
                signal = model.measure_signal(state)
            
            elif system_type == SystemType.HYPERPOLARIZED_13C:
                B_rf = control_params.get('B_rf_amplitude', 0.0)
                B_rf_phase = control_params.get('B_rf_phase', 0.0)
                detuning = control_params.get('detuning', 0.0)
                state = model.evolve(state, dt_ns_or_us, B_rf, B_rf_phase, detuning, noise_strength)
                signal = model.measure_signal(state)
            
            elif system_type == SystemType.RADICAL_PAIR:
                state = model.evolve(state, dt_ns_or_us, noise_strength)
                signal = model.measure_signal(state)
            
            else:
                raise ValueError(f"Unknown system type: {system_type}")
            
            signals.append(signal)
        
        all_signals.append(signals)
    
    # Convertir en array
    all_signals = np.array(all_signals)  # shape: (n_trials, n_steps)
    
    # Métriques
    final_signals = all_signals[:, -1]
    final_signal_mean = np.mean(final_signals)
    final_signal_std = np.std(final_signals)
    robustness_cost = np.var(final_signals)  # Variance = mesure de non-robustesse
    
    return {
        'signals': all_signals,
        'final_signal_mean': final_signal_mean,
        'final_signal_std': final_signal_std,
        'robustness_cost': robustness_cost
    }


def create_p3_control_sequence(n_steps: int, system_type: SystemType) -> list:
    """
    Crée une séquence de contrôle P3 (ramp dynamique).
    
    Pour chaque type de système, on définit un protocole de contrôle simple:
    - NV: Linear ramp du Rabi drive
    - 13C: Linear ramp du champ RF
    - RP: Pas de contrôle actif (évolution libre sous champ)
    
    Returns:
        Liste de dicts de paramètres de contrôle
    """
    sequence = []
    
    for i in range(n_steps):
        t_normalized = i / (n_steps - 1)  # 0 → 1
        
        if system_type == SystemType.NV_CENTER:
            # Ramp du Rabi drive de 0 à 0.1 GHz
            omega_rabi = 0.1 * t_normalized
            sequence.append({
                'omega_rabi': omega_rabi,
                'noise_strength': 0.1
            })
        
        elif system_type == SystemType.HYPERPOLARIZED_13C:
            # Ramp du champ RF
            B_rf = 0.05 * t_normalized  # en unités de γ·B
            sequence.append({
                'B_rf_amplitude': B_rf,
                'B_rf_phase': 0.0,
                'detuning': 0.0,
                'noise_strength': 0.1
            })
        
        elif system_type == SystemType.RADICAL_PAIR:
            # Pas de contrôle actif (évolution libre)
            sequence.append({
                'noise_strength': 0.1
            })
    
    return sequence


def create_p4_control_sequence(n_steps: int, system_type: SystemType) -> list:
    """
    Crée une séquence de contrôle P4 (boucle géométrique fermée).
    
    Pour accumuler une phase géométrique, on fait une boucle dans l'espace
    des paramètres de contrôle (ex: (ω_rabi, phase) pour NV).
    
    Returns:
        Liste de dicts de paramètres de contrôle
    """
    sequence = []
    
    for i in range(n_steps):
        theta = 2 * np.pi * i / (n_steps - 1)  # 0 → 2π (loop)
        
        if system_type == SystemType.NV_CENTER:
            # Boucle elliptique dans (ω_rabi, phase_implicite)
            omega_rabi = 0.05 + 0.05 * np.cos(theta)
            # On peut aussi moduler la phase du drive, mais simplifions
            sequence.append({
                'omega_rabi': omega_rabi,
                'noise_strength': 0.1
            })
        
        elif system_type == SystemType.HYPERPOLARIZED_13C:
            # Boucle dans (B_rf, phase)
            B_rf = 0.03 + 0.02 * np.cos(theta)
            B_rf_phase = theta  # Phase tourne
            sequence.append({
                'B_rf_amplitude': B_rf,
                'B_rf_phase': B_rf_phase,
                'detuning': 0.0,
                'noise_strength': 0.1
            })
        
        elif system_type == SystemType.RADICAL_PAIR:
            # Pour RP, on ne peut pas contrôler directement, mais on peut
            # imaginer un champ magnétique modulé. Simplifions: pas de loop actif.
            # Le "geometric control" serait via modulation du champ externe
            # Pour cette démo, on fait juste une évolution constante
            sequence.append({
                'noise_strength': 0.1
            })
    
    return sequence


def compare_p3_vs_p4_single_system(
    system_id: str,
    mapper: AtlasMapper,
    n_steps: int = 100,
    n_trials: int = 5
) -> dict:
    """
    Compare P3 vs P4 pour un système donné.
    
    Returns:
        Dict avec résultats de comparaison
    """
    print(f"\n{'='*70}")
    print(f"Système: {system_id}")
    print(f"{'='*70}")
    
    # Charger profil Atlas
    profile = mapper.get_profile(system_id)
    system_type = infer_system_type(system_id)
    
    print(f"Type: {system_type.value}")
    print(f"T2: {profile.t2_us:.2f} µs")
    print(f"Temperature: {profile.temperature_k:.0f} K")
    print(f"Noise level: {profile.noise_level:.3f}")
    
    # Créer le modèle physique
    if system_type == SystemType.NV_CENTER:
        model = NVCenterModel(
            T1_us=profile.t1_us,
            T2_us=profile.t2_us,
            temperature_k=profile.temperature_k
        )
        dt = 1.0  # ns
    
    elif system_type == SystemType.HYPERPOLARIZED_13C:
        model = Hyperpolarized13CModel(
            T1_us=profile.t1_us,
            T2_us=profile.t2_us,
            temperature_k=profile.temperature_k
        )
        dt = 0.1  # µs
    
    elif system_type == SystemType.RADICAL_PAIR:
        model = RadicalPairModel(
            T2_us=profile.t2_us,
            temperature_k=profile.temperature_k
        )
        dt = 0.05  # µs
    
    else:
        raise ValueError(f"Unknown system type: {system_type}")
    
    # Créer générateur de bruit adaptatif
    noise_gen = AdaptiveNoiseGenerator(
        T1_us=profile.t1_us,
        T2_us=profile.t2_us,
        temperature_k=profile.temperature_k,
        base_noise_scale=1.0
    )
    
    # Créer séquences de contrôle
    p3_sequence = create_p3_control_sequence(n_steps, system_type)
    p4_sequence = create_p4_control_sequence(n_steps, system_type)
    
    # Simuler P3
    print(f"\n  Simulating P3 (dynamic ramp)...")
    p3_results = simulate_control_trajectory_realistic(
        model, system_type, p3_sequence, dt, noise_gen, n_trials
    )
    
    # Reset noise generator
    noise_gen.reset()
    
    # Simuler P4
    print(f"  Simulating P4 (geometric loop)...")
    p4_results = simulate_control_trajectory_realistic(
        model, system_type, p4_sequence, dt, noise_gen, n_trials
    )
    
    # Comparer
    p3_cost = p3_results['robustness_cost']
    p4_cost = p4_results['robustness_cost']
    
    if p4_cost < p3_cost:
        winner = 'P4'
        improvement = (p3_cost - p4_cost) / (p3_cost + 1e-10) * 100
    else:
        winner = 'P3'
        improvement = (p4_cost - p3_cost) / (p4_cost + 1e-10) * 100
    
    print(f"\n  RÉSULTATS:")
    print(f"    P3 robustness cost: {p3_cost:.6f}")
    print(f"    P4 robustness cost: {p4_cost:.6f}")
    print(f"    Winner: {winner}")
    print(f"    Improvement: {improvement:.1f}%")
    
    return {
        'system_id': system_id,
        'system_type': system_type.value,
        'T2_us': profile.t2_us,
        'temperature_k': profile.temperature_k,
        'noise_level': profile.noise_level,
        'p3_robustness_cost': p3_cost,
        'p3_final_signal_mean': p3_results['final_signal_mean'],
        'p3_final_signal_std': p3_results['final_signal_std'],
        'p4_robustness_cost': p4_cost,
        'p4_final_signal_mean': p4_results['final_signal_mean'],
        'p4_final_signal_std': p4_results['final_signal_std'],
        'winner': winner,
        'improvement_percent': improvement,
        'p3_signals': p3_results['signals'],
        'p4_signals': p4_results['signals']
    }


def main():
    """Pipeline principal."""
    print("="*70)
    print("REALISTIC PHYSICS P3 VS P4 COMPARISON")
    print("="*70)
    print("\nModèles utilisés:")
    print("  - NV Centers: Spin-1 Hamiltonian avec dephasing")
    print("  - 13C Hyperpolarized: Bloch equations avec T1/T2")
    print("  - Radical Pairs: 2-spin Hamiltonian avec recombination")
    print("\nBruit: Gaussian + drift 1/f + shot noise")
    print("="*70)
    
    # Charger Atlas
    mapper = AtlasMapper(mode='mock')
    systems = mapper.list_systems()
    
    print(f"\nSystèmes chargés: {len(systems)}")
    for sys_id in systems:
        prof = mapper.get_profile(sys_id)
        print(f"  - {sys_id}: T2={prof.t2_us:.2f} µs, T={prof.temperature_k:.0f} K")
    
    # Paramètres de simulation
    n_steps = 80
    n_trials = 5
    
    print(f"\nParamètres simulation:")
    print(f"  Steps: {n_steps}")
    print(f"  Trials per system: {n_trials}")
    
    # Comparer tous les systèmes
    all_results = []
    
    for sys_id in tqdm(systems, desc="Processing systems"):
        try:
            result = compare_p3_vs_p4_single_system(
                sys_id, mapper, n_steps, n_trials
            )
            all_results.append(result)
        except Exception as e:
            print(f"\n  ERROR for {sys_id}: {e}")
            continue
    
    # Sauvegarder les résultats
    output_dir = Path("figures/realistic_p3_vs_p4")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # CSV résumé
    df_results = pd.DataFrame([
        {
            'system_id': r['system_id'],
            'system_type': r['system_type'],
            'T2_us': r['T2_us'],
            'temperature_k': r['temperature_k'],
            'p3_robustness_cost': r['p3_robustness_cost'],
            'p4_robustness_cost': r['p4_robustness_cost'],
            'winner': r['winner'],
            'improvement_percent': r['improvement_percent']
        }
        for r in all_results
    ])
    
    csv_path = output_dir / "results_table.csv"
    df_results.to_csv(csv_path, index=False)
    print(f"\n[OK] Resultats sauvegardes: {csv_path}")
    
    # Statistiques globales
    print(f"\n{'='*70}")
    print("STATISTIQUES GLOBALES")
    print(f"{'='*70}")
    print(f"Nombre de systèmes: {len(all_results)}")
    print(f"P4 gagne: {sum(1 for r in all_results if r['winner'] == 'P4')} fois")
    print(f"P3 gagne: {sum(1 for r in all_results if r['winner'] == 'P3')} fois")
    
    p4_improvements = [r['improvement_percent'] for r in all_results if r['winner'] == 'P4']
    if p4_improvements:
        print(f"\nAmélioration moyenne P4: {np.mean(p4_improvements):.1f}% ± {np.std(p4_improvements):.1f}%")
    
    # Générer figures
    generate_figures(all_results, output_dir)
    
    print(f"\n{'='*70}")
    print("PIPELINE TERMINÉ")
    print(f"{'='*70}")
    print(f"Outputs: {output_dir}")


def generate_figures(all_results: list, output_dir: Path):
    """Génère les figures publication-ready."""
    print(f"\nGénération des figures...")
    
    # Figure 1: Robustness cost par système
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    
    system_ids = [r['system_id'] for r in all_results]
    p3_costs = [r['p3_robustness_cost'] for r in all_results]
    p4_costs = [r['p4_robustness_cost'] for r in all_results]
    
    x = np.arange(len(system_ids))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, p3_costs, width, label='P3 (Dynamic)', color='#3498db', alpha=0.8, edgecolor='black')
    bars2 = ax.bar(x + width/2, p4_costs, width, label='P4 (Geometric)', color='#e74c3c', alpha=0.8, edgecolor='black')
    
    ax.set_ylabel('Robustness Cost (lower = better)', fontsize=11)
    ax.set_title('P3 vs P4 Robustness Comparison: Realistic Physics Models', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(system_ids, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    fig_path = output_dir / "figure1_robustness_comparison.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  [OK] {fig_path}")
    
    # Figure 2: Amélioration P4 vs P3
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    
    improvements = [r['improvement_percent'] if r['winner'] == 'P4' else -r['improvement_percent'] for r in all_results]
    colors = ['green' if imp > 0 else 'red' for imp in improvements]
    
    ax.bar(system_ids, improvements, color=colors, alpha=0.8, edgecolor='black')
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.set_ylabel('P4 Improvement over P3 (%)', fontsize=11)
    ax.set_title('Geometric Control Performance Gain', fontsize=12, fontweight='bold')
    ax.set_xticklabels(system_ids, rotation=45, ha='right')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    fig_path = output_dir / "figure2_improvement.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  [OK] {fig_path}")
    
    # Figure 3: Par type de système
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    system_types = ['nv', '13c', 'rp']
    type_labels = ['NV Centers', '13C Hyperpolarized', 'Radical Pairs']
    
    for i, (sys_type, label) in enumerate(zip(system_types, type_labels)):
        results_of_type = [r for r in all_results if r['system_type'] == sys_type]
        
        if not results_of_type:
            continue
        
        sys_ids = [r['system_id'] for r in results_of_type]
        p3_costs = [r['p3_robustness_cost'] for r in results_of_type]
        p4_costs = [r['p4_robustness_cost'] for r in results_of_type]
        
        x = np.arange(len(sys_ids))
        width = 0.35
        
        axes[i].bar(x - width/2, p3_costs, width, label='P3', color='#3498db', alpha=0.8)
        axes[i].bar(x + width/2, p4_costs, width, label='P4', color='#e74c3c', alpha=0.8)
        
        axes[i].set_title(label, fontsize=11, fontweight='bold')
        axes[i].set_ylabel('Robustness Cost', fontsize=10)
        axes[i].set_xticks(x)
        axes[i].set_xticklabels([s.replace(sys_type.upper(), '').replace('-', '') for s in sys_ids], rotation=45, ha='right', fontsize=9)
        axes[i].legend()
        axes[i].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    fig_path = output_dir / "figure3_by_system_type.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  [OK] {fig_path}")


if __name__ == "__main__":
    main()

