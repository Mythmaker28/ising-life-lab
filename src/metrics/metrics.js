/**
 * Metrics calculation for cellular automata grids.
 * Provides measures of complexity, density, and information content.
 */

/**
 * Calculates basic metrics for a grid.
 * 
 * @param {Array<Array<0|1>>} grid - The grid to analyze
 * @returns {Object} Metrics object with:
 *   - density: fraction of alive cells (0-1)
 *   - entropy: Shannon entropy in bits
 *   - population: total number of alive cells
 */
export function getBasicMetrics(grid) {
  const height = grid.length;
  const width = grid[0].length;
  const totalCells = width * height;
  
  // Count alive cells
  let population = 0;
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      if (grid[y][x] === 1) {
        population++;
      }
    }
  }
  
  // Calculate density
  const density = totalCells > 0 ? population / totalCells : 0;
  
  // Calculate Shannon entropy: H = -p·log₂(p) - q·log₂(q)
  // where p = density (alive), q = 1 - p (dead)
  let entropy = 0;
  const p = density;
  const q = 1 - p;
  
  // Handle edge cases: p=0 or p=1 (entropy = 0)
  if (p > 0 && p < 1) {
    entropy = -(p * Math.log2(p) + q * Math.log2(q));
  }
  
  return {
    density: density,
    entropy: entropy,
    population: population
  };
}

