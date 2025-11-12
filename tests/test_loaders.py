"""
Tests pour design_space/loaders.py

Valide le chargement et la validation de datasets.
"""

import pytest
import pandas as pd
from pathlib import Path
from design_space.loaders import (
    load_atlas_optical,
    load_generic_design_space,
    validate_design_space_schema,
    convert_atlas_to_design_space,
    list_available_atlas_tiers,
    get_column_summary,
    ValidationReport
)


# Fixtures
@pytest.fixture
def mini_design_space_path():
    """Chemin vers mini dataset de test"""
    return Path("tests/fixtures/mini_design_space.csv")


@pytest.fixture
def mini_design_space(mini_design_space_path):
    """Charge mini dataset de test"""
    return pd.read_csv(mini_design_space_path)


# Tests ValidationReport
def test_validation_report_pass():
    """Test ValidationReport avec succès"""
    report = ValidationReport()
    report.add_info("Test info")
    
    assert report.passed is True
    assert len(report.errors) == 0
    assert len(report.info) == 1


def test_validation_report_fail():
    """Test ValidationReport avec échec"""
    report = ValidationReport()
    report.add_error("Test error")
    
    assert report.passed is False
    assert len(report.errors) == 1


def test_validation_report_to_dict():
    """Test conversion ValidationReport → dict"""
    report = ValidationReport()
    report.add_error("Error 1")
    report.add_warning("Warning 1")
    
    result = report.to_dict()
    
    assert result['passed'] is False
    assert len(result['errors']) == 1
    assert len(result['warnings']) == 1


# Tests load_generic_design_space
def test_load_generic_design_space(mini_design_space_path):
    """Test chargement CSV générique"""
    df = load_generic_design_space(mini_design_space_path)
    
    assert len(df) == 10
    assert 'system_id' in df.columns
    assert 'protein_name' in df.columns


def test_load_generic_design_space_not_found():
    """Test chargement CSV inexistant"""
    with pytest.raises(FileNotFoundError):
        load_generic_design_space("does_not_exist.csv")


# Tests validate_design_space_schema
def test_validate_schema_pass(mini_design_space):
    """Test validation schéma OK"""
    report = validate_design_space_schema(mini_design_space)
    
    assert report.passed is True
    assert len(report.errors) == 0


def test_validate_schema_missing_columns():
    """Test validation avec colonnes manquantes"""
    df = pd.DataFrame({
        'system_id': ['S1', 'S2'],
        'family': ['A', 'B']
        # Manque 'protein_name', 'platform'
    })
    
    report = validate_design_space_schema(df, strict=False)
    
    assert len(report.warnings) > 0
    assert any('Missing columns' in w for w in report.warnings)


def test_validate_schema_duplicate_ids():
    """Test validation avec duplicates"""
    df = pd.DataFrame({
        'system_id': ['S1', 'S1', 'S2'],  # S1 dupliqué
        'protein_name': ['A', 'B', 'C'],
        'family': ['X', 'Y', 'Z'],
        'platform': ['P', 'P', 'P']
    })
    
    report = validate_design_space_schema(df)
    
    assert report.passed is False
    assert len(report.errors) > 0
    assert any('duplicate' in e.lower() for e in report.errors)


def test_validate_schema_negative_temp():
    """Test validation température négative"""
    df = pd.DataFrame({
        'system_id': ['S1'],
        'protein_name': ['A'],
        'family': ['X'],
        'platform': ['P'],
        'temp_k': [-10.0]  # Température négative
    })
    
    report = validate_design_space_schema(df)
    
    assert len(report.warnings) > 0


def test_validate_schema_negative_contrast():
    """Test validation contraste négatif"""
    df = pd.DataFrame({
        'system_id': ['S1'],
        'protein_name': ['A'],
        'family': ['X'],
        'platform': ['P'],
        'contrast_normalized': [-1.0]  # Contraste négatif
    })
    
    report = validate_design_space_schema(df)
    
    assert report.passed is False
    assert any('contrast' in e.lower() for e in report.errors)


# Tests list_available_atlas_tiers
def test_list_available_atlas_tiers():
    """Test liste tiers Atlas disponibles"""
    tiers = list_available_atlas_tiers()
    
    # Peut être vide si Atlas pas téléchargé (pas une erreur)
    assert isinstance(tiers, list)
    
    # Si curated existe, vérifier format
    if 'curated' in tiers:
        assert 'curated' in ['curated', 'candidates', 'unknown', 'all']


# Tests get_column_summary
def test_get_column_summary(mini_design_space):
    """Test génération résumé colonnes"""
    summary = get_column_summary(mini_design_space)
    
    assert isinstance(summary, pd.DataFrame)
    assert 'column' in summary.columns
    assert 'dtype' in summary.columns
    assert 'missing_%' in summary.columns
    assert len(summary) == len(mini_design_space.columns)


def test_get_column_summary_numeric_ranges(mini_design_space):
    """Test résumé colonnes numériques (min/max/median)"""
    summary = get_column_summary(mini_design_space)
    
    # temp_k est numérique, devrait avoir min/max/median
    temp_row = summary[summary['column'] == 'temp_k']
    
    if len(temp_row) > 0:
        assert 'min' in temp_row.columns
        assert 'max' in temp_row.columns
        assert 'median' in temp_row.columns


# Tests convert_atlas_to_design_space
def test_convert_atlas_to_design_space_basic():
    """Test conversion Atlas → design_space"""
    # Simuler DataFrame Atlas minimal
    df_atlas = pd.DataFrame({
        'SystemID': ['FP_001', 'FP_002'],
        'protein_name': ['ProteinA', 'ProteinB'],
        'family': ['Calcium', 'Voltage'],
        'temperature_K': [298.0, 310.0],
        'contrast_normalized': [5.0, 2.0]
    })
    
    df_converted = convert_atlas_to_design_space(df_atlas)
    
    assert 'system_id' in df_converted.columns
    assert 'platform' in df_converted.columns
    assert len(df_converted) == 2
    assert df_converted['platform'].iloc[0] == 'fluorescent_protein'


# Tests load_atlas_optical (si disponible)
def test_load_atlas_optical_invalid_tier():
    """Test chargement tier invalide"""
    with pytest.raises(ValueError):
        load_atlas_optical(tier="invalid_tier")


@pytest.mark.skipif(
    not Path("data/atlas_optical/atlas_fp_optical_v2_2_curated.csv").exists(),
    reason="Atlas curated CSV not downloaded"
)
def test_load_atlas_optical_curated():
    """Test chargement Atlas curated (si disponible)"""
    df = load_atlas_optical(tier="curated")
    
    assert len(df) > 0
    assert 'SystemID' in df.columns or 'system_id' in df.columns


# Tests intégration
def test_full_pipeline(mini_design_space_path):
    """Test pipeline complet: load → validate"""
    # Charger
    df = load_generic_design_space(mini_design_space_path)
    assert len(df) == 10
    
    # Valider
    report = validate_design_space_schema(df)
    assert report.passed is True
    
    # Résumé
    summary = get_column_summary(df)
    assert len(summary) == len(df.columns)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

