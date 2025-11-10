"""
Ising Model Engine - Classical Ising spin dynamics.

Provides deterministic/stochastic Ising evolution with:
- Classical 2D Ising Hamiltonian
- External field support
- Glauber/Metropolis dynamics
- Temperature control
"""

import numpy as np
from typing import Tuple, Optional


class IsingEngine:
    """
    Core engine for Ising model evolution.
    
    Implements classical Ising model on 2D lattice with configurable dynamics.
    """
    
    def __init__(
        self,
        grid_size: Tuple[int, int],
        J: float = 1.0,
        h: float = 0.0,
        temperature: float = 1.0,
        dynamics: str = "glauber",
        boundary: str = "periodic",
        seed: Optional[int] = None
    ):
        """
        Initialize Ising engine.
        
        Args:
            grid_size: (height, width) of spin lattice
            J: Coupling strength (positive = ferromagnetic)
            h: External magnetic field
            temperature: Temperature (in units of J/k_B)
            dynamics: Update rule ("glauber" or "metropolis")
            boundary: Boundary conditions ("periodic" or "fixed")
            seed: Random seed for reproducibility
        """
        self.grid_size = grid_size
        self.J = J
        self.h = h
        self.temperature = temperature
        self.dynamics = dynamics
        self.boundary = boundary
        self.seed = seed
        
        if seed is not None:
            np.random.seed(seed)
        
        # Initialize spins (+1 or -1)
        self.spins = self._initialize_spins()
        self.history = [self.spins.copy()]
        
    def _initialize_spins(self) -> np.ndarray:
        """Initialize spin configuration randomly."""
        return np.random.choice([-1, 1], size=self.grid_size).astype(np.int8)
    
    def _local_energy(self, i: int, j: int) -> float:
        """
        Compute local energy at site (i, j).
        
        H_local = -J * s_ij * sum(neighbors) - h * s_ij
        """
        h, w = self.grid_size
        spin = self.spins[i, j]
        
        # Sum over nearest neighbors
        neighbor_sum = 0.0
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if self.boundary == "periodic":
                ni = (i + di) % h
                nj = (j + dj) % w
            else:
                ni = i + di
                nj = j + dj
                if ni < 0 or ni >= h or nj < 0 or nj >= w:
                    continue
            
            neighbor_sum += self.spins[ni, nj]
        
        return -self.J * spin * neighbor_sum - self.h * spin
    
    def _energy_change(self, i: int, j: int) -> float:
        """
        Compute energy change if spin at (i, j) is flipped.
        
        ΔE = 2 * H_local
        """
        return 2.0 * self._local_energy(i, j)
    
    def step(self, n_flips: Optional[int] = None) -> np.ndarray:
        """
        Perform one Monte Carlo sweep (or n_flips attempts).
        
        Args:
            n_flips: Number of flip attempts (default: grid size)
            
        Returns:
            Updated spin configuration
        """
        if n_flips is None:
            n_flips = self.spins.size
        
        h, w = self.grid_size
        
        for _ in range(n_flips):
            # Random site
            i = np.random.randint(h)
            j = np.random.randint(w)
            
            # Compute energy change
            dE = self._energy_change(i, j)
            
            # Accept/reject flip
            if self.dynamics == "glauber":
                # Glauber dynamics: p_accept = 1 / (1 + exp(β * ΔE))
                if self.temperature > 0:
                    p_accept = 1.0 / (1.0 + np.exp(dE / self.temperature))
                else:
                    p_accept = 1.0 if dE <= 0 else 0.0
            elif self.dynamics == "metropolis":
                # Metropolis: p_accept = min(1, exp(-β * ΔE))
                if self.temperature > 0:
                    p_accept = min(1.0, np.exp(-dE / self.temperature))
                else:
                    p_accept = 1.0 if dE <= 0 else 0.0
            else:
                raise ValueError(f"Unknown dynamics: {self.dynamics}")
            
            # Flip spin if accepted
            if np.random.rand() < p_accept:
                self.spins[i, j] *= -1
        
        self.history.append(self.spins.copy())
        return self.spins
    
    def total_energy(self) -> float:
        """Compute total Hamiltonian."""
        h, w = self.grid_size
        energy = 0.0
        
        for i in range(h):
            for j in range(w):
                # Interaction energy (count each pair once)
                for di, dj in [(0, 1), (1, 0)]:  # Right and down only
                    if self.boundary == "periodic":
                        ni = (i + di) % h
                        nj = (j + dj) % w
                    else:
                        ni = i + di
                        nj = j + dj
                        if ni >= h or nj >= w:
                            continue
                    
                    energy += -self.J * self.spins[i, j] * self.spins[ni, nj]
                
                # External field
                energy += -self.h * self.spins[i, j]
        
        return energy
    
    def magnetization(self) -> float:
        """Compute total magnetization."""
        return np.sum(self.spins) / self.spins.size
    
    def run(self, steps: int) -> list:
        """
        Run Ising dynamics for specified number of steps.
        
        Args:
            steps: Number of Monte Carlo sweeps
            
        Returns:
            History of spin configurations
        """
        for _ in range(steps):
            self.step()
        
        return self.history
    
    def reset(self, new_seed: Optional[int] = None):
        """Reset to new initial spin configuration."""
        if new_seed is not None:
            self.seed = new_seed
            np.random.seed(new_seed)
        
        self.spins = self._initialize_spins()
        self.history = [self.spins.copy()]

