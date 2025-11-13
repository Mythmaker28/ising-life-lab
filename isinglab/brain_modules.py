"""
Brain Modules v4.0 — Catalogue canonique des modules CA validés.

Ce module expose les 5 brain modules v3.5 avec leurs propriétés documentées.
"""

from typing import Dict, List, Tuple, Optional
from .core.ca_vectorized import create_rule_function_vectorized


# Catalogue des brain modules validés
BRAIN_MODULES = {
    "life": {
        "notation": "B3/S23",
        "born": [3],
        "survive": [2, 3],
        "profile": "sparse_memory",
        "life_capacity": 0.70,
        "robustness": 0.20,
        "functional_score": 0.00,
        "description": "Conway's Life — Baseline compute/mémoire propre, référence pour patterns Life canoniques",
        "role": "Compute / Mémoire propre / Référence",
        "tier": 1
    },
    "highlife": {
        "notation": "B36/S23",
        "born": [3, 6],
        "survive": [2, 3],
        "profile": "replicator",
        "life_capacity": 0.70,
        "robustness": 0.20,
        "functional_score": 0.00,
        "description": "HighLife — Life-compatible avec réplication additionnelle (B6), propagation",
        "role": "Réplication / Propagation",
        "tier": 1
    },
    "life_dense": {
        "notation": "B3/S234",
        "born": [3],
        "survive": [2, 3, 4],
        "profile": "dense_memory",
        "life_capacity": 0.68,
        "robustness": 0.24,
        "functional_score": 0.00,
        "description": "Life dense stable — Variante Life avec stabilité accrue (S4), tolérance bruit améliorée",
        "role": "Variante Life dense/stable",
        "tier": 1
    },
    "34life": {
        "notation": "B34/S34",
        "born": [3, 4],
        "survive": [3, 4],
        "profile": "robust_frontend",
        "life_capacity": 0.32,
        "robustness": 0.20,
        "functional_score": 0.00,
        "description": "34 Life — Front-end robuste, préserve still-lifes + spaceships, tue oscillateurs period-2",
        "role": "Front-end robuste / Filtrage",
        "tier": 1,
        "limitation": "Ne pas utiliser pour mémoire patterns complexes (life_capacity limitée)"
    },
    "36_234": {
        "notation": "B36/S234",
        "born": [3, 6],
        "survive": [2, 3, 4],
        "profile": "spin_glass_like",
        "life_capacity": 0.68,  # Estimé basé sur documentation
        "robustness": 0.25,  # Estimé basé sur documentation
        "functional_score": 0.00,
        "description": "HighLife stabilisé — HighLife + S4, réplication + robustesse",
        "role": "Backup / HighLife stabilisé",
        "tier": 2
    }
}


def get_brain(name: str) -> Optional[Dict]:
    """
    Récupère la configuration d'un brain module par son nom.
    
    Args:
        name: Nom du module ("life", "highlife", "life_dense", "34life", "36_234")
    
    Returns:
        Dict avec configuration du module, ou None si non trouvé
    """
    return BRAIN_MODULES.get(name)


def list_brains() -> List[str]:
    """
    Liste tous les brain modules disponibles.
    
    Returns:
        Liste des noms de modules
    """
    return list(BRAIN_MODULES.keys())


def get_brain_by_notation(notation: str) -> Optional[Dict]:
    """
    Récupère un brain module par sa notation B/S.
    
    Args:
        notation: Notation B/S (ex: "B3/S23")
    
    Returns:
        Dict avec configuration du module, ou None si non trouvé
    """
    for name, config in BRAIN_MODULES.items():
        if config["notation"] == notation:
            return config
    return None


def get_brain_rule_function(name: str):
    """
    Récupère la fonction règle vectorisée d'un brain module.
    
    Args:
        name: Nom du module
    
    Returns:
        Fonction règle vectorisée (grid -> new_grid)
    """
    config = get_brain(name)
    if config is None:
        raise ValueError(f"Brain module '{name}' not found")
    
    return create_rule_function_vectorized(config["born"], config["survive"])


def get_tier1_brains() -> List[str]:
    """
    Récupère la liste des brain modules Tier 1 (validés prioritaires).
    
    Returns:
        Liste des noms de modules Tier 1
    """
    return [name for name, config in BRAIN_MODULES.items() if config.get("tier", 2) == 1]


__all__ = [
    'BRAIN_MODULES',
    'get_brain',
    'list_brains',
    'get_brain_by_notation',
    'get_brain_rule_function',
    'get_tier1_brains'
]



