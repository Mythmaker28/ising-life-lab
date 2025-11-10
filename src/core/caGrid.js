/**
 * Core grid manipulation functions for cellular automata.
 * Grid format: Array<Array<0|1>> where grid[y][x] represents cell at (x,y)
 */

/**
 * Creates a 2D array (height rows × width cols) filled with a default value.
 * @param {number} width - Number of columns
 * @param {number} height - Number of rows
 * @param {0|1} fillValue - Initial value for all cells (default: 0)
 * @returns {Array<Array<0|1>>} New grid
 */
export function createGrid(width, height, fillValue = 0) {
  return Array(height).fill(null).map(() => Array(width).fill(fillValue));
}

/**
 * Creates a deep copy of the grid without mutation.
 * @param {Array<Array<0|1>>} grid - Source grid
 * @returns {Array<Array<0|1>>} New grid with copied values
 */
export function cloneGrid(grid) {
  return grid.map(row => [...row]);
}

/**
 * Sets cells to 1 with probability = density.
 * Handles edge cases: density=0 (all dead), density=1 (all alive).
 * @param {Array<Array<0|1>>} grid - Grid to randomize (will be mutated)
 * @param {number} density - Probability of cell being alive (0-1)
 * @returns {Array<Array<0|1>>} The same grid (mutated)
 */
export function randomizeGrid(grid, density = 0.2) {
  // Handle edge cases
  if (density <= 0) {
    // All dead
    for (let y = 0; y < grid.length; y++) {
      for (let x = 0; x < grid[y].length; x++) {
        grid[y][x] = 0;
      }
    }
    return grid;
  }
  
  if (density >= 1) {
    // All alive
    for (let y = 0; y < grid.length; y++) {
      for (let x = 0; x < grid[y].length; x++) {
        grid[y][x] = 1;
      }
    }
    return grid;
  }
  
  // Randomize with given density
  for (let y = 0; y < grid.length; y++) {
    for (let x = 0; x < grid[y].length; x++) {
      grid[y][x] = Math.random() < density ? 1 : 0;
    }
  }
  
  return grid;
}

