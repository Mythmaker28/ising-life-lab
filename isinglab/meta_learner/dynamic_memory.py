"""Dynamic Memory Manager pour AGI v3

Gère la mémoire dynamique avec HoF pendant la découverte.
Compatible avec l'API attendue par ClosedLoopAGIv3.
"""

import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import numpy as np

from isinglab.rules import load_hof_rules, add_or_update_rule, save_hof_rules


def convert_numpy_types(obj):
    """Convertit récursivement les types NumPy en types Python natifs."""
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


class DynamicMemoryManager:
    """Gestionnaire mémoire dynamique pour boucle AGI."""
    
    def __init__(self, memory_path='results/agi_memory.json', hof_path='isinglab/rules/hof_rules.json'):
        self.memory_path = Path(memory_path)
        self.hof_path = Path(hof_path)
        self.memory_rules: List[Dict] = []
        self.hof_rules: List[Dict] = []
        self.hof_config = {
            'max_size': 25,
            'composite_min': 80,
            'memory_score_min_abs': 0.01,
            'edge_score_min_abs': 0.05,
            'entropy_min_abs': 0.0
        }
    
    def aggregate_memory(self):
        """Charge la mémoire existante + HoF."""
        # Charger mémoire
        if self.memory_path.exists():
            with open(self.memory_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.memory_rules = data.get('rules', [])
        else:
            self.memory_rules = []
        
        # Charger HoF
        self.hof_rules = load_hof_rules()
    
    def add_or_update_rule(self, rule: Dict):
        """Ajoute ou met à jour une règle dans la mémoire."""
        notation = rule.get('notation')
        if not notation:
            return
        
        # Chercher si existe
        existing_idx = None
        for i, r in enumerate(self.memory_rules):
            if r.get('notation') == notation:
                existing_idx = i
                break
        
        if existing_idx is not None:
            # Mise à jour
            self.memory_rules[existing_idx].update(rule)
        else:
            # Ajout
            self.memory_rules.append(rule)
    
    def update_hof(self):
        """Met à jour le Hall of Fame basé sur les règles en mémoire."""
        # Filtrer rules non-triviales avec functional_score
        candidates = [
            r for r in self.memory_rules
            if not r.get('trivial', False) and r.get('functional_score', 0) > 0
        ]
        
        # Trier par functional_score
        candidates_sorted = sorted(
            candidates,
            key=lambda r: r.get('functional_score', 0),
            reverse=True
        )
        
        # Top N
        max_size = self.hof_config['max_size']
        self.hof_rules = candidates_sorted[:max_size]
    
    def save_memory(self):
        """Sauvegarde la mémoire (convertit types NumPy)."""
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'meta': {
                'updated': datetime.now().isoformat(),
                'count': len(self.memory_rules)
            },
            'rules': convert_numpy_types(self.memory_rules)
        }
        
        with open(self.memory_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def save_hof(self):
        """Sauvegarde le HoF (convertit types NumPy)."""
        # Convertir en format HoF
        hof_data = {
            'meta': {
                'updated': datetime.now().isoformat(),
                'count': len(self.hof_rules)
            },
            'rules': convert_numpy_types(self.hof_rules)
        }
        
        self.hof_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.hof_path, 'w', encoding='utf-8') as f:
            json.dump(hof_data, f, indent=2)


__all__ = ['DynamicMemoryManager']

