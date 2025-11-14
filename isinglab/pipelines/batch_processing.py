"""
Batch Processing Pipeline : Traitement à grande échelle sur l'Atlas complet.

P5 IMPLEMENTATION : Exécute le pipeline P1-P2-P3-P4 sur l'ensemble des
systèmes quantiques de l'Atlas pour générer un rapport de stratégie global.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import json
from tqdm import tqdm
from datetime import datetime

from ..data_bridge.atlas_loader import AtlasLoader
from ..data_bridge.atlas_map import AtlasMapper
from .holonomy_optimization import compare_geometric_vs_dynamic_robustness


def process_single_system(
    system_id: str,
    atlas_mapper: AtlasMapper,
    target_profiles: List[str] = ['uniform', 'fragmented'],
    best_ramp_params_default: Optional[Dict] = None,
    n_trials: int = 3,
    verbose: bool = True
) -> Dict:
    """
    Traite un seul système : compare P3 vs P4 pour chaque cible phéno.
    
    Args:
        system_id: ID du système à traiter
        atlas_mapper: Mapper Atlas
        target_profiles: Liste de cibles phéno à tester
        best_ramp_params_default: Paramètres par défaut si non optimisés
        n_trials: Nombre de trials pour robustesse
        verbose: Affichage
        
    Returns:
        Dict avec résultats pour ce système
    """
    if best_ramp_params_default is None:
        best_ramp_params_default = {
            'k_start': 0.7,
            'k_end': 0.9,
            'duration': 1.0,
            'annealing_start': 0.1,
            'annealing_end': 0.5
        }
    
    profile = atlas_mapper.get_profile(system_id)
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Processing: {system_id}")
        print(f"  T2={profile.t2_us:.1f}µs, T={profile.temperature_k:.0f}K")
        print(f"{'='*60}")
    
    results_per_target = {}
    
    for target in target_profiles:
        if verbose:
            print(f"\n  Target: {target}")
        
        try:
            result = compare_geometric_vs_dynamic_robustness(
                target_profile=target,
                atlas_profile=system_id,
                best_ramp_params=best_ramp_params_default,
                noise_multiplier=2.0,
                n_trials=n_trials,
                output_dir=None,  # Pas de sauvegarde individuelle
                seed=42,
                atlas_mapper=atlas_mapper
            )
            
            results_per_target[target] = {
                'winner': result['winner'],
                'p3_robustness': result['p3_robustness_mean'],
                'p4_robustness': result['p4_robustness_mean'],
                'improvement_percent': result['improvement'],
                'geometric_phase': result['geometric_phase'],
                'p3_variance': result['p3_stability_variance'],
                'p4_variance': result['p4_stability_variance']
            }
            
            if verbose:
                print(f"    Winner: {result['winner']} ({result['improvement']:.1f}% improvement)")
        
        except Exception as e:
            if verbose:
                print(f"    Error: {e}")
            results_per_target[target] = {'error': str(e)}
    
    return {
        'system_id': system_id,
        'profile': profile,
        'results': results_per_target
    }


def run_atlas_batch_processing(
    atlas_loader: Optional[AtlasLoader] = None,
    target_profiles: List[str] = ['uniform', 'fragmented'],
    systems_filter: Optional[Dict] = None,
    n_trials_per_system: int = 3,
    output_dir: str = 'results/atlas_batch',
    verbose: bool = True
) -> pd.DataFrame:
    """
    P5 MAIN PIPELINE : Traite tous les systèmes de l'Atlas.
    
    Args:
        atlas_loader: AtlasLoader (si None, créé en mode repository)
        target_profiles: Cibles phéno à tester
        systems_filter: Filtres optionnels {'min_t2': 1.0, 'max_temp': 350}
        n_trials_per_system: Trials pour robustesse
        output_dir: Répertoire de sortie
        verbose: Affichage
        
    Returns:
        DataFrame avec tous les résultats (le rapport final)
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print("="*70)
    print("P5 BATCH PROCESSING : Atlas Control Strategy Report")
    print("="*70)
    
    # 1. Charger l'Atlas
    if atlas_loader is None:
        # Essayer de charger l'Atlas réel, sinon fallback vers mock
        atlas_loader = AtlasLoader(mode='all', tier='tier1')  # Tous les systèmes tier1
    
    print(f"\n>> Loading Atlas...")
    all_profiles = atlas_loader.load_all_profiles()
    print(f"   Loaded {len(all_profiles)} systems")
    print(f"   Mode: {atlas_loader.mode}")
    
    # 2. Filtrer si nécessaire
    if systems_filter:
        print(f"\n>> Applying filters: {systems_filter}")
        all_profiles = atlas_loader.filter_profiles(**systems_filter)
        print(f"   Filtered to {len(all_profiles)} systems")
    
    # 3. Créer l'AtlasMapper
    atlas_mapper = AtlasMapper(atlas_loader=atlas_loader)
    atlas_mapper.profiles = all_profiles
    
    # 4. Traiter chaque système
    print(f"\n>> Processing {len(all_profiles)} systems...")
    
    all_results = []
    
    for system_id in tqdm(all_profiles.keys(), desc="Systems", disable=not verbose):
        result = process_single_system(
            system_id=system_id,
            atlas_mapper=atlas_mapper,
            target_profiles=target_profiles,
            n_trials=n_trials_per_system,
            verbose=False  # Désactiver le verbose individuel
        )
        all_results.append(result)
    
    # 5. Compiler le rapport
    print(f"\n>> Compiling report...")
    
    report_data = []
    
    for result in all_results:
        system_id = result['system_id']
        profile = result['profile']
        
        for target, target_results in result['results'].items():
            if 'error' in target_results:
                continue
            
            report_data.append({
                'system_id': system_id,
                'system_name': profile.system_name,
                't2_us': profile.t2_us,
                't1_us': profile.t1_us,
                'temperature_k': profile.temperature_k,
                'noise_level': profile.noise_level,
                'target_phenomenology': target,
                'winner_strategy': target_results['winner'],
                'robustness_gain_percent': target_results['improvement_percent'],
                'p3_robustness': target_results['p3_robustness'],
                'p4_robustness': target_results['p4_robustness'],
                'geometric_phase_rad': target_results['geometric_phase'],
                'p3_variance_r': target_results['p3_variance'],
                'p4_variance_r': target_results['p4_variance']
            })
    
    df_report = pd.DataFrame(report_data)
    
    # 6. Analyser les résultats
    print(f"\n{'='*70}")
    print("ANALYSE GLOBALE")
    print(f"{'='*70}")
    
    if len(df_report) == 0:
        print("\n[WARNING] Aucun résultat généré. Vérifiez les erreurs ci-dessus.")
        # Retourner un DataFrame vide mais avec les bonnes colonnes
        df_report = pd.DataFrame(columns=[
            'system_id', 'system_name', 't2_us', 't1_us', 'temperature_k',
            'noise_level', 'target_phenomenology', 'winner_strategy',
            'robustness_gain_percent', 'p3_robustness', 'p4_robustness',
            'geometric_phase_rad', 'p3_variance_r', 'p4_variance_r'
        ])
        return df_report
    
    # Répartition gagnants
    winner_counts = df_report['winner_strategy'].value_counts()
    print(f"\nRépartition des gagnants :")
    for winner, count in winner_counts.items():
        percentage = count / len(df_report) * 100
        print(f"  {winner} : {count} / {len(df_report)} ({percentage:.1f}%)")
    
    # Corrélation T2 vs stratégie gagnante
    df_p3_wins = df_report[df_report['winner_strategy'] == 'P3']
    df_p4_wins = df_report[df_report['winner_strategy'] == 'P4']
    
    if len(df_p3_wins) > 0:
        print(f"\nP3 gagne pour :")
        print(f"  T2 moyen : {df_p3_wins['t2_us'].mean():.1f}µs")
        print(f"  T2 range : [{df_p3_wins['t2_us'].min():.1f}, {df_p3_wins['t2_us'].max():.1f}]µs")
    
    if len(df_p4_wins) > 0:
        print(f"\nP4 gagne pour :")
        print(f"  T2 moyen : {df_p4_wins['t2_us'].mean():.1f}µs")
        print(f"  T2 range : [{df_p4_wins['t2_us'].min():.1f}, {df_p4_wins['t2_us'].max():.1f}]µs")
    
    # Amélioration moyenne
    avg_improvement = df_report['robustness_gain_percent'].mean()
    print(f"\nAmélioration moyenne P4 vs P3 : {avg_improvement:.1f}%")
    
    # 7. Sauvegarder
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Rapport principal
    report_csv = output_path / f'ATLAS_CONTROL_STRATEGY_REPORT_{timestamp}.csv'
    df_report.to_csv(report_csv, index=False)
    
    # Copie sans timestamp (dernière version)
    report_csv_latest = output_path / 'ATLAS_CONTROL_STRATEGY_REPORT.csv'
    df_report.to_csv(report_csv_latest, index=False)
    
    print(f"\n[OK] Rapport sauvegarde : {report_csv_latest}")
    
    # Métadonnées
    metadata = {
        'timestamp': timestamp,
        'n_systems': len(all_profiles),
        'n_results': len(df_report),
        'target_profiles': target_profiles,
        'n_trials_per_system': n_trials_per_system,
        'atlas_mode': atlas_loader.mode if atlas_loader else 'unknown',
        'winner_distribution': winner_counts.to_dict(),
        'average_improvement_p4': float(avg_improvement)
    }
    
    with open(output_path / 'batch_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return df_report


def generate_strategy_recommendations(
    report_df: pd.DataFrame,
    output_path: Optional[str] = None
) -> str:
    """
    Génère des recommandations de stratégie de contrôle basées sur le rapport.
    
    Args:
        report_df: DataFrame du rapport Atlas
        output_path: Chemin de sauvegarde (optionnel)
        
    Returns:
        Texte des recommandations
    """
    recommendations = []
    recommendations.append("# RECOMMANDATIONS DE STRATÉGIE DE CONTRÔLE\n")
    recommendations.append(f"Basé sur l'analyse de {len(report_df)} configurations\n")
    recommendations.append("="*70 + "\n")
    
    # Analyser par régime de T2
    df_short = report_df[report_df['t2_us'] < 10]
    df_medium = report_df[(report_df['t2_us'] >= 10) & (report_df['t2_us'] < 100)]
    df_long = report_df[report_df['t2_us'] >= 100]
    
    recommendations.append("\n## Par régime de cohérence :\n")
    
    if len(df_short) > 0:
        p4_wins_short = (df_short['winner_strategy'] == 'P4').sum()
        total_short = len(df_short)
        recommendations.append(f"\n### T2 < 10µs (Ultra-court) : {total_short} systèmes\n")
        recommendations.append(f"- P4 gagne dans {p4_wins_short}/{total_short} cas ({p4_wins_short/total_short*100:.0f}%)\n")
        if p4_wins_short / total_short > 0.6:
            recommendations.append("- **RECOMMANDATION** : Utiliser P4 (boucles fermées) pour ces systèmes bruits\n")
    
    if len(df_medium) > 0:
        p4_wins_med = (df_medium['winner_strategy'] == 'P4').sum()
        total_med = len(df_medium)
        recommendations.append(f"\n### 10us <= T2 < 100us (Court-Moyen) : {total_med} systemes\n")
        recommendations.append(f"- P4 gagne dans {p4_wins_med}/{total_med} cas ({p4_wins_med/total_med*100:.0f}%)\n")
        recommendations.append("- **RECOMMANDATION** : Évaluer au cas par cas (mix P3/P4)\n")
    
    if len(df_long) > 0:
        p3_wins_long = (df_long['winner_strategy'] == 'P3').sum()
        total_long = len(df_long)
        recommendations.append(f"\n### T2 >= 100us (Long) : {total_long} systemes\n")
        recommendations.append(f"- P3 gagne dans {p3_wins_long}/{total_long} cas ({p3_wins_long/total_long*100:.0f}%)\n")
        if p3_wins_long / total_long > 0.6:
            recommendations.append("- **RECOMMANDATION** : Utiliser P3 (ramps) pour convergence rapide\n")
    
    # Par phénoménologie cible
    recommendations.append("\n## Par phénoménologie cible :\n")
    
    for target in report_df['target_phenomenology'].unique():
        df_target = report_df[report_df['target_phenomenology'] == target]
        p4_wins = (df_target['winner_strategy'] == 'P4').sum()
        total = len(df_target)
        
        recommendations.append(f"\n### Cible '{target}' : {total} tests\n")
        recommendations.append(f"- P4 gagne dans {p4_wins}/{total} cas ({p4_wins/total*100:.0f}%)\n")
    
    # Synthèse
    recommendations.append("\n## SYNTHÈSE STRATÉGIQUE :\n")
    
    overall_p4_wins = (report_df['winner_strategy'] == 'P4').sum()
    overall_total = len(report_df)
    overall_p4_percentage = overall_p4_wins / overall_total * 100
    
    recommendations.append(f"\n- P4 (Geometric) gagne dans **{overall_p4_percentage:.1f}%** des cas\n")
    recommendations.append(f"- Amélioration moyenne : **{report_df['robustness_gain_percent'].mean():.1f}%**\n")
    
    if overall_p4_percentage > 60:
        recommendations.append("\n**CONCLUSION GLOBALE** : La protection topologique (P4) est **généralement supérieure**, surtout pour les systèmes bruités.\n")
    elif overall_p4_percentage < 40:
        recommendations.append("\n**CONCLUSION GLOBALE** : Le contrôle dynamique (P3) est **généralement suffisant** pour la plupart des systèmes.\n")
    else:
        recommendations.append("\n**CONCLUSION GLOBALE** : **Choix stratégique** dépendant du système. Évaluer T2 et bruit.\n")
    
    recommendations.append("\n" + "="*70 + "\n")
    
    text = ''.join(recommendations)
    
    # Sauvegarder
    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
    
    return text

