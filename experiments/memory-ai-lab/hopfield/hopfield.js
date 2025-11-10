export class HopfieldNetwork {
  constructor(size) {
    this.size = size;
    this.weights = new Float32Array(size * size);
  }
  
  train(patterns) {
    if (patterns.length === 0) throw new Error('Aucun pattern fourni');
    this.weights.fill(0);
    for (const pattern of patterns) {
      if (pattern.length !== this.size) {
        throw new Error(`Pattern de taille ${pattern.length} incompatible avec réseau de taille ${this.size}`);
      }
      for (let i = 0; i < this.size; i++) {
        for (let j = 0; j < this.size; j++) {
          if (i !== j) {
            const pi = pattern[i] * 2 - 1;
            const pj = pattern[j] * 2 - 1;
            this.weights[i * this.size + j] += pi * pj;
          }
        }
      }
    }
    const scale = 1 / patterns.length;
    for (let i = 0; i < this.weights.length; i++) {
      this.weights[i] *= scale;
    }
  }
  
  recall(state, maxSteps = 100) {
    if (state.length !== this.size) {
      throw new Error(`État de taille ${state.length} incompatible avec réseau de taille ${this.size}`);
    }
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
  
  shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
    }
  }
}

