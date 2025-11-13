"""
Export Memory Library v2.1 - Exporte le HoF et la méta-mémoire vers un format réutilisable.

Usage:
    python -m isinglab.export_memory_library
    
Produit:
    results/agi_export_hof.json : HoF exporté avec scores, profils et usages suggérés
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

from .metrics.functional import infer_module_profile


def load_meta_memory(path: str = 'results/meta_memory.json') -> List[Dict]:
    """Charge la méta-mémoire."""
    meta_path = Path(path)
    if not meta_path.exists():
        print(f"[WARN] {path} n'existe pas.")
        return []
    
    with open(meta_path, encoding='utf-8') as fh:
        data = json.load(fh)
    return data.get('rules', [])


def load_hof_rules(path: str = 'isinglab/rules/hof_rules.json') -> List[Dict]:
    """Charge les règles du Hall of Fame."""
    hof_path = Path(path)
    if not hof_path.exists():
        print(f"[WARN] {path} n'existe pas.")
        return []
    
    with open(hof_path, encoding='utf-8') as fh:
        data = json.load(fh)
    return data.get('rules', [])


def compute_diversity_signature(born: List, survive: List) -> str:
    """Calcule une signature de diversité pour une règle."""
    born_str = ''.join(map(str, sorted(born)))
    survive_str = ''.join(map(str, sorted(survive)))
    # Signature : B{count}_{digits}/S{count}_{digits}
    return f"B{len(born)}_{born_str}/S{len(survive)}_{survive_str}"


def infer_tags_from_scores(scores: Dict) -> List[str]:
    """Infère des tags enrichis à partir des scores."""
    tags = []
    
    memory = scores.get('memory_score', 0)
    edge = scores.get('edge_score', 0)
    entropy = scores.get('entropy', 0)
    
    # Tags de mémoire
    if memory > 0.5:
        tags.append('high_memory')
    elif memory > 0.1:
        tags.append('moderate_memory')
    else:
        tags.append('low_memory')
    
    # Tags d'edge/robustesse
    if edge > 0.3:
        tags.append('robust')
    elif edge > 0.15:
        tags.append('moderate_edge')
    else:
        tags.append('fragile')
    
    # Tags d'entropie/dynamisme
    if entropy > 0.7:
        tags.append('high_entropy')
        tags.append('dynamic')
    elif entropy > 0.3:
        tags.append('moderate_entropy')
    else:
        tags.append('static')
    
    return tags


def export_hof_library(output_path: str = 'results/agi_export_hof.json'):
    """
    v2.0: Exporte le HoF + méta-mémoire avec diversity_signature et tags enrichis.
    """
    print("=" * 64)
    print("EXPORT MEMORY LIBRARY v2.0")
    print("=" * 64)
    
    # Charger les sources
    meta_memory = load_meta_memory()
    hof_rules = load_hof_rules()
    
    print(f"[OK] Charge {len(meta_memory)} regles depuis meta_memory.json")
    print(f"[OK] Charge {len(hof_rules)} regles depuis hof_rules.json")
    
    # Fusionner et enrichir
    export_data = {
        'meta': {
            'exported_at': datetime.now().isoformat(),
            'version': 'v2.0',
            'description': 'Ising Life Lab - AGI Memory & Hall of Fame Export (Adaptive + Diversity)',
            'origin': 'ising-life-lab',
            'total_hof_rules': len(hof_rules),
            'total_memory_rules': len(meta_memory)
        },
        'hall_of_fame': [],
        'memory_library': []
    }
    
    # Exporter le HoF avec enrichissements v2.0
    for rule in hof_rules:
        born = rule.get('born', [])
        survive = rule.get('survive', [])
        scores = {
            'memory_score': rule.get('avg_recall', 0) / 100 if rule.get('avg_recall') else 0,
            'edge_score': rule.get('edge_score', 0),
            'entropy': rule.get('entropy', 0),
            'composite': rule.get('composite_score', 0)
        }
        
        # Tags enrichis
        inferred_tags = infer_tags_from_scores(scores)
        existing_tags = rule.get('tags', [])
        all_tags = sorted(set(existing_tags + inferred_tags))
        
        # v2.1: Profil et usage suggéré
        module_profile = rule.get('module_profile')
        suggested_use = rule.get('suggested_use')
        
        if not module_profile:
            # Inférer si absent
            capacity = scores.get('composite', 0)  # Approximation
            robustness = scores.get('edge_score', 0)
            basin_div = 0.5
            module_profile, suggested_use = infer_module_profile(
                capacity, robustness, basin_div, scores.get('entropy', 0.5)
            )
        
        export_data['hall_of_fame'].append({
            'module_id': f"mem_{rule.get('notation', 'unknown').replace('/', '_')}",
            'notation': rule.get('notation'),
            'born': born,
            'survive': survive,
            'tier': rule.get('tier', 'unknown'),
            'diversity_signature': compute_diversity_signature(born, survive),
            'module_profile': module_profile,
            'suggested_use': suggested_use,
            'scores': scores,
            'metadata': {
                'discovered_by': rule.get('discovered_by', 'unknown'),
                'discovered_date': rule.get('discovered_date', 'unknown'),
                'promotion_reason': rule.get('promotion_reason', 'unknown'),
                'tags': all_tags,
                'origin': 'ising-life-lab'
            }
        })
    
    # Exporter la méta-mémoire (top rules)
    # Trier par score composite si disponible
    def get_composite(rule):
        scores = rule.get('scores', {})
        return (scores.get('memory_score', 0) * 0.5 + 
                scores.get('edge_score', 0) * 0.3 + 
                scores.get('entropy', 0) * 0.2)
    
    sorted_memory = sorted(meta_memory, key=get_composite, reverse=True)
    
    for rule in sorted_memory[:100]:  # Exporter top 100
        born = rule.get('born', [])
        survive = rule.get('survive', [])
        scores = rule.get('scores', {})
        scores_enriched = {
            'memory_score': scores.get('memory_score', 0),
            'edge_score': scores.get('edge_score', 0),
            'entropy': scores.get('entropy', 0),
            'composite': get_composite(rule)
        }
        
        # Tags enrichis
        inferred_tags = infer_tags_from_scores(scores_enriched)
        existing_labels = rule.get('labels', [])
        all_tags = sorted(set(existing_labels + inferred_tags))
        
        export_data['memory_library'].append({
            'notation': rule.get('notation'),
            'born': born,
            'survive': survive,
            'diversity_signature': compute_diversity_signature(born, survive),
            'scores': scores_enriched,
            'labels': all_tags,
            'metadata': {
                **rule.get('metadata', {}),
                'origin': 'ising-life-lab'
            }
        })
    
    # Sauvegarder
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as fh:
        json.dump(export_data, fh, indent=2)
    
    print(f"\n[OK] Export reussi : {output_path}")
    print(f"   - {len(export_data['hall_of_fame'])} regles HoF")
    print(f"   - {len(export_data['memory_library'])} regles dans la bibliotheque memoire")
    print("=" * 64)
    
    return export_data


def main():
    """Point d'entrée principal."""
    try:
        export_hof_library()
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'export : {e}")
        import traceback
        traceback.print_exc()
        return 1
    return 0


if __name__ == '__main__':
    exit(main())

