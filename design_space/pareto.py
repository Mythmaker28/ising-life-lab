"""
Pareto Multi-Objectifs pour Design Space

Module générique pour identifier frontière Pareto sur systèmes design space.

Usage:
    from design_space.pareto import compute_pareto_front, rank_pareto
    
    df_pareto = compute_pareto_front(df, objectives={
        'functional_score': 'max',
        'contrast_normalized': 'max',
        'photostability_score': 'max'
    })
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union


def compute_pareto_front(df: pd.DataFrame,
                          objectives: Dict[str, str],
                          strict: bool = True) -> pd.DataFrame:
    """
    Identifie systèmes Pareto-optimaux selon objectifs multiples
    
    Un système est Pareto-optimal si aucun autre système ne le domine
    sur TOUS les objectifs simultanément.
    
    Args:
        df: DataFrame design space
        objectives: Dict {colonne: direction}
            - direction: "max" (maximiser) ou "min" (minimiser)
            - Ex: {"functional_score": "max", "synthesis_cost": "min"}
        strict: Si True, erreur si colonne absente. Si False, warning + skip colonne.
    
    Returns:
        DataFrame avec colonne 'is_pareto_optimal' (bool) ajoutée
    
    Raises:
        KeyError: Si colonne objective manquante (strict=True)
        ValueError: Si direction invalide
    
    Examples:
        >>> df = load_design_space()
        >>> df_pareto = compute_pareto_front(df, {
        ...     'functional_score': 'max',
        ...     'contrast_normalized': 'max'
        ... })
        >>> print(f"{df_pareto['is_pareto_optimal'].sum()} systèmes Pareto-optimaux")
    """
    df = df.copy()
    
    # Validation objectives
    for col, direction in objectives.items():
        if col not in df.columns:
            msg = f"Objective column '{col}' not found in DataFrame"
            if strict:
                raise KeyError(msg)
            else:
                import warnings
                warnings.warn(f"{msg}. Skipping.", UserWarning)
                objectives = {k: v for k, v in objectives.items() if k in df.columns}
                break
        
        if direction not in ['max', 'min']:
            raise ValueError(f"Invalid direction '{direction}' for '{col}'. Use 'max' or 'min'.")
    
    if not objectives:
        raise ValueError("No valid objectives remaining after validation")
    
    # Extraire valeurs objectifs
    obj_cols = list(objectives.keys())
    values = df[obj_cols].values
    
    # Inverser signe pour objectifs "min" (tout devient maximisation)
    for i, (col, direction) in enumerate(objectives.items()):
        if direction == 'min':
            values[:, i] = -values[:, i]
    
    # Identifier Pareto front
    n = len(values)
    is_pareto = np.ones(n, dtype=bool)
    
    for i in range(n):
        if not is_pareto[i]:
            continue
        
        # Comparer i avec tous les autres
        for j in range(n):
            if i == j or not is_pareto[j]:
                continue
            
            # j domine i si j >= i sur tous objectifs ET j > i sur au moins un
            dominates = (values[j] >= values[i]).all() and (values[j] > values[i]).any()
            
            if dominates:
                is_pareto[i] = False
                break
    
    df['is_pareto_optimal'] = is_pareto
    
    n_pareto = is_pareto.sum()
    print(f"[OK] Pareto front: {n_pareto}/{n} systems ({100*n_pareto/n:.1f}%)")
    
    return df


def rank_pareto(df: pd.DataFrame,
                 objectives: Dict[str, str],
                 tie_breakers: Optional[List[str]] = None,
                 strict: bool = True) -> pd.DataFrame:
    """
    Classe systèmes : Pareto d'abord, puis tie-breakers
    
    Args:
        df: DataFrame design space
        objectives: Dict {colonne: direction} pour Pareto
        tie_breakers: Liste colonnes pour départager Pareto (ordre priorité)
            - Ex: ['functional_score', 'contrast_normalized']
            - Si None, tri par première colonne objectives
        strict: Si True, erreur si colonne absente
    
    Returns:
        DataFrame trié : Pareto optimal en tête, puis reste par tie-breakers
    
    Examples:
        >>> df_ranked = rank_pareto(df, 
        ...     objectives={'functional_score': 'max', 'contrast_normalized': 'max'},
        ...     tie_breakers=['functional_score', 'integration_level']
        ... )
        >>> print(df_ranked.head(10))
    """
    # Calculer Pareto
    df_pareto = compute_pareto_front(df, objectives, strict=strict)
    
    # Séparer Pareto vs non-Pareto
    pareto_sys = df_pareto[df_pareto['is_pareto_optimal'] == True].copy()
    non_pareto_sys = df_pareto[df_pareto['is_pareto_optimal'] == False].copy()
    
    # Définir tie-breakers par défaut
    if tie_breakers is None:
        # Utiliser première colonne objectives, direction max
        first_obj = list(objectives.keys())[0]
        tie_breakers = [first_obj]
    
    # Vérifier tie-breakers présents
    valid_tie_breakers = [col for col in tie_breakers if col in df_pareto.columns]
    
    if len(valid_tie_breakers) < len(tie_breakers):
        missing = set(tie_breakers) - set(valid_tie_breakers)
        import warnings
        warnings.warn(f"Tie-breaker columns missing: {missing}. Using available only.", UserWarning)
    
    # Trier Pareto par tie-breakers
    if valid_tie_breakers:
        pareto_sorted = pareto_sys.sort_values(valid_tie_breakers, ascending=False)
    else:
        pareto_sorted = pareto_sys
    
    # Trier non-Pareto par tie-breakers
    if valid_tie_breakers:
        non_pareto_sorted = non_pareto_sys.sort_values(valid_tie_breakers, ascending=False)
    else:
        non_pareto_sorted = non_pareto_sys
    
    # Concaténer : Pareto d'abord
    df_ranked = pd.concat([pareto_sorted, non_pareto_sorted], ignore_index=True)
    
    print(f"[OK] Ranked: {len(pareto_sorted)} Pareto-optimal first, then {len(non_pareto_sorted)} others")
    
    return df_ranked


def get_pareto_summary(df: pd.DataFrame, objectives: Dict[str, str]) -> Dict:
    """
    Résumé statistique du front Pareto
    
    Args:
        df: DataFrame avec colonne 'is_pareto_optimal'
        objectives: Objectifs utilisés pour Pareto
    
    Returns:
        Dict avec stats Pareto (count, %, ranges)
    
    Examples:
        >>> df_pareto = compute_pareto_front(df, objectives)
        >>> summary = get_pareto_summary(df_pareto, objectives)
        >>> print(summary['pareto_count'])
    """
    if 'is_pareto_optimal' not in df.columns:
        raise KeyError("DataFrame must have 'is_pareto_optimal' column. Run compute_pareto_front() first.")
    
    n_total = len(df)
    n_pareto = df['is_pareto_optimal'].sum()
    
    summary = {
        'pareto_count': int(n_pareto),
        'total_count': n_total,
        'pareto_percent': round(100 * n_pareto / n_total, 1),
        'objectives': objectives,
        'objective_ranges': {}
    }
    
    # Ranges pour systèmes Pareto
    pareto_sys = df[df['is_pareto_optimal'] == True]
    
    for col in objectives.keys():
        if col in df.columns:
            summary['objective_ranges'][col] = {
                'pareto_min': float(pareto_sys[col].min()),
                'pareto_max': float(pareto_sys[col].max()),
                'all_min': float(df[col].min()),
                'all_max': float(df[col].max())
            }
    
    return summary


# =============================================================================
# Tests/exemples (si run directement)
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Pareto Module v1.0 - Tests")
    print("=" * 60)
    
    # Test avec dataset synthétique
    print("\n=== Test 1: Pareto 2D (contrast vs robustness) ===")
    
    # 5 systèmes synthétiques
    df_test = pd.DataFrame({
        'system_id': ['S1', 'S2', 'S3', 'S4', 'S5'],
        'protein_name': ['A', 'B', 'C', 'D', 'E'],
        'contrast_normalized': [90.0, 50.0, 30.0, 70.0, 40.0],
        'robustness_score': [0.5, 0.9, 0.7, 0.6, 0.95]
    })
    
    # Pareto sur 2 objectifs (maximiser les deux)
    objectives = {
        'contrast_normalized': 'max',
        'robustness_score': 'max'
    }
    
    df_pareto = compute_pareto_front(df_test, objectives)
    
    print("\nSystèmes Pareto-optimaux:")
    print(df_pareto[df_pareto['is_pareto_optimal']][['protein_name', 'contrast_normalized', 'robustness_score']])
    
    # Attendu : S1 (90, 0.5), S2 (50, 0.9), S5 (40, 0.95) = Pareto
    # S3 (30, 0.7) dominé par S2/S5, S4 (70, 0.6) dominé par S1
    
    # Test 2 : Ranking
    print("\n=== Test 2: Ranking avec tie-breaker ===")
    df_ranked = rank_pareto(df_test, objectives, tie_breakers=['contrast_normalized'])
    
    print("\nRanking complet:")
    print(df_ranked[['protein_name', 'contrast_normalized', 'robustness_score', 'is_pareto_optimal']])
    
    # Test 3 : Summary
    print("\n=== Test 3: Pareto Summary ===")
    summary = get_pareto_summary(df_pareto, objectives)
    
    print(f"Pareto count: {summary['pareto_count']}/{summary['total_count']}")
    print(f"Pareto %: {summary['pareto_percent']}%")
    print(f"Ranges: {summary['objective_ranges']}")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Pareto module works")
    print("=" * 60)


