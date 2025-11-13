"""
Opérations sur règles CA : compléments, duals, distances, normalisations.

Utilitaires pour manipuler et analyser les règles Life-like.
"""

from typing import List, Tuple


def parse_notation(notation: str) -> Tuple[List[int], List[int]]:
    """Parse notation B.../S... en listes born/survive."""
    if '/' not in notation:
        raise ValueError(f"Invalid notation: {notation}")
    
    parts = notation.split('/')
    born_str = parts[0].replace('B', '').replace('b', '')
    survive_str = parts[1].replace('S', '').replace('s', '')
    
    born = [int(c) for c in born_str if c.isdigit()]
    survive = [int(c) for c in survive_str if c.isdigit()]
    
    return sorted(born), sorted(survive)


def to_notation(born: List[int], survive: List[int]) -> str:
    """Convertit born/survive en notation standard."""
    born_str = ''.join(map(str, sorted(born)))
    survive_str = ''.join(map(str, sorted(survive)))
    return f"B{born_str}/S{survive_str}"


def complement_rule(notation: str) -> str:
    """
    Calcule le complément d'une règle.
    
    Complément = règle qui donne résultat inverse sur grille inversée.
    Pour Life-like: born_complement = {8-n for n in survive}, survive_complement = {8-n for n in born}
    
    Exemple:
        B3/S23 → B456/S0145678
        Day & Night B3678/S34678 → B3678/S34678 (auto-complémentaire)
    
    Returns:
        Notation du complément
    """
    born, survive = parse_notation(notation)
    
    # Complément : inverser born ↔ survive et prendre 8-n
    born_comp = sorted([8 - s for s in survive])
    survive_comp = sorted([8 - s for s in born])
    
    return to_notation(born_comp, survive_comp)


def is_self_complementary(notation: str) -> bool:
    """Vérifie si une règle est auto-complémentaire (règle = complément)."""
    comp = complement_rule(notation)
    return normalize_notation(notation) == normalize_notation(comp)


def normalize_notation(notation: str) -> str:
    """Normalise notation (tri born/survive, uppercase)."""
    born, survive = parse_notation(notation)
    return to_notation(born, survive).upper()


def rule_distance(notation1: str, notation2: str) -> int:
    """
    Distance de Hamming entre deux règles.
    
    Compte différences dans born et survive.
    """
    born1, survive1 = parse_notation(notation1)
    born2, survive2 = parse_notation(notation2)
    
    born1_set = set(born1)
    born2_set = set(born2)
    survive1_set = set(survive1)
    survive2_set = set(survive2)
    
    # Différence symétrique
    dist_born = len(born1_set ^ born2_set)
    dist_survive = len(survive1_set ^ survive2_set)
    
    return dist_born + dist_survive


def generate_neighbors(notation: str, radius: int = 1) -> List[str]:
    """
    Génère voisins à distance radius (mutations single-flip).
    
    Args:
        notation: Règle de base
        radius: Distance de mutation (1 = add/remove 1 digit)
    
    Returns:
        Liste de notations voisines
    """
    born, survive = parse_notation(notation)
    neighbors = []
    seen = set([notation])
    
    # Mutations born
    for b in range(9):
        if b in born and len(born) > 1:
            new_born = [x for x in born if x != b]
            new_notation = to_notation(new_born, survive)
            if new_notation not in seen:
                neighbors.append(new_notation)
                seen.add(new_notation)
        elif b not in born:
            new_born = sorted(born + [b])
            new_notation = to_notation(new_born, survive)
            if new_notation not in seen:
                neighbors.append(new_notation)
                seen.add(new_notation)
    
    # Mutations survive
    for s in range(9):
        if s in survive and len(survive) > 1:
            new_survive = [x for x in survive if x != s]
            new_notation = to_notation(born, new_survive)
            if new_notation not in seen:
                neighbors.append(new_notation)
                seen.add(new_notation)
        elif s not in survive:
            new_survive = sorted(survive + [s])
            new_notation = to_notation(born, new_survive)
            if new_notation not in seen:
                neighbors.append(new_notation)
                seen.add(new_notation)
    
    return neighbors


__all__ = [
    'parse_notation',
    'to_notation',
    'complement_rule',
    'is_self_complementary',
    'normalize_notation',
    'rule_distance',
    'generate_neighbors'
]

