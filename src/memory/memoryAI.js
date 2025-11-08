/**
 * MemoryAI - Multi-Engine Memory System
 * 7 CA champions + Hopfield baseline
 */

import { CAMemoryEngine } from './caMemoryEngine.js';
import { HopfieldMemoryEngine } from './hopfieldMemoryEngine.js';
import { EngineSelector } from '../ai/engineSelector.js';

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
  constructor({ width = 32, height = 32, steps = 80, useSelector = false } = {}) {
    this.width = width;
    this.height = height;
    this.steps = steps;
    this.useSelector = useSelector;
    this.selector = null;
    this.storedPatterns = null;
    
    this.caEngines = MEMORY_CHAMPIONS.map(rule => ({
      rule,
      engine: CAMemoryEngine.create({ rule, width, height, steps })
    }));
    
    this.hopfield = HopfieldMemoryEngine.create({ width, height });
  }
  
  store(patterns) {
    this.caEngines.forEach(({ engine }) => engine.store(patterns));
    this.hopfield.store(patterns);
    this.storedPatterns = patterns;
    
    // Train selector asynchronously if enabled
    if (this.useSelector && patterns && patterns.length > 0) {
      this.selector = new EngineSelector();
      this.selector.train({
        memAI: this,
        patterns,
        noiseLevels: [0.05, 0.08],
        samplesPerPattern: 10
      }).catch(err => {
        console.warn('⚠️ EngineSelector training failed:', err.message);
        this.selector = null;
      });
    }
  }
  
  recall(noisy, { usePrediction = false, patternIndex = null } = {}) {
    const allResults = [];
    
    const testEngine = (rule, engine) => {
      const r = engine.recall(noisy, { steps: this.steps });
      const result = { rule, distance: r.distance, success: r.success };
      allResults.push(result);
      return result;
    };
    
    const testAll = () => {
      this.caEngines.forEach(({ rule, engine }) => testEngine(rule, engine));
      const hr = this.hopfield.recall(noisy);
      allResults.push({ rule: 'Hopfield', distance: hr.distance, success: hr.success });
    };
    
    // Use prediction if enabled and trained
    if (usePrediction && this.selector && this.selector.trained) {
      let chosenEngine = null;
      
      if (patternIndex != null) {
        chosenEngine = this.selector.suggestForPattern(patternIndex);
      }
      if (!chosenEngine) {
        chosenEngine = this.selector.bestGlobal();
      }
      
      if (chosenEngine) {
        // Test only predicted engine
        if (chosenEngine === 'Hopfield') {
          const hr = this.hopfield.recall(noisy);
          const result = { rule: 'Hopfield', distance: hr.distance, success: hr.success };
          allResults.push(result);
          return { best: result, all: allResults, predicted: true };
        } else {
          const ca = this.caEngines.find(e => e.rule === chosenEngine);
          if (ca) {
            const result = testEngine(ca.rule, ca.engine);
            return { best: result, all: allResults, predicted: true };
          }
        }
      }
    }
    
    // Fallback: test all engines
    testAll();
    allResults.sort((a, b) => a.distance - b.distance);
    return { best: allResults[0], all: allResults, predicted: false };
  }
}

export function createMemoryAI(opts) {
  return new MemoryAI(opts);
}

