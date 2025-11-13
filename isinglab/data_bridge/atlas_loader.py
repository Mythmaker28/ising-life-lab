"""
AtlasLoader : Gestion de la connexion à l'Atlas quantique.

Supporte :
    - Mock data (par défaut)
    - Répertoire local de CSV
    - Connexion future à biological-qubits-atlas (dépôt externe)
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import glob

from .atlas_map import AtlasProfile


class AtlasLoader:
    """
    Loader universel pour charger les données de l'Atlas quantique.
    
    Modes de chargement :
        1. 'mock' : Utilise atlas_mock.csv (par défaut, pour tests)
        2. 'local' : Scanne un répertoire local contenant des CSV
        3. 'repository' : Se connecte au dépôt biological-qubits-atlas (futur)
    
    Usage:
        # Mode mock (défaut)
        loader = AtlasLoader()
        
        # Mode local avec répertoire personnalisé
        loader = AtlasLoader(mode='local', data_dir='../biological-qubits-atlas/data')
        
        # Charger les profils
        profiles = loader.load_all_profiles()
    """
    
    def __init__(
        self,
        mode: str = 'mock',
        data_dir: Optional[str] = None,
        repo_path: Optional[str] = None
    ):
        """
        Args:
            mode: 'mock', 'local', ou 'repository'
            data_dir: Chemin vers le répertoire de données (pour mode 'local')
            repo_path: Chemin vers le dépôt biological-qubits-atlas (pour mode 'repository')
        """
        self.mode = mode
        self.data_dir = data_dir
        self.repo_path = repo_path
        
        # Cache des profils chargés
        self._profiles_cache: Dict[str, AtlasProfile] = {}
        self._metadata: Dict[str, any] = {}
        
    def load_all_profiles(self) -> Dict[str, AtlasProfile]:
        """
        Charge tous les profils disponibles selon le mode.
        
        Returns:
            Dict de {system_id: AtlasProfile}
        """
        if self.mode == 'mock':
            return self._load_mock_profiles()
        elif self.mode == 'local':
            return self._load_local_profiles()
        elif self.mode == 'repository':
            return self._load_repository_profiles()
        else:
            raise ValueError(f"Mode inconnu : {self.mode}")
    
    def _load_mock_profiles(self) -> Dict[str, AtlasProfile]:
        """Charge depuis le mock CSV."""
        mock_path = Path(__file__).parent / 'atlas_mock.csv'
        
        if not mock_path.exists():
            raise FileNotFoundError(f"Mock Atlas not found: {mock_path}")
        
        df = pd.read_csv(mock_path)
        return self._parse_dataframe_to_profiles(df)
    
    def _load_local_profiles(self) -> Dict[str, AtlasProfile]:
        """
        Charge depuis un répertoire local de CSV.
        
        Scanne tous les fichiers *.csv dans data_dir et les fusionne.
        """
        if self.data_dir is None:
            raise ValueError("data_dir doit être spécifié pour le mode 'local'")
        
        data_path = Path(self.data_dir)
        
        if not data_path.exists():
            raise FileNotFoundError(f"Data directory not found: {data_path}")
        
        # Scanner tous les CSV
        csv_files = list(data_path.glob('**/*.csv'))
        
        if len(csv_files) == 0:
            raise FileNotFoundError(f"Aucun fichier CSV trouvé dans {data_path}")
        
        # Fusionner tous les CSV
        dfs = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                # Ajouter métadata sur la source
                df['source_file'] = csv_file.name
                dfs.append(df)
            except Exception as e:
                print(f"Warning: Failed to load {csv_file}: {e}")
        
        if len(dfs) == 0:
            raise ValueError("Aucun CSV valide chargé")
        
        # Concaténer
        df_combined = pd.concat(dfs, ignore_index=True)
        
        # Dédupliquer par system_id
        if 'system_id' in df_combined.columns:
            df_combined = df_combined.drop_duplicates(subset='system_id', keep='first')
        
        self._metadata['n_sources'] = len(csv_files)
        self._metadata['n_systems'] = len(df_combined)
        
        return self._parse_dataframe_to_profiles(df_combined)
    
    def _load_repository_profiles(self) -> Dict[str, AtlasProfile]:
        """
        Charge depuis le dépôt biological-qubits-atlas.
        
        TODO : Implémentation complète quand le dépôt existe.
        Pour l'instant : fallback vers local ou mock.
        """
        if self.repo_path is None:
            # Essayer des chemins standards
            possible_paths = [
                Path(__file__).parent.parent.parent.parent / 'biological-qubits-atlas' / 'data',
                Path.home() / 'Documents' / 'biological-qubits-atlas' / 'data',
                Path('../biological-qubits-atlas/data')
            ]
            
            for path in possible_paths:
                if path.exists():
                    print(f"✓ Found biological-qubits-atlas at: {path}")
                    self.data_dir = str(path)
                    return self._load_local_profiles()
            
            # Fallback vers mock
            print(f"Warning: biological-qubits-atlas not found. Falling back to mock.")
            return self._load_mock_profiles()
        else:
            # Utiliser le chemin spécifié
            self.data_dir = str(Path(self.repo_path) / 'data')
            return self._load_local_profiles()
    
    def _parse_dataframe_to_profiles(self, df: pd.DataFrame) -> Dict[str, AtlasProfile]:
        """
        Parse un DataFrame en AtlasProfile.
        
        Colonnes requises : system_id, system_name, temperature_k, t1_us, t2_us,
                           frequency_ghz, noise_level, regime_notes
        """
        profiles = {}
        
        required_cols = ['system_id', 'system_name', 'temperature_k', 't1_us', 
                        't2_us', 'frequency_ghz', 'noise_level', 'regime_notes']
        
        # Vérifier les colonnes
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Colonnes manquantes dans le CSV : {missing_cols}")
        
        for _, row in df.iterrows():
            try:
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
                profiles[profile.system_id] = profile
            except Exception as e:
                print(f"Warning: Failed to parse row {row.get('system_id', '?')}: {e}")
        
        return profiles
    
    def get_metadata(self) -> Dict:
        """Retourne les métadonnées du chargement."""
        return {
            'mode': self.mode,
            'data_dir': self.data_dir,
            'n_systems': len(self._profiles_cache),
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
    
    def group_by_regime(self) -> Dict[str, List[str]]:
        """
        Groupe les systèmes par type de régime.
        
        Returns:
            Dict de {regime_type: [system_ids]}
        """
        groups = {}
        
        for sys_id, profile in self._profiles_cache.items():
            # Catégoriser par T2
            if profile.t2_us < 10:
                regime = "ultra_short_coherence"
            elif profile.t2_us < 100:
                regime = "short_coherence"
            elif profile.t2_us < 500:
                regime = "medium_coherence"
            else:
                regime = "long_coherence"
            
            if regime not in groups:
                groups[regime] = []
            groups[regime].append(sys_id)
        
        return groups
