"""Hall of Fame rule helpers."""

import json
from pathlib import Path
from typing import Dict, List

HOF_PATH = Path(__file__).resolve().parent / 'hof_rules.json'


def load_hof_rules() -> List[Dict]:
    if not HOF_PATH.exists():
        return []
    with open(HOF_PATH, encoding='utf-8') as fh:
        payload = json.load(fh)
    return payload.get('rules', [])


def save_hof_rules(rules: List[Dict]):
    HOF_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        'meta': {'updated': Path(HOF_PATH).stat().st_mtime if HOF_PATH.exists() else None},
        'rules': rules
    }
    with open(HOF_PATH, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, indent=2)


def add_or_update_rule(rule: Dict) -> bool:
    rules = load_hof_rules()
    notation = rule['notation']
    updated = False
    for existing in rules:
        if existing.get('notation') == notation:
            existing.update(rule)
            updated = True
            break
    if not updated:
        rules.append(rule)
    save_hof_rules(rules)
    return not updated


__all__ = ['load_hof_rules', 'save_hof_rules', 'add_or_update_rule']
