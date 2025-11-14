"""
Modèles de bruit réalistes pour les systèmes quantiques biologiques.

Au lieu d'un bruit blanc purement gaussien, on implémente:
1. Bruit gaussien (rapide, non-corrélé)
2. Drift 1/f (lent, basses fréquences)
3. Sauts discrets (shot noise, événements rares)

Cela capture mieux les sources de bruit en milieu biologique:
- Fluctuations thermiques rapides (phonons)
- Dérives lentes (température, champs magnétiques)
- Événements discrets (spins nucléaires flip, collisions)
"""

import numpy as np
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class NoiseParameters:
    """Paramètres du modèle de bruit."""
    
    # Bruit blanc gaussien
    gaussian_amplitude: float = 0.1
    
    # Drift 1/f
    drift_amplitude: float = 0.02
    drift_timescale_us: float = 10.0  # Échelle temporelle du drift
    
    # Shot noise (événements discrets)
    shot_rate_per_us: float = 0.01  # Taux d'événements par µs
    shot_amplitude: float = 0.05
    
    # Random seed (for reproducibility)
    seed: Optional[int] = None


class RealisticNoiseGenerator:
    """
    Générateur de bruit réaliste multi-composantes.
    
    Le bruit total est:
        ξ(t) = ξ_gaussian(t) + ξ_drift(t) + ξ_shot(t)
    
    Où:
    - ξ_gaussian: Bruit blanc (non-corrélé)
    - ξ_drift: Processus Ornstein-Uhlenbeck (drift lent)
    - ξ_shot: Processus de Poisson (sauts discrets)
    """
    
    def __init__(self, params: NoiseParameters):
        """
        Args:
            params: Paramètres du bruit
        """
        self.params = params
        
        # État interne du drift (Ornstein-Uhlenbeck)
        self.drift_state = 0.0
        
        # RNG
        if params.seed is not None:
            np.random.seed(params.seed)
    
    def generate(self, dt_us: float, shape: Optional[tuple] = None) -> np.ndarray:
        """
        Génère un échantillon de bruit.
        
        Args:
            dt_us: Pas de temps (µs)
            shape: Forme du bruit (si None, retourne un scalaire)
            
        Returns:
            Bruit ξ(t) avec la forme demandée
        """
        if shape is None:
            shape = ()
        
        # 1. Bruit gaussien (blanc)
        gaussian_noise = self.params.gaussian_amplitude * np.random.randn(*shape)
        
        # 2. Drift 1/f (Ornstein-Uhlenbeck)
        drift_noise = self._generate_drift(dt_us, shape)
        
        # 3. Shot noise (Poisson)
        shot_noise = self._generate_shot_noise(dt_us, shape)
        
        # Total
        total_noise = gaussian_noise + drift_noise + shot_noise
        
        return total_noise
    
    def _generate_drift(self, dt_us: float, shape: tuple) -> np.ndarray:
        """
        Génère un drift via processus Ornstein-Uhlenbeck.
        
        dX = -X/τ·dt + σ·dW
        
        Où:
            τ: Timescale du drift
            σ: Amplitude du bruit
            dW: Wiener process
        """
        tau = self.params.drift_timescale_us
        sigma = self.params.drift_amplitude
        
        # Mise à jour du state (single scalar pour simplifier)
        # Pour un array, on aurait un vecteur d'états
        drift_decay = np.exp(-dt_us / tau)
        drift_diffusion = sigma * np.sqrt(1 - drift_decay**2)
        
        self.drift_state = (
            drift_decay * self.drift_state +
            drift_diffusion * np.random.randn()
        )
        
        # Broadcast à la forme demandée
        if shape:
            drift_array = self.drift_state * np.ones(shape)
        else:
            drift_array = self.drift_state
        
        return drift_array
    
    def _generate_shot_noise(self, dt_us: float, shape: tuple) -> np.ndarray:
        """
        Génère des événements discrets (Poisson).
        
        Chaque événement a une amplitude fixe et arrive avec un taux λ.
        """
        lambda_rate = self.params.shot_rate_per_us * dt_us
        
        # Nombre d'événements dans dt
        if shape:
            size = np.prod(shape) if shape else 1
            n_events = np.random.poisson(lambda_rate, size=int(size))
            shot_noise = n_events * self.params.shot_amplitude
            shot_noise = shot_noise.reshape(shape)
        else:
            n_events = np.random.poisson(lambda_rate)
            shot_noise = n_events * self.params.shot_amplitude
        
        return shot_noise
    
    def reset(self):
        """Reset l'état interne du générateur."""
        self.drift_state = 0.0


class AdaptiveNoiseGenerator:
    """
    Générateur de bruit adaptatif basé sur T1, T2, température.
    
    Calibre automatiquement les paramètres de bruit selon les propriétés
    physiques du système.
    """
    
    def __init__(
        self,
        T1_us: float,
        T2_us: float,
        temperature_k: float,
        base_noise_scale: float = 1.0
    ):
        """
        Args:
            T1_us: Temps de relaxation (µs)
            T2_us: Temps de cohérence (µs)
            temperature_k: Température (K)
            base_noise_scale: Facteur multiplicatif global
        """
        self.T1 = T1_us
        self.T2 = T2_us
        self.temperature_k = temperature_k
        self.base_noise_scale = base_noise_scale
        
        # Calibration automatique
        self.params = self._calibrate_noise_params()
        
        # Générateur sous-jacent
        self.generator = RealisticNoiseGenerator(self.params)
    
    def _calibrate_noise_params(self) -> NoiseParameters:
        """
        Calibre les paramètres de bruit selon T1, T2, T.
        
        Heuristiques:
        - Gaussian ∝ 1/T2 (dephasing rapide)
        - Drift ∝ exp(T/300) (activation thermique)
        - Shot rate ∝ T / T2 (événements discrets)
        """
        # Référence: T2 = 100 µs, T = 300 K
        T2_ref = 100.0
        T_ref = 300.0
        
        # 1. Gaussian (dephasing rapide)
        gaussian_amp = self.base_noise_scale * 0.1 * (T2_ref / self.T2)
        gaussian_amp = np.clip(gaussian_amp, 0.01, 0.5)
        
        # 2. Drift (activation thermique)
        thermal_factor = np.exp((self.temperature_k - T_ref) / 100.0)
        drift_amp = self.base_noise_scale * 0.02 * thermal_factor
        drift_amp = np.clip(drift_amp, 0.001, 0.1)
        
        # Timescale du drift: quelques T2
        drift_timescale = 5.0 * self.T2
        
        # 3. Shot noise (événements rares)
        # Taux proportionnel à kT/T2
        shot_rate = self.base_noise_scale * 0.01 * (self.temperature_k / T_ref) / (self.T2 / T2_ref)
        shot_rate = np.clip(shot_rate, 0.001, 0.1)
        
        shot_amp = self.base_noise_scale * 0.05
        
        return NoiseParameters(
            gaussian_amplitude=gaussian_amp,
            drift_amplitude=drift_amp,
            drift_timescale_us=drift_timescale,
            shot_rate_per_us=shot_rate,
            shot_amplitude=shot_amp,
            seed=None
        )
    
    def generate(self, dt_us: float, shape: Optional[tuple] = None) -> np.ndarray:
        """
        Génère du bruit adapté au système.
        
        Args:
            dt_us: Pas de temps (µs)
            shape: Forme du bruit
            
        Returns:
            Échantillon de bruit
        """
        return self.generator.generate(dt_us, shape)
    
    def reset(self):
        """Reset le générateur."""
        self.generator.reset()


# ============================================================================
# NOISE UTILITIES
# ============================================================================

def create_noise_generator(
    T1_us: float,
    T2_us: float,
    temperature_k: float,
    noise_multiplier: float = 1.0,
    use_adaptive: bool = True
) -> RealisticNoiseGenerator:
    """
    Factory pour créer un générateur de bruit.
    
    Args:
        T1_us: Temps T1 (µs)
        T2_us: Temps T2 (µs)
        temperature_k: Température (K)
        noise_multiplier: Facteur multiplicatif global
        use_adaptive: Si True, utilise AdaptiveNoiseGenerator
        
    Returns:
        Générateur de bruit configuré
    """
    if use_adaptive:
        gen = AdaptiveNoiseGenerator(
            T1_us=T1_us,
            T2_us=T2_us,
            temperature_k=temperature_k,
            base_noise_scale=noise_multiplier
        )
        return gen.generator  # Return the underlying RealisticNoiseGenerator
    else:
        # Paramètres par défaut
        params = NoiseParameters(
            gaussian_amplitude=0.1 * noise_multiplier,
            drift_amplitude=0.02 * noise_multiplier,
            drift_timescale_us=10.0,
            shot_rate_per_us=0.01,
            shot_amplitude=0.05 * noise_multiplier
        )
        return RealisticNoiseGenerator(params)


def compare_noise_models(
    T1_us: float,
    T2_us: float,
    temperature_k: float,
    duration_us: float = 100.0,
    dt_us: float = 0.1
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compare le bruit gaussien simple vs réaliste.
    
    Args:
        T1_us, T2_us, temperature_k: Paramètres système
        duration_us: Durée de la simulation
        dt_us: Pas de temps
        
    Returns:
        (times, simple_noise, realistic_noise)
    """
    n_steps = int(duration_us / dt_us)
    times = np.arange(n_steps) * dt_us
    
    # Simple (gaussien pur)
    simple_noise = 0.1 * np.random.randn(n_steps)
    
    # Réaliste (multi-composantes)
    gen = AdaptiveNoiseGenerator(T1_us, T2_us, temperature_k)
    realistic_noise = np.array([gen.generate(dt_us) for _ in range(n_steps)])
    
    return times, simple_noise, realistic_noise

