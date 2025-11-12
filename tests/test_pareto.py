"""
Tests pour design_space/pareto.py

Valide identification frontière Pareto et ranking multi-objectifs.
"""

import pytest
import pandas as pd
import numpy as np
from design_space.pareto import (
    compute_pareto_front,
    rank_pareto,
    get_pareto_summary
)


# Fixtures
@pytest.fixture
def simple_pareto_df():
    """Dataset simple pour tests Pareto 2D"""
    return pd.DataFrame({
        'system_id': ['S1', 'S2', 'S3', 'S4', 'S5'],
        'protein_name': ['A', 'B', 'C', 'D', 'E'],
        'contrast': [90.0, 50.0, 30.0, 70.0, 40.0],
        'robustness': [0.5, 0.9, 0.7, 0.6, 0.95]
    })


@pytest.fixture
def mini_design_space():
    """Charge mini dataset test"""
    return pd.read_csv("tests/fixtures/mini_design_space.csv")


# Tests compute_pareto_front
def test_compute_pareto_front_2d(simple_pareto_df):
    """Test Pareto 2D (contrast, robustness)"""
    objectives = {
        'contrast': 'max',
        'robustness': 'max'
    }
    
    df_pareto = compute_pareto_front(simple_pareto_df, objectives)
    
    assert 'is_pareto_optimal' in df_pareto.columns
    assert df_pareto['is_pareto_optimal'].dtype == bool
    
    # Vérifier nombre Pareto
    n_pareto = df_pareto['is_pareto_optimal'].sum()
    assert n_pareto >= 2  # Au moins 2 systèmes (extrêmes)


def test_compute_pareto_front_dominance(simple_pareto_df):
    """Test détection dominance correcte"""
    objectives = {'contrast': 'max', 'robustness': 'max'}
    
    df_pareto = compute_pareto_front(simple_pareto_df, objectives)
    
    # S1 (90, 0.5) devrait être Pareto (max contrast)
    s1_pareto = df_pareto[df_pareto['system_id'] == 'S1']['is_pareto_optimal'].iloc[0]
    assert s1_pareto == True
    
    # S5 (40, 0.95) devrait être Pareto (max robustness)
    s5_pareto = df_pareto[df_pareto['system_id'] == 'S5']['is_pareto_optimal'].iloc[0]
    assert s5_pareto == True
    
    # S3 (30, 0.7) devrait être dominé par S2 ou S5
    s3_pareto = df_pareto[df_pareto['system_id'] == 'S3']['is_pareto_optimal'].iloc[0]
    assert s3_pareto == False


def test_compute_pareto_front_minimize():
    """Test objectif minimisation"""
    df = pd.DataFrame({
        'system_id': ['S1', 'S2', 'S3'],
        'benefit': [10, 5, 8],
        'cost': [100, 50, 80]  # À minimiser
    })
    
    objectives = {'benefit': 'max', 'cost': 'min'}
    
    df_pareto = compute_pareto_front(df, objectives)
    
    # S2 (5, 50) devrait être Pareto (min cost)
    s2_pareto = df_pareto[df_pareto['system_id'] == 'S2']['is_pareto_optimal'].iloc[0]
    assert s2_pareto == True


def test_compute_pareto_front_missing_column():
    """Test colonne objective manquante"""
    df = pd.DataFrame({
        'system_id': ['S1'],
        'contrast': [10.0]
        # Manque 'robustness'
    })
    
    objectives = {'contrast': 'max', 'robustness': 'max'}
    
    # Mode strict : erreur
    with pytest.raises(KeyError):
        compute_pareto_front(df, objectives, strict=True)
    
    # Mode non-strict : warning + skip colonne
    with pytest.warns(UserWarning):
        df_pareto = compute_pareto_front(df, objectives, strict=False)
        # Devrait fonctionner avec seulement 'contrast'


def test_compute_pareto_front_invalid_direction():
    """Test direction invalide"""
    df = pd.DataFrame({
        'system_id': ['S1'],
        'contrast': [10.0]
    })
    
    objectives = {'contrast': 'maximize'}  # Invalid (devrait être 'max')
    
    with pytest.raises(ValueError):
        compute_pareto_front(df, objectives)


# Tests rank_pareto
def test_rank_pareto_basic(simple_pareto_df):
    """Test ranking Pareto basique"""
    objectives = {'contrast': 'max', 'robustness': 'max'}
    
    df_ranked = rank_pareto(simple_pareto_df, objectives)
    
    assert 'is_pareto_optimal' in df_ranked.columns
    assert len(df_ranked) == len(simple_pareto_df)
    
    # Premiers systèmes devraient être Pareto
    first_n = 3  # Estimer ~3 systèmes Pareto
    assert df_ranked['is_pareto_optimal'].iloc[:first_n].any()


def test_rank_pareto_with_tie_breakers(simple_pareto_df):
    """Test ranking avec tie-breakers"""
    objectives = {'contrast': 'max', 'robustness': 'max'}
    tie_breakers = ['contrast']  # Départager Pareto par contrast
    
    df_ranked = rank_pareto(simple_pareto_df, objectives, tie_breakers=tie_breakers)
    
    # Pareto triés par contrast décroissant
    pareto_systems = df_ranked[df_ranked['is_pareto_optimal'] == True]
    
    if len(pareto_systems) > 1:
        contrasts = pareto_systems['contrast'].values
        # Vérifier tri décroissant
        assert all(contrasts[i] >= contrasts[i+1] for i in range(len(contrasts)-1))


def test_rank_pareto_no_tie_breakers(simple_pareto_df):
    """Test ranking sans tie-breakers explicites"""
    objectives = {'contrast': 'max', 'robustness': 'max'}
    
    df_ranked = rank_pareto(simple_pareto_df, objectives, tie_breakers=None)
    
    # Devrait utiliser première colonne objectives par défaut
    assert len(df_ranked) == len(simple_pareto_df)


# Tests get_pareto_summary
def test_get_pareto_summary(simple_pareto_df):
    """Test résumé statistique Pareto"""
    objectives = {'contrast': 'max', 'robustness': 'max'}
    
    df_pareto = compute_pareto_front(simple_pareto_df, objectives)
    summary = get_pareto_summary(df_pareto, objectives)
    
    assert isinstance(summary, dict)
    assert 'pareto_count' in summary
    assert 'total_count' in summary
    assert 'pareto_percent' in summary
    assert 'objective_ranges' in summary
    
    assert summary['total_count'] == len(simple_pareto_df)
    assert 0 < summary['pareto_count'] <= summary['total_count']


def test_get_pareto_summary_ranges(simple_pareto_df):
    """Test ranges objectifs dans summary"""
    objectives = {'contrast': 'max', 'robustness': 'max'}
    
    df_pareto = compute_pareto_front(simple_pareto_df, objectives)
    summary = get_pareto_summary(df_pareto, objectives)
    
    # Vérifier ranges contrast
    assert 'contrast' in summary['objective_ranges']
    contrast_range = summary['objective_ranges']['contrast']
    
    assert 'pareto_min' in contrast_range
    assert 'pareto_max' in contrast_range
    assert contrast_range['pareto_min'] <= contrast_range['pareto_max']


def test_get_pareto_summary_no_pareto_column():
    """Test summary sans colonne Pareto"""
    df = pd.DataFrame({
        'system_id': ['S1'],
        'contrast': [10.0]
    })
    
    with pytest.raises(KeyError):
        get_pareto_summary(df, {'contrast': 'max'})


# Tests intégration
def test_pareto_on_real_dataset(mini_design_space):
    """Test Pareto sur mini_design_space (10 systèmes)"""
    # Utiliser colonnes réelles
    objectives = {
        'contrast_normalized': 'max',
        'temp_k': 'min'  # Minimiser température (cryogenic)
    }
    
    df_pareto = compute_pareto_front(mini_design_space, objectives, strict=False)
    
    assert 'is_pareto_optimal' in df_pareto.columns
    assert df_pareto['is_pareto_optimal'].sum() >= 1  # Au moins 1 système Pareto


def test_full_pareto_pipeline(simple_pareto_df):
    """Test pipeline complet: compute → rank → summary"""
    objectives = {'contrast': 'max', 'robustness': 'max'}
    
    # 1. Compute Pareto
    df_pareto = compute_pareto_front(simple_pareto_df, objectives)
    
    # 2. Rank
    df_ranked = rank_pareto(simple_pareto_df, objectives, tie_breakers=['contrast'])
    
    # 3. Summary
    summary = get_pareto_summary(df_pareto, objectives)
    
    assert summary['pareto_count'] == df_pareto['is_pareto_optimal'].sum()
    assert summary['pareto_count'] == df_ranked['is_pareto_optimal'].sum()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

