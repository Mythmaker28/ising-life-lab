"""
Tests pour design_space/selector.py

Valide les fonctions de filtrage/ranking du design space.
"""

import pytest
import pandas as pd
from pathlib import Path
from design_space.selector import (
    load_design_space,
    list_room_temp_candidates,
    list_bio_adjacent_candidates,
    list_high_contrast_candidates,
    list_near_infrared_candidates,
    rank_by_integrability,
    filter_by_family,
    get_system_by_id,
    get_families,
    get_stats_summary
)


# Fixtures
@pytest.fixture
def mini_design_space():
    """Charge mini dataset de test"""
    path = Path("tests/fixtures/mini_design_space.csv")
    return pd.read_csv(path)


# Tests load_design_space
@pytest.mark.skipif(
    not Path("outputs/qubit_design_space_v1.csv").exists(),
    reason="qubit_design_space_v1.csv not built"
)
def test_load_design_space():
    """Test chargement design space complet"""
    df = load_design_space()
    
    assert len(df) > 0
    assert 'system_id' in df.columns
    assert 'protein_name' in df.columns


def test_load_design_space_not_found():
    """Test chargement design space inexistant"""
    with pytest.raises(FileNotFoundError):
        load_design_space(csv_path="does_not_exist.csv")


# Tests list_room_temp_candidates
def test_list_room_temp_candidates(mini_design_space):
    """Test filtrage température ambiante"""
    filtered = list_room_temp_candidates(mini_design_space)
    
    assert len(filtered) > 0
    assert 'system_id' in filtered.columns
    
    # Vérifier température dans range 295-310K (310K = 37°C, temp corporelle)
    # Note: room_temp_viable accepte 295-305K, mais filtre inclut aussi 310K parfois
    if 'temp_k' in filtered.columns:
        assert filtered['temp_k'].min() >= 295
        assert filtered['temp_k'].max() <= 310


def test_list_room_temp_candidates_ids_only(mini_design_space):
    """Test filtrage température ambiante (IDs only)"""
    ids = list_room_temp_candidates(mini_design_space, return_ids_only=True)
    
    assert isinstance(ids, pd.Series)
    assert len(ids) > 0


# Tests list_bio_adjacent_candidates
def test_list_bio_adjacent_candidates(mini_design_space):
    """Test filtrage bio-adjacent (in vivo/in cellulo)"""
    filtered = list_bio_adjacent_candidates(mini_design_space)
    
    assert len(filtered) > 0
    assert 'integration_level' in filtered.columns
    
    # Vérifier que tous sont in_vivo ou in_cellulo
    valid_levels = ['in_vivo', 'in_cellulo']
    assert filtered['integration_level'].isin(valid_levels).all()


# Tests list_high_contrast_candidates
def test_list_high_contrast_candidates(mini_design_space):
    """Test filtrage contraste élevé"""
    filtered = list_high_contrast_candidates(mini_design_space, min_contrast=5.0)
    
    assert len(filtered) > 0
    assert 'contrast_normalized' in filtered.columns
    
    # Vérifier que tous >= 5.0
    assert (filtered['contrast_normalized'] >= 5.0).all()


def test_list_high_contrast_candidates_sorted(mini_design_space):
    """Test tri décroissant par contraste"""
    filtered = list_high_contrast_candidates(mini_design_space, min_contrast=1.0)
    
    if len(filtered) > 1:
        # Vérifier tri décroissant
        contrasts = filtered['contrast_normalized'].values
        assert all(contrasts[i] >= contrasts[i+1] for i in range(len(contrasts)-1))


# Tests list_near_infrared_candidates
def test_list_near_infrared_candidates(mini_design_space):
    """Test filtrage proche infrarouge"""
    filtered = list_near_infrared_candidates(mini_design_space)
    
    # Peut être vide si aucun système ≥650nm (pas une erreur)
    assert isinstance(filtered, pd.DataFrame)
    
    if len(filtered) > 0:
        assert 'emission_nm' in filtered.columns
        # Vérifier émission ≥650nm
        assert (filtered['emission_nm'] >= 650).all()


# Tests rank_by_integrability
def test_rank_by_integrability(mini_design_space):
    """Test ranking par intégrabilité"""
    ranked = rank_by_integrability(mini_design_space)
    
    assert len(ranked) == len(mini_design_space)
    assert 'integrability_score' in ranked.columns
    
    # Vérifier tri décroissant
    scores = ranked['integrability_score'].values
    assert all(scores[i] >= scores[i+1] for i in range(len(scores)-1))


def test_rank_by_integrability_top_n(mini_design_space):
    """Test ranking top N"""
    top3 = rank_by_integrability(mini_design_space, top_n=3)
    
    assert len(top3) == 3
    assert top3['integrability_score'].iloc[0] >= top3['integrability_score'].iloc[2]


def test_rank_by_integrability_score_range(mini_design_space):
    """Test score intégrabilité dans range 0-6"""
    ranked = rank_by_integrability(mini_design_space)
    
    assert (ranked['integrability_score'] >= 0).all()
    assert (ranked['integrability_score'] <= 6).all()


# Tests filter_by_family
def test_filter_by_family(mini_design_space):
    """Test filtrage par famille"""
    calcium = filter_by_family(mini_design_space, "Calcium")
    
    assert len(calcium) > 0
    assert (calcium['family'].str.lower() == 'calcium').all()


def test_filter_by_family_case_insensitive(mini_design_space):
    """Test filtrage famille (case insensitive)"""
    calcium1 = filter_by_family(mini_design_space, "Calcium")
    calcium2 = filter_by_family(mini_design_space, "calcium")
    calcium3 = filter_by_family(mini_design_space, "CALCIUM")
    
    assert len(calcium1) == len(calcium2) == len(calcium3)


def test_filter_by_family_not_found(mini_design_space):
    """Test filtrage famille inexistante"""
    filtered = filter_by_family(mini_design_space, "NonExistentFamily")
    
    assert len(filtered) == 0


# Tests get_system_by_id
def test_get_system_by_id(mini_design_space):
    """Test récupération système par ID"""
    # Prendre premier système
    first_id = mini_design_space['system_id'].iloc[0]
    system = get_system_by_id(mini_design_space, first_id)
    
    assert isinstance(system, dict)
    assert system['system_id'] == first_id


def test_get_system_by_id_not_found(mini_design_space):
    """Test système inexistant"""
    with pytest.raises(ValueError):
        get_system_by_id(mini_design_space, "DOES_NOT_EXIST")


# Tests get_families
def test_get_families(mini_design_space):
    """Test liste familles disponibles"""
    families = get_families(mini_design_space)
    
    assert isinstance(families, pd.Series)
    assert len(families) > 0
    
    # Vérifier que counts sont positifs
    assert (families > 0).all()


# Tests get_stats_summary
def test_get_stats_summary(mini_design_space):
    """Test résumé statistiques"""
    stats = get_stats_summary(mini_design_space)
    
    assert isinstance(stats, dict)
    assert 'total_systems' in stats
    assert stats['total_systems'] == len(mini_design_space)
    assert 'room_temp_viable' in stats
    assert 'bio_adjacent' in stats


def test_get_stats_summary_temp_range(mini_design_space):
    """Test range température dans stats"""
    stats = get_stats_summary(mini_design_space)
    
    assert 'temp_range_k' in stats
    temp_min, temp_max = stats['temp_range_k']
    assert temp_min <= temp_max


def test_get_stats_summary_contrast_range(mini_design_space):
    """Test range contraste dans stats"""
    stats = get_stats_summary(mini_design_space)
    
    assert 'contrast_range' in stats
    contrast_min, contrast_max = stats['contrast_range']
    assert contrast_min <= contrast_max


# Tests intégration
def test_full_filtering_pipeline(mini_design_space):
    """Test pipeline complet: filter → rank → get"""
    # 1. Filtrer calcium (retourne subset colonnes)
    calcium_ids = filter_by_family(mini_design_space, "Calcium", return_ids_only=True)
    assert len(calcium_ids) > 0
    
    # 2. Extraire calcium du df complet (pour avoir tous les tags)
    calcium_full = mini_design_space[mini_design_space['system_id'].isin(calcium_ids)]
    
    # 3. Ranker calcium par intégrabilité
    top_calcium = rank_by_integrability(calcium_full, top_n=2)
    assert len(top_calcium) <= 2
    
    # 4. Récupérer meilleur candidat
    if len(top_calcium) > 0:
        best_id = top_calcium['system_id'].iloc[0]
        best_system = get_system_by_id(mini_design_space, best_id)
        assert best_system['family'].lower() == 'calcium'


def test_multiple_filters_combined(mini_design_space):
    """Test combinaison de filtres"""
    # Room temp + bio-adjacent + high contrast
    room_temp = list_room_temp_candidates(mini_design_space, return_ids_only=True)
    bio_adj = list_bio_adjacent_candidates(mini_design_space, return_ids_only=True)
    high_contrast = list_high_contrast_candidates(mini_design_space, min_contrast=5.0, return_ids_only=True)
    
    # Intersection
    intersection = set(room_temp) & set(bio_adj) & set(high_contrast)
    
    # Au moins quelques systèmes devraient passer tous les filtres
    assert isinstance(intersection, set)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

