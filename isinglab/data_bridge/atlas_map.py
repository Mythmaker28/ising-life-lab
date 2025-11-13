"""
Atlas Mapper : Pont entre paramètres physiques quantiques et paramètres phénoménologiques.

Objectif : Traduire les contraintes physiques (T1, T2, Température, Fréquence)
en paramètres du moteur d'oscillateurs (K, Bruit, Annealing).

Formules de mapping empiriques :
    - Bruit ∝ 1/T2 (cohérence courte → bruit élevé)
    - K_max ∝ √(T1·T2) (force de couplage limitée par cohérence)
    - Annealing ∝ exp(-T/T_ref) (température → taux de relaxation)
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass


@dataclass
class AtlasProfile:
    """Profil physique d'un système quantique extrait de l'Atlas."""
    
    system_id: str
    system_name: str
    temperature_k: float
    t1_us: float  # Temps de relaxation (microseconds)
    t2_us: float  # Temps de cohérence (microseconds)
    frequency_ghz: float
    noise_level: float
    regime_notes: str
    
    def __repr__(self):
        return (f"AtlasProfile(id={self.system_id}, T={self.temperature_k}K, "
                f"T2={self.t2_us}µs, noise={self.noise_level:.3f})")


@dataclass
class PhenoParams:
    """Paramètres phénoménologiques pour le moteur d'oscillateurs."""
    
    k1_strength: float
    k2_strength: float
    k3_strength: float
    dt: float
    noise_amplitude: float
    annealing_rate: float
    
    # Métadonnées
    source_system: str
    physical_validity: float  # Score [0, 1] de plausibilité physique
    
    def to_dict(self) -> Dict:
        return {
            'k1_strength': self.k1_strength,
            'k2_strength': self.k2_strength,
            'k3_strength': self.k3_strength,
            'dt': self.dt,
            'noise_amplitude': self.noise_amplitude,
            'annealing_rate': self.annealing_rate,
        }


class AtlasMapper:
    """
    Mapper central : Atlas physique → Paramètres phénoménologiques.
    
    Usage:
        mapper = AtlasMapper()
        mapper.load_atlas('path/to/atlas.csv')
        
        profile = mapper.get_profile('NV-298K')
        pheno_params = mapper.map_to_pheno(profile, regime='uniform')
    """
    
    # Constantes de normalisation (calibrées empiriquement)
    T2_REF = 100.0  # µs (référence pour le bruit)
    T_REF = 300.0   # K (température de référence pour annealing)
    COUPLING_SCALE = 0.01  # Facteur d'échelle √(T1·T2) → K
    
    def __init__(
        self,
        atlas_path: Optional[str] = None,
        atlas_loader=None,
        mode: str = 'mock'
    ):
        """
        Args:
            atlas_path: Chemin vers le CSV de l'Atlas (legacy)
            atlas_loader: Instance d'AtlasLoader (nouveau, P5)
            mode: 'mock', 'local', ou 'repository' (si atlas_loader est None)
        """
        self.atlas_df: Optional[pd.DataFrame] = None
        self.profiles: Dict[str, AtlasProfile] = {}
        self.loader = atlas_loader
        
        if atlas_loader is not None:
            # P5 : Utiliser AtlasLoader
            self.profiles = atlas_loader.load_all_profiles()
            atlas_loader._profiles_cache = self.profiles
        elif atlas_path is None:
            # Legacy : Charger le mock par défaut
            default_path = Path(__file__).parent / 'atlas_mock.csv'
            if default_path.exists():
                self.load_atlas(str(default_path))
        else:
            # Legacy : Charger depuis un chemin spécifique
            self.load_atlas(atlas_path)
    
    def load_atlas(self, path: str) -> None:
        """Charge l'Atlas depuis un fichier CSV."""
        self.atlas_df = pd.read_csv(path)
        
        # Parser en AtlasProfile
        self.profiles = {}
        for _, row in self.atlas_df.iterrows():
            profile = AtlasProfile(
                system_id=row['system_id'],
                system_name=row['system_name'],
                temperature_k=float(row['temperature_k']),
                t1_us=float(row['t1_us']),
                t2_us=float(row['t2_us']),
                frequency_ghz=float(row['frequency_ghz']),
                noise_level=float(row['noise_level']),
                regime_notes=row['regime_notes']
            )
            self.profiles[profile.system_id] = profile
    
    def get_profile(self, system_id: str) -> AtlasProfile:
        """Récupère un profil physique par son ID."""
        if system_id not in self.profiles:
            raise ValueError(
                f"System '{system_id}' not found in Atlas. "
                f"Available: {list(self.profiles.keys())}"
            )
        return self.profiles[system_id]
    
    def list_systems(self) -> list:
        """Liste tous les systèmes disponibles."""
        return list(self.profiles.keys())
    
    def map_to_pheno(
        self,
        profile: AtlasProfile,
        regime: str = 'balanced',
        target_k1: Optional[float] = None
    ) -> PhenoParams:
        """
        Mappe un profil physique en paramètres phénoménologiques.
        
        Args:
            profile: Profil physique Atlas
            regime: 'uniform' (5-MeO-like), 'fragmented' (DMT-like), 'balanced'
            target_k1: Si spécifié, force K1 à cette valeur
            
        Returns:
            PhenoParams calibrés
        """
        # 1. Bruit : inversement proportionnel à T2
        noise_amplitude = self._compute_noise(profile.t2_us)
        
        # 2. Force de couplage : limitée par √(T1·T2)
        k_max = self._compute_k_max(profile.t1_us, profile.t2_us)
        
        # 3. Annealing : dépend de la température
        annealing_rate = self._compute_annealing(profile.temperature_k)
        
        # 4. Configuration des kernels selon le régime
        if regime == 'uniform':
            # Configuration 5-MeO-DMT : K1 dominant
            k1 = target_k1 if target_k1 is not None else min(k_max, 2.0)
            k2 = 0.0
            k3 = 0.0
            
        elif regime == 'fragmented':
            # Configuration DMT : kernels compétitifs
            k1 = target_k1 if target_k1 is not None else min(k_max * 0.6, 1.2)
            k2 = min(k_max * 0.4, 0.8)  # Compétitif (sera négatif dans le preset)
            k3 = min(k_max * 0.15, 0.3)
            
        else:  # balanced
            k1 = target_k1 if target_k1 is not None else min(k_max * 0.7, 1.5)
            k2 = min(k_max * 0.2, 0.4)
            k3 = min(k_max * 0.1, 0.2)
        
        # 5. Pas de temps : ajusté selon la fréquence
        dt = self._compute_dt(profile.frequency_ghz)
        
        # 6. Validation physique
        validity = self._assess_validity(profile, k1, noise_amplitude)
        
        return PhenoParams(
            k1_strength=k1,
            k2_strength=k2,
            k3_strength=k3,
            dt=dt,
            noise_amplitude=noise_amplitude,
            annealing_rate=annealing_rate,
            source_system=profile.system_id,
            physical_validity=validity
        )
    
    def _compute_noise(self, t2_us: float) -> float:
        """
        Bruit ∝ 1/T2.
        
        T2 court → bruit élevé (décohérence rapide)
        T2 long → bruit faible (cohérence préservée)
        """
        noise = (self.T2_REF / t2_us) * 0.05  # Normalisé à ~0.05 pour T2=100µs
        return np.clip(noise, 0.001, 0.5)
    
    def _compute_k_max(self, t1_us: float, t2_us: float) -> float:
        """
        Force de couplage maximale ∝ √(T1·T2).
        
        Interprétation : Les couplages forts nécessitent à la fois
        longue cohérence (T2) et stabilité énergétique (T1).
        """
        k_max = self.COUPLING_SCALE * np.sqrt(t1_us * t2_us)
        return np.clip(k_max, 0.1, 10.0)
    
    def _compute_annealing(self, temperature_k: float) -> float:
        """
        Annealing ∝ exp(-T/T_ref).
        
        Haute température → annealing fort (relaxation thermique)
        Basse température → annealing faible (figé)
        """
        annealing = 0.5 * np.exp(-(temperature_k / self.T_REF))
        return np.clip(annealing, 0.0, 1.0)
    
    def _compute_dt(self, frequency_ghz: float) -> float:
        """Pas de temps adapté à la fréquence du système."""
        # dt ~ 1/(10·f) pour capturer la dynamique
        dt = 1.0 / (10.0 * frequency_ghz + 1.0)
        return np.clip(dt, 0.01, 0.2)
    
    def _assess_validity(
        self,
        profile: AtlasProfile,
        k1: float,
        noise: float
    ) -> float:
        """
        Évalue la plausibilité physique des paramètres mappés.
        
        Returns:
            Score [0, 1] où 1 = physiquement réalisable
        """
        validity = 1.0
        
        # Pénalité si K1 trop fort pour le T2 disponible
        k_max_safe = self._compute_k_max(profile.t1_us, profile.t2_us)
        if k1 > k_max_safe * 1.5:
            validity *= 0.5
        
        # Pénalité si bruit incohérent avec T2
        expected_noise = self._compute_noise(profile.t2_us)
        if abs(noise - expected_noise) > expected_noise * 0.5:
            validity *= 0.7
        
        # Bonus si T2 > 10µs (cohérence minimale)
        if profile.t2_us > 10.0:
            validity *= 1.0
        else:
            validity *= 0.6
        
        return np.clip(validity, 0.0, 1.0)
    
    def compare_systems(self, system_ids: list) -> pd.DataFrame:
        """Compare plusieurs systèmes côte à côte."""
        data = []
        for sys_id in system_ids:
            profile = self.get_profile(sys_id)
            pheno_uniform = self.map_to_pheno(profile, regime='uniform')
            pheno_frag = self.map_to_pheno(profile, regime='fragmented')
            
            data.append({
                'system_id': sys_id,
                'T (K)': profile.temperature_k,
                'T2 (µs)': profile.t2_us,
                'K1_uniform': pheno_uniform.k1_strength,
                'Noise_uniform': pheno_uniform.noise_amplitude,
                'K1_frag': pheno_frag.k1_strength,
                'Noise_frag': pheno_frag.noise_amplitude,
                'Validity': pheno_uniform.physical_validity
            })
        
        return pd.DataFrame(data)

