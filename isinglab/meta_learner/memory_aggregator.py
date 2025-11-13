"""Aggregation centralisée de la mémoire expérimentale."""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

import pandas as pd


class MemoryAggregator:
    """Collecte Hall of Fame, logs d'exploration et méta-mémoire consolidée."""

    def __init__(
        self,
        hof_path: str = 'isinglab/rules/hof_rules.json',
        scans_dir: str = 'results/scans',
        output_path: str = 'results/meta_memory.json'
    ):
        self.hof_path = Path(hof_path)
        self.scans_dir = Path(scans_dir)
        self.output_path = Path(output_path)
        self.meta_memory: List[Dict] = []

    # ------------------------------------------------------------------
    # Chargement des sources
    # ------------------------------------------------------------------
    def load_hall_of_fame(self) -> List[Dict]:
        if not self.hof_path.exists():
            return []
        with open(self.hof_path, encoding='utf-8') as fh:
            data = json.load(fh)
        return data.get('rules', [])

    def load_exploration_logs(self) -> List[Dict]:
        if not self.scans_dir.exists():
            return []
        collected: List[Dict] = []
        for path in self.scans_dir.glob('**/*'):
            if path.suffix.lower() == '.csv':
                try:
                    df = pd.read_csv(path)
                    collected.extend(df.to_dict('records'))
                except Exception:
                    continue
            elif path.suffix.lower() == '.json':
                try:
                    with open(path, encoding='utf-8') as fh:
                        payload = json.load(fh)
                    if isinstance(payload, dict) and 'results' in payload:
                        collected.extend(payload['results'])
                except Exception:
                    continue
        return collected

    # ------------------------------------------------------------------
    # Normalisation et agrégation
    # ------------------------------------------------------------------
    def normalize_rule_entry(self, entry: Dict, source: str) -> Dict:
        notation = entry.get('notation') or entry.get('rule') or 'unknown'
        born = entry.get('born', [])
        survive = entry.get('survive', [])

        if not born and '/' in notation:
            parts = notation.split('/')
            born_digits = ''.join(filter(str.isdigit, parts[0]))
            survive_digits = ''.join(filter(str.isdigit, parts[1] if len(parts) > 1 else ''))
            born = [int(ch) for ch in born_digits] if born_digits else []
            survive = [int(ch) for ch in survive_digits] if survive_digits else []

        scores = {}
        if 'memory_score' in entry and entry['memory_score'] is not None:
            scores['memory_score'] = float(entry['memory_score'])
        if 'edge_score' in entry and entry['edge_score'] is not None:
            scores['edge_score'] = float(entry['edge_score'])
        if 'entropy' in entry and entry['entropy'] is not None:
            scores['entropy'] = float(entry['entropy'])

        labels = []
        tier = entry.get('tier')
        if tier:
            labels.append(tier)
        labels.extend(entry.get('labels', []))
        labels.extend(entry.get('tags', []))

        return {
            'notation': notation,
            'born': born,
            'survive': survive,
            'scores': scores,
            'labels': sorted(set(labels)),
            'metadata': {
                'source': source,
                'discovered_date': entry.get('discovered_date', datetime.now().strftime('%Y-%m-%d'))
            }
        }

    def load_existing_meta_memory(self) -> List[Dict]:
        """Charge la méta-mémoire existante depuis le fichier de sortie."""
        if not self.output_path.exists():
            return []
        try:
            with open(self.output_path, encoding='utf-8') as fh:
                payload = json.load(fh)
            return payload.get('rules', [])
        except Exception:
            return []

    def aggregate(self) -> List[Dict]:
        """Agrège toutes les sources : meta_memory existant + HoF + exploration logs."""
        self.meta_memory = []
        seen = set()

        # 1. Charger PRIORITAIREMENT la méta-mémoire existante
        for entry in self.load_existing_meta_memory():
            self.meta_memory.append(entry)
            seen.add(entry['notation'])

        # 2. Enrichir avec le Hall of Fame
        for entry in self.load_hall_of_fame():
            normalized = self.normalize_rule_entry(entry, 'hall_of_fame')
            if normalized['notation'] not in seen:
                self.meta_memory.append(normalized)
                seen.add(normalized['notation'])
            else:
                # enrichir l'existant
                existing = next((r for r in self.meta_memory if r['notation'] == normalized['notation']), None)
                if existing:
                    existing['scores'].update(normalized['scores'])
                    existing['labels'] = sorted(set(existing['labels']) | set(normalized['labels']))
                    if 'hof' not in existing['labels']:
                        existing['labels'].append('hof')
                        existing['labels'] = sorted(existing['labels'])

        # 3. Enrichir avec les logs d'exploration
        for entry in self.load_exploration_logs():
            normalized = self.normalize_rule_entry(entry, 'exploration_log')
            if normalized['notation'] not in seen:
                self.meta_memory.append(normalized)
                seen.add(normalized['notation'])
            else:
                # enrichir l'existant avec nouveaux scores
                existing = next((r for r in self.meta_memory if r['notation'] == normalized['notation']), None)
                if existing:
                    existing['scores'].update(normalized['scores'])
                    existing['labels'] = sorted(set(existing['labels']) | set(normalized['labels']))

        return self.meta_memory

    # ------------------------------------------------------------------
    # Persistance & stats
    # ------------------------------------------------------------------
    def save(self):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            'meta': {
                'updated': datetime.now().isoformat(),
                'count': len(self.meta_memory)
            },
            'rules': self.meta_memory
        }
        with open(self.output_path, 'w', encoding='utf-8') as fh:
            json.dump(payload, fh, indent=2)

    def get_statistics(self) -> Dict:
        labels_count: Dict[str, int] = {}
        for rule in self.meta_memory:
            for label in rule.get('labels', []):
                labels_count[label] = labels_count.get(label, 0) + 1
        return {
            'total_rules': len(self.meta_memory),
            'by_label': labels_count
        }


__all__ = ['MemoryAggregator']
