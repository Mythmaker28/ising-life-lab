"""
Détection de défauts topologiques dans les champs de phase.

Défauts = singularités du champ de phase (vortex, anti-vortex).
Le Winding Number mesure la charge topologique :
    W = (1/2π) ∮ ∇θ · dl

Métrique phénoménologique : #défauts_actifs ~ fragmentation perceptuelle
"""

import numpy as np
from numba import jit
from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class DefectMetrics:
    """Métriques des défauts topologiques."""
    
    n_defects: int  # Nombre total de défauts
    n_positive: int  # Vortex (+1)
    n_negative: int  # Anti-vortex (-1)
    defect_positions: List[Tuple[int, int]]  # Positions (x, y)
    defect_charges: List[int]  # Charges topologiques
    defect_density: float  # Densité de défauts par unité d'aire
    
    def get_annihilation_potential(self) -> float:
        """
        Potentiel d'annihilation : mesure de la proximité vortex/anti-vortex.
        
        Interprétation phénoménologique :
            - Faible : système stable (uniformité comme 5-MeO-DMT)
            - Élevé : système chaotique (fragmentation comme N,N-DMT)
        """
        if len(self.defect_positions) < 2:
            return 0.0
        
        total_potential = 0.0
        for i, (xi, yi) in enumerate(self.defect_positions):
            qi = self.defect_charges[i]
            for j in range(i + 1, len(self.defect_positions)):
                xj, yj = self.defect_positions[j]
                qj = self.defect_charges[j]
                
                dist = np.sqrt((xi - xj)**2 + (yi - yj)**2)
                if dist < 1e-6:
                    continue
                
                # Attraction vortex/anti-vortex
                if qi * qj < 0:
                    total_potential += 1.0 / (dist + 1.0)
        
        return total_potential


@jit(nopython=True)
def _compute_plaquette_winding(
    phase: np.ndarray,
    i: int,
    j: int
) -> float:
    """
    Calcule le winding number sur une plaquette 2×2.
    
    Plaquette :
        (i,j) → (i,j+1)
          ↑         ↓
        (i+1,j) ← (i+1,j+1)
    
    Returns:
        Winding number normalisé [-1, 1]
    """
    h, w = phase.shape
    
    # Coins de la plaquette
    p00 = phase[i, j]
    p01 = phase[i, (j + 1) % w]
    p10 = phase[(i + 1) % h, j]
    p11 = phase[(i + 1) % h, (j + 1) % w]
    
    # Différences de phase le long du contour
    # Astuce : utiliser arctan2 pour gérer le wrapping [-π, π]
    d1 = np.arctan2(np.sin(p01 - p00), np.cos(p01 - p00))
    d2 = np.arctan2(np.sin(p11 - p01), np.cos(p11 - p01))
    d3 = np.arctan2(np.sin(p10 - p11), np.cos(p10 - p11))
    d4 = np.arctan2(np.sin(p00 - p10), np.cos(p00 - p10))
    
    # Winding number = somme totale / 2π
    winding = (d1 + d2 + d3 + d4) / (2 * np.pi)
    
    return winding


def compute_winding_number(phase_field: np.ndarray) -> np.ndarray:
    """
    Calcule le champ de winding number pour chaque plaquette.
    
    Args:
        phase_field: Champ de phase 2D (H, W) avec θ ∈ [0, 2π)
        
    Returns:
        Champ 2D (H, W) de winding numbers. Valeurs typiques :
            ≈ 0 : pas de défaut
            ≈ +1 : vortex
            ≈ -1 : anti-vortex
    """
    h, w = phase_field.shape
    winding_field = np.zeros((h, w), dtype=np.float32)
    
    for i in range(h):
        for j in range(w):
            winding_field[i, j] = _compute_plaquette_winding(phase_field, i, j)
    
    return winding_field


def detect_vortices(
    phase_field: np.ndarray,
    threshold: float = 0.5
) -> DefectMetrics:
    """
    Détecte les défauts topologiques (vortices) dans un champ de phase.
    
    Args:
        phase_field: Champ de phase 2D
        threshold: Seuil pour détecter un défaut (|winding| > threshold)
        
    Returns:
        DefectMetrics contenant positions et charges des défauts
    """
    winding_field = compute_winding_number(phase_field)
    
    defect_positions = []
    defect_charges = []
    
    h, w = phase_field.shape
    
    for i in range(h):
        for j in range(w):
            w_val = winding_field[i, j]
            
            if abs(w_val) > threshold:
                defect_positions.append((i, j))
                # Quantification : +1 ou -1
                charge = +1 if w_val > 0 else -1
                defect_charges.append(charge)
    
    n_positive = sum(1 for c in defect_charges if c > 0)
    n_negative = sum(1 for c in defect_charges if c < 0)
    
    density = len(defect_positions) / (h * w)
    
    return DefectMetrics(
        n_defects=len(defect_positions),
        n_positive=n_positive,
        n_negative=n_negative,
        defect_positions=defect_positions,
        defect_charges=defect_charges,
        defect_density=density
    )


def track_defects_over_time(
    phase_history: List[np.ndarray],
    threshold: float = 0.5
) -> List[DefectMetrics]:
    """
    Analyse temporelle des défauts.
    
    Args:
        phase_history: Liste de champs de phase successifs
        threshold: Seuil de détection
        
    Returns:
        Liste de DefectMetrics par timestep
    """
    metrics_history = []
    
    for phase_field in phase_history:
        metrics = detect_vortices(phase_field, threshold)
        metrics_history.append(metrics)
    
    return metrics_history


def compute_defect_annihilation_rate(
    metrics_history: List[DefectMetrics],
    window: int = 10
) -> np.ndarray:
    """
    Calcule le taux d'annihilation des défauts (lissé).
    
    Interprétation :
        - Taux élevé : système converge vers uniformité (5-MeO-DMT)
        - Taux faible : défauts persistent (DMT chaotique)
        
    Args:
        metrics_history: Historique des métriques
        window: Taille de la fenêtre de lissage
        
    Returns:
        Taux d'annihilation par timestep
    """
    n_defects = np.array([m.n_defects for m in metrics_history], dtype=float)
    
    # Dérivée temporelle lissée
    if len(n_defects) < 2:
        return np.zeros_like(n_defects)
    
    rate = np.zeros_like(n_defects)
    for i in range(1, len(n_defects)):
        rate[i] = n_defects[i-1] - n_defects[i]
    
    # Lissage (convolution)
    if window > 1 and len(rate) >= window:
        kernel = np.ones(window) / window
        rate = np.convolve(rate, kernel, mode='same')
    
    return rate

