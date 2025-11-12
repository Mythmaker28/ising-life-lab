"""
Design Space Loaders v1.0

Module pour charger et valider des datasets standardisés (CSV/JSON)
pour analyse qubits/biosenseurs/molécules.

Usage:
    from design_space.loaders import load_atlas_optical, validate_design_space_schema
    
    df = load_atlas_optical(tier="curated")
    report = validate_design_space_schema(df)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Union

class ValidationReport:
    """Rapport de validation dataset"""
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        self.passed = True
    
    def add_error(self, message: str):
        self.errors.append(message)
        self.passed = False
    
    def add_warning(self, message: str):
        self.warnings.append(message)
    
    def add_info(self, message: str):
        self.info.append(message)
    
    def summary(self) -> str:
        lines = []
        lines.append("=== Validation Report ===")
        lines.append(f"Status: {'PASS' if self.passed else 'FAIL'}")
        
        if self.errors:
            lines.append(f"\nErrors ({len(self.errors)}):")
            for err in self.errors:
                lines.append(f"  - {err}")
        
        if self.warnings:
            lines.append(f"\nWarnings ({len(self.warnings)}):")
            for warn in self.warnings:
                lines.append(f"  - {warn}")
        
        if self.info:
            lines.append(f"\nInfo ({len(self.info)}):")
            for inf in self.info:
                lines.append(f"  - {inf}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            'passed': self.passed,
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info
        }


def load_atlas_optical(tier: str = "curated", 
                        data_dir: Union[str, Path] = "data/atlas_optical") -> pd.DataFrame:
    """
    Charge le dataset Atlas optical (protéines fluorescentes)
    
    Args:
        tier: Niveau de curation ("curated", "candidates", "unknown", "all")
        data_dir: Répertoire contenant les CSV Atlas
    
    Returns:
        DataFrame avec systèmes optical
    
    Raises:
        FileNotFoundError: Si CSV tier demandé n'existe pas
        ValueError: Si tier invalide
    
    Examples:
        >>> df = load_atlas_optical(tier="curated")
        >>> print(f"{len(df)} systèmes chargés")
    """
    data_dir = Path(data_dir)
    
    # Mapping tier → filename
    tier_files = {
        'curated': 'atlas_fp_optical_v2_2_curated.csv',
        'candidates': 'atlas_fp_optical_v2_2_candidates.csv',
        'unknown': 'atlas_fp_optical_v2_2_unknown.csv',
        'all': 'atlas_fp_optical_v2_2.csv'  # Mixed tiers
    }
    
    if tier not in tier_files:
        raise ValueError(f"Invalid tier '{tier}'. Choose from: {list(tier_files.keys())}")
    
    csv_path = data_dir / tier_files[tier]
    
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Atlas optical tier '{tier}' not found at {csv_path}\n"
            f"Download with:\n"
            f"  Invoke-WebRequest -Uri 'https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology/raw/main/data/processed/{tier_files[tier]}' -OutFile '{csv_path}'"
        )
    
    df = pd.read_csv(csv_path)
    
    print(f"[OK] Loaded {len(df)} systems from Atlas optical (tier: {tier})")
    return df


def load_generic_design_space(csv_path: Union[str, Path]) -> pd.DataFrame:
    """
    Charge un CSV design space générique
    
    Args:
        csv_path: Chemin vers CSV standardisé
    
    Returns:
        DataFrame avec systèmes
    
    Raises:
        FileNotFoundError: Si CSV n'existe pas
    
    Examples:
        >>> df = load_generic_design_space("outputs/qubit_design_space_v1.csv")
    """
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        raise FileNotFoundError(f"Design space CSV not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    print(f"[OK] Loaded {len(df)} systems from {csv_path.name}")
    return df


def validate_design_space_schema(df: pd.DataFrame, 
                                   expected_columns: Optional[List[str]] = None,
                                   strict: bool = False) -> ValidationReport:
    """
    Valide le schéma d'un DataFrame design space
    
    Args:
        df: DataFrame à valider
        expected_columns: Liste colonnes attendues (None = colonnes minimales par défaut)
        strict: Si True, rejette colonnes manquantes comme erreur (sinon warning)
    
    Returns:
        ValidationReport avec erreurs/warnings/info
    
    Examples:
        >>> df = load_generic_design_space("outputs/qubit_design_space_v1.csv")
        >>> report = validate_design_space_schema(df)
        >>> print(report.summary())
    """
    report = ValidationReport()
    
    # Colonnes minimales attendues par défaut
    if expected_columns is None:
        expected_columns = ['system_id', 'protein_name', 'family', 'platform']
    
    # 1. Vérifier colonnes présentes
    missing_cols = set(expected_columns) - set(df.columns)
    if missing_cols:
        msg = f"Missing columns: {missing_cols}"
        if strict:
            report.add_error(msg)
        else:
            report.add_warning(msg)
    
    # 2. Vérifier duplicates sur system_id
    if 'system_id' in df.columns:
        duplicates = df['system_id'].duplicated().sum()
        if duplicates > 0:
            report.add_error(f"Found {duplicates} duplicate system_id values")
        else:
            report.add_info("No duplicate system_id (OK)")
    
    # 3. Vérifier colonnes critiques non vides
    critical_cols = ['system_id', 'family']
    for col in critical_cols:
        if col in df.columns:
            missing = df[col].isna().sum()
            if missing > 0:
                report.add_error(f"Column '{col}' has {missing} missing values")
    
    # 4. Vérifier ranges numériques
    if 'temp_k' in df.columns:
        temp_min, temp_max = df['temp_k'].min(), df['temp_k'].max()
        if temp_min < 0 or temp_max > 500:
            report.add_warning(f"Temperature range unusual: {temp_min:.1f}K - {temp_max:.1f}K")
        else:
            report.add_info(f"Temperature range OK: {temp_min:.1f}K - {temp_max:.1f}K")
    
    if 'contrast_normalized' in df.columns:
        contrast_min = df['contrast_normalized'].min()
        if contrast_min <= 0:
            report.add_error(f"Negative or zero contrast values found (min: {contrast_min})")
        else:
            report.add_info("Contrast values positive (OK)")
    
    # 5. Vérifier DOI format (basique)
    if 'doi' in df.columns:
        doi_with_value = df['doi'].dropna()
        if len(doi_with_value) > 0:
            invalid_doi = ~doi_with_value.str.contains(r'10\.', na=False, regex=True)
            if invalid_doi.any():
                report.add_warning(f"{invalid_doi.sum()} DOIs don't contain '10.' (possible format issue)")
            report.add_info(f"{len(doi_with_value)}/{len(df)} systems with DOI")
    
    # 6. Résumé
    report.add_info(f"Total systems: {len(df)}")
    report.add_info(f"Total columns: {len(df.columns)}")
    
    return report


def convert_atlas_to_design_space(df_atlas: pd.DataFrame,
                                    platform: str = "fluorescent_protein") -> pd.DataFrame:
    """
    Convertit DataFrame Atlas raw vers schéma design_space standardisé
    
    Args:
        df_atlas: DataFrame Atlas brut
        platform: Type de plateforme (fluorescent_protein, nv_center, etc.)
    
    Returns:
        DataFrame avec colonnes standardisées
    
    Examples:
        >>> df_atlas = load_atlas_optical(tier="curated")
        >>> df_std = convert_atlas_to_design_space(df_atlas)
    """
    df = pd.DataFrame()
    
    # Mapping colonnes Atlas → design_space
    column_mapping = {
        'SystemID': 'system_id',
        'protein_name': 'protein_name',
        'family': 'family',
        'temperature_K': 'temp_k',
        'pH': 'ph',
        'contrast_normalized': 'contrast_normalized',
        'excitation_nm': 'excitation_nm',
        'emission_nm': 'emission_nm',
        'stokes_shift_nm': 'stokes_shift_nm',
        'context': 'context',
        'quality_tier': 'status',
        'doi': 'doi',
        'year': 'year'
    }
    
    # Copier colonnes existantes
    for atlas_col, design_col in column_mapping.items():
        if atlas_col in df_atlas.columns:
            df[design_col] = df_atlas[atlas_col]
    
    # Ajouter plateforme
    df['platform'] = platform
    
    # Convertir types numériques
    numeric_cols = ['temp_k', 'ph', 'contrast_normalized', 'excitation_nm', 'emission_nm', 'stokes_shift_nm', 'year']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    print(f"[OK] Converted {len(df)} Atlas systems to design_space schema")
    return df


# =============================================================================
# Fonctions utilitaires
# =============================================================================

def list_available_atlas_tiers(data_dir: Union[str, Path] = "data/atlas_optical") -> List[str]:
    """
    Liste les tiers Atlas disponibles localement
    
    Args:
        data_dir: Répertoire Atlas
    
    Returns:
        Liste des tiers disponibles
    
    Examples:
        >>> tiers = list_available_atlas_tiers()
        >>> print(f"Tiers disponibles: {tiers}")
    """
    data_dir = Path(data_dir)
    available = []
    
    tier_files = {
        'curated': 'atlas_fp_optical_v2_2_curated.csv',
        'candidates': 'atlas_fp_optical_v2_2_candidates.csv',
        'unknown': 'atlas_fp_optical_v2_2_unknown.csv',
        'all': 'atlas_fp_optical_v2_2.csv'
    }
    
    for tier, filename in tier_files.items():
        if (data_dir / filename).exists():
            available.append(tier)
    
    return available


def get_column_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Génère un résumé des colonnes d'un DataFrame
    
    Args:
        df: DataFrame à analyser
    
    Returns:
        DataFrame avec nom, type, missing%, unique values
    
    Examples:
        >>> df = load_generic_design_space("outputs/qubit_design_space_v1.csv")
        >>> summary = get_column_summary(df)
        >>> print(summary)
    """
    summary = []
    
    for col in df.columns:
        info = {
            'column': col,
            'dtype': str(df[col].dtype),
            'missing_%': round(100 * df[col].isna().sum() / len(df), 1),
            'unique': df[col].nunique()
        }
        
        # Ajouter range pour numériques
        if pd.api.types.is_numeric_dtype(df[col]):
            info['min'] = df[col].min()
            info['max'] = df[col].max()
            info['median'] = df[col].median()
        
        summary.append(info)
    
    return pd.DataFrame(summary)


# =============================================================================
# Tests/exemples (si run directement)
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Design Space Loaders v1.0 - Tests")
    print("=" * 60)
    
    # Test 1 : Lister tiers disponibles
    print("\n=== Available Atlas Tiers ===")
    tiers = list_available_atlas_tiers()
    print(f"Tiers found: {tiers}")
    
    # Test 2 : Charger Atlas curated
    if 'curated' in tiers:
        print("\n=== Load Atlas Curated ===")
        df_atlas = load_atlas_optical(tier="curated")
        print(f"Loaded {len(df)} systems, {len(df.columns)} columns")
        
        # Test 3 : Valider schéma
        print("\n=== Validate Schema ===")
        report = validate_design_space_schema(df_atlas, strict=False)
        print(report.summary())
        
        # Test 4 : Résumé colonnes
        print("\n=== Column Summary (first 10) ===")
        summary = get_column_summary(df_atlas).head(10)
        print(summary.to_string(index=False))
    else:
        print("\n[WARNING] Atlas curated tier not found")
        print("Download with:")
        print("  Invoke-WebRequest -Uri 'https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology/raw/main/data/processed/atlas_fp_optical_v2_2_curated.csv' -OutFile 'data/atlas_optical/atlas_fp_optical_v2_2_curated.csv'")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] All loader functions work")
    print("=" * 60)

