"""
Moteur d'oscillateurs de phase Kuramoto/XY-Model.
Vectorisé (Numba-optimisé) pour grilles 2D haute résolution.

Architecture:
- Champ de phase θ(x,y) ∈ [0, 2π)
- Multi-kernel : K1, K2, K3 avec portées et signes indépendants
- Support GPU-ready via Numba

Équation de base (Kuramoto):
dθ_i/dt = ω_i + Σ_j K_ij * sin(θ_j - θ_i)
"""

import numpy as np
from numba import jit, prange
from typing import Tuple, Optional, Dict
from dataclasses import dataclass


@dataclass
class MultiKernelConfig:
    """Configuration des kernels de couplage multi-échelle."""
    
    # Kernel 1 : couplage court-range (voisinage proche)
    k1_strength: float = 1.0
    k1_range: int = 1
    k1_sign: float = 1.0  # +1 = attractif, -1 = répulsif
    
    # Kernel 2 : couplage mid-range
    k2_strength: float = 0.0
    k2_range: int = 3
    k2_sign: float = 1.0
    
    # Kernel 3 : couplage long-range
    k3_strength: float = 0.0
    k3_range: int = 7
    k3_sign: float = 1.0
    
    # Paramètres dynamiques
    dt: float = 0.1
    noise_amplitude: float = 0.01
    annealing_rate: float = 0.0  # Réduction progressive du bruit


@jit(nopython=True, parallel=True, fastmath=True)
def _kuramoto_step_kernel(
    phase_current: np.ndarray,
    phase_next: np.ndarray,
    omega: np.ndarray,
    k1_strength: float, k1_range: int, k1_sign: float,
    k2_strength: float, k2_range: int, k2_sign: float,
    k3_strength: float, k3_range: int, k3_sign: float,
    dt: float,
    noise: np.ndarray
) -> None:
    """
    Kernel Numba pour l'évolution temporelle des oscillateurs.
    
    Calcule dθ/dt = ω + Σ_kernels K * Σ_voisins sin(θ_j - θ_i) + bruit
    """
    h, w = phase_current.shape
    
    for i in prange(h):
        for j in range(w):
            coupling = 0.0
            norm = 0.0
            
            # Kernel 1 : court-range
            if k1_strength > 0:
                for di in range(-k1_range, k1_range + 1):
                    for dj in range(-k1_range, k1_range + 1):
                        if di == 0 and dj == 0:
                            continue
                        ni = (i + di) % h
                        nj = (j + dj) % w
                        delta_phase = phase_current[ni, nj] - phase_current[i, j]
                        coupling += k1_sign * k1_strength * np.sin(delta_phase)
                        norm += k1_strength
            
            # Kernel 2 : mid-range
            if k2_strength > 0:
                for di in range(-k2_range, k2_range + 1):
                    for dj in range(-k2_range, k2_range + 1):
                        dist_sq = di*di + dj*dj
                        if dist_sq <= k2_range * k2_range and dist_sq > k1_range * k1_range:
                            ni = (i + di) % h
                            nj = (j + dj) % w
                            delta_phase = phase_current[ni, nj] - phase_current[i, j]
                            coupling += k2_sign * k2_strength * np.sin(delta_phase)
                            norm += k2_strength
            
            # Kernel 3 : long-range
            if k3_strength > 0:
                for di in range(-k3_range, k3_range + 1):
                    for dj in range(-k3_range, k3_range + 1):
                        dist_sq = di*di + dj*dj
                        if dist_sq <= k3_range * k3_range and dist_sq > k2_range * k2_range:
                            ni = (i + di) % h
                            nj = (j + dj) % w
                            delta_phase = phase_current[ni, nj] - phase_current[i, j]
                            coupling += k3_sign * k3_strength * np.sin(delta_phase)
                            norm += k3_strength
            
            # Normalisation et intégration
            if norm > 0:
                coupling /= norm
            
            dtheta = omega[i, j] + coupling + noise[i, j]
            phase_next[i, j] = (phase_current[i, j] + dt * dtheta) % (2 * np.pi)


class KuramotoXYEngine:
    """
    Moteur principal pour simuler un champ d'oscillateurs de phase.
    
    Usage:
        config = MultiKernelConfig(k1_strength=1.0, k1_range=1)
        engine = KuramotoXYEngine(shape=(512, 512), config=config)
        engine.reset()
        
        for _ in range(1000):
            engine.step()
            
        phase_field = engine.get_phase_field()
    """
    
    def __init__(
        self,
        shape: Tuple[int, int] = (256, 256),
        config: Optional[MultiKernelConfig] = None,
        seed: Optional[int] = None
    ):
        """
        Args:
            shape: (height, width) de la grille d'oscillateurs
            config: Configuration des kernels de couplage
            seed: Seed pour reproductibilité
        """
        self.shape = shape
        self.config = config or MultiKernelConfig()
        self.rng = np.random.default_rng(seed)
        
        # État interne
        self.phase_current = np.zeros(shape, dtype=np.float32)
        self.phase_next = np.zeros(shape, dtype=np.float32)
        self.omega = np.zeros(shape, dtype=np.float32)  # Fréquences naturelles
        
        self.t = 0
        self.iteration = 0
        
    def reset(self, initial_phase: Optional[np.ndarray] = None) -> None:
        """
        Réinitialise le champ de phase.
        
        Args:
            initial_phase: Condition initiale. Si None, phase aléatoire uniforme.
        """
        if initial_phase is not None:
            self.phase_current = initial_phase.astype(np.float32) % (2 * np.pi)
        else:
            self.phase_current = self.rng.uniform(0, 2 * np.pi, self.shape).astype(np.float32)
        
        self.phase_next = self.phase_current.copy()
        self.omega = self.rng.normal(0, 0.1, self.shape).astype(np.float32)
        self.t = 0
        self.iteration = 0
        
    def step(self) -> None:
        """Avance la simulation d'un pas de temps."""
        # Génération du bruit
        effective_noise = self.config.noise_amplitude
        if self.config.annealing_rate > 0:
            effective_noise *= np.exp(-self.config.annealing_rate * self.t)
        
        noise = self.rng.normal(0, effective_noise, self.shape).astype(np.float32)
        
        # Kernel Numba
        _kuramoto_step_kernel(
            self.phase_current,
            self.phase_next,
            self.omega,
            self.config.k1_strength, self.config.k1_range, self.config.k1_sign,
            self.config.k2_strength, self.config.k2_range, self.config.k2_sign,
            self.config.k3_strength, self.config.k3_range, self.config.k3_sign,
            self.config.dt,
            noise
        )
        
        # Swap buffers
        self.phase_current, self.phase_next = self.phase_next, self.phase_current
        
        self.t += self.config.dt
        self.iteration += 1
        
    def get_phase_field(self) -> np.ndarray:
        """Retourne le champ de phase actuel."""
        return self.phase_current.copy()
    
    def get_order_parameter(self) -> Tuple[float, float]:
        """
        Calcule le paramètre d'ordre de Kuramoto.
        
        Returns:
            (r, psi) où r ∈ [0, 1] mesure la cohérence globale,
            et psi est la phase moyenne.
        """
        z = np.mean(np.exp(1j * self.phase_current))
        r = np.abs(z)
        psi = np.angle(z)
        return r, psi
    
    def get_local_order(self, radius: int = 3) -> np.ndarray:
        """
        Calcule le paramètre d'ordre local pour chaque oscillateur.
        
        Args:
            radius: Rayon du voisinage pour calculer la cohérence locale
            
        Returns:
            Champ 2D de cohérence locale r(x,y) ∈ [0, 1]
        """
        h, w = self.shape
        order_field = np.zeros(self.shape, dtype=np.float32)
        
        for i in range(h):
            for j in range(w):
                neighbors = []
                for di in range(-radius, radius + 1):
                    for dj in range(-radius, radius + 1):
                        ni = (i + di) % h
                        nj = (j + dj) % w
                        neighbors.append(self.phase_current[ni, nj])
                
                z = np.mean(np.exp(1j * np.array(neighbors)))
                order_field[i, j] = np.abs(z)
        
        return order_field
    
    def set_coupling_modulation(self, modulation_field: np.ndarray, kernel: str = 'k1') -> None:
        """
        Module spatialement la force de couplage (pour contrôle externe).
        
        Args:
            modulation_field: Champ 2D multiplicatif [0, inf)
            kernel: 'k1', 'k2', ou 'k3'
        """
        # Cette méthode est un placeholder pour le contrôle holonomique
        # L'implémentation complète nécessiterait un refactoring du kernel
        pass
    
    def get_statistics(self) -> Dict[str, float]:
        """Retourne des statistiques sur l'état actuel."""
        r, psi = self.get_order_parameter()
        
        return {
            'time': self.t,
            'iteration': self.iteration,
            'order_parameter_r': r,
            'order_parameter_psi': psi,
            'mean_phase': float(np.mean(self.phase_current)),
            'std_phase': float(np.std(self.phase_current)),
        }

