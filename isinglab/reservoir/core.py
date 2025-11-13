"""
Reservoir Computing Core — Implémentation CA Reservoir.

Ce module implémente un réservoir computationnel basé sur automates cellulaires
pour tâches de machine learning (mémoire séquentielle, prédiction, débruitage).
"""

import numpy as np
from typing import Callable, List, Tuple, Optional, Dict
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


class CAReservoir:
    """
    Réservoir computationnel basé sur automates cellulaires.
    
    Pipeline :
    1. encode_input : Encoder données d'entrée dans grille CA
    2. evolve : Évolution CA sur N steps
    3. extract_features : Extraire features de l'historique
    4. train_readout : Entraîner readout linéaire
    5. predict : Pipeline complet
    """
    
    def __init__(self, rule_function: Callable, grid_size: Tuple[int, int] = (32, 32),
                 steps: int = 50, input_encoder: str = 'spatial', readout_type: str = 'linear',
                 alpha: float = 1.0):
        """
        Initialise le réservoir CA.
        
        Args:
            rule_function: Fonction règle CA (grid -> new_grid)
            grid_size: Taille de la grille (height, width)
            steps: Nombre de steps d'évolution CA
            input_encoder: Type d'encodage ('spatial', 'temporal', 'noise')
            readout_type: Type de readout ('linear', 'ridge')
            alpha: Paramètre de régularisation Ridge (si readout_type='ridge')
        """
        self.rule_function = rule_function
        self.grid_size = grid_size
        self.steps = steps
        self.input_encoder = input_encoder
        self.readout_type = readout_type
        self.alpha = alpha
        
        self.readout_model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def encode_input(self, input_data: np.ndarray) -> np.ndarray:
        """
        Encode les données d'entrée dans une grille CA.
        
        Args:
            input_data: Données d'entrée (forme dépend de input_encoder)
        
        Returns:
            Grille CA initiale (2D array 0/1)
        """
        height, width = self.grid_size
        
        if self.input_encoder == 'spatial':
            # Encodage spatial : input_data est une grille 2D ou 1D
            if input_data.ndim == 1:
                # 1D -> reshape en 2D
                size = min(len(input_data), height * width)
                grid = np.zeros((height, width), dtype=int)
                flat = input_data[:size]
                # Normaliser et binariser
                if flat.max() > flat.min():
                    flat_norm = (flat - flat.min()) / (flat.max() - flat.min())
                    grid.flat[:size] = (flat_norm > 0.5).astype(int)
                else:
                    grid.flat[:size] = (flat > 0).astype(int)
            else:
                # 2D -> redimensionner si nécessaire
                grid = np.zeros((height, width), dtype=int)
                h_src, w_src = input_data.shape[:2]
                h_dst = min(h_src, height)
                w_dst = min(w_src, width)
                grid[:h_dst, :w_dst] = (input_data[:h_dst, :w_dst] > 0.5).astype(int)
            return grid
            
        elif self.input_encoder == 'temporal':
            # Encodage temporel : input_data est une séquence temporelle
            # On encode chaque timestep dans une ligne de la grille
            grid = np.zeros((height, width), dtype=int)
            seq_len = min(len(input_data), height)
            for i in range(seq_len):
                # Encoder valeur dans ligne (binarisation)
                val = input_data[i]
                if isinstance(val, (int, float)):
                    # Convertir en binaire sur la largeur
                    binary = int(val * width) % width
                    grid[i, binary] = 1
            return grid
            
        elif self.input_encoder == 'noise':
            # Encodage par bruit contrôlé : input_data est un pattern + niveau bruit
            if isinstance(input_data, tuple):
                pattern, noise_level = input_data
            else:
                pattern = input_data
                noise_level = 0.1
            
            # Pattern de base
            if pattern.ndim == 1:
                grid = self.encode_input(pattern)  # Réutiliser spatial
            else:
                grid = pattern.copy()
            
            # Ajouter bruit
            n_flips = int(height * width * noise_level)
            for _ in range(n_flips):
                i, j = np.random.randint(0, height), np.random.randint(0, width)
                grid[i, j] = 1 - grid[i, j]
            
            return grid
            
        else:
            raise ValueError(f"Unknown input_encoder: {self.input_encoder}")
    
    def evolve(self, initial_state: np.ndarray, steps: Optional[int] = None) -> List[np.ndarray]:
        """
        Fait évoluer la grille CA sur N steps.
        
        Args:
            initial_state: État initial de la grille
            steps: Nombre de steps (None = utiliser self.steps)
        
        Returns:
            Liste des états à chaque step
        """
        if steps is None:
            steps = self.steps
        
        history = [initial_state.copy()]
        current_state = initial_state.copy()
        
        for _ in range(steps):
            current_state = self.rule_function(current_state)
            history.append(current_state.copy())
        
        return history
    
    def extract_features(self, history: List[np.ndarray]) -> np.ndarray:
        """
        Extrait des features de l'historique d'évolution.
        
        Stratégies :
        - Flatten : Aplatir chaque état
        - Pooling : Moyenne/max sur patches
        - Temporal : Features temporelles
        
        Args:
            history: Liste des états CA (chaque état est 2D)
        
        Returns:
            Vecteur de features (1D)
        """
        if len(history) == 0:
            return np.array([])
        
        features_list = []
        
        # 1. Flatten de chaque état
        for state in history:
            features_list.append(state.flatten())
        
        # 2. Features temporelles (différences)
        if len(history) > 1:
            for i in range(len(history) - 1):
                diff = history[i+1] - history[i]
                features_list.append(diff.flatten())
        
        # 3. Statistiques globales
        final_state = history[-1]
        features_list.append(np.array([
            final_state.mean(),
            final_state.std(),
            final_state.sum(),
            (final_state == 1).sum() / final_state.size  # Densité
        ]))
        
        # Concaténer toutes les features
        features = np.concatenate(features_list)
        
        return features
    
    def train_readout(self, X_features: np.ndarray, y_target: np.ndarray):
        """
        Entraîne le readout linéaire.
        
        Args:
            X_features: Features extraites (n_samples, n_features)
            y_target: Targets (n_samples, n_outputs)
        """
        # Normaliser features
        X_scaled = self.scaler.fit_transform(X_features)
        
        # Entraîner modèle
        if self.readout_type == 'linear' or self.readout_type == 'ridge':
            self.readout_model = Ridge(alpha=self.alpha)
        else:
            raise ValueError(f"Unknown readout_type: {self.readout_type}")
        
        self.readout_model.fit(X_scaled, y_target)
        self.is_trained = True
    
    def predict(self, input_data: np.ndarray) -> np.ndarray:
        """
        Pipeline complet : encode → evolve → extract → predict.
        
        Args:
            input_data: Données d'entrée
        
        Returns:
            Prédictions
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train_readout() first.")
        
        # Encode
        initial_state = self.encode_input(input_data)
        
        # Evolve
        history = self.evolve(initial_state)
        
        # Extract
        features = self.extract_features(history)
        features = features.reshape(1, -1)
        
        # Predict
        features_scaled = self.scaler.transform(features)
        prediction = self.readout_model.predict(features_scaled)
        
        return prediction.flatten()


__all__ = ['CAReservoir']



