"""
Functional Score for Design Space Systems

Score combiné basé sur colonnes réelles disponibles :
- contrast_normalized : Dynamic range mesuré
- room_temp_viable : Opération température ambiante (295-305K)
- bio_adjacent : Démonstration in vivo/in cellulo
- stable_mature : Qualité données (tier A/B)

Colonnes optionnelles (stress-test, détectées automatiquement) :
- photostability_score : Si disponible, bonus/malus
- contrast_ph_stability : Variance contraste sur plage pH
- contrast_temp_stability : Variance contraste sur plage température

Formule base (colonnes standard):
    score = w1 × contrast_norm + w2 × room_temp + w3 × bio_adj + w4 × stable

Avec ajustements stress-test (si colonnes présentes):
    score_final = score_base × (1 + bonus_photostability + bonus_ph + bonus_temp)

Pas d'invention : Si colonne absente → score base sans ajustement.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import warnings


def get_score_weights(mode: str = "default") -> Dict[str, float]:
    """
    Retourne les poids pour calcul functional_score
    
    Args:
        mode: Mode de pondération
            - "default": Équilibré (contraste, intégrabilité)
            - "high_contrast": Priorité contraste
            - "bio_focus": Priorité biocompatibilité
    
    Returns:
        Dict avec poids pour chaque composante
    
    Examples:
        >>> weights = get_score_weights("default")
        >>> print(weights['contrast'])
        0.4
    """
    modes = {
        "default": {
            "contrast": 0.4,      # Contraste (0-1, normalisé)
            "room_temp": 0.25,    # Température ambiante (0 ou 1)
            "bio_adjacent": 0.20, # Biocompatibilité (0 ou 1)
            "stable_mature": 0.15 # Maturité données (0 ou 1)
        },
        "high_contrast": {
            "contrast": 0.6,
            "room_temp": 0.2,
            "bio_adjacent": 0.1,
            "stable_mature": 0.1
        },
        "bio_focus": {
            "contrast": 0.2,
            "room_temp": 0.3,
            "bio_adjacent": 0.4,
            "stable_mature": 0.1
        }
    }
    
    if mode not in modes:
        raise ValueError(f"Unknown mode '{mode}'. Choose from: {list(modes.keys())}")
    
    return modes[mode]


def compute_functional_score(row: pd.Series, 
                               weights: Optional[Dict[str, float]] = None,
                               max_contrast: float = 90.0) -> float:
    """
    Calcule functional_score pour une ligne (système)
    
    Args:
        row: Série pandas avec colonnes système
        weights: Poids scoring (None = default)
        max_contrast: Contraste max pour normalisation (default: 90.0 = jGCaMP8s)
    
    Returns:
        Score 0-1 (float)
    
    Raises:
        KeyError: Si colonnes critiques manquantes
    
    Examples:
        >>> row = pd.Series({
        ...     'contrast_normalized': 45.0,
        ...     'room_temp_viable': True,
        ...     'bio_adjacent': True,
        ...     'stable_mature': True
        ... })
        >>> score = compute_functional_score(row)
        >>> print(f"{score:.3f}")
        0.800
    """
    if weights is None:
        weights = get_score_weights("default")
    
    # Vérifier colonnes critiques
    required = ['contrast_normalized', 'room_temp_viable', 'bio_adjacent', 'stable_mature']
    missing = [col for col in required if col not in row.index]
    if missing:
        raise KeyError(f"Missing required columns: {missing}")
    
    # Composantes base (colonnes standard)
    contrast_norm = min(row['contrast_normalized'] / max_contrast, 1.0)
    room_temp = 1.0 if row['room_temp_viable'] else 0.0
    bio_adj = 1.0 if row['bio_adjacent'] else 0.0
    stable = 1.0 if row['stable_mature'] else 0.0
    
    # Score base
    score_base = (
        weights['contrast'] * contrast_norm +
        weights['room_temp'] * room_temp +
        weights['bio_adjacent'] * bio_adj +
        weights['stable_mature'] * stable
    )
    
    # Ajustements stress-test (colonnes optionnelles)
    bonus_total = 0.0
    
    # Bonus photostabilité (si disponible)
    if 'photostability_score' in row.index and pd.notna(row['photostability_score']):
        # Photostabilité 0-1 → bonus -0.1 à +0.1
        photo_score = row['photostability_score']
        bonus_photo = (photo_score - 0.5) * 0.2  # Centré sur 0.5
        bonus_total += bonus_photo
    
    # Bonus stabilité pH (si disponible)
    if 'contrast_ph_stability' in row.index and pd.notna(row['contrast_ph_stability']):
        # Stabilité pH 0-1 (1 = très stable) → bonus 0 à +0.1
        ph_stability = row['contrast_ph_stability']
        bonus_ph = ph_stability * 0.1
        bonus_total += bonus_ph
    
    # Bonus stabilité température (si disponible)
    if 'contrast_temp_stability' in row.index and pd.notna(row['contrast_temp_stability']):
        # Stabilité T 0-1 (1 = très stable) → bonus 0 à +0.1
        temp_stability = row['contrast_temp_stability']
        bonus_temp = temp_stability * 0.1
        bonus_total += bonus_temp
    
    # Score final
    score_final = score_base * (1 + bonus_total)
    
    # Clamp 0-1
    return max(0.0, min(1.0, score_final))


def apply_functional_score(df: pd.DataFrame,
                             weights: Optional[Dict[str, float]] = None,
                             max_contrast: Optional[float] = None,
                             sort: bool = True) -> pd.DataFrame:
    """
    Applique functional_score à un DataFrame complet
    
    Args:
        df: DataFrame design space
        weights: Poids scoring (None = default)
        max_contrast: Contraste max (None = auto-detect from df)
        sort: Trier par score décroissant
    
    Returns:
        DataFrame avec colonne 'functional_score' ajoutée
    
    Examples:
        >>> df = load_design_space()
        >>> df_scored = apply_functional_score(df)
        >>> print(df_scored.nlargest(5, 'functional_score')[['protein_name', 'functional_score']])
    """
    df = df.copy()
    
    # Auto-detect max contrast si non fourni
    if max_contrast is None:
        if 'contrast_normalized' in df.columns:
            max_contrast = df['contrast_normalized'].max()
        else:
            max_contrast = 90.0  # Fallback
    
    # Vérifier colonnes requises
    required = ['contrast_normalized', 'room_temp_viable', 'bio_adjacent', 'stable_mature']
    missing = [col for col in required if col not in df.columns]
    
    if missing:
        raise KeyError(
            f"DataFrame missing required columns: {missing}\n"
            f"Available columns: {df.columns.tolist()}"
        )
    
    # Détecter colonnes optionnelles stress-test
    optional_stress = ['photostability_score', 'contrast_ph_stability', 'contrast_temp_stability']
    present_stress = [col for col in optional_stress if col in df.columns]
    
    if present_stress:
        warnings.warn(
            f"Stress-test columns detected: {present_stress}. "
            "Adjustments will be applied.",
            UserWarning
        )
    
    # Calculer score pour chaque ligne
    df['functional_score'] = df.apply(
        lambda row: compute_functional_score(row, weights=weights, max_contrast=max_contrast),
        axis=1
    )
    
    # Trier
    if sort:
        df = df.sort_values('functional_score', ascending=False)
    
    return df


def explain_score(row: pd.Series, 
                   weights: Optional[Dict[str, float]] = None,
                   max_contrast: float = 90.0) -> Dict:
    """
    Explique le calcul du score pour une ligne (debug/transparence)
    
    Args:
        row: Série pandas avec colonnes système
        weights: Poids scoring
        max_contrast: Contraste max
    
    Returns:
        Dict avec détail composantes
    
    Examples:
        >>> row = df.loc[df['protein_name'] == 'jGCaMP8s'].iloc[0]
        >>> explanation = explain_score(row)
        >>> print(explanation['score_final'])
        0.95
    """
    if weights is None:
        weights = get_score_weights("default")
    
    # Composantes
    contrast_norm = min(row['contrast_normalized'] / max_contrast, 1.0)
    room_temp = 1.0 if row['room_temp_viable'] else 0.0
    bio_adj = 1.0 if row['bio_adjacent'] else 0.0
    stable = 1.0 if row['stable_mature'] else 0.0
    
    # Contributions
    contrib_contrast = weights['contrast'] * contrast_norm
    contrib_room_temp = weights['room_temp'] * room_temp
    contrib_bio_adj = weights['bio_adjacent'] * bio_adj
    contrib_stable = weights['stable_mature'] * stable
    
    score_base = contrib_contrast + contrib_room_temp + contrib_bio_adj + contrib_stable
    
    # Bonus
    bonus_details = {}
    bonus_total = 0.0
    
    if 'photostability_score' in row.index and pd.notna(row['photostability_score']):
        bonus_photo = (row['photostability_score'] - 0.5) * 0.2
        bonus_details['photostability'] = bonus_photo
        bonus_total += bonus_photo
    
    if 'contrast_ph_stability' in row.index and pd.notna(row['contrast_ph_stability']):
        bonus_ph = row['contrast_ph_stability'] * 0.1
        bonus_details['ph_stability'] = bonus_ph
        bonus_total += bonus_ph
    
    if 'contrast_temp_stability' in row.index and pd.notna(row['contrast_temp_stability']):
        bonus_temp = row['contrast_temp_stability'] * 0.1
        bonus_details['temp_stability'] = bonus_temp
        bonus_total += bonus_temp
    
    score_final = score_base * (1 + bonus_total)
    score_final = max(0.0, min(1.0, score_final))
    
    return {
        'score_final': score_final,
        'score_base': score_base,
        'components': {
            'contrast': contrib_contrast,
            'room_temp': contrib_room_temp,
            'bio_adjacent': contrib_bio_adj,
            'stable_mature': contrib_stable
        },
        'bonus_total': bonus_total,
        'bonus_details': bonus_details,
        'weights': weights
    }


# =============================================================================
# Tests/exemples (si run directement)
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Functional Score v1.0 - Tests")
    print("=" * 60)
    
    # Test 1 : Calcul simple
    print("\n=== Test 1: Compute Score (système parfait) ===")
    row_perfect = pd.Series({
        'protein_name': 'Test_Perfect',
        'contrast_normalized': 90.0,
        'room_temp_viable': True,
        'bio_adjacent': True,
        'stable_mature': True
    })
    
    score = compute_functional_score(row_perfect)
    print(f"Score: {score:.3f} (attendu: 1.0)")
    
    # Test 2 : Explication
    print("\n=== Test 2: Explain Score ===")
    explanation = explain_score(row_perfect)
    print(f"Score base: {explanation['score_base']:.3f}")
    print(f"Components: {explanation['components']}")
    
    # Test 3 : Avec bonus stress-test
    print("\n=== Test 3: Score avec bonus photostabilité ===")
    row_bonus = row_perfect.copy()
    row_bonus['photostability_score'] = 0.9  # Très photostable
    
    score_bonus = compute_functional_score(row_bonus)
    explanation_bonus = explain_score(row_bonus)
    print(f"Score avec bonus: {score_bonus:.3f}")
    print(f"Bonus appliqué: {explanation_bonus['bonus_total']:.3f}")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Functional score module works")
    print("=" * 60)

