"""
Profile Inference v0.1 - Inférence simple de modules pour systèmes physiques.

Système déterministe basé sur règles heuristiques.
PAS un modèle ML entraîné, juste un squelette pour démonstration.

Version 0.1 : Règles fixes
Version future : ML entraîné sur données Atlas + résultats Ising
"""

from typing import Dict, List, Tuple
from .module_matcher import suggest_modules_for_system_features
from .target_profiles import PHYSICAL_TARGET_PROFILES, PhysicalTargetProfile


def infer_best_profile_for_system(system_features: Dict) -> str:
    """
    Infère le profil cible le plus adapté pour un système physique.
    
    v0.1 : Heuristique simple basée sur system_class et modalités.
    
    Args:
        system_features: Dict avec clés:
            - system_class: type de système
            - modality: modalité principale
            - temp_k: température
            - noise_environment: niveau de bruit
            - integration_hint: contrainte d'intégration
    
    Returns:
        Nom du profil cible (str)
    """
    system_class = system_features.get('system_class', '').lower()
    modality = system_features.get('modality', '').lower()
    noise_env = system_features.get('noise_environment', 'moderate')
    
    # Règles heuristiques v0.1
    if 'nv' in system_class or 'diamond' in system_class:
        return 'nv_cqed_device_grade'
    
    elif 'sic' in system_class or '31p' in system_class or 'solid' in system_class:
        return 'solid_state_non_optical_device_grade'
    
    elif 'radical' in system_class or 'crypto' in system_class or 'bird' in system_class:
        return 'bio_spin_radical_pair'
    
    elif 'biosensor' in system_class or 'gcamp' in system_class or 'dlight' in system_class:
        return 'biosensor_high_contrast'
    
    elif 'ep' in system_class or 'exceptional' in system_class or 'non-hermitian' in system_class:
        return 'ep_like_sensor'
    
    elif 'many-body' in system_class or 'ensemble' in system_class or 'collective' in system_class:
        return 'many_body_enhanced'
    
    elif noise_env == 'high':
        return 'bio_spin_radical_pair'  # Environnement bruité → radical pair
    
    elif 'optical' in modality and noise_env == 'low':
        return 'biosensor_high_contrast'
    
    else:
        return 'quantum_inspired_computing'  # Fallback générique


def suggest_modules_for_system(system_features: Dict, top_k: int = 5,
                               export_path: str = 'results/agi_export_hof.json') -> Dict:
    """
    API principale : suggère modules Ising pour un système physique.
    
    Retourne un dictionnaire structuré avec:
    - profil cible inféré
    - top_k modules classés
    - justification
    
    v0.1 : Système déterministe/heuristique
    """
    # Inférer le profil cible
    profile_name = infer_best_profile_for_system(system_features)
    target_profile = PHYSICAL_TARGET_PROFILES.get(profile_name)
    
    if not target_profile:
        return {
            'error': f'Profile {profile_name} not found',
            'system_features': system_features
        }
    
    # Ranker les modules
    suggestions = suggest_modules_for_system_features(
        system_features,
        export_path=export_path,
        top_k=top_k
    )
    
    # Formater résultat
    result = {
        'system_features': system_features,
        'inferred_profile': profile_name,
        'profile_description': target_profile.description,
        'atlas_system_classes': target_profile.atlas_system_classes,
        'recommendations': []
    }
    
    for score, module, matched_profile in suggestions:
        result['recommendations'].append({
            'rank': len(result['recommendations']) + 1,
            'module_notation': module['notation'],
            'module_profile': module.get('module_profile', 'unknown'),
            'match_score': round(score, 3),
            'scores': module.get('scores', {}),
            'labels': module.get('labels', [])[:5],
            'justification': f"Score={score:.3f}, profil={module.get('module_profile')}"
        })
    
    return result


__all__ = [
    'infer_best_profile_for_system',
    'suggest_modules_for_system'
]

