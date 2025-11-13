"""
Sélection Pareto multi-objectif pour le Hall of Fame.

Au lieu de top N d'un score composite, on garde un ensemble de règles
non-dominées sur plusieurs objectifs.
"""

from typing import List, Dict, Tuple
import numpy as np


def dominates(rule_a: Dict, rule_b: Dict, objectives: List[str]) -> bool:
    """
    Vérifie si rule_a domine rule_b sur tous les objectifs.
    
    rule_a domine rule_b si :
    - rule_a >= rule_b sur tous les objectifs
    - rule_a > rule_b sur au moins un objectif
    """
    better_or_equal_all = True
    strictly_better_any = False
    
    for obj in objectives:
        val_a = rule_a.get(obj, 0)
        val_b = rule_b.get(obj, 0)
        
        if val_a < val_b:
            better_or_equal_all = False
            break
        if val_a > val_b:
            strictly_better_any = True
    
    return better_or_equal_all and strictly_better_any


def pareto_front(rules: List[Dict], objectives: List[str]) -> List[Dict]:
    """
    Calcule le front de Pareto : ensemble des règles non-dominées.
    
    Une règle est non-dominée si aucune autre règle ne la domine.
    """
    if not rules:
        return []
    
    pareto_set = []
    
    for rule_a in rules:
        is_dominated = False
        for rule_b in rules:
            if rule_a is rule_b:
                continue
            if dominates(rule_b, rule_a, objectives):
                is_dominated = True
                break
        
        if not is_dominated:
            pareto_set.append(rule_a)
    
    return pareto_set


def select_pareto_hof(candidates: List[Dict], current_hof: List[Dict],
                     objectives: List[str], max_size: int = 20,
                     diversity_threshold: float = 2.0) -> Tuple[List[Dict], List[Dict]]:
    """
    Sélectionne les règles HoF selon critère Pareto + diversité.
    
    Processus :
    1. Fusionner candidates + current_hof
    2. Calculer front de Pareto
    3. Appliquer filtre diversité
    4. Limiter à max_size
    5. Retourner (promoted, removed)
    """
    # Fusionner tout
    all_rules = current_hof + candidates
    
    # Calculer front de Pareto
    pareto_rules = pareto_front(all_rules, objectives)
    
    # Si trop de règles, garder les max_size meilleures
    if len(pareto_rules) > max_size:
        # Trier par score composite pour départager
        composite_scores = []
        for rule in pareto_rules:
            composite = sum(rule.get(obj, 0) for obj in objectives) / len(objectives)
            composite_scores.append((composite, rule))
        composite_scores.sort(key=lambda x: x[0], reverse=True)
        pareto_rules = [rule for _, rule in composite_scores[:max_size]]
    
    # Appliquer diversité (distance Hamming)
    diverse_rules = []
    for rule in pareto_rules:
        # Vérifier distance avec règles déjà dans diverse_rules
        is_diverse = True
        for existing in diverse_rules:
            dist = compute_hamming_distance(rule, existing)
            if dist < diversity_threshold:
                # Garder la meilleure des deux
                composite_rule = sum(rule.get(obj, 0) for obj in objectives) / len(objectives)
                composite_existing = sum(existing.get(obj, 0) for obj in objectives) / len(objectives)
                if composite_rule > composite_existing:
                    diverse_rules.remove(existing)
                    diverse_rules.append(rule)
                is_diverse = False
                break
        
        if is_diverse:
            diverse_rules.append(rule)
    
    # Déterminer promoted et removed
    current_notations = {r.get('notation') for r in current_hof}
    promoted = [r for r in diverse_rules if r.get('notation') not in current_notations]
    
    new_notations = {r.get('notation') for r in diverse_rules}
    removed = [r for r in current_hof if r.get('notation') not in new_notations]
    
    return promoted, removed


def compute_hamming_distance(rule1: Dict, rule2: Dict) -> int:
    """Calcule distance de Hamming entre born/survive."""
    born1 = set(rule1.get('born', []))
    born2 = set(rule2.get('born', []))
    survive1 = set(rule1.get('survive', []))
    survive2 = set(rule2.get('survive', []))
    
    dist = len(born1 ^ born2) + len(survive1 ^ survive2)
    return dist


__all__ = ['pareto_front', 'select_pareto_hof', 'dominates']

