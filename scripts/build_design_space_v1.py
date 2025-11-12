#!/usr/bin/env python3
"""
Build qubit_design_space_v1.csv from Atlas Tier 1 (optical systems)

Extraction et standardisation des systèmes biologiques quantiques/senseurs
pour cartographie design space v8.0.

Input: data/atlas_optical/atlas_fp_optical_v2_2_curated.csv (180 systems, Tier 1)
Output: outputs/qubit_design_space_v1.csv (standardized schema)
"""

import pandas as pd
import numpy as np
from pathlib import Path

def load_atlas_curated():
    """Charge le dataset Atlas Tier 1 curated"""
    atlas_path = Path("data/atlas_optical/atlas_fp_optical_v2_2_curated.csv")
    
    if not atlas_path.exists():
        raise FileNotFoundError(
            f"Atlas curated CSV not found at {atlas_path}\n"
            "Download with:\n"
            "  Invoke-WebRequest -Uri 'https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology/raw/main/data/processed/atlas_fp_optical_v2_2_curated.csv' -OutFile 'data/atlas_optical/atlas_fp_optical_v2_2_curated.csv'"
        )
    
    df = pd.read_csv(atlas_path)
    print(f"[OK] Loaded {len(df)} systems from Atlas Tier 1 curated")
    return df

def standardize_schema(df_raw):
    """
    Standardise le schéma vers qubit_design_space_v1.csv
    
    Colonnes cibles (adaptées aux données optiques réelles) :
    - system_id : Identifiant unique
    - platform : Type de système (optical_biosensor, optical_passive, etc.)
    - family : Famille fonctionnelle (Calcium, Voltage, GFP-like, etc.)
    - temp_k : Température d'opération (Kelvin)
    - context : Contexte d'intégration (in_vivo, in_cellulo, etc.)
    - contrast : Contraste normalisé (dynamic range)
    - brightness_proxy : Proxy de brillance (pour optical readout)
    - readout_type : Type de lecture (fluorescence, FRET)
    - integration_level : Niveau d'intégration (in_vivo, in_cellulo, etc.)
    - bio_compatible : Booléen biocompatibilité
    - status : Statut/maturité (evidence level)
    - ex_nm : Excitation (nm)
    - em_nm : Émission (nm)
    - stokes_shift_nm : Décalage de Stokes
    - doi : Référence publication
    - year : Année publication
    """
    
    df = pd.DataFrame()
    
    # Identifiants
    df['system_id'] = df_raw['SystemID']
    df['protein_name'] = df_raw['protein_name']
    
    # Plateforme : toutes sont des optical systems (Tier 1 = fluorescent proteins)
    df['platform'] = 'fluorescent_protein'
    
    # Famille fonctionnelle
    df['family'] = df_raw['family']
    
    # Biosensor vs passive marker
    df['is_biosensor'] = df_raw['is_biosensor'].fillna(0.0).astype(bool)
    
    # Température (Kelvin)
    df['temp_k'] = df_raw['temperature_K'].fillna(298.0)  # Default = room temp
    
    # pH (important pour optical stability)
    df['ph'] = df_raw['pH'].fillna(7.4)
    
    # Contexte d'intégration
    df['context'] = df_raw['context'].fillna('unknown')
    df['integration_level'] = df['context'].apply(classify_integration_level)
    
    # Contraste (dynamic range normalisé)
    df['contrast_normalized'] = df_raw['contrast_normalized'].fillna(1.0)
    
    # Proxy brillance (ex_nm × em_nm comme indicateur très grossier)
    # Note: vraie brillance nécessiterait quantum_yield × extinction_coeff
    ex = pd.to_numeric(df_raw['excitation_nm'], errors='coerce').fillna(0)
    em = pd.to_numeric(df_raw['emission_nm'], errors='coerce').fillna(0)
    df['brightness_proxy'] = np.where((ex > 0) & (em > 0), np.sqrt(ex * em), np.nan)
    
    # Type de lecture (tous fluorescence pour Tier 1 optical)
    df['readout_type'] = df_raw['method'].fillna('fluorescence')
    
    # Biocompatibilité (toutes les protéines fluorescentes sont bio-sources)
    df['bio_compatible'] = True
    
    # Statut/maturité (evidence level)
    df['status'] = df_raw['quality_tier'].fillna('unknown')
    
    # Propriétés optiques (conversion numérique avec coerce pour valeurs manquantes)
    df['excitation_nm'] = pd.to_numeric(df_raw['excitation_nm'], errors='coerce')
    df['emission_nm'] = pd.to_numeric(df_raw['emission_nm'], errors='coerce')
    df['stokes_shift_nm'] = pd.to_numeric(df_raw['stokes_shift_nm'], errors='coerce')
    
    # Métadonnées
    df['doi'] = df_raw['doi']
    df['year'] = df_raw['year'].fillna(0).astype(int)
    
    # Tags dérivés (voir fonction tag_systems)
    df = tag_systems(df)
    
    print(f"[OK] Standardized schema: {len(df)} systems, {len(df.columns)} columns")
    return df

def classify_integration_level(context_str):
    """
    Classifie le niveau d'intégration basé sur le contexte
    
    Niveaux :
    - in_vivo : Démontré dans organisme vivant (neurons, striatum, etc.)
    - in_cellulo : Démontré en cellules (HEK293, HeLa, etc.)
    - in_vitro : Purified protein, test tube
    - unknown : Non spécifié
    """
    if pd.isna(context_str):
        return 'unknown'
    
    context_lower = str(context_str).lower()
    
    if 'in_vivo' in context_lower or 'neuron' in context_lower or 'striatum' in context_lower:
        return 'in_vivo'
    elif 'in_cellulo' in context_lower or 'hek' in context_lower or 'hela' in context_lower:
        return 'in_cellulo'
    elif 'in_vitro' in context_lower or 'purified' in context_lower:
        return 'in_vitro'
    else:
        return 'unknown'

def tag_systems(df):
    """
    Ajoute des tags booléens pour filtrage rapide
    
    Tags :
    - room_temp_viable : Fonctionne à température ambiante (~298K)
    - bio_adjacent : Utilisable en contexte biologique
    - high_contrast : Contraste élevé (>5.0)
    - near_infrared : Émission dans proche infrarouge (>650nm)
    - stable_mature : Statut mature (quality_tier A ou B)
    """
    # Température ambiante (295-305K = 22-32°C)
    df['room_temp_viable'] = (df['temp_k'] >= 295) & (df['temp_k'] <= 305)
    
    # Bio-adjacent (toutes les protéines fluorescentes le sont par définition)
    df['bio_adjacent'] = df['integration_level'].isin(['in_vivo', 'in_cellulo'])
    
    # Contraste élevé (seuil arbitraire à 5.0, ajustable)
    df['high_contrast'] = df['contrast_normalized'] >= 5.0
    
    # Proche infrarouge (>650nm, meilleure pénétration tissulaire)
    df['near_infrared'] = df['emission_nm'].fillna(0) >= 650
    
    # Statut mature (quality_tier A ou B)
    df['stable_mature'] = df['status'].isin(['A', 'B'])
    
    # CMOS-friendly (pour protéines fluorescentes, pas vraiment applicable - toujours False)
    df['cmos_friendly'] = False
    
    print(f"[OK] Tagged systems:")
    print(f"  - room_temp_viable: {df['room_temp_viable'].sum()}/{len(df)}")
    print(f"  - bio_adjacent: {df['bio_adjacent'].sum()}/{len(df)}")
    print(f"  - high_contrast: {df['high_contrast'].sum()}/{len(df)}")
    print(f"  - near_infrared: {df['near_infrared'].sum()}/{len(df)}")
    print(f"  - stable_mature: {df['stable_mature'].sum()}/{len(df)}")
    
    return df

def validate_output(df):
    """Valide le CSV standardisé"""
    print("\n=== Validation ===")
    
    # 1. Pas de doublons sur system_id
    duplicates = df['system_id'].duplicated().sum()
    assert duplicates == 0, f"Found {duplicates} duplicate system_ids"
    print("[OK] No duplicate system_ids")
    
    # 2. Colonnes critiques non vides
    critical = ['system_id', 'platform', 'family']
    for col in critical:
        missing = df[col].isna().sum()
        assert missing == 0, f"Column {col} has {missing} missing values"
    print(f"[OK] Critical columns complete: {critical}")
    
    # 3. Température dans range raisonnable (270-320K = -3°C à 47°C)
    temp_ok = ((df['temp_k'] >= 270) & (df['temp_k'] <= 320)).all()
    assert temp_ok, "Temperature out of range (270-320K)"
    print("[OK] Temperature range valid (270-320K)")
    
    # 4. Contraste positif
    contrast_ok = (df['contrast_normalized'] > 0).all()
    assert contrast_ok, "Negative contrast values found"
    print("[OK] Contrast values positive")
    
    # 5. DOI format basique (contient '10.')
    doi_with_value = df['doi'].dropna()
    doi_format_ok = doi_with_value.str.contains(r'10\.').all()
    assert doi_format_ok, "Some DOIs don't contain '10.'"
    print(f"[OK] DOI format valid ({len(doi_with_value)}/{len(df)} with DOI)")
    
    print("\n[SUCCESS] All validations passed")

def save_output(df, output_path):
    """Sauvegarde le CSV standardisé"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_path, index=False)
    print(f"\n[OK] Saved to: {output_path}")
    print(f"  - {len(df)} systems")
    print(f"  - {len(df.columns)} columns")
    print(f"  - Size: {output_path.stat().st_size / 1024:.1f} KB")

def print_summary(df):
    """Affiche un résumé des données"""
    print("\n=== Summary ===")
    print(f"Total systems: {len(df)}")
    print(f"\nPlatform distribution:")
    print(df['platform'].value_counts())
    print(f"\nTop 5 families:")
    print(df['family'].value_counts().head())
    print(f"\nIntegration levels:")
    print(df['integration_level'].value_counts())
    print(f"\nTemperature range: {df['temp_k'].min():.1f}K - {df['temp_k'].max():.1f}K")
    print(f"Contrast range: {df['contrast_normalized'].min():.2f} - {df['contrast_normalized'].max():.2f}")
    print(f"\nYear range: {df[df['year']>0]['year'].min():.0f} - {df[df['year']>0]['year'].max():.0f}")

def main():
    print("=" * 60)
    print("Building qubit_design_space_v1.csv from Atlas Tier 1")
    print("=" * 60)
    
    # 1. Charger Atlas curated
    df_raw = load_atlas_curated()
    
    # 2. Standardiser schéma
    df_std = standardize_schema(df_raw)
    
    # 3. Valider
    validate_output(df_std)
    
    # 4. Sauvegarder
    output_path = "outputs/qubit_design_space_v1.csv"
    save_output(df_std, output_path)
    
    # 5. Résumé
    print_summary(df_std)
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Design space v1 built successfully")
    print("=" * 60)

if __name__ == "__main__":
    main()

