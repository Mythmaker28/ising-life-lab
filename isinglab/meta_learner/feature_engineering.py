"""Feature engineering for Life-like CA rules."""

from typing import Dict, List, Tuple
import numpy as np

FEATURE_NAMES = [
    'born_count',
    'survive_count',
    'born_density',
    'survive_density',
    'total_density',
    'born_survive_overlap',
    'born_range',
    'survive_range',
    'parity_alignment',
    'low_neighbor_bias',
    'high_neighbor_bias'
]


def _ensure_lists(born: List[int], survive: List[int]) -> Tuple[List[int], List[int]]:
    born = born or []
    survive = survive or []
    return sorted(born), sorted(survive)


def extract_rule_features(notation: str = None, born: List[int] = None, survive: List[int] = None) -> Dict[str, float]:
    if born is None or survive is None:
        born = []
        survive = []
        if notation and '/' in notation:
            b_part, s_part = notation.split('/')
            born = [int(c) for c in ''.join(filter(str.isdigit, b_part))]
            survive = [int(c) for c in ''.join(filter(str.isdigit, s_part))]
    born, survive = _ensure_lists(born, survive)

    born_count = len(born)
    survive_count = len(survive)
    overlap = len(set(born) & set(survive))

    born_density = born_count / 9.0
    survive_density = survive_count / 9.0
    total_density = (born_count + survive_count) / 18.0

    born_range = (max(born) - min(born)) if born else 0
    survive_range = (max(survive) - min(survive)) if survive else 0

    parity_alignment = 0
    if born and survive:
        born_parity = sum(x % 2 for x in born) / born_count
        survive_parity = sum(x % 2 for x in survive) / survive_count
        parity_alignment = 1.0 - abs(born_parity - survive_parity)

    low_bias = sum(1 for x in born if x <= 2) / born_count if born_count else 0
    high_bias = sum(1 for x in survive if x >= 5) / survive_count if survive_count else 0

    return {
        'born_count': float(born_count),
        'survive_count': float(survive_count),
        'born_density': float(born_density),
        'survive_density': float(survive_density),
        'total_density': float(total_density),
        'born_survive_overlap': float(overlap / 9.0),
        'born_range': float(born_range / 8.0),
        'survive_range': float(survive_range / 8.0),
        'parity_alignment': float(parity_alignment),
        'low_neighbor_bias': float(low_bias),
        'high_neighbor_bias': float(high_bias)
    }


def features_to_vector(features: Dict[str, float]) -> np.ndarray:
    return np.array([features.get(name, 0.0) for name in FEATURE_NAMES], dtype=float)


def extract_dataset_features(meta_memory: List[Dict]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    X: List[np.ndarray] = []
    y: List[int] = []
    notations: List[str] = []

    for entry in meta_memory:
        notation = entry.get('notation')
        features = extract_rule_features(
            notation=notation,
            born=entry.get('born'),
            survive=entry.get('survive')
        )
        scores = entry.get('scores', {})
        labels = entry.get('labels', [])

        memory_score = scores.get('memory_score')
        edge_score = scores.get('edge_score')

        positive = False
        if memory_score is not None and memory_score >= 0.7:
            positive = True
        elif edge_score is not None and edge_score >= 0.35:
            positive = True
        elif any(lbl in {'champion', 'validated', 'promising'} for lbl in labels):
            positive = True

        X.append(features_to_vector(features))
        y.append(1 if positive else 0)
        notations.append(notation)

    if not X:
        return np.empty((0, len(FEATURE_NAMES))), np.empty((0,)), []

    return np.vstack(X), np.array(y, dtype=int), notations


__all__ = [
    'FEATURE_NAMES',
    'extract_rule_features',
    'features_to_vector',
    'extract_dataset_features'
]
