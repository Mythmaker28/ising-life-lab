"""
Tests pour metrics/functional_score.py

Valide le calcul du score fonctionnel pour systèmes design space.
"""

import pytest
import pandas as pd
import numpy as np
from metrics.functional_score import (
    compute_functional_score,
    apply_functional_score,
    get_score_weights,
    explain_score
)


# Fixtures
@pytest.fixture
def mini_design_space():
    """Charge mini dataset de test"""
    return pd.read_csv("tests/fixtures/mini_design_space.csv")


@pytest.fixture
def perfect_system():
    """Système parfait (score max)"""
    return pd.Series({
        'system_id': 'TEST_001',
        'protein_name': 'Perfect',
        'contrast_normalized': 90.0,
        'room_temp_viable': True,
        'bio_adjacent': True,
        'stable_mature': True
    })


@pytest.fixture
def minimal_system():
    """Système minimal (score min)"""
    return pd.Series({
        'system_id': 'TEST_002',
        'protein_name': 'Minimal',
        'contrast_normalized': 0.5,
        'room_temp_viable': False,
        'bio_adjacent': False,
        'stable_mature': False
    })


# Tests get_score_weights
def test_get_score_weights_default():
    """Test poids mode default"""
    weights = get_score_weights("default")
    
    assert isinstance(weights, dict)
    assert 'contrast' in weights
    assert 'room_temp' in weights
    assert 'bio_adjacent' in weights
    assert 'stable_mature' in weights
    
    # Vérifier somme = 1.0
    total = sum(weights.values())
    assert abs(total - 1.0) < 0.01


def test_get_score_weights_modes():
    """Test différents modes de pondération"""
    modes = ['default', 'high_contrast', 'bio_focus']
    
    for mode in modes:
        weights = get_score_weights(mode)
        assert isinstance(weights, dict)
        assert all(0 <= w <= 1 for w in weights.values())


def test_get_score_weights_invalid():
    """Test mode invalide"""
    with pytest.raises(ValueError):
        get_score_weights("invalid_mode")


# Tests compute_functional_score
def test_compute_functional_score_perfect(perfect_system):
    """Test score système parfait"""
    score = compute_functional_score(perfect_system)
    
    assert 0.0 <= score <= 1.0
    assert score == 1.0  # Système parfait


def test_compute_functional_score_minimal(minimal_system):
    """Test score système minimal"""
    score = compute_functional_score(minimal_system)
    
    assert 0.0 <= score <= 1.0
    assert score < 0.1  # Système minimal


def test_compute_functional_score_missing_column():
    """Test avec colonne manquante"""
    row = pd.Series({
        'protein_name': 'Test',
        'contrast_normalized': 10.0
        # Manque room_temp_viable, bio_adjacent, stable_mature
    })
    
    with pytest.raises(KeyError):
        compute_functional_score(row)


def test_compute_functional_score_range(mini_design_space):
    """Test scores dans range 0-1"""
    for idx, row in mini_design_space.iterrows():
        score = compute_functional_score(row)
        assert 0.0 <= score <= 1.0


def test_compute_functional_score_with_bonus():
    """Test score avec bonus photostabilité"""
    row = pd.Series({
        'protein_name': 'Test_Bonus',
        'contrast_normalized': 45.0,
        'room_temp_viable': True,
        'bio_adjacent': True,
        'stable_mature': True,
        'photostability_score': 0.9  # Très photostable
    })
    
    score_with_bonus = compute_functional_score(row)
    
    # Retirer colonne bonus
    row_no_bonus = row.drop('photostability_score')
    score_no_bonus = compute_functional_score(row_no_bonus)
    
    # Score avec bonus devrait être supérieur
    assert score_with_bonus > score_no_bonus


# Tests apply_functional_score
def test_apply_functional_score_basic(mini_design_space):
    """Test application score à DataFrame"""
    df_scored = apply_functional_score(mini_design_space)
    
    assert 'functional_score' in df_scored.columns
    assert len(df_scored) == len(mini_design_space)
    assert (df_scored['functional_score'] >= 0).all()
    assert (df_scored['functional_score'] <= 1).all()


def test_apply_functional_score_sorted(mini_design_space):
    """Test tri par score décroissant"""
    df_scored = apply_functional_score(mini_design_space, sort=True)
    
    scores = df_scored['functional_score'].values
    
    # Vérifier tri décroissant
    assert all(scores[i] >= scores[i+1] for i in range(len(scores)-1))


def test_apply_functional_score_top_system(mini_design_space):
    """Test top système a meilleur contraste + tags"""
    df_scored = apply_functional_score(mini_design_space, sort=True)
    
    top = df_scored.iloc[0]
    
    # jGCaMP8s devrait être top (90.0 contrast, tous tags True)
    assert top['protein_name'] == 'jGCaMP8s'
    assert top['contrast_normalized'] == 90.0


def test_apply_functional_score_no_sort(mini_design_space):
    """Test application sans tri"""
    df_scored = apply_functional_score(mini_design_space, sort=False)
    
    # Ordre devrait être conservé
    assert df_scored['system_id'].tolist() == mini_design_space['system_id'].tolist()


def test_apply_functional_score_custom_weights(mini_design_space):
    """Test avec poids custom"""
    weights = get_score_weights("high_contrast")
    
    df_scored = apply_functional_score(mini_design_space, weights=weights)
    
    assert 'functional_score' in df_scored.columns


# Tests explain_score
def test_explain_score_structure(perfect_system):
    """Test structure explication score"""
    explanation = explain_score(perfect_system)
    
    assert isinstance(explanation, dict)
    assert 'score_final' in explanation
    assert 'score_base' in explanation
    assert 'components' in explanation
    assert 'bonus_total' in explanation
    assert 'weights' in explanation


def test_explain_score_components_sum(perfect_system):
    """Test somme composantes = score_base"""
    explanation = explain_score(perfect_system)
    
    components_sum = sum(explanation['components'].values())
    
    # Arrondi pour float precision
    assert abs(components_sum - explanation['score_base']) < 0.001


def test_explain_score_with_bonus():
    """Test explication avec bonus"""
    row = pd.Series({
        'protein_name': 'Test',
        'contrast_normalized': 45.0,
        'room_temp_viable': True,
        'bio_adjacent': True,
        'stable_mature': True,
        'photostability_score': 0.8,
        'contrast_ph_stability': 0.7
    })
    
    explanation = explain_score(row)
    
    assert explanation['bonus_total'] > 0
    assert 'photostability' in explanation['bonus_details']
    assert 'ph_stability' in explanation['bonus_details']


# Tests intégration
def test_full_scoring_pipeline(mini_design_space):
    """Test pipeline complet: load → score → explain top"""
    # Score
    df_scored = apply_functional_score(mini_design_space)
    
    # Top système
    top = df_scored.iloc[0]
    
    # Expliquer
    explanation = explain_score(top)
    
    assert explanation['score_final'] == top['functional_score']
    assert 0.0 <= explanation['score_final'] <= 1.0


def test_comparison_vs_simple_ranking(mini_design_space):
    """Test: functional_score vs simple tri contraste"""
    # Ranking functional_score
    df_scored = apply_functional_score(mini_design_space, sort=True)
    top5_func = df_scored.head(5)['protein_name'].tolist()
    
    # Ranking simple contraste
    df_contrast = mini_design_space.sort_values('contrast_normalized', ascending=False)
    top5_contrast = df_contrast.head(5)['protein_name'].tolist()
    
    # Overlap devrait être élevé mais pas 100% (score capture autres aspects)
    overlap = len(set(top5_func) & set(top5_contrast))
    
    assert overlap >= 3  # Au moins 3/5 en commun
    
    print(f"\nOverlap top5: {overlap}/5")
    print(f"Functional: {top5_func}")
    print(f"Contrast: {top5_contrast}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


