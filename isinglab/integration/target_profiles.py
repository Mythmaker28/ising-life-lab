"""
Profils physiques cibles inspirés de l'Atlas Quantum-Sensors-Qubits-in-Biology.

Ces profils définissent des exigences qualitatives pour mapper des modules mémoire Ising
vers des classes de systèmes physiques réels (NV, SiC, colour centers, biosenseurs, etc.).

IMPORTANT : Ceci est un bridge conceptuel heuristique.
Les liens Atlas ↔ Ising sont indicatifs, pas des preuves expérimentales.
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class PhysicalTargetProfile:
    """Profil cible physique avec exigences et liens Atlas."""
    
    name: str
    description: str
    
    # Exigences qualitatives (métriques Ising)
    min_robustness: float = 0.0
    min_capacity: float = 0.0
    min_functional: float = 0.0
    
    entropy_range: tuple = (0.0, 1.0)
    basin_diversity_range: tuple = (0.0, 1.0)
    
    # Contraintes contextuelles
    temp_range_k: tuple = (270, 320)  # Température biologique
    preferred_module_profiles: List[str] = None
    
    # Liens textuels Atlas (read-only, conceptuels)
    atlas_system_classes: List[str] = None
    atlas_modalities: List[str] = None
    atlas_notes: str = ""


# === PROFILS INSPIRÉS DE L'ATLAS ===

PHYSICAL_TARGET_PROFILES = {
    'nv_cqed_device_grade': PhysicalTargetProfile(
        name='NV-CQED Device Grade',
        description='Nitrogen-Vacancy centers in diamond, CQED-compatible',
        min_robustness=0.7,
        min_capacity=0.5,
        min_functional=0.6,
        entropy_range=(0.2, 0.5),  # Stable mais pas chaotique
        basin_diversity_range=(0.3, 0.7),
        temp_range_k=(4, 320),  # Large gamme (cryogénique possible)
        preferred_module_profiles=['stable_memory', 'robust_memory'],
        atlas_system_classes=['NV centers', 'Diamond color centers', 'Solid-state spins'],
        atlas_modalities=['optical', 'RF', 'magnetic'],
        atlas_notes='Ref: Atlas Tier 1, NV systems with T2 > 1ms, room temp or cryo'
    ),
    
    'solid_state_non_optical_device_grade': PhysicalTargetProfile(
        name='Solid-State Non-Optical Device Grade',
        description='SiC, 31P, autres systèmes solid-state sans optique',
        min_robustness=0.6,
        min_capacity=0.4,
        min_functional=0.5,
        entropy_range=(0.1, 0.4),  # Très stable
        basin_diversity_range=(0.2, 0.5),
        temp_range_k=(270, 320),
        preferred_module_profiles=['stable_memory', 'attractor_dominant'],
        atlas_system_classes=['SiC defects', '31P in silicon', 'Solid-state qubits'],
        atlas_modalities=['RF', 'magnetic', 'electrical'],
        atlas_notes='Ref: Atlas Tier 1, solid-state with CMOS integration hints'
    ),
    
    'ep_like_sensor': PhysicalTargetProfile(
        name='Exceptional Point-Like Sensor',
        description='Senseurs non-Hermitiens, points exceptionnels',
        min_robustness=0.3,  # Sensibles par nature
        min_capacity=0.2,
        min_functional=0.3,
        entropy_range=(0.5, 0.9),  # Dynamiques sensibles
        basin_diversity_range=(0.4, 0.8),
        temp_range_k=(270, 320),
        preferred_module_profiles=['sensitive_detector', 'chaotic_probe'],
        atlas_system_classes=['Hybrid systems', 'Coupled biosensors', 'Non-Hermitian platforms'],
        atlas_modalities=['optical', 'coupled modes'],
        atlas_notes='Conceptuel: sensibilité amplifiée par proximité points exceptionnels'
    ),
    
    'many_body_enhanced': PhysicalTargetProfile(
        name='Many-Body Enhanced System',
        description='Systèmes many-body / Ising physiques réels',
        min_robustness=0.5,
        min_capacity=0.4,
        min_functional=0.5,
        entropy_range=(0.3, 0.7),
        basin_diversity_range=(0.4, 0.8),  # Bassins multiples
        temp_range_k=(270, 320),
        preferred_module_profiles=['diverse_memory', 'robust_memory'],
        atlas_system_classes=['Coupled spin systems', 'Molecular ensembles', 'Collective modes'],
        atlas_modalities=['magnetic', 'RF', 'optical collective'],
        atlas_notes='Inspiration: systemes many-body de l''Atlas (radical pairs, ensembles moleculaires)'
    ),
    
    'bio_spin_radical_pair': PhysicalTargetProfile(
        name='Bio-Spin Radical Pair',
        description='Radical pairs biologiques (oiseaux, cryptochrome)',
        min_robustness=0.4,
        min_capacity=0.3,
        min_functional=0.4,
        entropy_range=(0.4, 0.8),  # Environnement bruité biologique
        basin_diversity_range=(0.3, 0.7),
        temp_range_k=(285, 310),  # Température physiologique
        preferred_module_profiles=['robust_memory', 'sensitive_detector'],
        atlas_system_classes=['Radical pairs', 'Bio spins', 'Cryptochromes'],
        atlas_modalities=['magnetic', 'optical'],
        atlas_notes='Ref: Atlas Tier 1+2, radical pairs sous bruit thermique, magnetosensors'
    ),
    
    'biosensor_high_contrast': PhysicalTargetProfile(
        name='Biosensor High Contrast',
        description='Biosenseurs optiques (GCaMP, dLight, iGluSnFR)',
        min_robustness=0.6,
        min_capacity=0.5,
        min_functional=0.5,
        entropy_range=(0.2, 0.6),  # Stable pour mesures répétées
        basin_diversity_range=(0.3, 0.6),
        temp_range_k=(295, 310),  # In vivo
        preferred_module_profiles=['stable_memory', 'robust_memory'],
        atlas_system_classes=['GCaMP', 'dLight', 'iGluSnFR', 'Calcium sensors', 'Voltage sensors'],
        atlas_modalities=['optical fluorescence'],
        atlas_notes='Ref: Atlas 180 biosenseurs cures, contrast > 1.5, temperature in vivo'
    ),
    
    'quantum_inspired_computing': PhysicalTargetProfile(
        name='Quantum-Inspired Computing Module',
        description='Modules pour calcul inspiré quantique (pas qubits réels)',
        min_robustness=0.5,
        min_capacity=0.6,
        min_functional=0.6,
        entropy_range=(0.3, 0.7),
        basin_diversity_range=(0.5, 0.9),  # Diversité importante
        temp_range_k=(270, 320),
        preferred_module_profiles=['diverse_memory', 'stable_memory'],
        atlas_system_classes=['Conceptuel: inspiration des architectures Atlas'],
        atlas_modalities=['abstrait'],
        atlas_notes='Bridge conceptuel: metastabilite quantique -> memoire Ising'
    ),
}


def get_profile_by_name(name: str) -> PhysicalTargetProfile:
    """Récupère un profil par nom."""
    return PHYSICAL_TARGET_PROFILES.get(name)


def list_all_profiles() -> List[str]:
    """Liste tous les noms de profils disponibles."""
    return list(PHYSICAL_TARGET_PROFILES.keys())


__all__ = [
    'PhysicalTargetProfile',
    'PHYSICAL_TARGET_PROFILES',
    'get_profile_by_name',
    'list_all_profiles'
]

