/**
 * EngineSelector - Learn which memory engine performs best
 * Meta-learning pour optimiser le choix d'engine par pattern
 */

const DEFAULT_ENGINES = [
  'B01/S3', 'B01/S23', 'B01/S34',
  'B01/S2', 'B01/S4', 'B01/S13',
  'B46/S58', 'Hopfield',
];

export class EngineSelector {
  constructor(engines = DEFAULT_ENGINES) {
    this.engines = engines;
    this.globalWins = {};          // engine -> total wins
    this.perPattern = new Map();   // patternIndex -> bestEngine
    this.trained = false;
  }

  async train({ memAI, patterns, noiseLevels = [0.05, 0.08], samplesPerPattern = 10 }) {
    console.log('🧠 Training EngineSelector...');
    
    const addNoise = (grid, rate) => {
      const noisy = new Uint8Array(grid);
      for (let i = 0; i < noisy.length; i++) {
        if (Math.random() < rate) noisy[i] = 1 - noisy[i];
      }
      return noisy;
    };

    const rand = (n) => Math.floor(Math.random() * n);

    for (let pi = 0; pi < patterns.length; pi++) {
      const base = patterns[pi];
      const wins = {};

      for (let s = 0; s < samplesPerPattern; s++) {
        const rate = noiseLevels[rand(noiseLevels.length)];
        const noisy = addNoise(base, rate);
        const { best } = memAI.recall(noisy);
        const e = best.rule;
        wins[e] = (wins[e] || 0) + 1;
        this.globalWins[e] = (this.globalWins[e] || 0) + 1;
      }

      const entries = Object.entries(wins);
      if (!entries.length) continue;
      entries.sort((a, b) => b[1] - a[1]);
      const [topEngine, topCount] = entries[0];
      const total = entries.reduce((sum, [, c]) => sum + c, 0);
      
      // Map pattern if clear winner (>60%)
      if (topCount / total >= 0.6) {
        this.perPattern.set(pi, topEngine);
      }
    }

    this.trained = true;
    
    console.log('✅ EngineSelector trained', {
      globalWins: this.globalWins,
      mappedPatterns: this.perPattern.size,
      totalSamples: patterns.length * samplesPerPattern
    });
  }

  suggestForPattern(patternIndex) {
    return this.perPattern.get(patternIndex) || null;
  }

  bestGlobal() {
    const entries = Object.entries(this.globalWins);
    if (!entries.length) return null;
    entries.sort((a, b) => b[1] - a[1]);
    return entries[0][0];
  }
}

// Expose for debugging
if (typeof window !== 'undefined') {
  window.EngineSelector = EngineSelector;
}

