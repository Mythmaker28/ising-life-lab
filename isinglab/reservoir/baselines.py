"""
Baselines ML standards pour comparaison avec CA Reservoir.

Implémente :
- ESN (Echo State Network) simple
- MLP simple (2 couches)
- Régression linéaire directe
"""

import numpy as np
from typing import Dict, Tuple, Optional
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler


class SimpleESN:
    """
    Echo State Network simple (réseau récurrent aléatoire).
    
    Architecture :
    - Réservoir récurrent aléatoire (non entraîné)
    - Readout linéaire entraîné
    """
    
    def __init__(self, reservoir_size: int = 100, spectral_radius: float = 0.9,
                 input_scaling: float = 1.0, alpha: float = 1.0, seed: Optional[int] = None):
        """
        Initialise ESN.
        
        Args:
            reservoir_size: Taille du réservoir
            spectral_radius: Rayon spectral de la matrice de récurrence
            input_scaling: Scaling des inputs
            alpha: Régularisation Ridge
            seed: Seed pour reproductibilité
        """
        self.reservoir_size = reservoir_size
        self.spectral_radius = spectral_radius
        self.input_scaling = input_scaling
        self.alpha = alpha
        
        if seed is not None:
            np.random.seed(seed)
        
        # Matrice de récurrence aléatoire
        W = np.random.randn(reservoir_size, reservoir_size)
        # Normaliser pour avoir le bon rayon spectral
        eigenvals = np.linalg.eigvals(W)
        max_eigenval = np.max(np.abs(eigenvals))
        self.W = W * (spectral_radius / max_eigenval)
        
        # Matrice d'input aléatoire
        self.W_in = np.random.randn(reservoir_size, 1) * input_scaling
        
        self.readout = Ridge(alpha=alpha)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def _update_reservoir(self, u: float, x_prev: np.ndarray) -> np.ndarray:
        """Met à jour l'état du réservoir."""
        x_new = np.tanh(self.W @ x_prev + (self.W_in * u).flatten())
        return x_new
    
    def _compute_reservoir_states(self, u_seq: np.ndarray) -> np.ndarray:
        """Calcule les états du réservoir pour une séquence d'inputs."""
        n = len(u_seq)
        states = np.zeros((n, self.reservoir_size))
        x = np.zeros(self.reservoir_size)
        
        for i in range(n):
            x = self._update_reservoir(u_seq[i], x)
            states[i] = x
        
        return states
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """
        Entraîne le readout.
        
        Args:
            X: Inputs (n_samples, input_dim) ou (n_samples,) pour séquences
            y: Targets (n_samples, output_dim)
        """
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        # Calculer états du réservoir
        reservoir_states = []
        for i in range(len(X)):
            if X.shape[1] == 1:
                # Séquence temporelle
                states = self._compute_reservoir_states(X[i])
                reservoir_states.append(states[-1])  # Dernier état
            else:
                # Features déjà calculées (utiliser directement)
                states = self._compute_reservoir_states(X[i])
                reservoir_states.append(states[-1])
        
        reservoir_states = np.array(reservoir_states)
        
        # Normaliser
        reservoir_states_scaled = self.scaler.fit_transform(reservoir_states)
        
        # Entraîner readout
        self.readout.fit(reservoir_states_scaled, y)
        self.is_trained = True
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Prédit."""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        reservoir_states = []
        for i in range(len(X)):
            states = self._compute_reservoir_states(X[i])
            reservoir_states.append(states[-1])
        
        reservoir_states = np.array(reservoir_states)
        reservoir_states_scaled = self.scaler.transform(reservoir_states)
        
        return self.readout.predict(reservoir_states_scaled)


class SimpleMLP:
    """
    MLP simple (2 couches).
    """
    
    def __init__(self, hidden_size: int = 50, alpha: float = 0.01,
                 max_iter: int = 500, random_state: Optional[int] = None):
        """
        Initialise MLP.
        
        Args:
            hidden_size: Taille de la couche cachée
            alpha: Régularisation L2
            max_iter: Nombre max d'itérations
            random_state: Seed
        """
        self.hidden_size = hidden_size
        self.model = MLPRegressor(
            hidden_layer_sizes=(hidden_size,),
            alpha=alpha,
            max_iter=max_iter,
            random_state=random_state,
            early_stopping=True,
            validation_fraction=0.1
        )
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """Entraîne le MLP."""
        # Flatten si nécessaire
        if X.ndim > 2:
            X = X.reshape(X.shape[0], -1)
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Prédit."""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        if X.ndim > 2:
            X = X.reshape(X.shape[0], -1)
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)


class LinearBaseline:
    """
    Régression linéaire directe (baseline trivial).
    """
    
    def __init__(self, alpha: float = 1.0):
        """
        Initialise régression linéaire.
        
        Args:
            alpha: Régularisation Ridge (0 = LinearRegression, >0 = Ridge)
        """
        if alpha == 0:
            self.model = LinearRegression()
        else:
            self.model = Ridge(alpha=alpha)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """Entraîne le modèle."""
        # Flatten si nécessaire
        if X.ndim > 2:
            X = X.reshape(X.shape[0], -1)
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Prédit."""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        if X.ndim > 2:
            X = X.reshape(X.shape[0], -1)
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)


__all__ = ['SimpleESN', 'SimpleMLP', 'LinearBaseline']


