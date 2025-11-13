"""
Module Matcher - Apparie modules mémoire Ising avec profils physiques cibles.

Fonctions pures pour scorer et ranker les modules selon leur adéquation
avec des profils cibles (NV, SiC, biosenseurs, etc.).
"""

import json
from pathlib import Path
from typing import List, Dict
from .target_profiles import PhysicalTargetProfile


def load_modules_from_export(export_path: str = 'results/agi_export_hof.json') -> Dict:
    """
    Charge l'export AGI (HoF + memory library).
    
    Returns:
        {'hall_of_fame': [...], 'memory_library': [...]}
    """
    path = Path(export_path)
    if not path.exists():
        return {'hall_of_fame': [], 'memory_library': []}
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data


def score_module_for_profile(module: Dict, target_profile: PhysicalTargetProfile) -> float:
    """
    Score un module Ising pour un profil physique cible.
    
    Scoring :
    - Conformité des métriques (robustness, capacity, functional)
    - Adéquation du module_profile
    - Conformité des ranges (entropy, basin_diversity)
    
    Returns:
        Score dans [0, 1], 1 = parfait match
    """
    scores = module.get('scores', {})
    module_profile = module.get('module_profile', 'unknown')
    
    # 1. Scores fonctionnels
    robustness = scores.get('robustness_score', scores.get('edge_score', 0))
    capacity = scores.get('capacity_score', scores.get('memory_score', 0))
    functional = scores.get('functional_score', scores.get('composite', 0))
    
    # Score robustness
    rob_score = min(robustness / max(target_profile.min_robustness, 0.01), 1.0) if target_profile.min_robustness > 0 else 1.0
    
    # Score capacity
    cap_score = min(capacity / max(target_profile.min_capacity, 0.01), 1.0) if target_profile.min_capacity > 0 else 1.0
    
    # Score functional
    func_score = min(functional / max(target_profile.min_functional, 0.01), 1.0) if target_profile.min_functional > 0 else 1.0
    
    # 2. Conformité entropy
    entropy = scores.get('entropy', 0.5)
    entropy_min, entropy_max = target_profile.entropy_range
    if entropy_min <= entropy <= entropy_max:
        entropy_score = 1.0
    else:
        # Pénalité proportionnelle à la distance
        if entropy < entropy_min:
            entropy_score = max(0, 1.0 - (entropy_min - entropy))
        else:
            entropy_score = max(0, 1.0 - (entropy - entropy_max))
    
    # 3. Conformité basin_diversity
    basin_div = scores.get('basin_diversity', 0.5)
    basin_min, basin_max = target_profile.basin_diversity_range
    if basin_min <= basin_div <= basin_max:
        basin_score = 1.0
    else:
        if basin_div < basin_min:
            basin_score = max(0, 1.0 - (basin_min - basin_div))
        else:
            basin_score = max(0, 1.0 - (basin_div - basin_max))
    
    # 4. Bonus module_profile
    profile_bonus = 0.0
    if target_profile.preferred_module_profiles:
        if module_profile in target_profile.preferred_module_profiles:
            profile_bonus = 0.2
    
    # Score agrégé : pondération
    base_score = (rob_score * 0.3) + (cap_score * 0.25) + (func_score * 0.25) + (entropy_score * 0.1) + (basin_score * 0.1)
    final_score = min(base_score + profile_bonus, 1.0)
    
    return final_score


def rank_modules_for_profile(target_profile: PhysicalTargetProfile,
                             export_path: str = 'results/agi_export_hof.json',
                             source: str = 'memory_library',
                             top_k: int = 10) -> List[tuple]:
    """
    Classe les modules par adéquation avec un profil cible.
    
    Args:
        target_profile: Profil physique cible
        export_path: Chemin vers l'export AGI
        source: 'hall_of_fame' ou 'memory_library'
        top_k: Nombre de top modules à retourner
    
    Returns:
        Liste de (score, module_dict) triée par score décroissant
    """
    data = load_modules_from_export(export_path)
    modules = data.get(source, [])
    
    if not modules:
        return []
    
    # Scorer chaque module
    scored = []
    for module in modules:
        score = score_module_for_profile(module, target_profile)
        scored.append((score, module))
    
    # Trier par score décroissant
    scored.sort(key=lambda x: x[0], reverse=True)
    
    return scored[:top_k]


def suggest_modules_for_system_features(system_features: Dict,
                                       export_path: str = 'results/agi_export_hof.json',
                                       top_k: int = 5) -> List[tuple]:
    """
    Suggère des modules Ising pour un système physique donné.
    
    Args:
        system_features: Dict avec clés possibles:
            - modality: 'optical', 'RF', 'magnetic', etc.
            - temp_k: température de fonctionnement
            - noise_environment: 'low', 'moderate', 'high'
            - integration_hint: 'CMOS', 'fiber', 'cavity', etc.
            - system_class: 'NV', 'SiC', 'biosensor', 'radical_pair', etc.
        export_path: Chemin export AGI
        top_k: Nombre de suggestions
    
    Returns:
        Liste de (score, module, matched_profile_name)
    """
    # Heuristique simple : mapper features → profils cibles
    system_class = system_features.get('system_class', '').lower()
    noise_env = system_features.get('noise_environment', 'moderate')
    temp_k = system_features.get('temp_k', 300)
    
    # Sélection du profil cible (heuristique)
    if 'nv' in system_class or 'diamond' in system_class:
        profile_name = 'nv_cqed_device_grade'
    elif 'sic' in system_class or '31p' in system_class or 'solid' in system_class:
        profile_name = 'solid_state_non_optical_device_grade'
    elif 'radical' in system_class or 'spin' in system_class or 'crypto' in system_class:
        profile_name = 'bio_spin_radical_pair'
    elif 'biosensor' in system_class or 'gcamp' in system_class or 'dlight' in system_class:
        profile_name = 'biosensor_high_contrast'
    elif 'ep' in system_class or 'exceptional' in system_class or 'non-hermitian' in system_class:
        profile_name = 'ep_like_sensor'
    elif noise_env == 'high':
        profile_name = 'bio_spin_radical_pair'  # Environnement bruité
    else:
        profile_name = 'quantum_inspired_computing'  # Fallback générique
    
    # Importer le profil
    from .target_profiles import PHYSICAL_TARGET_PROFILES
    target_profile = PHYSICAL_TARGET_PROFILES.get(profile_name)
    
    if not target_profile:
        return []
    
    # Ranker les modules
    ranked = rank_modules_for_profile(target_profile, export_path, 'memory_library', top_k)
    
    # Ajouter le nom du profil matché
    results = [(score, module, profile_name) for score, module in ranked]
    
    return results


__all__ = [
    'load_modules_from_export',
    'score_module_for_profile',
    'rank_modules_for_profile',
    'suggest_modules_for_system_features'
]

