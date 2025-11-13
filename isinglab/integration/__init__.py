"""
Integration modules for bridging Ising-Life-Lab with external systems.

Ce module fournit des bridges conceptuels entre les modules mémoire Ising
et des systèmes physiques réels catalogués dans des atlas externes.
"""

from .target_profiles import PHYSICAL_TARGET_PROFILES
from .module_matcher import (
    load_modules_from_export,
    score_module_for_profile,
    rank_modules_for_profile
)

__all__ = [
    'PHYSICAL_TARGET_PROFILES',
    'load_modules_from_export',
    'score_module_for_profile',
    'rank_modules_for_profile'
]

