/**
 * Cellular automata rule application logic.
 * Supports Life-like rules with Moore neighborhood (8 neighbors) and toroidal wrapping.
 */

/**
 * Counts alive neighbors in Moore neighborhood (8 surrounding cells).
 * Uses toroidal wrapping: cells at edges wrap around to opposite side.
 * @param {Array<Array<0|1>>} grid - The grid
 * @param {number} x - Column index
 * @param {number} y - Row index
 * @returns {number} Count of alive neighbors (0-8)
 */
export function countAliveNeighbors(grid, x, y) {
  const height = grid.length;
  const width = grid[0].length;
  let count = 0;
  
  // Moore neighborhood: check all 8 surrounding cells
  const offsets = [
    [-1, -1], [0, -1], [1, -1],  // Top row
    [-1,  0],          [1,  0],  // Middle row (skip center)
    [-1,  1], [0,  1], [1,  1]   // Bottom row
  ];
  
  for (const [dx, dy] of offsets) {
    // Toroidal wrapping: (x + width) % width handles negative and overflow
    const nx = (x + dx + width) % width;
    const ny = (y + dy + height) % height;
    
    if (grid[ny][nx] === 1) {
      count++;
    }
  }
  
  return count;
}

/**
 * Applies a Life-like rule to a single cell.
 * Rule format: { born: number[], survive: number[] }
 * - born: list of neighbor counts that cause dead cell to become alive
 * - survive: list of neighbor counts that allow alive cell to stay alive
 * 
 * @param {Array<Array<0|1>>} grid - The grid
 * @param {number} x - Column index
 * @param {number} y - Row index
 * @param {Object} rule - Rule object with 'born' and 'survive' arrays
 * @returns {0|1} New cell state
 */
export function applyRuleToCell(grid, x, y, rule) {
  const currentState = grid[y][x];
  const neighbors = countAliveNeighbors(grid, x, y);
  
  if (currentState === 0) {
    // Dead cell: becomes alive if neighbor count is in 'born' list
    return rule.born.includes(neighbors) ? 1 : 0;
  } else {
    // Alive cell: stays alive if neighbor count is in 'survive' list
    return rule.survive.includes(neighbors) ? 1 : 0;
  }
}

