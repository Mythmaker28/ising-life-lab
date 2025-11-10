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
    filepath = data_dir / filename
    
    if not filepath.exists():
        available = list_available_datasets()
        raise AtlasDataError(
            f"Optical data file not found: {filepath}\\n"
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
    filepath = data_dir / filename
    
    if not filepath.exists():
        available = list_available_datasets()
        raise AtlasDataError(
            f"Non-optical data file not found: {filepath}\\n"
            f"Available datasets: {available}\\n"
            f"Expected directory: {data_dir}\\n"
            f"Ensure Atlas CSV exports are placed in data/ directory."
        )
    
    try:
        df = pd.read_csv(filepath)
        return df.copy()  # Return copy to ensure READ-ONLY
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

