"""
Atlas Data Loader (READ-ONLY)

Loads CSV data from Biological Qubits Atlas exports.
NEVER modifies source files.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List


class AtlasDataError(Exception):
    """Raised when Atlas data cannot be loaded"""
    pass


def _get_data_directory() -> Path:
    """
    Get Atlas data directory.
    
    Expected structure:
        ising-life-lab/
        ├── data/              # Atlas CSV exports (gitignored)
        │   ├── optical_tier1.csv
        │   ├── nonoptical_tier1.csv
        │   └── ...
        └── isinglab/
    
    Returns:
        Path to data directory
    """
    # Start from this file's location
    current_file = Path(__file__).resolve()
    repo_root = current_file.parent.parent.parent
    data_dir = repo_root / "data"
    
    return data_dir


def list_available_datasets() -> List[str]:
    """
    List all available CSV datasets in data/ directory.
    
    Returns:
        List of available dataset filenames
    """
    data_dir = _get_data_directory()
    
    if not data_dir.exists():
        return []
    
    csv_files = [f.name for f in data_dir.glob("*.csv")]
    return sorted(csv_files)


def load_optical_systems(
    tier: str = "tier1",
    data_dir: Optional[Path] = None
) -> pd.DataFrame:
    """
    Load optical qubit systems data (READ-ONLY).
    
    Args:
        tier: Data tier ("tier1", "tier2", "all")
        data_dir: Override default data directory (for testing)
        
    Returns:
        DataFrame with optical systems
        
    Raises:
        AtlasDataError: If file not found or cannot be read
        
    Example:
        >>> from isinglab.data_bridge import load_optical_systems
        >>> df = load_optical_systems(tier="tier1")
        >>> print(f"Loaded {len(df)} optical systems")
    """
    if data_dir is None:
        data_dir = _get_data_directory()
    
    filename = f"optical_{tier}.csv"
    
    # Try multiple locations (for flexibility in testing/deployment)
    possible_paths = [
        data_dir / "atlas_optical" / filename,  # Structured subdirectory
        data_dir / filename,                    # Direct in data/
    ]
    
    filepath = None
    for path in possible_paths:
        if path.exists():
            filepath = path
            break
    
    if filepath is None:
        available = list_available_datasets()
        raise AtlasDataError(
            f"Optical data file not found. Tried:\\n"
            f"  - {possible_paths[0]}\\n"
            f"  - {possible_paths[1]}\\n"
            f"Available datasets: {available}\\n"
            f"Expected directory: {data_dir}\\n"
            f"Ensure Atlas CSV exports are placed in data/ directory."
        )
    
    try:
        df = pd.read_csv(filepath)
        return df.copy()  # Return copy to ensure READ-ONLY
    except Exception as e:
        raise AtlasDataError(f"Failed to read {filepath}: {e}")


def load_nonoptical_systems(
    tier: str = "tier1",
    data_dir: Optional[Path] = None
) -> pd.DataFrame:
    """
    Load non-optical qubit systems data (READ-ONLY).
    
    Includes: spin, nuclear, radical pairs, etc.
    
    Args:
        tier: Data tier ("tier1", "tier2", "all")
        data_dir: Override default data directory (for testing)
        
    Returns:
        DataFrame with non-optical systems
        
    Raises:
        AtlasDataError: If file not found or cannot be read
        
    Example:
        >>> from isinglab.data_bridge import load_nonoptical_systems
        >>> df = load_nonoptical_systems(tier="tier1")
        >>> print(f"Loaded {len(df)} non-optical systems")
    """
    if data_dir is None:
        data_dir = _get_data_directory()
    
    filename = f"nonoptical_{tier}.csv"
    
    # Try multiple locations
    possible_paths = [
        data_dir / "atlas_nonoptical" / filename,
        data_dir / filename,
    ]
    
    filepath = None
    for path in possible_paths:
        if path.exists():
            filepath = path
            break
    
    if filepath is None:
        available = list_available_datasets()
        raise AtlasDataError(
            f"Non-optical data file not found. Tried:\\n"
            f"  - {possible_paths[0]}\\n"
            f"  - {possible_paths[1]}\\n"
            f"Available datasets: {available}\\n"
            f"Expected directory: {data_dir}\\n"
            f"Ensure Atlas CSV exports are placed in data/ directory."
        )
    
    try:
        df = pd.read_csv(filepath)
        return df.copy()  # Return copy to ensure READ-ONLY
    except Exception as e:
        raise AtlasDataError(f"Failed to read {filepath}: {e}")


def load_spin_qubits(
    data_dir: Optional[Path] = None
) -> pd.DataFrame:
    """
    Load spin qubit systems data (READ-ONLY).
    
    Includes: NV centers, SiC defects, SiV, GeV, P1 centers, endohedral fullerenes, etc.
    
    Args:
        data_dir: Override default data directory (for testing)
        
    Returns:
        DataFrame with spin qubit systems
        
    Raises:
        AtlasDataError: If file not found or cannot be read
        
    Example:
        >>> from isinglab.data_bridge import load_spin_qubits
        >>> df = load_spin_qubits()
        >>> print(f"Loaded {len(df)} spin qubit systems")
    """
    if data_dir is None:
        data_dir = _get_data_directory()
    
    # Look in atlas_nonoptical subdirectory
    filepath = data_dir / "atlas_nonoptical" / "spin_qubit_candidates.csv"
    
    if not filepath.exists():
        # Fallback: try root data directory
        filepath = data_dir / "spin_qubit_candidates.csv"
    
    if not filepath.exists():
        available = list_available_datasets()
        raise AtlasDataError(
            f"Spin qubit data file not found: {filepath}\\n"
            f"Available datasets: {available}\\n"
            f"Expected: data/atlas_nonoptical/spin_qubit_candidates.csv\\n"
            f"See data/README.md for download instructions."
        )
    
    try:
        df = pd.read_csv(filepath)
        return df.copy()  # Return copy to ensure READ-ONLY
    except Exception as e:
        raise AtlasDataError(f"Failed to read {filepath}: {e}")


def load_nuclear_spins(
    data_dir: Optional[Path] = None
) -> pd.DataFrame:
    """
    Load nuclear spin systems data (READ-ONLY).
    
    Includes: 13C, 31P, 14N, 29Si, 15N, 1H nuclear spins in diamond, silicon, proteins, etc.
    
    Args:
        data_dir: Override default data directory (for testing)
        
    Returns:
        DataFrame with nuclear spin systems
        
    Raises:
        AtlasDataError: If file not found or cannot be read
        
    Example:
        >>> from isinglab.data_bridge import load_nuclear_spins
        >>> df = load_nuclear_spins()
        >>> print(f"Loaded {len(df)} nuclear spin systems")
    """
    if data_dir is None:
        data_dir = _get_data_directory()
    
    # Look in atlas_nonoptical subdirectory
    filepath = data_dir / "atlas_nonoptical" / "nuclear_spin_candidates.csv"
    
    if not filepath.exists():
        filepath = data_dir / "nuclear_spin_candidates.csv"
    
    if not filepath.exists():
        available = list_available_datasets()
        raise AtlasDataError(
            f"Nuclear spin data file not found: {filepath}\\n"
            f"Available datasets: {available}\\n"
            f"Expected: data/atlas_nonoptical/nuclear_spin_candidates.csv\\n"
            f"See data/README.md for download instructions."
        )
    
    try:
        df = pd.read_csv(filepath)
        return df.copy()
    except Exception as e:
        raise AtlasDataError(f"Failed to read {filepath}: {e}")


def load_radical_pairs(
    data_dir: Optional[Path] = None
) -> pd.DataFrame:
    """
    Load radical pair systems data (READ-ONLY).
    
    Includes: Cryptochrome, photolyase, photosystem II, bacterial reaction centers, etc.
    
    Args:
        data_dir: Override default data directory (for testing)
        
    Returns:
        DataFrame with radical pair systems
        
    Raises:
        AtlasDataError: If file not found or cannot be read
        
    Example:
        >>> from isinglab.data_bridge import load_radical_pairs
        >>> df = load_radical_pairs()
        >>> print(f"Loaded {len(df)} radical pair systems")
    """
    if data_dir is None:
        data_dir = _get_data_directory()
    
    filepath = data_dir / "atlas_nonoptical" / "radical_pair_candidates.csv"
    
    if not filepath.exists():
        filepath = data_dir / "radical_pair_candidates.csv"
    
    if not filepath.exists():
        available = list_available_datasets()
        raise AtlasDataError(
            f"Radical pair data file not found: {filepath}\\n"
            f"Available datasets: {available}\\n"
            f"Expected: data/atlas_nonoptical/radical_pair_candidates.csv\\n"
            f"See data/README.md for download instructions."
        )
    
    try:
        df = pd.read_csv(filepath)
        return df.copy()
    except Exception as e:
        raise AtlasDataError(f"Failed to read {filepath}: {e}")


def load_custom_dataset(
    filename: str,
    data_dir: Optional[Path] = None
) -> pd.DataFrame:
    """
    Load a custom CSV dataset (READ-ONLY).
    
    Args:
        filename: Name of CSV file (e.g., "my_systems.csv")
        data_dir: Override default data directory
        
    Returns:
        DataFrame with loaded data
        
    Raises:
        AtlasDataError: If file not found or cannot be read
    """
    if data_dir is None:
        data_dir = _get_data_directory()
    
    filepath = data_dir / filename
    
    if not filepath.exists():
        available = list_available_datasets()
        raise AtlasDataError(
            f"Dataset not found: {filepath}\\n"
            f"Available datasets: {available}"
        )
    
    try:
        df = pd.read_csv(filepath)
        return df.copy()  # Return copy to ensure READ-ONLY
    except Exception as e:
        raise AtlasDataError(f"Failed to read {filepath}: {e}")


def get_schema_info(df: pd.DataFrame) -> Dict:
    """
    Get schema information for a loaded dataset.
    
    Useful for debugging and validation.
    
    Args:
        df: Loaded DataFrame
        
    Returns:
        Dictionary with schema info (columns, dtypes, null counts)
    """
    return {
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "null_counts": df.isnull().sum().to_dict(),
        "shape": df.shape,
        "sample_row": df.head(1).to_dict("records")[0] if len(df) > 0 else {}
    }


# ============================================================================
# P5 ADDITION : OOP Facade for Atlas Data
# ============================================================================

from .atlas_map import AtlasProfile


class AtlasLoader:
    """
    OOP Facade pour le chargement de l'Atlas.
    
    Intègre les fonctions de chargement existantes (load_optical_systems, etc.)
    dans une interface orientée objet compatible avec AtlasMapper (P2-P5).
    
    Modes de chargement :
        - 'optical' : Systèmes optiques uniquement
        - 'nonoptical' : Systèmes non-optiques uniquement
        - 'all' : Tous les systèmes disponibles
        - 'mock' : Mock data (atlas_mock.csv) pour tests
    
    Usage:
        # Charger tous les systèmes
        loader = AtlasLoader(mode='all', tier='tier1')
        profiles = loader.load_all_profiles()
        
        # Mode mock pour tests
        loader = AtlasLoader(mode='mock')
        profiles = loader.load_all_profiles()
    """
    
    def __init__(
        self,
        mode: str = 'mock',
        tier: str = 'tier1',
        data_dir: Optional[Path] = None
    ):
        """
        Args:
            mode: 'optical', 'nonoptical', 'all', ou 'mock'
            tier: 'tier1', 'tier2', ou 'all' (pour optical/nonoptical)
            data_dir: Override du répertoire de données
        """
        self.mode = mode
        self.tier = tier
        self.data_dir = data_dir
        
        # Cache
        self._profiles_cache: Dict[str, AtlasProfile] = {}
        self._raw_dataframes: Dict[str, pd.DataFrame] = {}
        self._metadata: Dict[str, any] = {}
    
    def load_all_profiles(self) -> Dict[str, AtlasProfile]:
        """
        Charge tous les profils disponibles selon le mode.
        
        Returns:
            Dict de {system_id: AtlasProfile}
        """
        if self.mode == 'mock':
            return self._load_mock_profiles()
        elif self.mode == 'optical':
            return self._load_optical_profiles()
        elif self.mode == 'nonoptical':
            return self._load_nonoptical_profiles()
        elif self.mode == 'all':
            return self._load_all_real_profiles()
        else:
            raise ValueError(f"Mode inconnu : {self.mode}. Utilisez 'optical', 'nonoptical', 'all', ou 'mock'.")
    
    def _load_mock_profiles(self) -> Dict[str, AtlasProfile]:
        """Charge depuis le mock CSV (pour tests)."""
        mock_path = Path(__file__).parent / 'atlas_mock.csv'
        
        if not mock_path.exists():
            raise FileNotFoundError(f"Mock Atlas not found: {mock_path}")
        
        df = pd.read_csv(mock_path)
        return self._parse_dataframe_to_profiles(df, source='mock')
    
    def _load_optical_profiles(self) -> Dict[str, AtlasProfile]:
        """Charge les systèmes optiques via load_optical_systems()."""
        try:
            df = load_optical_systems(tier=self.tier, data_dir=self.data_dir)
            self._raw_dataframes['optical'] = df
            return self._parse_dataframe_to_profiles(df, source='optical')
        except AtlasDataError:
            # Fallback : essayer de charger directement le fichier atlas_fp_optical_v2_2_curated.csv
            try:
                data_dir = self.data_dir if self.data_dir else _get_data_directory()
                fallback_path = data_dir / "atlas_optical" / "atlas_fp_optical_v2_2_curated.csv"
                if fallback_path.exists():
                    df = pd.read_csv(fallback_path)
                    self._raw_dataframes['optical'] = df
                    return self._parse_dataframe_to_profiles(df, source='optical_fp')
            except:
                pass
            return {}
    
    def _load_nonoptical_profiles(self) -> Dict[str, AtlasProfile]:
        """Charge les systèmes non-optiques via load_nonoptical_systems()."""
        try:
            df = load_nonoptical_systems(tier=self.tier, data_dir=self.data_dir)
            self._raw_dataframes['nonoptical'] = df
            return self._parse_dataframe_to_profiles(df, source='nonoptical')
        except AtlasDataError as e:
            print(f"Warning: Cannot load nonoptical systems: {e}")
            return {}
    
    def _load_all_real_profiles(self) -> Dict[str, AtlasProfile]:
        """Charge tous les systèmes (optical + nonoptical)."""
        profiles = {}
        
        # Optical
        optical_profiles = self._load_optical_profiles()
        profiles.update(optical_profiles)
        
        # Nonoptical
        nonoptical_profiles = self._load_nonoptical_profiles()
        profiles.update(nonoptical_profiles)
        
        return profiles
    
    def _parse_dataframe_to_profiles(
        self,
        df: pd.DataFrame,
        source: str = 'unknown'
    ) -> Dict[str, AtlasProfile]:
        """
        Parse un DataFrame en AtlasProfile.
        
        Adapte le schéma Atlas réel au format AtlasProfile (P2).
        """
        profiles = {}
        
        for idx, row in df.iterrows():
            try:
                # Adapter le schéma selon la source
                if source == 'mock':
                    # Mock : schéma simplifié
                    profile = AtlasProfile(
                        system_id=str(row['system_id']),
                        system_name=str(row['system_name']),
                        temperature_k=float(row['temperature_k']),
                        t1_us=float(row['t1_us']),
                        t2_us=float(row['t2_us']),
                        frequency_ghz=float(row['frequency_ghz']),
                        noise_level=float(row['noise_level']),
                        regime_notes=str(row['regime_notes'])
                    )
                else:
                    # Atlas réel : schéma du biological-qubits-atlas
                    protein_name = str(row.get('protein_name', f'sys_{idx}'))
                    system_id = protein_name.replace(' ', '_').replace('/', '_')
                    
                    # Température (défaut biologique : 298K)
                    temp = row.get('temperature_k', 298.0)
                    if pd.isna(temp):
                        temp = 298.0
                    
                    # T1, T2 : Approximations basées sur les propriétés optiques
                    # Pour protéines fluorescentes : tau ~ 1-5 ns, T2 ~ 0.1-10 µs
                    brightness = row.get('brightness_relative', 1.0)
                    if pd.isna(brightness):
                        brightness = 1.0
                    
                    # Approximation : protéines brillantes = meilleure cohérence
                    t1 = 5000.0 * brightness  # 5000 µs * brightness
                    t2 = 10.0 * brightness  # 10 µs * brightness
                    t2 = max(0.1, min(t2, 500))  # Clamp [0.1, 500] µs
                    
                    # Fréquence (optique : ex/em wavelength → frequency)
                    ex_nm = row.get('ex_nm', 500)
                    if pd.isna(ex_nm):
                        ex_nm = 500
                    
                    # λ (nm) → f (GHz): c/λ, mais pour THz on divise par 1000
                    freq_ghz = 299792.458 / ex_nm / 1000  # THz → GHz approx
                    
                    # Noise level : inversement proportionnel au brightness
                    noise = 0.15 / (brightness + 0.1)
                    noise = min(noise, 0.5)
                    
                    # Notes
                    family = row.get('family', 'Unknown')
                    notes = f"{source} | family={family} | brightness={brightness:.2f}"
                    
                    profile = AtlasProfile(
                        system_id=system_id,
                        system_name=protein_name,
                        temperature_k=float(temp),
                        t1_us=float(t1),
                        t2_us=float(t2),
                        frequency_ghz=float(freq_ghz),
                        noise_level=float(noise),
                        regime_notes=notes
                    )
                
                profiles[profile.system_id] = profile
                
            except Exception as e:
                # Skip silencieusement les lignes problématiques
                continue
        
        return profiles
    
    def get_metadata(self) -> Dict:
        """Retourne les métadonnées du chargement."""
        return {
            'mode': self.mode,
            'tier': self.tier,
            'n_systems': len(self._profiles_cache),
            'sources': list(self._raw_dataframes.keys()),
            **self._metadata
        }
    
    def filter_profiles(
        self,
        min_t2: Optional[float] = None,
        max_t2: Optional[float] = None,
        min_temp: Optional[float] = None,
        max_temp: Optional[float] = None
    ) -> Dict[str, AtlasProfile]:
        """
        Filtre les profils selon des critères.
        
        Args:
            min_t2: T2 minimal (µs)
            max_t2: T2 maximal (µs)
            min_temp: Température minimale (K)
            max_temp: Température maximale (K)
            
        Returns:
            Dict filtré de profils
        """
        # Charger si pas encore fait
        if not self._profiles_cache:
            self._profiles_cache = self.load_all_profiles()
        
        filtered = {}
        
        for sys_id, profile in self._profiles_cache.items():
            # Filtres T2
            if min_t2 is not None and profile.t2_us < min_t2:
                continue
            if max_t2 is not None and profile.t2_us > max_t2:
                continue
            
            # Filtres température
            if min_temp is not None and profile.temperature_k < min_temp:
                continue
            if max_temp is not None and profile.temperature_k > max_temp:
                continue
            
            filtered[sys_id] = profile
        
        return filtered
    
    def group_by_coherence_regime(self) -> Dict[str, List[str]]:
        """
        Groupe les systèmes par régime de cohérence (T2).
        
        Returns:
            Dict de {regime_type: [system_ids]}
        """
        # Charger si pas encore fait
        if not self._profiles_cache:
            self._profiles_cache = self.load_all_profiles()
        
        groups = {
            "ultra_short": [],  # T2 < 10µs
            "short": [],        # 10-100µs
            "medium": [],       # 100-500µs
            "long": []          # > 500µs
        }
        
        for sys_id, profile in self._profiles_cache.items():
            if profile.t2_us < 10:
                groups["ultra_short"].append(sys_id)
            elif profile.t2_us < 100:
                groups["short"].append(sys_id)
            elif profile.t2_us < 500:
                groups["medium"].append(sys_id)
            else:
                groups["long"].append(sys_id)
        
        return groups
