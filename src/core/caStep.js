/**
 * Single-step evolution of cellular automata grid.
 * Applies rule simultaneously to all cells (synchronous update).
 */

import { createGrid } from './caGrid.js';
import { applyRuleToCell } from './caRules.js';

/**
 * Evolves the grid one generation by applying the rule to all cells simultaneously.
 * Returns a NEW grid, never mutates the input.
 * 
 * @param {Array<Array<0|1>>} grid - Current generation grid
 * @param {Object} rule - Rule object with 'born' and 'survive' arrays
 * @returns {Array<Array<0|1>>} New grid representing next generation
 */
export function step(grid, rule) {
  const height = grid.length;
  const width = grid[0].length;
  
  // Create fresh output grid
  const nextGrid = createGrid(width, height, 0);
  
  // Apply rule to all cells simultaneously
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      nextGrid[y][x] = applyRuleToCell(grid, x, y, rule);
    }
  }
  
  return nextGrid;
}

