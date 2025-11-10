"""
System Property Mapping (Heuristic, Deterministic, Transparent)

Maps physical qubit systems to conceptual categories for Ising/CA exploration.

IMPORTANT:
- All mappings are HEURISTIC, not predictive
- Rules are DETERMINISTIC and TRACEABLE
- Missing data → "unknown", NEVER invented
- No claims about predicting T₂ or actual quantum behavior
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


# ============================================================================
# MODALITY MAPPING
# ============================================================================

def classify_modality(row: pd.Series) -> str:
    """
    Classify system modality based on available columns.
    
    Logic (deterministic):
        1. If 'modality' column exists → use it directly
        2. Check for explicit markers:
           - 'family' column (optical FP families)
           - 'system_type' (NV_center, SiC_defect, etc.)
           - 'nucleus' column → nuclear
           - 'protein_or_complex' with radical → radical_pair
        3. Infer from system_type keywords
        4. Otherwise → "unknown"
    
    Args:
        row: DataFrame row (one system)
        
    Returns:
        Modality: "optical", "spin", "nuclear", "radical_pair", "unknown"
    """
    # Direct modality column
    if 'modality' in row.index and pd.notna(row['modality']):
        return str(row['modality']).lower().strip()
    
    # Optical systems: have 'family' column (GFP-like, Calcium, Voltage, etc.)
    if 'family' in row.index and pd.notna(row['family']):
        family = str(row['family']).lower()
        # All FP families are optical
        if family != 'unknown':
            return "optical"
    
    # Nuclear spin systems: have 'nucleus' column
    if 'nucleus' in row.index and pd.notna(row['nucleus']):
        return "nuclear"
    
    # Radical pair systems: have 'protein_or_complex' column
    if 'protein_or_complex' in row.index and pd.notna(row['protein_or_complex']):
        complex_name = str(row['protein_or_complex']).lower()
        if 'crypto' in complex_name or 'radical' in complex_name or 'photolyase' in complex_name:
            return "radical_pair"
    
    # Spin qubit systems: check system_type
    if 'system_type' in row.index and pd.notna(row['system_type']):
        system_type = str(row['system_type']).lower()
        
        if 'nv' in system_type or 'defect' in system_type or 'spin' in system_type:
            return "spin"
        elif 'optical' in system_type or 'photon' in system_type or 'fluorescent' in system_type:
            return "optical"
        elif 'nuclear' in system_type or 'nmr' in system_type:
            return "nuclear"
        elif 'radical' in system_type or 'pair' in system_type:
            return "radical_pair"
    
    return "unknown"


# ============================================================================
# TEMPERATURE REGIME MAPPING
# ============================================================================

def classify_temperature_regime(row: pd.Series) -> str:
    """
    Classify temperature regime based on operating temperature.
    
    Logic (deterministic):
        1. If 'temperature_K' or 'temp_K' column exists:
           - T < 10 K → "cryogenic"
           - 10 K ≤ T < 280 K → "intermediate"
           - 280 K ≤ T ≤ 320 K → "physiological"
           - T > 320 K → "high"
        2. If 'environment' mentions 'room temp' → "physiological"
        3. If 'environment' mentions 'cryo' or 'mK' → "cryogenic"
        4. Otherwise → "unknown"
    
    Args:
        row: DataFrame row
        
    Returns:
        Temperature regime: "cryogenic", "intermediate", "physiological", "high", "unknown"
    """
    # Direct temperature column
    for col in ['temperature_K', 'temp_K', 'T', 'operating_temp']:
        if col in row.index and pd.notna(row[col]):
            try:
                temp = float(row[col])
                if temp < 10:
                    return "cryogenic"
                elif temp < 280:
                    return "intermediate"
                elif temp <= 320:
                    return "physiological"
                else:
                    return "high"
            except (ValueError, TypeError):
                pass
    
    # Infer from environment description
    if 'environment' in row.index and pd.notna(row['environment']):
        env = str(row['environment']).lower()
        
        if 'room temp' in env or 'ambient' in env or '300' in env:
            return "physiological"
        elif 'cryo' in env or 'mk' in env or 'dilution' in env or '<1 k' in env:
            return "cryogenic"
        elif 'intermediate' in env or '100 k' in env:
            return "intermediate"
    
    return "unknown"


# ============================================================================
# COHERENCE CLASS MAPPING
# ============================================================================

def classify_coherence_class(row: pd.Series) -> str:
    """
    Classify coherence class based on T₂ (decoherence time).
    
    Logic (deterministic):
        1. Check multiple T₂ column formats:
           - T2_seconds, T2_milliseconds, T2_microseconds
           - coherence_time, t2, T2
        2. Convert to seconds and classify:
           - T₂ < 1 µs → "short"
           - 1 µs ≤ T₂ < 1 ms → "medium"
           - 1 ms ≤ T₂ < 1 s → "long"
           - T₂ ≥ 1 s → "record"
        3. Otherwise → "unknown"
    
    Args:
        row: DataFrame row
        
    Returns:
        Coherence class: "short", "medium", "long", "record", "unknown"
    """
    # Check T₂ in various units
    t2_seconds = None
    
    # T2 in seconds
    for col in ['T2_seconds', 'coherence_time', 't2', 'T2']:
        if col in row.index and pd.notna(row[col]):
            try:
                t2_seconds = float(row[col])
                break
            except (ValueError, TypeError):
                pass
    
    # T2 in milliseconds (non-optical systems often use ms)
    if t2_seconds is None:
        for col in ['T2_milliseconds', 't2_ms', 'T2_ms']:
            if col in row.index and pd.notna(row[col]):
                try:
                    t2_seconds = float(row[col]) / 1000.0  # Convert ms → s
                    break
                except (ValueError, TypeError):
                    pass
    
    # T2 in microseconds
    if t2_seconds is None:
        for col in ['T2_microseconds', 't2_us', 'T2_us', 'T2_star_microseconds']:
            if col in row.index and pd.notna(row[col]):
                try:
                    t2_seconds = float(row[col]) / 1e6  # Convert µs → s
                    break
                except (ValueError, TypeError):
                    pass
    
    # Classify
    if t2_seconds is not None:
        if t2_seconds < 1e-6:  # < 1 µs
            return "short"
        elif t2_seconds < 1e-3:  # < 1 ms
            return "medium"
        elif t2_seconds < 1.0:  # < 1 s
            return "long"
        else:  # ≥ 1 s
            return "record"
    
    return "unknown"


# ============================================================================
# MAIN MAPPING FUNCTION
# ============================================================================

def map_system_properties(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all heuristic mappings to a DataFrame of systems.
    
    Adds columns:
        - modality: optical | spin | nuclear | radical_pair | unknown
        - temperature_regime: cryogenic | intermediate | physiological | high | unknown
        - coherence_class: short | medium | long | record | unknown
    
    Args:
        df: Input DataFrame with system data
        
    Returns:
        DataFrame with added mapping columns (original data unchanged)
    """
    result = df.copy()
    
    # Apply mappings row by row
    result['modality'] = result.apply(classify_modality, axis=1)
    result['temperature_regime'] = result.apply(classify_temperature_regime, axis=1)
    result['coherence_class'] = result.apply(classify_coherence_class, axis=1)
    
    return result


def generate_system_profiles(df: pd.DataFrame) -> List[Dict]:
    """
    Generate system profiles for Ising/CA regime exploration.
    
    Each profile is a summary dict suitable for searching CA/Ising space.
    
    Args:
        df: DataFrame with mapped properties
        
    Returns:
        List of profile dictionaries
    """
    profiles = []
    
    for _, row in df.iterrows():
        profile = {
            "system_id": row.get("id", row.get("system_name", "unknown")),
            "modality": row.get("modality", "unknown"),
            "temperature_regime": row.get("temperature_regime", "unknown"),
            "coherence_class": row.get("coherence_class", "unknown"),
            
            # Optional: include raw metrics if available
            "T2_seconds": row.get("T2_seconds", None),
            "temperature_K": row.get("temperature_K", None),
            
            # Metadata
            "source": row.get("source", "atlas"),
            "notes": row.get("notes", "")
        }
        
        profiles.append(profile)
    
    return profiles


def summary_statistics(df: pd.DataFrame) -> Dict:
    """
    Compute summary statistics for mapped systems.
    
    Useful for sanity checks and reporting.
    
    Args:
        df: DataFrame with mapped properties
        
    Returns:
        Dictionary with counts and distributions
    """
    stats = {
        "total_systems": len(df),
        "modality_counts": df['modality'].value_counts().to_dict() if 'modality' in df else {},
        "temperature_regime_counts": df['temperature_regime'].value_counts().to_dict() if 'temperature_regime' in df else {},
        "coherence_class_counts": df['coherence_class'].value_counts().to_dict() if 'coherence_class' in df else {},
    }
    
    return stats

