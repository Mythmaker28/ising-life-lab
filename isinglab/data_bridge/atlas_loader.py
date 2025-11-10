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

