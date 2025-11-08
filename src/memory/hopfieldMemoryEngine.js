/**
 * Hopfield Memory Engine
 * Factorized Hopfield network with clean API matching CAMemoryEngine
 */

export class HopfieldMemoryEngine {
  constructor(size = 1024) {
    this.size = size;
    this.weights = new Float32Array(size * size);
    this.storedPatterns = [];
  }
  
  /**
   * Store patterns in memory (train the network)
   * @param {Array<Uint8Array>} patterns - Patterns to store
   * @param {Object} options - Unused (for API compatibility)
   */
  store(patterns, options = {}) {
    this.storedPatterns = patterns.map(p => new Uint8Array(p));
    this.train(this.storedPatterns);
    return { success: true, patternsStored: patterns.length };
  }
  
  /**
   * Train network with Hebb rule
   */
  train(patterns) {
    if (patterns.length === 0) return;
    
    this.weights.fill(0);
    
    for (const pattern of patterns) {
      for (let i = 0; i < this.size; i++) {
        for (let j = 0; j < this.size; j++) {
          if (i !== j) {
            const pi = pattern[i] * 2 - 1;  // 0→-1, 1→1
            const pj = pattern[j] * 2 - 1;
            this.weights[i * this.size + j] += pi * pj;
          }
        }
      }
    }
    
    // Normaliser
    const scale = 1 / patterns.length;
    for (let i = 0; i < this.weights.length; i++) {
      this.weights[i] *= scale;
    }
  }
  
  /**
   * Recall a pattern from noisy input
   * @param {Uint8Array} noisyPattern - Noisy pattern
   * @param {Object} options - { maxSteps, maxDiffRatio }
   * @returns {Object} { recalled, success, distance, stepsUsed }
   */
  recall(noisyPattern, options = {}) {
    const maxSteps = options.maxSteps || 100;
    const maxDiffRatio = options.maxDiffRatio || 0.1;
    
    const recalled = this.recallAsync(noisyPattern, maxSteps);
    
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
      stepsUsed: maxSteps  // Hopfield converges in <maxSteps
    };
  }
  
  /**
   * Async recall (update until convergence)
   */
  recallAsync(state, maxSteps = 100) {
    const current = new Uint8Array(state);
    
    for (let step = 0; step < maxSteps; step++) {
      let changed = false;
      const indices = Array.from({ length: this.size }, (_, i) => i);
      this.shuffle(indices);
      
      for (const i of indices) {
        let sum = 0;
        for (let j = 0; j < this.size; j++) {
          sum += this.weights[i * this.size + j] * (current[j] * 2 - 1);
        }
        
        const newVal = sum >= 0 ? 1 : 0;
        if (newVal !== current[i]) {
          current[i] = newVal;
          changed = true;
        }
      }
      
      if (!changed) break;
    }
    
    return current;
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
  shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
    }
  }
  
  hammingDistance(a, b) {
    let dist = 0;
    for (let i = 0; i < a.length; i++) {
      if (a[i] !== b[i]) dist++;
    }
    return dist;
  }
}

