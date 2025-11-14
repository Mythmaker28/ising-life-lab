"""
Modèles physiques réalistes pour NV, 13C hyperpolarisés, et radical pairs.

Ce module implémente des modèles physiques plus réalistes que le modèle jouet
Kuramoto-XY, tout en restant computationnellement tractables.

MODÈLES IMPLÉMENTÉS:

1. NV Centers (Spin-1):
   - Hamiltonien spin-1 avec zero-field splitting
   - H_NV = D·S_z^2 + γ·B·S_z + dephasing
   - T1, T2, dephasing channels

2. Hyperpolarized 13C (Bloch equations):
   - Modèle Bloch au niveau effectif
   - dM/dt = γ(M × B) - (M-M0)/T1 - M_perp/T2
   - Relaxation longitudinale et transverse

3. Radical Pairs (2-spin system):
   - Hamiltonien 2-spins couplés (espace 4D)
   - H_RP = ω1·S1_z + ω2·S2_z + J·(S1·S2) + hyperfine
   - Recombination et décohérence

CONTRAINTES:
- Pas de fabrication de données physiques
- Paramètres justifiés ou documentés comme assumptions
- Simple mais plus réaliste que Kuramoto-XY
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional
from enum import Enum


class SystemType(Enum):
    """Types de systèmes quantiques biologiques."""
    NV_CENTER = "nv"
    HYPERPOLARIZED_13C = "13c"
    RADICAL_PAIR = "rp"


@dataclass
class PhysicalState:
    """État physique d'un système quantique."""
    
    # Vecteur d'état (dimension dépend du système)
    state_vector: np.ndarray
    
    # Observable d'intérêt (signal mesuré)
    observable: float
    
    # Temps actuel
    time: float
    
    # Type de système
    system_type: SystemType


# ============================================================================
# 1. NV CENTER (Spin-1 System)
# ============================================================================

class NVCenterModel:
    """
    Modèle spin-1 pour NV center en diamant.
    
    Hamiltonien effectif (sous-espace m_s = 0, ±1):
        H = D·S_z^2 + γ·B_z·S_z + Ω(t)·(S_+ + S_-)
    
    Où:
        D ~ 2.87 GHz : Zero-field splitting
        γ ~ 2.8 MHz/G : Rapport gyromagnétique
        Ω(t) : Drive Rabi (contrôle)
    
    Décohérence:
        - T1 : Relaxation spin-lattice (typiquement ms-scale à 300K)
        - T2 : Dephasing (limité par phonons, surface, ~ µs-scale à 300K)
    
    Références:
        Schirhagl et al., Ann. Rev. Phys. Chem. 65, 83 (2014)
        Doherty et al., Phys. Rep. 528, 1 (2013)
    """
    
    def __init__(
        self,
        D_ghz: float = 2.87,  # Zero-field splitting
        B_gauss: float = 0.0,  # Champ magnétique externe
        T1_us: float = 5000.0,  # Relaxation
        T2_us: float = 1.8,     # Dephasing
        temperature_k: float = 298.0
    ):
        """
        Args:
            D_ghz: Zero-field splitting (GHz)
            B_gauss: Champ magnétique externe (Gauss)
            T1_us: Temps de relaxation T1 (µs)
            T2_us: Temps de dephasing T2 (µs)
            temperature_k: Température (K)
        """
        self.D = D_ghz * 2 * np.pi  # Convert to angular frequency (rad/ns)
        self.gamma = 2.8 * 2 * np.pi / 1000  # 2.8 MHz/G → rad/(ns·G)
        self.B = B_gauss
        self.T1 = T1_us  # µs
        self.T2 = T2_us  # µs
        self.temperature_k = temperature_k
        
        # Opérateurs spin-1 dans la base {|+1⟩, |0⟩, |-1⟩}
        # S_z
        self.S_z = np.diag([1.0, 0.0, -1.0])
        
        # S_z^2
        self.S_z2 = np.diag([1.0, 0.0, 1.0])
        
        # S_+ (raising operator)
        self.S_plus = np.sqrt(2) * np.array([
            [0, 1, 0],
            [0, 0, 1],
            [0, 0, 0]
        ])
        
        # S_- (lowering operator)
        self.S_minus = self.S_plus.T.conj()
        
        # Hamiltonien statique (sans drive)
        self.H_static = self.D * self.S_z2 + self.gamma * self.B * self.S_z
    
    def get_hamiltonian(self, omega_rabi: float = 0.0) -> np.ndarray:
        """
        Hamiltonien total avec drive.
        
        Args:
            omega_rabi: Fréquence Rabi du drive MW (GHz)
            
        Returns:
            H(t) (3×3)
        """
        H_drive = omega_rabi * (self.S_plus + self.S_minus)
        return self.H_static + H_drive
    
    def evolve(
        self,
        state: np.ndarray,
        dt_ns: float,
        omega_rabi: float = 0.0,
        noise_strength: float = 0.0
    ) -> np.ndarray:
        """
        Évolution Schrödinger + dephasing.
        
        Approximation: T1 >> T2, donc on néglige T1 sur les courtes durées.
        Dephasing modeled as random phase kicks.
        
        Args:
            state: Vecteur d'état (3,) complexe
            dt_ns: Pas de temps (ns)
            omega_rabi: Drive MW (GHz)
            noise_strength: Amplitude du bruit de phase
            
        Returns:
            État évolué (3,)
        """
        # 1. Évolution unitaire
        H = self.get_hamiltonian(omega_rabi)
        U = self._expm(-1j * H * dt_ns)  # H est en rad/ns, dt en ns
        state = U @ state
        
        # 2. Dephasing (random phase kick sur chaque composante)
        if noise_strength > 0:
            # T2 dephasing: phase noise proportionnel à √(dt/T2)
            phase_noise_scale = np.sqrt(dt_ns / (self.T2 * 1000))  # T2 en µs → ns
            phase_kicks = noise_strength * phase_noise_scale * np.random.randn(3)
            dephasing_operator = np.exp(1j * phase_kicks)
            state = dephasing_operator * state
        
        # 3. Renormalisation (approx conserve la norme)
        state = state / np.linalg.norm(state)
        
        return state
    
    def _expm(self, A: np.ndarray) -> np.ndarray:
        """Matrix exponential (3×3 optimized)."""
        from scipy.linalg import expm
        return expm(A)
    
    def measure_population(self, state: np.ndarray) -> Tuple[float, float, float]:
        """
        Mesure les populations |⟨+1|ψ⟩|^2, |⟨0|ψ⟩|^2, |⟨-1|ψ⟩|^2.
        
        Returns:
            (p_plus, p_zero, p_minus)
        """
        p_plus = np.abs(state[0])**2
        p_zero = np.abs(state[1])**2
        p_minus = np.abs(state[2])**2
        return p_plus, p_zero, p_minus
    
    def measure_signal(self, state: np.ndarray) -> float:
        """
        Signal optique effectif (proportionnel à m_s=0 population).
        
        Dans les manips NV, on détecte la fluorescence différentielle
        entre m_s=0 et m_s=±1.
        
        Returns:
            Signal normalisé [0, 1]
        """
        _, p_zero, _ = self.measure_population(state)
        return p_zero


# ============================================================================
# 2. HYPERPOLARIZED 13C (Bloch Equations)
# ============================================================================

class Hyperpolarized13CModel:
    """
    Modèle Bloch pour spins nucléaires 13C hyperpolarisés.
    
    Équations de Bloch:
        dM/dt = γ(M × B) - (M_z - M0)/T1·ẑ - (M_x·x̂ + M_y·ŷ)/T2
    
    Où:
        M = (M_x, M_y, M_z) : Magnétisation
        B = (0, 0, B_z) + B_rf(t) : Champ (statique + RF)
        γ ~ 10.7 MHz/T : Rapport gyromagnétique 13C
        T1 ~ 45 s (in vivo après injection DNP)
        T2 ~ 3.5 µs (effective, in vivo)
    
    Note:
        On travaille dans le référentiel tournant à la fréquence Larmor,
        donc B_z effectif = Δω (detuning).
    
    Références:
        Ardenkjær-Larsen, PNAS 117, 11902 (2020)
        Kurhanewicz et al., Neoplasia 21, 1 (2019)
    """
    
    def __init__(
        self,
        B_z_tesla: float = 3.0,  # Champ principal (T)
        T1_us: float = 45e6,     # T1 long (converti en µs)
        T2_us: float = 3.5,      # T2 effectif (µs)
        temperature_k: float = 310.0
    ):
        """
        Args:
            B_z_tesla: Champ magnétique principal (T)
            T1_us: Relaxation longitudinale (µs)
            T2_us: Relaxation transverse (µs)
            temperature_k: Température (K)
        """
        self.gamma = 10.7 * 2 * np.pi  # MHz/T → rad/(µs·T)
        self.B_z = B_z_tesla
        self.omega_larmor = self.gamma * self.B_z  # rad/µs
        self.T1 = T1_us
        self.T2 = T2_us
        self.temperature_k = temperature_k
        
        # Magnétisation d'équilibre (proportionnelle à B_z via Curie)
        # À 310K, 13C à 3T: M0 ~ 10^-5 (très faible sans hyperpolarisation)
        # Avec DNP: M0 peut être augmenté de 10^4×
        self.M0_hyperpolarized = 1.0  # Normalisé après hyperpolarisation
    
    def evolve(
        self,
        M: np.ndarray,
        dt_us: float,
        B_rf_amplitude: float = 0.0,
        B_rf_phase: float = 0.0,
        detuning: float = 0.0,
        noise_strength: float = 0.0
    ) -> np.ndarray:
        """
        Évolution Bloch avec relaxation.
        
        Args:
            M: Magnétisation (M_x, M_y, M_z)
            dt_us: Pas de temps (µs)
            B_rf_amplitude: Amplitude du champ RF (en unités de γ·B)
            B_rf_phase: Phase du champ RF (rad)
            detuning: Detuning Δω = ω_rf - ω_larmor (rad/µs)
            noise_strength: Amplitude du bruit
            
        Returns:
            Magnétisation évoluée (3,)
        """
        M_x, M_y, M_z = M
        
        # 1. Champ effectif (référentiel tournant)
        # B_eff = (B_rf·cos(φ), B_rf·sin(φ), Δω/γ)
        B_eff_x = B_rf_amplitude * np.cos(B_rf_phase)
        B_eff_y = B_rf_amplitude * np.sin(B_rf_phase)
        B_eff_z = detuning / self.gamma  # Convert detuning to field
        
        # 2. Précession: dM/dt = γ(M × B_eff)
        dM_x_precession = self.gamma * (M_y * B_eff_z - M_z * B_eff_y)
        dM_y_precession = self.gamma * (M_z * B_eff_x - M_x * B_eff_z)
        dM_z_precession = self.gamma * (M_x * B_eff_y - M_y * B_eff_x)
        
        # 3. Relaxation
        dM_x_relax = -M_x / self.T2
        dM_y_relax = -M_y / self.T2
        dM_z_relax = -(M_z - self.M0_hyperpolarized) / self.T1
        
        # 4. Bruit (gaussien sur chaque composante)
        if noise_strength > 0:
            noise_x = noise_strength * np.random.randn() * np.sqrt(dt_us)
            noise_y = noise_strength * np.random.randn() * np.sqrt(dt_us)
            noise_z = noise_strength * np.random.randn() * np.sqrt(dt_us)
        else:
            noise_x = noise_y = noise_z = 0.0
        
        # 5. Intégration Euler
        M_x_new = M_x + dt_us * (dM_x_precession + dM_x_relax + noise_x)
        M_y_new = M_y + dt_us * (dM_y_precession + dM_y_relax + noise_y)
        M_z_new = M_z + dt_us * (dM_z_precession + dM_z_relax + noise_z)
        
        return np.array([M_x_new, M_y_new, M_z_new])
    
    def measure_signal(self, M: np.ndarray) -> float:
        """
        Signal RMN (magnitude transverse).
        
        On détecte typiquement |M_xy| = √(M_x^2 + M_y^2).
        
        Returns:
            Signal normalisé [0, 1]
        """
        M_xy = np.sqrt(M[0]**2 + M[1]**2)
        return M_xy / (self.M0_hyperpolarized + 1e-9)


# ============================================================================
# 3. RADICAL PAIR (2-Spin System)
# ============================================================================

class RadicalPairModel:
    """
    Modèle 2-spins pour radical pairs (cryptochrome, etc.).
    
    Hamiltonien (espace 4D: |↑↑⟩, |↑↓⟩, |↓↑⟩, |↓↓⟩):
        H = ω1·S1_z + ω2·S2_z + J·(S1·S2) + A·I·S1
    
    Où:
        ω1, ω2 : Fréquences Zeeman des deux radicaux
        J : Couplage exchange
        A·I·S1 : Couplage hyperfin (simplifié)
    
    Recombination:
        Les radical pairs peuvent se recombiner (singulet → produit).
        Modélisé comme un decay Γ·|S⟩⟨S|.
    
    Références:
        Hore & Mouritsen, Annu. Rev. Biophys. 45, 299 (2016)
        Timmel et al., Mol. Phys. 95, 71 (1998)
    """
    
    def __init__(
        self,
        omega1_mhz: float = 0.01,  # Zeeman freq spin 1 (MHz)
        omega2_mhz: float = 0.01,  # Zeeman freq spin 2 (MHz)
        J_mhz: float = 0.001,      # Exchange coupling (MHz)
        A_mhz: float = 0.002,      # Hyperfine coupling (MHz)
        T2_us: float = 0.8,        # Dephasing time (µs)
        k_recomb_inv_us: float = 0.01,  # Recombination rate (1/µs)
        temperature_k: float = 310.0
    ):
        """
        Args:
            omega1_mhz: Fréquence Zeeman spin 1 (MHz)
            omega2_mhz: Fréquence Zeeman spin 2 (MHz)
            J_mhz: Couplage exchange (MHz)
            A_mhz: Couplage hyperfin effectif (MHz)
            T2_us: Dephasing (µs)
            k_recomb_inv_us: Taux de recombinaison (1/µs)
            temperature_k: Température (K)
        """
        self.omega1 = omega1_mhz * 2 * np.pi  # rad/µs
        self.omega2 = omega2_mhz * 2 * np.pi
        self.J = J_mhz * 2 * np.pi
        self.A = A_mhz * 2 * np.pi
        self.T2 = T2_us
        self.k_recomb = k_recomb_inv_us
        self.temperature_k = temperature_k
        
        # Opérateurs Pauli pour chaque spin (4×4)
        # Base: |↑↑⟩, |↑↓⟩, |↓↑⟩, |↓↓⟩ = |0⟩, |1⟩, |2⟩, |3⟩
        
        # S1_z (spin 1)
        self.S1_z = 0.5 * np.diag([1, 1, -1, -1])
        
        # S2_z (spin 2)
        self.S2_z = 0.5 * np.diag([1, -1, 1, -1])
        
        # S1·S2 = S1_x·S2_x + S1_y·S2_y + S1_z·S2_z
        # Pour S=1/2: S1·S2 = (1/4)[σ1·σ2]
        # Simplifié: S1·S2 = (|S⟩⟨S| - 3|T⟩⟨T|)/4
        # Où |S⟩ = (|↑↓⟩ - |↓↑⟩)/√2, |T⟩ = états triplet
        
        # Projection singulet
        self.P_singlet = np.zeros((4, 4))
        # |S⟩ = (|↑↓⟩ - |↓↑⟩)/√2 = (|1⟩ - |2⟩)/√2
        singlet_state = np.array([0, 1, -1, 0]) / np.sqrt(2)
        self.P_singlet = np.outer(singlet_state, singlet_state.conj())
        
        # Opérateur S1·S2 (approximation via projections)
        # S1·S2 ≈ -3/4·(1 - 2·P_singlet)
        self.S1_dot_S2 = -0.75 * (np.eye(4) - 2 * self.P_singlet)
        
        # Hamiltonien statique
        self.H_static = (
            self.omega1 * self.S1_z +
            self.omega2 * self.S2_z +
            self.J * self.S1_dot_S2
        )
        
        # Pour simplifier hyperfin: A·I·S1 ~ A·S1_z (field-like)
        self.H_static += self.A * self.S1_z
    
    def evolve(
        self,
        state: np.ndarray,
        dt_us: float,
        noise_strength: float = 0.0
    ) -> np.ndarray:
        """
        Évolution avec dephasing + recombination.
        
        Args:
            state: Vecteur d'état (4,) complexe
            dt_us: Pas de temps (µs)
            noise_strength: Amplitude du bruit
            
        Returns:
            État évolué (4,)
        """
        # 1. Évolution unitaire
        U = self._expm(-1j * self.H_static * dt_us)
        state = U @ state
        
        # 2. Recombination (decay du singulet)
        # Approximation: on réduit la population singulet exponentiellement
        decay_factor = np.exp(-self.k_recomb * dt_us)
        # Projet sur singulet
        singlet_amplitude = np.dot(self.P_singlet @ state, state.conj())
        # Appliquer decay seulement au singulet
        state = state - (1 - decay_factor) * singlet_amplitude * self.P_singlet @ state
        
        # 3. Dephasing (random phase kicks)
        if noise_strength > 0:
            phase_noise_scale = np.sqrt(dt_us / self.T2)
            phase_kicks = noise_strength * phase_noise_scale * np.random.randn(4)
            state = np.exp(1j * phase_kicks) * state
        
        # 4. Renormalisation
        norm = np.linalg.norm(state)
        if norm > 1e-9:
            state = state / norm
        
        return state
    
    def _expm(self, A: np.ndarray) -> np.ndarray:
        """Matrix exponential (4×4)."""
        from scipy.linalg import expm
        return expm(A)
    
    def measure_singlet_population(self, state: np.ndarray) -> float:
        """
        Population dans l'état singulet.
        
        Returns:
            P_S = |⟨S|ψ⟩|^2
        """
        singlet_amplitude = np.dot(self.P_singlet @ state, state.conj())
        return np.abs(singlet_amplitude)
    
    def measure_signal(self, state: np.ndarray) -> float:
        """
        Signal effectif (ex: taux de recombinaison product yield).
        
        Dans les manips magnétoréception, on détecte indirectement
        via les produits de recombinaison.
        
        Returns:
            Signal normalisé [0, 1]
        """
        return self.measure_singlet_population(state)


# ============================================================================
# UNIFIED INTERFACE
# ============================================================================

def create_model(system_type: SystemType, **kwargs):
    """
    Factory pour créer un modèle physique.
    
    Args:
        system_type: Type de système (NV_CENTER, HYPERPOLARIZED_13C, RADICAL_PAIR)
        **kwargs: Paramètres spécifiques au modèle
        
    Returns:
        Instance du modèle approprié
    """
    if system_type == SystemType.NV_CENTER:
        return NVCenterModel(**kwargs)
    elif system_type == SystemType.HYPERPOLARIZED_13C:
        return Hyperpolarized13CModel(**kwargs)
    elif system_type == SystemType.RADICAL_PAIR:
        return RadicalPairModel(**kwargs)
    else:
        raise ValueError(f"Unknown system type: {system_type}")


def initial_state(system_type: SystemType) -> np.ndarray:
    """
    État initial par défaut pour chaque système.
    
    Returns:
        État initial normalisé
    """
    if system_type == SystemType.NV_CENTER:
        # État |0⟩ (m_s = 0)
        return np.array([0.0, 1.0, 0.0], dtype=complex)
    
    elif system_type == SystemType.HYPERPOLARIZED_13C:
        # Magnétisation initiale le long de +z (hyperpolarisée)
        return np.array([0.0, 0.0, 1.0])
    
    elif system_type == SystemType.RADICAL_PAIR:
        # État singulet (corrélé)
        return np.array([0, 1, -1, 0], dtype=complex) / np.sqrt(2)
    
    else:
        raise ValueError(f"Unknown system type: {system_type}")

