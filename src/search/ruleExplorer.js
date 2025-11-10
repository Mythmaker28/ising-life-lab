/**
 * Automatic rule discovery for Life-like cellular automata.
 * Generates random rules, simulates them, and selects the most interesting ones.
 */

import { createGrid, randomizeGrid } from '../core/caGrid.js';
import { step } from '../core/caStep.js';
import { getBasicMetrics } from '../metrics/metrics.js';
import { totalEnergy } from '../energy/localEnergyStub.js';

/**
 * Generates a random Life-like rule.
 * @returns {Object} Rule with name, born, survive
 */
export function generateRandomRule() {
  const pickSubset = (values, min, max) => {
    const count = Math.floor(Math.random() * (max - min + 1)) + min;
    const set = new Set();
    while (set.size < count && set.size < values.length) {
      set.add(values[Math.floor(Math.random() * values.length)]);
    }
    return Array.from(set).sort((a, b) => a - b);
  };

  const nums = [0, 1, 2, 3, 4, 5, 6, 7, 8];
  const born = pickSubset(nums, 1, 4);
  const survive = pickSubset(nums, 0, 5);
  
  const bornStr = born.join('');
  const surviveStr = survive.join('');
  
  return {
    name: `Auto (B${bornStr}/S${surviveStr})`,
    born,
    survive
  };
}

/**
 * Evaluates a rule by simulating it on a small grid.
 * Classifies rules by type and detects oscillators.
 * @param {Object} rule - Rule to evaluate
 * @param {Object} options - { width, height, steps, density }
 * @returns {Object} { rule, score, densityFinal, entropyMean, variationMean, type, period }
 */
export function evaluateRule(rule, options = {}) {
  const width = options.width || 40;
  const height = options.height || 40;
  const steps = options.steps || 60;
  const density = options.density || 0.25;
  
  // Create and randomize grid
  let grid = createGrid(width, height, 0);
  randomizeGrid(grid, density);
  let previousGrid = null;
  
  // Track metrics over time
  const densities = [];
  const entropies = [];
  const variations = [];
  const hashes = [];
  
  // Simulate
  for (let i = 0; i < steps; i++) {
    const metrics = getBasicMetrics(grid);
    densities.push(metrics.density);
    entropies.push(metrics.entropy);
    
    // Calculate variation (Hamming distance)
    if (previousGrid) {
      let changes = 0;
      const totalCells = width * height;
      for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
          if (grid[y][x] !== previousGrid[y][x]) {
            changes++;
          }
        }
      }
      variations.push(changes / totalCells);
    }
    
    // Simple hash
    const hash = grid.map(row => row.join('')).join('|');
    hashes.push(hash);
    
    previousGrid = grid.map(row => [...row]);
    grid = step(grid, rule);
  }
  
  // Calculate metrics
  const densityFinal = densities[densities.length - 1];
  const entropyMean = entropies.reduce((a, b) => a + b, 0) / entropies.length;
  const variationMean = variations.length > 0 
    ? variations.slice(10).reduce((a, b) => a + b, 0) / Math.max(1, variations.length - 10)
    : 0;
  
  // Detect oscillator (check last 10 steps for repeating hash)
  let isOscillator = false;
  let period = null;
  if (hashes.length >= 20) {
    const lastHash = hashes[hashes.length - 1];
    for (let p = 2; p <= 10; p++) {
      if (hashes.length > p && hashes[hashes.length - 1 - p] === lastHash) {
        isOscillator = true;
        period = p;
        break;
      }
    }
  }
  
  // Check if frozen (very low variation in last 10 steps)
  const variationLast10 = variations.length >= 10
    ? variations.slice(-10).reduce((a, b) => a + b, 0) / 10
    : variationMean;
  
  // Classify rule type
  let type = 'boring';
  
  if (densityFinal < 0.02) {
    type = 'dead';
  } else if (densityFinal > 0.9) {
    type = 'full';
  } else if (variationLast10 < 0.001) {
    type = 'frozen';
  } else if (isOscillator) {
    type = 'oscillating';
  } else if (densityFinal >= 0.05 && densityFinal <= 0.8 && entropyMean > 0.7 && variationMean > 0.02) {
    type = 'complex';
  }
  
  // Calculate score for interesting rules
  let score = 0;
  if (type === 'complex' || type === 'oscillating') {
    score = entropyMean
      + 0.5 * (1 - Math.abs(densityFinal - 0.3))
      + 0.5 * variationMean;
  }
  
  return { rule, score, densityFinal, entropyMean, variationMean, type, period };
}

/**
 * Explores many random rules and returns the best complex/oscillating ones.
 * @param {number} numCandidates - Number of rules to generate
 * @param {Object} options - Simulation options
 * @returns {Array} Top interesting rules sorted by score
 */
export function exploreRules(numCandidates = 30, options = {}) {
  const results = [];
  
  for (let i = 0; i < numCandidates; i++) {
    const rule = generateRandomRule();
    const evaluation = evaluateRule(rule, options);
    
    // Only keep complex or oscillating rules with good scores
    if ((evaluation.type === 'complex' || evaluation.type === 'oscillating') && evaluation.score > 1.0) {
      results.push(evaluation);
    }
  }
  
  // Sort by score descending
  results.sort((a, b) => b.score - a.score);
  
  // Return top 5
  return results.slice(0, 5);
}

