#!/usr/bin/env python3
"""
Score FP-Qubit-Design Predictions

Script pour scorer des prédictions ML venant de fp-qubit-design avec
le functional_score d'ising-life-lab.

Usage:
    python scripts/score_fp_predictions.py --input predictions.csv --output scored.csv

Format attendu (minimal):
    - mutant_id (str): Identifiant mutant
    - parent_protein (str): Protéine de référence
    - contrast_pred (float): Contraste prédit
    - excitation_nm_pred (float, optionnel): Excitation prédite
    - emission_nm_pred (float, optionnel): Émission prédite

Output:
    - Toutes colonnes d'entrée
    - functional_score (float): Score 0-1
    - rank (int): Rang par score décroissant
"""

import argparse
import pandas as pd
from pathlib import Path
import sys

# Ajouter parent dir au path pour imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from metrics.functional_score import apply_functional_score
from design_space.loaders import validate_design_space_schema


def harmonize_fp_predictions(df_pred: pd.DataFrame) -> pd.DataFrame:
    """
    Harmonise colonnes fp-qubit-design vers schéma design_space
    
    Mapping:
        mutant_id → system_id
        parent_protein → protein_name (si absent)
        contrast_pred → contrast_normalized
        *_pred → * (colonnes standard)
    
    Ajout colonnes manquantes avec valeurs par défaut :
        platform = "fluorescent_protein"
        family = parent_protein (ou "unknown")
        room_temp_viable = True (hypothèse: designs pour temp ambiante)
        bio_adjacent = True (hypothèse: designs biocompatibles)
        stable_mature = False (predictions non validées)
    """
    df = pd.DataFrame()
    
    # Mapping colonnes
    if 'mutant_id' in df_pred.columns:
        df['system_id'] = df_pred['mutant_id']
    elif 'system_id' in df_pred.columns:
        df['system_id'] = df_pred['system_id']
    else:
        df['system_id'] = [f"MUTANT_{i:04d}" for i in range(len(df_pred))]
    
    if 'parent_protein' in df_pred.columns:
        df['protein_name'] = df_pred['parent_protein']
        df['family'] = df_pred['parent_protein']  # Famille = parent par défaut
    else:
        df['protein_name'] = df['system_id']
        df['family'] = 'unknown'
    
    # Contraste prédit
    if 'contrast_pred' in df_pred.columns:
        df['contrast_normalized'] = df_pred['contrast_pred']
    elif 'contrast_normalized' in df_pred.columns:
        df['contrast_normalized'] = df_pred['contrast_normalized']
    else:
        raise KeyError("Missing 'contrast_pred' or 'contrast_normalized' column")
    
    # Propriétés optiques (si disponibles)
    if 'excitation_nm_pred' in df_pred.columns:
        df['excitation_nm'] = df_pred['excitation_nm_pred']
    if 'emission_nm_pred' in df_pred.columns:
        df['emission_nm'] = df_pred['emission_nm_pred']
    
    # Tags par défaut (hypothèses raisonnables pour prédictions)
    df['platform'] = 'fluorescent_protein'
    df['room_temp_viable'] = True  # Designs ciblant usage pratique
    df['bio_adjacent'] = True      # Designs biocompatibles
    df['stable_mature'] = False    # Prédictions non validées expérimentalement
    
    # Colonnes stress-test (si présentes dans prédictions)
    stress_cols = ['photostability_score', 'contrast_ph_stability', 'contrast_temp_stability']
    for col in stress_cols:
        if col in df_pred.columns:
            df[col] = df_pred[col]
    
    # Copier autres colonnes utiles
    if 'confidence' in df_pred.columns:
        df['confidence'] = df_pred['confidence']
    if 'mutations' in df_pred.columns:
        df['mutations'] = df_pred['mutations']
    
    print(f"[OK] Harmonized {len(df)} predictions to design_space schema")
    return df


def filter_predictions(df: pd.DataFrame, 
                        min_contrast: float = 1.0,
                        min_confidence: float = 0.0) -> pd.DataFrame:
    """
    Filtre prédictions selon critères physiques
    
    Filtres:
        - contrast_normalized >= min_contrast (réalisme)
        - confidence >= min_confidence (si disponible)
        - excitation_nm 300-700nm (si disponible)
        - emission_nm 300-700nm (si disponible)
    """
    df_filtered = df.copy()
    
    # Filtre contraste
    df_filtered = df_filtered[df_filtered['contrast_normalized'] >= min_contrast]
    
    # Filtre confidence (si disponible)
    if 'confidence' in df_filtered.columns and min_confidence > 0:
        df_filtered = df_filtered[df_filtered['confidence'] >= min_confidence]
    
    # Filtre longueurs d'onde biologiques (si disponibles)
    if 'excitation_nm' in df_filtered.columns:
        df_filtered = df_filtered[
            (df_filtered['excitation_nm'] >= 300) & 
            (df_filtered['excitation_nm'] <= 700)
        ]
    
    if 'emission_nm' in df_filtered.columns:
        df_filtered = df_filtered[
            (df_filtered['emission_nm'] >= 300) & 
            (df_filtered['emission_nm'] <= 700)
        ]
    
    n_removed = len(df) - len(df_filtered)
    print(f"[OK] Filtered: {len(df)} -> {len(df_filtered)} ({n_removed} removed)")
    
    return df_filtered


def main():
    parser = argparse.ArgumentParser(
        description="Score fp-qubit-design predictions avec functional_score"
    )
    parser.add_argument(
        "--input", 
        required=True,
        help="CSV prédictions fp-qubit-design"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="CSV scored output"
    )
    parser.add_argument(
        "--min-contrast",
        type=float,
        default=1.0,
        help="Contraste minimum (default: 1.0)"
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.0,
        help="Confiance minimum (default: 0.0)"
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=None,
        help="Garder seulement top N (default: tous)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Score FP-Qubit-Design Predictions")
    print("=" * 60)
    
    # 1. Charger prédictions
    print(f"\n[1/5] Loading predictions from {args.input}")
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)
    
    df_pred = pd.read_csv(input_path)
    print(f"  Loaded {len(df_pred)} predictions")
    
    # 2. Harmoniser schéma
    print("\n[2/5] Harmonizing to design_space schema")
    df_harmonized = harmonize_fp_predictions(df_pred)
    
    # 3. Filtrer
    print(f"\n[3/5] Filtering (min_contrast={args.min_contrast}, min_confidence={args.min_confidence})")
    df_filtered = filter_predictions(
        df_harmonized,
        min_contrast=args.min_contrast,
        min_confidence=args.min_confidence
    )
    
    if len(df_filtered) == 0:
        print("[WARNING] No predictions passed filters")
        sys.exit(0)
    
    # 4. Scorer
    print("\n[4/5] Computing functional_score")
    df_scored = apply_functional_score(df_filtered, sort=True)
    
    # Top N
    if args.top_n is not None:
        df_scored = df_scored.head(args.top_n)
        print(f"  Keeping top {args.top_n}")
    
    # Ajouter rang
    df_scored.insert(1, 'rank', range(1, len(df_scored) + 1))
    
    # 5. Sauvegarder
    print(f"\n[5/5] Saving scored predictions to {args.output}")
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df_scored.to_csv(output_path, index=False)
    print(f"  Saved {len(df_scored)} scored predictions")
    
    # Résumé
    print("\n=== Summary ===")
    print(f"Input: {len(df_pred)} predictions")
    print(f"Filtered: {len(df_filtered)} passed filters")
    print(f"Output: {len(df_scored)} scored")
    print(f"\nTop 5:")
    print(df_scored.head(5)[['rank', 'system_id', 'protein_name', 'contrast_normalized', 'functional_score']].to_string(index=False))
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Scoring completed")
    print("=" * 60)


if __name__ == "__main__":
    main()

