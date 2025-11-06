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
 * Classifies rules by type: dead, full, frozen, or complex.
 * @param {Object} rule - Rule to evaluate
 * @param {Object} options - { width, height, steps, density }
 * @returns {Object} { rule, score, densityMean, entropyMean, type }
 */
export function evaluateRule(rule, options = {}) {
  const width = options.width || 40;
  const height = options.height || 40;
  const steps = options.steps || 60;
  const density = options.density || 0.25;
  
  // Create and randomize grid
  let grid = createGrid(width, height, 0);
  randomizeGrid(grid, density);
  
  // Track metrics over time
  const densities = [];
  const entropies = [];
  let populationChanges = 0;
  let previousPopulation = 0;
  let changesAfterStep20 = 0;
  
  // Simulate
  for (let i = 0; i < steps; i++) {
    const metrics = getBasicMetrics(grid);
    densities.push(metrics.density);
    entropies.push(metrics.entropy);
    
    if (i > 0 && metrics.population !== previousPopulation) {
      populationChanges++;
      if (i >= 20) {
        changesAfterStep20++;
      }
    }
    previousPopulation = metrics.population;
    
    grid = step(grid, rule);
  }
  
  // Calculate means
  const densityMean = densities.reduce((a, b) => a + b, 0) / densities.length;
  const entropyMean = entropies.reduce((a, b) => a + b, 0) / entropies.length;
  const densityFinal = densities[densities.length - 1];
  const variationNorm = populationChanges / steps;
  
  // Classify rule type
  let type = 'complex';
  
  if (densityFinal < 0.02) {
    type = 'dead';
  } else if (densityFinal > 0.9) {
    type = 'full';
  } else if (changesAfterStep20 < 5) {
    type = 'frozen';
  } else if (densityFinal < 0.05 || densityFinal > 0.8 || entropyMean < 0.7 || variationNorm < 0.1) {
    // Doesn't meet complexity criteria
    type = 'boring';
  }
  
  // Score only for complex rules
  let score = 0;
  if (type === 'complex') {
    score = entropyMean
      + 0.5 * (1 - Math.abs(densityMean - 0.3))
      + 0.3 * variationNorm;
  }
  
  return { rule, score, densityMean, entropyMean, type };
}

/**
 * Explores many random rules and returns the best complex ones.
 * @param {number} numCandidates - Number of rules to generate
 * @param {Object} options - Simulation options
 * @returns {Array} Top complex rules sorted by score
 */
export function exploreRules(numCandidates = 30, options = {}) {
  const results = [];
  
  for (let i = 0; i < numCandidates; i++) {
    const rule = generateRandomRule();
    const evaluation = evaluateRule(rule, options);
    
    // Only keep complex rules with good scores
    if (evaluation.type === 'complex' && evaluation.score > 1.0) {
      results.push(evaluation);
    }
  }
  
  // Sort by score descending
  results.sort((a, b) => b.score - a.score);
  
  // Return top 5
  return results.slice(0, 5);
}

