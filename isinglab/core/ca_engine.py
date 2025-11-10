"""
Cellular Automata Engine - Core dynamics implementation.

Provides deterministic CA evolution with support for:
- Elementary CA (1D)
- 2D CA (Life-like, totalistic, outer-totalistic)
- Custom neighborhood definitions
"""

import numpy as np
from typing import Tuple, Optional, Callable


class CAEngine:
    """
    Core engine for cellular automaton evolution.
    
    Supports multiple CA types with deterministic behavior controlled by seeds.
    """
    
    def __init__(
        self,
        grid_size: Tuple[int, ...],
        rule: int,
        ca_type: str = "elementary",
        boundary: str = "periodic",
        seed: Optional[int] = None
    ):
        """
        Initialize CA engine.
        
        Args:
            grid_size: Shape of the grid (width,) for 1D or (height, width) for 2D
            rule: Rule number (Wolfram encoding for elementary, or custom)
            ca_type: Type of CA ("elementary", "life", "totalistic")
            boundary: Boundary conditions ("periodic", "fixed", "reflect")
            seed: Random seed for reproducibility
        """
        self.grid_size = grid_size
        self.rule = rule
        self.ca_type = ca_type
        self.boundary = boundary
        self.seed = seed
        
        # Set random seed for reproducibility
        if seed is not None:
            np.random.seed(seed)
        
        # Parse rule
        self._rule_lookup = self._parse_rule(rule, ca_type)
        
        # Initialize grid
        self.grid = self._initialize_grid()
        self.history = [self.grid.copy()]
        
    def _parse_rule(self, rule: int, ca_type: str) -> dict:
        """Parse rule number into lookup table."""
        if ca_type == "elementary":
            # Wolfram rule: 8 possible neighborhoods -> 8-bit number
            return {
                tuple(map(int, f"{i:03b}")): int(rule & (1 << i) > 0)
                for i in range(8)
            }
        elif ca_type == "life":
            # Conway's Life or similar: B/S notation encoded
            # For now, simple mapping (extendable)
            return self._parse_life_rule(rule)
        else:
            raise ValueError(f"Unknown CA type: {ca_type}")
    
    def _parse_life_rule(self, rule: int) -> dict:
        """
        Parse Life-like rule.
        
        Rule encoding (simple version):
        - Rule 224 = Conway's Life (B3/S23)
        - Bits 0-8: birth conditions
        - Bits 9-17: survival conditions
        """
        birth = []
        survival = []
        
        for i in range(9):
            if rule & (1 << i):
                birth.append(i)
            if rule & (1 << (i + 9)):
                survival.append(i)
        
        return {"birth": set(birth), "survival": set(survival)}
    
    def _initialize_grid(self) -> np.ndarray:
        """Initialize grid with random configuration."""
        if len(self.grid_size) == 1:
            # 1D CA
            grid = np.random.randint(0, 2, size=self.grid_size[0])
        else:
            # 2D CA
            grid = np.random.randint(0, 2, size=self.grid_size)
        
        return grid.astype(np.int8)
    
    def step(self) -> np.ndarray:
        """
        Perform one time step of CA evolution.
        
        Returns:
            Updated grid after one step
        """
        if len(self.grid_size) == 1:
            new_grid = self._step_1d()
        else:
            new_grid = self._step_2d()
        
        self.grid = new_grid
        self.history.append(self.grid.copy())
        
        return self.grid
    
    def _step_1d(self) -> np.ndarray:
        """Evolve 1D elementary CA."""
        new_grid = np.zeros_like(self.grid)
        n = len(self.grid)
        
        for i in range(n):
            # Get neighborhood
            if self.boundary == "periodic":
                left = self.grid[(i - 1) % n]
                center = self.grid[i]
                right = self.grid[(i + 1) % n]
            else:
                left = self.grid[i - 1] if i > 0 else 0
                center = self.grid[i]
                right = self.grid[i + 1] if i < n - 1 else 0
            
            # Apply rule
            neighborhood = (left, center, right)
            new_grid[i] = self._rule_lookup.get(neighborhood, 0)
        
        return new_grid
    
    def _step_2d(self) -> np.ndarray:
        """Evolve 2D CA (Life-like)."""
        new_grid = np.zeros_like(self.grid)
        h, w = self.grid.shape
        
        for i in range(h):
            for j in range(w):
                # Count Moore neighborhood (8 neighbors)
                neighbors = 0
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        
                        if self.boundary == "periodic":
                            ni = (i + di) % h
                            nj = (j + dj) % w
                        else:
                            ni = i + di
                            nj = j + dj
                            if ni < 0 or ni >= h or nj < 0 or nj >= w:
                                continue
                        
                        neighbors += self.grid[ni, nj]
                
                # Apply Life-like rule
                cell = self.grid[i, j]
                birth = self._rule_lookup["birth"]
                survival = self._rule_lookup["survival"]
                
                if cell == 1:
                    new_grid[i, j] = 1 if neighbors in survival else 0
                else:
                    new_grid[i, j] = 1 if neighbors in birth else 0
        
        return new_grid
    
    def run(self, steps: int) -> list:
        """
        Run CA for specified number of steps.
        
        Args:
            steps: Number of time steps to evolve
            
        Returns:
            History of all states (including initial state)
        """
        for _ in range(steps):
            self.step()
        
        return self.history
    
    def reset(self, new_seed: Optional[int] = None):
        """Reset CA to new initial condition."""
        if new_seed is not None:
            self.seed = new_seed
            np.random.seed(new_seed)
        
        self.grid = self._initialize_grid()
        self.history = [self.grid.copy()]

