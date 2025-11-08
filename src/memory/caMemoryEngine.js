/**
 * CA Memory Engine
 * Factorized CA-based memory system with clean API
 */

import { createGrid, randomizeGrid } from '../core/caGrid.js';
import { step } from '../core/caStep.js';

export class CAMemoryEngine {
  constructor(width = 32, height = 32) {
    this.width = width;
    this.height = height;
    this.rule = null;
    this.storedPatterns = [];
  }
  
  /**
   * Store patterns in memory (set the CA rule)
   * @param {Array<Uint8Array>} patterns - Patterns to store
   * @param {Object} options - { rule: {born, survive}, steps: 80 }
   */
  store(patterns, options = {}) {
    this.storedPatterns = patterns.map(p => new Uint8Array(p));
    this.rule = options.rule || { born: [0, 1], survive: [3] };  // Default: B01/S3
    this.storeSteps = options.steps || 80;
    return { success: true, patternsStored: patterns.length };
  }
  
  /**
   * Recall a pattern from noisy input
   * @param {Uint8Array} noisyPattern - Noisy pattern
   * @param {Object} options - { steps, maxDiffRatio }
   * @returns {Object} { recalled, success, distance, stepsUsed }
   */
  recall(noisyPattern, options = {}) {
    const steps = options.steps || this.storeSteps || 80;
    const maxDiffRatio = options.maxDiffRatio || 0.1;
    
    // Convert to 2D grid format
    const grid = this.uint8ToGrid(noisyPattern);
    
    // Evolve with CA rule
    let current = grid;
    for (let i = 0; i < steps; i++) {
      current = step(current, this.rule);
    }
    
    // Convert back to Uint8Array
    const recalled = this.gridToUint8(current);
    
    // Find closest stored pattern
    let bestMatch = null;
    let bestDistance = Infinity;
    
    for (const pattern of this.storedPatterns) {
      const dist = this.hammingDistance(recalled, pattern);
      if (dist < bestDistance) {
        bestDistance = dist;
        bestMatch = pattern;
      }
    }
    
    const distance = bestDistance;
    const ratio = distance / noisyPattern.length;
    const success = ratio <= maxDiffRatio;
    
    return {
      recalled,
      success,
      distance,
      ratio,
      stepsUsed: steps
    };
  }
  
  /**
   * Score a recall attempt
   * @param {Uint8Array} original - Original pattern
   * @param {Uint8Array} recalled - Recalled pattern
   * @returns {Object} { distance, ratio, success }
   */
  score(original, recalled, maxDiffRatio = 0.1) {
    const distance = this.hammingDistance(original, recalled);
    const ratio = distance / original.length;
    const success = ratio <= maxDiffRatio;
    
    return { distance, ratio, success };
  }
  
  // Helper methods
  uint8ToGrid(uint8Array) {
    const grid = [];
    for (let y = 0; y < this.height; y++) {
      const row = [];
      for (let x = 0; x < this.width; x++) {
        row.push(uint8Array[y * this.width + x]);
      }
      grid.push(row);
    }
    return grid;
  }
  
  gridToUint8(grid) {
    const uint8 = new Uint8Array(this.width * this.height);
    for (let y = 0; y < this.height; y++) {
      for (let x = 0; x < this.width; x++) {
        uint8[y * this.width + x] = grid[y][x];
      }
    }
    return uint8;
  }
  
  hammingDistance(a, b) {
    let dist = 0;
    for (let i = 0; i < a.length; i++) {
      if (a[i] !== b[i]) dist++;
    }
    return dist;
  }
}

