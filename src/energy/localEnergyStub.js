/**
 * Local energy functions for cellular automata grids.
 * 
 * This module provides a placeholder implementation for energy-based modeling
 * of CA dynamics. The energy function penalizes isolated cells and rewards
 * well-connected patterns, similar to Ising model ferromagnetic coupling.
 * 
 * FUTURE EXTENSIONS:
 * - Learn Hamiltonian functions that predict CA evolution
 * - Fit energy landscapes to observed CA dynamics
 * - Connect to Hopfield networks for pattern storage/retrieval
 * - Use energy minimization to find stable configurations
 * 
 * ISING MODEL CONNECTION:
 * In the Ising model, spins prefer to align with neighbors (ferromagnetic).
 * Here, alive cells prefer to have neighbors (lower energy = more stable).
 * Isolated alive cells have high energy (unstable), while clusters have low energy (stable).
 */

import { countAliveNeighbors } from '../core/caRules.js';

/**
 * Calculates local energy contribution of a single cell.
 * Lower energy = more stable configuration.
 * 
 * NOTE: This is NOT a physical Ising model, but a simple energy-like score
 * that can be refined later. The goal is to provide an intuitive measure
 * of pattern stability that hints at Ising-style energy landscapes.
 * 
 * Energy model:
 * - Alive cell: energy = 4 - min(neighbors, 4)
 *   - Penalizes isolation (0 neighbors = energy 4)
 *   - Rewards moderate connectivity (2-4 neighbors = lower energy)
 *   - Slight penalty for overcrowding (>4 neighbors)
 * - Dead cell: energy = neighbors > 5 ? 1 : 0
 *   - Slight cost for overcrowded dead zones
 * 
 * @param {Array<Array<0|1>>} grid - The grid
 * @param {number} x - Column index
 * @param {number} y - Row index
 * @returns {number} Local energy contribution
 */
export function localEnergy(grid, x, y) {
  const cell = grid[y][x];
  const neighbors = countAliveNeighbors(grid, x, y);
  
  if (cell === 1) {
    // Alive cell: penalize isolation, reward 2-4 neighbors
    return 4 - Math.min(neighbors, 4);
  } else {
    // Dead cell: slight penalty for overcrowded neighborhoods
    return neighbors > 5 ? 1 : 0;
  }
}

/**
 * Calculates total energy of the entire grid by summing local energies.
 * 
 * @param {Array<Array<0|1>>} grid - The grid
 * @returns {number} Total energy (sum of all local energies)
 */
export function totalEnergy(grid) {
  const height = grid.length;
  const width = grid[0].length;
  let energy = 0;
  
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      energy += localEnergy(grid, x, y);
    }
  }
  
  return energy;
}

