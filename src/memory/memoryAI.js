/**
 * MemoryAI - Multi-Engine Memory System
 * 7 CA champions + Hopfield baseline
 */

import { CAMemoryEngine } from './caMemoryEngine.js';
import { HopfieldMemoryEngine } from './hopfieldMemoryEngine.js';

export const MEMORY_CHAMPIONS = [
  'B01/S3',
  'B01/S23',
  'B01/S34',
  'B01/S2',
  'B01/S4',
  'B01/S13',
  'B46/S58',
];

export class MemoryAI {
  constructor({ width = 32, height = 32, steps = 80 } = {}) {
    this.width = width;
    this.height = height;
    this.steps = steps;
    
    this.caEngines = MEMORY_CHAMPIONS.map(rule => ({
      rule,
      engine: CAMemoryEngine.create({ rule, width, height, steps })
    }));
    
    this.hopfield = HopfieldMemoryEngine.create({ width, height });
  }
  
  store(patterns) {
    this.caEngines.forEach(({ engine }) => engine.store(patterns));
    this.hopfield.store(patterns);
  }
  
  recall(noisy) {
    const results = this.caEngines.map(({ rule, engine }) => {
      const r = engine.recall(noisy, { steps: this.steps });
      return { rule, distance: r.distance, success: r.success };
    });
    
    const hr = this.hopfield.recall(noisy);
    results.push({ rule: 'Hopfield', distance: hr.distance, success: hr.success });
    
    results.sort((a, b) => a.distance - b.distance);
    
    return {
      best: results[0],
      all: results
    };
  }
}

export function createMemoryAI(opts) {
  return new MemoryAI(opts);
}

