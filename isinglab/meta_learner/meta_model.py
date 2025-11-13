"""Trainable meta-model estimating rule potential."""

import json
from pathlib import Path
from typing import Dict, List

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from .feature_engineering import extract_rule_features, features_to_vector, extract_dataset_features


class MetaModel:
    def __init__(self):
        self.model = LogisticRegression(
            C=1.0, max_iter=1000, random_state=42, class_weight='balanced'
        )
        self.is_trained = False
        self.train_stats: Dict = {}

    def train(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2):
        if len(X) < 5:
            return
        if len(X) > 8 and 0 < test_size < 0.5:
            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y,
                test_size=test_size,
                random_state=42,
                stratify=y if len(set(y)) > 1 else None
            )
        else:
            X_train, X_test, y_train, y_test = X, X, y, y

        self.model.fit(X_train, y_train)
        self.is_trained = True

        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        self.train_stats = {
            'n_samples': int(len(X)),
            'train_accuracy': float(accuracy_score(y_train, train_pred)),
            'test_accuracy': float(accuracy_score(y_test, test_pred)),
            'class_balance': {
                'positive': int(np.sum(y)),
                'negative': int(len(y) - np.sum(y))
            }
        }

    def predict_proba(self, notation: str = None, born: List[int] = None, survive: List[int] = None) -> float:
        if not self.is_trained:
            return 0.5
        features = extract_rule_features(notation=notation, born=born, survive=survive)
        vector = features_to_vector(features).reshape(1, -1)
        return float(self.model.predict_proba(vector)[0, 1])

    def save(self, path: str = 'results/meta_model.json'):
        if not self.is_trained:
            return
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        payload = {
            'model': 'LogisticRegression',
            'train_stats': self.train_stats
        }
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(payload, fh, indent=2)


def train_meta_model(meta_memory: List[Dict], save_path: str = 'results/meta_model.json') -> MetaModel:
    X, y, _ = extract_dataset_features(meta_memory)
    model = MetaModel()
    if len(X) == 0:
        return model
    model.train(X, y)
    model.save(save_path)
    return model


__all__ = ['MetaModel', 'train_meta_model']
