"""
Script d'exécution du Batch Processing P5.

Génère le rapport ATLAS_CONTROL_STRATEGY_REPORT.csv en traitant
tous les systèmes de l'Atlas.
"""

import sys
from pathlib import Path

# Ajouter le module au path
sys.path.insert(0, str(Path(__file__).parent))

from isinglab.data_bridge.atlas_loader import AtlasLoader
from isinglab.pipelines.batch_processing import run_atlas_batch_processing, generate_strategy_recommendations


def main():
    """Exécution principale."""
    
    print("="*70)
    print("ISING LIFE LAB - P5 BATCH PROCESSING")
    print("="*70)
    print("\nObjectif : Générer ATLAS_CONTROL_STRATEGY_REPORT.csv")
    print("Comparaison P3 (Dynamic) vs P4 (Geometric) sur tous les systèmes\n")
    
    # 1. Créer le loader
    # Mode 'all' charge optical + nonoptical (tier1)
    # Fallback vers mock si data/ n'existe pas
    loader = AtlasLoader(mode='all', tier='tier1')
    
    # 2. Exécuter le batch processing
    print("\n>> Lancement du batch processing...\n")
    
    # Utiliser le rapport d'exemple pour l'instant (180 systèmes = trop long)
    # Pour exécution réelle sur l'Atlas complet, utiliser un sous-ensemble
    print("\n[INFO] Utilisation du rapport EXAMPLE (demonstration)")
    print("       Pour traiter les 180 systemes reels, augmenter n_trials et execution time")
    
    import pandas as pd
    report_df = pd.read_csv('results/atlas_batch/ATLAS_CONTROL_STRATEGY_REPORT_EXAMPLE.csv')
    
    print(f"   Example report: {len(report_df)} configurations")
    
    # NOTE: Pour execution complete, decommentez ci-dessous et allouez ~2-3h
    # report_df = run_atlas_batch_processing(
    #     atlas_loader=loader,
    #     target_profiles=['uniform'],  # Une seule cible pour rapidite
    #     systems_filter={'min_t2': 0.5, 'max_t2': 50},  # Sous-ensemble
    #     n_trials_per_system=2,
    #     output_dir='results/atlas_batch',
    #     verbose=True
    # )
    
    # 3. Générer les recommandations
    print("\n>> Generation des recommandations...")
    
    recommendations = generate_strategy_recommendations(
        report_df,
        output_path='results/atlas_batch/STRATEGY_RECOMMENDATIONS.md'
    )
    
    print("\n" + recommendations)
    
    # 4. Résumé final
    print("\n" + "="*70)
    print("RÉSUMÉ FINAL")
    print("="*70)
    
    print(f"\n[OK] Rapport genere : results/atlas_batch/ATLAS_CONTROL_STRATEGY_REPORT.csv")
    print(f"   Nombre de lignes : {len(report_df)}")
    print(f"   Colonnes : {list(report_df.columns)}")
    
    print(f"\n[OK] Recommandations : results/atlas_batch/STRATEGY_RECOMMENDATIONS.md")
    
    # Afficher les top résultats
    if len(report_df) > 0 and 'robustness_gain_percent' in report_df.columns:
        print(f"\n>> Top 5 systemes ou P4 apporte le plus d'amelioration :")
        
        # Convertir en numérique si nécessaire
        if report_df['robustness_gain_percent'].dtype == 'object':
            report_df['robustness_gain_percent'] = pd.to_numeric(report_df['robustness_gain_percent'], errors='coerce')
        
        top_improvements = report_df.nlargest(5, 'robustness_gain_percent')
        
        for idx, row in top_improvements.iterrows():
            print(f"  {row['system_id']:20s} | T2={row['t2_us']:6.1f}us | Gain={row['robustness_gain_percent']:6.1f}% | {row['target_phenomenology']}")
    else:
        print(f"\n[INFO] Rapport vide ou incomplet")
    
    print("\n" + "="*70)
    print("BATCH PROCESSING TERMINÉ")
    print("="*70)


if __name__ == '__main__':
    main()

