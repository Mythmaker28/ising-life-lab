/**
 * Attractor scanning for cellular automata.
 * Tests if a CA rule has memory by checking convergence to stable attractors.
 */

import { createGrid, cloneGrid } from '../core/caGrid.js';
import { step } from '../core/caStep.js';
import { RULES } from '../presets/rules.js';

/**
 * Gets a rule by name from RULES.
 * @param {string} name - Rule name
 * @returns {Object|null} Rule or null if not found
 */
export function getRuleByName(name) {
  return RULES.find(r => r.name === name) || null;
}

/**
 * Hashes a grid to a stable string.
 * @param {Array<Array<0|1>>} grid - Grid to hash
 * @returns {string} Hash string
 */
export function hashGrid(grid) {
  return grid.map(row => row.join('')).join('|');
}

/**
 * Applies noise to a grid (returns a new copy).
 * @param {Array<Array<0|1>>} grid - Original grid
 * @param {number} noise - Probability of flip per cell (0-1)
 * @returns {Array<Array<0|1>>} Noisy copy
 */
export function applyNoise(grid, noise) {
  const height = grid.length;
  const width = grid[0].length;
  const noisyGrid = cloneGrid(grid);
  
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      if (Math.random() < noise) {
        noisyGrid[y][x] = 1 - noisyGrid[y][x]; // Flip
      }
    }
  }
  
  return noisyGrid;
}

/**
 * Runs relaxation from a base grid with noise.
 * @param {Object} rule - CA rule
 * @param {Array<Array<0|1>>} baseGrid - Starting pattern
 * @param {Object} options - { noise, steps }
 * @returns {Object} { finalGrid, finalHash }
 */
export function runRelaxation(rule, baseGrid, { noise = 0, steps = 60 } = {}) {
  // Apply noise
  let grid = noise > 0 ? applyNoise(baseGrid, noise) : cloneGrid(baseGrid);
  
  // Evolve
  for (let i = 0; i < steps; i++) {
    grid = step(grid, rule);
  }
  
  return {
    finalGrid: grid,
    finalHash: hashGrid(grid)
  };
}

/**
 * Scans for attractors by running multiple relaxation trials.
 * @param {Object} rule - CA rule
 * @param {Array<Array<0|1>>} baseGrid - Base pattern
 * @param {Object} options - { runs, steps, noise, maxAttractors }
 * @returns {Object} Scan report with attractors
 */
export function scanAttractors(rule, baseGrid, {
  runs = 40,
  steps = 80,
  noise = 0.1,
  maxAttractors = 6
} = {}) {
  
  console.log(`🔬 Scanning attractors for ${rule.name}...`);
  console.log(`   Runs: ${runs}, Steps: ${steps}, Noise: ${noise}`);
  
  const attractorMap = new Map(); // hash -> { count, sampleGrid }
  
  for (let i = 0; i < runs; i++) {
    const { finalGrid, finalHash } = runRelaxation(rule, baseGrid, { noise, steps });
    
    if (attractorMap.has(finalHash)) {
      attractorMap.get(finalHash).count++;
    } else {
      attractorMap.set(finalHash, {
        count: 1,
        sampleGrid: finalGrid
      });
    }
  }
  
  // Build attractors array
  const attractors = Array.from(attractorMap.entries()).map(([hash, data]) => ({
    hash,
    count: data.count,
    frequency: data.count / runs,
    sampleGrid: data.sampleGrid
  }));
  
  // Sort by frequency descending
  attractors.sort((a, b) => b.frequency - a.frequency);
  
  // Limit to maxAttractors
  const topAttractors = attractors.slice(0, maxAttractors);
  
  console.log(`✅ Found ${attractors.length} distinct attractors (showing top ${topAttractors.length}):`);
  console.table(topAttractors.map((a, i) => ({
    rank: i + 1,
    count: a.count,
    frequency: (a.frequency * 100).toFixed(1) + '%'
  })));
  
  return {
    ruleName: rule.name,
    runs,
    steps,
    noise,
    totalAttractors: attractors.length,
    attractors: topAttractors
  };
}

