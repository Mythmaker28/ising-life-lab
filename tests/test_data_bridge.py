"""
Tests for Atlas data bridge (loaders + mapping)
"""
import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os

from isinglab.data_bridge import (
    load_optical_systems,
    load_spin_qubits,
    load_nuclear_spins,
    load_radical_pairs,
    map_system_properties,
    generate_system_profiles
)
from isinglab.data_bridge.atlas_loader import AtlasDataError
from isinglab.data_bridge.mapping import (
    classify_modality,
    classify_temperature_regime,
    classify_coherence_class
)


@pytest.fixture
def mock_optical_csv(tmp_path):
    """Create a mock optical systems CSV"""
    csv_content = """SystemID,protein_name,family,temperature_K,contrast_normalized
FP_001,GCaMP8s,Calcium,310.0,90.0
FP_002,ASAP4e,Voltage,298.0,1.62
FP_003,EGFP,GFP-like,298.0,1.2
"""
    csv_file = tmp_path / "atlas_optical" / "optical_curated.csv"
    csv_file.parent.mkdir(parents=True, exist_ok=True)
    csv_file.write_text(csv_content)
    return tmp_path


@pytest.fixture
def mock_spin_csv(tmp_path):
    """Create a mock spin qubit systems CSV"""
    csv_content = """id,label,system_type,T2_microseconds,temperature_K
SPIN_NV_001,NV- center,NV_center,1800,298
SPIN_SIC_001,VSi defect,SiC_defect,160,298
"""
    csv_file = tmp_path / "atlas_nonoptical" / "spin_qubit_candidates.csv"
    csv_file.parent.mkdir(parents=True, exist_ok=True)
    csv_file.write_text(csv_content)
    return tmp_path


@pytest.fixture
def mock_nuclear_csv(tmp_path):
    """Create a mock nuclear spin systems CSV"""
    csv_content = """id,nucleus,system_type,T2_milliseconds,temperature_K
NUC_13C_001,13C,diamond_NV_coupled,1000,298
NUC_31P_001,31P,phosphorus_donor,30000,2
"""
    csv_file = tmp_path / "atlas_nonoptical" / "nuclear_spin_candidates.csv"
    csv_file.parent.mkdir(parents=True, exist_ok=True)
    csv_file.write_text(csv_content)
    return tmp_path


def test_load_optical_systems_missing():
    """Test that missing optical CSV raises clear error"""
    with pytest.raises(AtlasDataError, match="Optical data file not found"):
        load_optical_systems(tier="curated", data_dir=Path("/nonexistent"))


def test_load_optical_systems_mock(mock_optical_csv):
    """Test loading optical systems from mock CSV"""
    df = load_optical_systems(tier="curated", data_dir=mock_optical_csv)
    
    assert len(df) == 3
    assert "protein_name" in df.columns
    assert "family" in df.columns
    assert df.iloc[0]["protein_name"] == "GCaMP8s"


def test_load_spin_qubits_mock(mock_spin_csv):
    """Test loading spin qubit systems"""
    df = load_spin_qubits(data_dir=mock_spin_csv)
    
    assert len(df) == 2
    assert "label" in df.columns
    assert "system_type" in df.columns


def test_load_nuclear_spins_mock(mock_nuclear_csv):
    """Test loading nuclear spin systems"""
    df = load_nuclear_spins(data_dir=mock_nuclear_csv)
    
    assert len(df) == 2
    assert "nucleus" in df.columns


def test_classify_modality_optical():
    """Test modality classification for optical systems"""
    row = pd.Series({
        "protein_name": "GCaMP8s",
        "family": "Calcium",
        "temperature_K": 310.0
    })
    
    modality = classify_modality(row)
    assert modality == "optical"


def test_classify_modality_spin():
    """Test modality classification for spin systems"""
    row = pd.Series({
        "label": "NV- center",
        "system_type": "NV_center",
        "temperature_K": 298.0
    })
    
    modality = classify_modality(row)
    assert modality == "spin"


def test_classify_modality_nuclear():
    """Test modality classification for nuclear spins"""
    row = pd.Series({
        "nucleus": "13C",
        "system_type": "diamond_NV_coupled",
        "T2_milliseconds": 1000.0
    })
    
    modality = classify_modality(row)
    assert modality == "nuclear"


def test_classify_temperature_regime():
    """Test temperature regime classification"""
    # Physiological
    row1 = pd.Series({"temperature_K": 310.0})
    assert classify_temperature_regime(row1) == "physiological"
    
    # Cryogenic
    row2 = pd.Series({"temperature_K": 4.0})
    assert classify_temperature_regime(row2) == "cryogenic"
    
    # Unknown
    row3 = pd.Series({"other_col": 100})
    assert classify_temperature_regime(row3) == "unknown"


def test_classify_coherence_class_seconds():
    """Test coherence classification with T2 in seconds"""
    # Short (< 1 µs)
    row1 = pd.Series({"T2_seconds": 1e-7})
    assert classify_coherence_class(row1) == "short"
    
    # Medium (1 µs - 1 ms)
    row2 = pd.Series({"T2_seconds": 1e-5})
    assert classify_coherence_class(row2) == "medium"
    
    # Long (1 ms - 1 s)
    row3 = pd.Series({"T2_seconds": 0.01})
    assert classify_coherence_class(row3) == "long"
    
    # Record (≥ 1 s)
    row4 = pd.Series({"T2_seconds": 2.0})
    assert classify_coherence_class(row4) == "record"


def test_classify_coherence_class_microseconds():
    """Test coherence classification with T2 in microseconds (spin qubits)"""
    # NV center: 1800 µs = 1.8 ms → long
    row = pd.Series({"T2_microseconds": 1800.0})
    assert classify_coherence_class(row) == "long"
    
    # Short coherence: 0.5 µs → short
    row2 = pd.Series({"T2_microseconds": 0.5})
    assert classify_coherence_class(row2) == "short"


def test_classify_coherence_class_milliseconds():
    """Test coherence classification with T2 in milliseconds (nuclear spins)"""
    # 13C in diamond: 1000 ms = 1 s → record
    row = pd.Series({"T2_milliseconds": 1000.0})
    assert classify_coherence_class(row) == "record"
    
    # 31P: 30000 ms = 30 s → record
    row2 = pd.Series({"T2_milliseconds": 30000.0})
    assert classify_coherence_class(row2) == "record"


def test_map_system_properties_optical(mock_optical_csv):
    """Test full mapping pipeline on optical systems"""
    df = load_optical_systems(tier="curated", data_dir=mock_optical_csv)
    df_mapped = map_system_properties(df)
    
    # Check new columns added
    assert "modality" in df_mapped.columns
    assert "temperature_regime" in df_mapped.columns
    assert "coherence_class" in df_mapped.columns
    
    # All should be optical
    assert all(df_mapped["modality"] == "optical")
    
    # Temperature regimes should be physiological (298-310 K)
    assert all(df_mapped["temperature_regime"] == "physiological")


def test_generate_system_profiles(mock_optical_csv):
    """Test system profile generation"""
    df = load_optical_systems(tier="curated", data_dir=mock_optical_csv)
    df_mapped = map_system_properties(df)
    
    profiles = generate_system_profiles(df_mapped)
    
    assert len(profiles) == 3
    assert all("system_id" in p for p in profiles)
    assert all("modality" in p for p in profiles)
    assert all("coherence_class" in p for p in profiles)


if __name__ == "__main__":
    print("Running data bridge tests...")
    pytest.main([__file__, "-v"])

