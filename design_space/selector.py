"""
Design Space Selector v1.0

Module pour interroger et filtrer la cartographie des systèmes biologiques
quantiques/senseurs (qubit_design_space_v1.csv).

Usage:
    from design_space.selector import load_design_space, list_room_temp_candidates
    
    df = load_design_space()
    candidates = list_room_temp_candidates(df)
"""

import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict

def load_design_space(csv_path: Optional[str] = None) -> pd.DataFrame:
    """
    Charge le design space standardisé
    
    Args:
        csv_path: Chemin vers le CSV. Si None, utilise le path par défaut.
    
    Returns:
        DataFrame avec tous les systèmes catalogués
    
    Raises:
        FileNotFoundError: Si le CSV n'existe pas
    """
    if csv_path is None:
        csv_path = Path("outputs/qubit_design_space_v1.csv")
    else:
        csv_path = Path(csv_path)
    
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Design space CSV not found at {csv_path}\n"
            "Run: python scripts/build_design_space_v1.py"
        )
    
    df = pd.read_csv(csv_path)
    return df

def list_room_temp_candidates(df: pd.DataFrame, return_ids_only: bool = False) -> pd.DataFrame:
    """
    Liste les systèmes fonctionnant à température ambiante (295-305K)
    
    Args:
        df: DataFrame design space
        return_ids_only: Si True, retourne seulement les system_id
    
    Returns:
        DataFrame filtré ou Series de system_id
    """
    filtered = df[df['room_temp_viable'] == True].copy()
    
    if return_ids_only:
        return filtered['system_id']
    
    return filtered[['system_id', 'protein_name', 'family', 'temp_k', 
                     'contrast_normalized', 'integration_level', 'status']]

def list_bio_adjacent_candidates(df: pd.DataFrame, return_ids_only: bool = False) -> pd.DataFrame:
    """
    Liste les systèmes utilisables en contexte biologique (in_vivo, in_cellulo)
    
    Args:
        df: DataFrame design space
        return_ids_only: Si True, retourne seulement les system_id
    
    Returns:
        DataFrame filtré ou Series de system_id
    """
    filtered = df[df['bio_adjacent'] == True].copy()
    
    if return_ids_only:
        return filtered['system_id']
    
    return filtered[['system_id', 'protein_name', 'family', 'integration_level',
                     'context', 'contrast_normalized', 'status']]

def list_high_contrast_candidates(df: pd.DataFrame, 
                                    min_contrast: float = 5.0,
                                    return_ids_only: bool = False) -> pd.DataFrame:
    """
    Liste les systèmes avec contraste élevé (dynamic range)
    
    Args:
        df: DataFrame design space
        min_contrast: Seuil minimum de contraste (default: 5.0)
        return_ids_only: Si True, retourne seulement les system_id
    
    Returns:
        DataFrame filtré ou Series de system_id
    """
    filtered = df[df['contrast_normalized'] >= min_contrast].copy()
    filtered = filtered.sort_values('contrast_normalized', ascending=False)
    
    if return_ids_only:
        return filtered['system_id']
    
    return filtered[['system_id', 'protein_name', 'family', 'contrast_normalized',
                     'integration_level', 'status']]

def list_near_infrared_candidates(df: pd.DataFrame, return_ids_only: bool = False) -> pd.DataFrame:
    """
    Liste les systèmes émettant dans le proche infrarouge (>650nm)
    Meilleure pénétration tissulaire, moins de photodommages
    
    Args:
        df: DataFrame design space
        return_ids_only: Si True, retourne seulement les system_id
    
    Returns:
        DataFrame filtré ou Series de system_id
    """
    filtered = df[df['near_infrared'] == True].copy()
    
    if return_ids_only:
        return filtered['system_id']
    
    return filtered[['system_id', 'protein_name', 'family', 'emission_nm',
                     'contrast_normalized', 'integration_level', 'status']]

def rank_by_integrability(df: pd.DataFrame, 
                           top_n: Optional[int] = None,
                           return_ids_only: bool = False) -> pd.DataFrame:
    """
    Classe les systèmes selon un critère combiné d'intégrabilité technologique
    
    Score = (room_temp_viable × 2) + (bio_adjacent × 2) + (high_contrast × 1) + (stable_mature × 1)
    
    Poids :
    - room_temp_viable: 2 (critique pour déploiement pratique)
    - bio_adjacent: 2 (in_vivo/in_cellulo démontré)
    - high_contrast: 1 (performance mesurable)
    - stable_mature: 1 (qualité des données)
    
    Max score = 6
    
    Args:
        df: DataFrame design space
        top_n: Nombre de top systèmes à retourner (None = tous)
        return_ids_only: Si True, retourne seulement les system_id
    
    Returns:
        DataFrame trié par score décroissant, ou Series de system_id
    """
    df = df.copy()
    
    # Calcul du score d'intégrabilité
    df['integrability_score'] = (
        df['room_temp_viable'].astype(int) * 2 +
        df['bio_adjacent'].astype(int) * 2 +
        df['high_contrast'].astype(int) * 1 +
        df['stable_mature'].astype(int) * 1
    )
    
    # Tri par score décroissant, puis par contraste
    df = df.sort_values(['integrability_score', 'contrast_normalized'], 
                        ascending=[False, False])
    
    if top_n is not None:
        df = df.head(top_n)
    
    if return_ids_only:
        return df['system_id']
    
    return df[['system_id', 'protein_name', 'family', 'integrability_score',
               'room_temp_viable', 'bio_adjacent', 'high_contrast', 'stable_mature',
               'contrast_normalized', 'temp_k', 'integration_level', 'status']]

def filter_by_family(df: pd.DataFrame, 
                      family: str,
                      return_ids_only: bool = False) -> pd.DataFrame:
    """
    Filtre par famille fonctionnelle (Calcium, Voltage, pH, etc.)
    
    Args:
        df: DataFrame design space
        family: Nom de la famille (case-insensitive)
        return_ids_only: Si True, retourne seulement les system_id
    
    Returns:
        DataFrame filtré ou Series de system_id
    """
    filtered = df[df['family'].str.lower() == family.lower()].copy()
    
    if return_ids_only:
        return filtered['system_id']
    
    return filtered[['system_id', 'protein_name', 'family', 'contrast_normalized',
                     'integration_level', 'temp_k', 'status']]

def get_system_by_id(df: pd.DataFrame, system_id: str) -> Dict:
    """
    Récupère toutes les infos d'un système par son ID
    
    Args:
        df: DataFrame design space
        system_id: Identifiant du système (ex: 'FP_0001')
    
    Returns:
        Dictionnaire avec toutes les propriétés
    
    Raises:
        ValueError: Si system_id n'existe pas
    """
    result = df[df['system_id'] == system_id]
    
    if len(result) == 0:
        raise ValueError(f"System ID '{system_id}' not found in design space")
    
    return result.iloc[0].to_dict()

def get_families(df: pd.DataFrame) -> pd.Series:
    """
    Liste toutes les familles disponibles avec leurs counts
    
    Args:
        df: DataFrame design space
    
    Returns:
        Series avec famille -> count
    """
    return df['family'].value_counts()

def get_stats_summary(df: pd.DataFrame) -> Dict:
    """
    Retourne un résumé statistique du design space
    
    Args:
        df: DataFrame design space
    
    Returns:
        Dictionnaire avec statistiques clés
    """
    return {
        'total_systems': len(df),
        'room_temp_viable': int(df['room_temp_viable'].sum()),
        'bio_adjacent': int(df['bio_adjacent'].sum()),
        'high_contrast': int(df['high_contrast'].sum()),
        'near_infrared': int(df['near_infrared'].sum()),
        'stable_mature': int(df['stable_mature'].sum()),
        'temp_range_k': (float(df['temp_k'].min()), float(df['temp_k'].max())),
        'contrast_range': (float(df['contrast_normalized'].min()), 
                           float(df['contrast_normalized'].max())),
        'families_count': len(df['family'].unique()),
        'top_3_families': df['family'].value_counts().head(3).to_dict()
    }

# =============================================================================
# Exemple d'usage (pour tests)
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Design Space Selector v1.0 - Tests")
    print("=" * 60)
    
    # Charger design space
    df = load_design_space()
    print(f"\n[OK] Loaded {len(df)} systems")
    
    # Stats globales
    stats = get_stats_summary(df)
    print("\n=== Global Stats ===")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Top 10 integrability
    print("\n=== Top 10 Integrability ===")
    top10 = rank_by_integrability(df, top_n=10)
    print(top10.to_string(index=False))
    
    # Room temp candidates
    print("\n=== Room Temp Candidates (first 5) ===")
    room_temp = list_room_temp_candidates(df).head()
    print(room_temp.to_string(index=False))
    
    # High contrast candidates
    print("\n=== High Contrast Candidates (first 5) ===")
    high_contrast = list_high_contrast_candidates(df, min_contrast=10.0).head()
    print(high_contrast.to_string(index=False))
    
    # Calcium sensors
    print("\n=== Calcium Sensors (first 5) ===")
    calcium = filter_by_family(df, "Calcium").head()
    print(calcium.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("[SUCCESS] All selector functions work")
    print("=" * 60)

