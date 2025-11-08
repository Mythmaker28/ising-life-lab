export function hashGrid(grid) {
  let hash = 0;
  for (let i = 0; i < grid.length; i++) {
    hash = ((hash << 5) - hash + grid[i]) | 0;
  }
  return hash.toString(16);
}

export function findDominantAttractors(attractorCounts, totalRuns) {
  const threshold = totalRuns * 0.05;
  const dominants = [];
  for (const [hash, count] of attractorCounts.entries()) {
    if (count >= threshold) {
      dominants.push({ hash, count, percentage: (count / totalRuns) * 100 });
    }
  }
  return dominants.sort((a, b) => b.count - a.count);
}

export function addNoise(grid, noiseLevel) {
  const noisy = new Uint8Array(grid);
  for (let i = 0; i < noisy.length; i++) {
    if (Math.random() < noiseLevel) {
      noisy[i] = 1 - noisy[i];
    }
  }
  return noisy;
}

export function hammingDistance(grid1, grid2) {
  if (grid1.length !== grid2.length) {
    throw new Error('Les grilles doivent avoir la même taille');
  }
  let dist = 0;
  for (let i = 0; i < grid1.length; i++) {
    if (grid1[i] !== grid2[i]) dist++;
  }
  return dist;
}

/**
 * Vérifie si le recall est considéré comme un succès
 * @param {Uint8Array} original - Pattern original
 * @param {Uint8Array} final - État final après évolution
 * @param {number} maxDiffRatio - Ratio max de différence acceptable (0-1)
 * @returns {boolean} True si succès
 */
export function isRecallSuccess(original, final, maxDiffRatio = 0.1) {
  const h = hammingDistance(original, final);
  const total = original.length;
  const ratio = total > 0 ? h / total : 1;
  return ratio <= maxDiffRatio;
}

/**
 * Retourne les patterns par défaut officiels pour tests automatiques
 * Ces patterns sont stables et reproductibles
 * @returns {Array} 4 patterns de test standard
 */
export function getDefaultPatterns() {
  const defaultPatterns = [];
  
  // Block 2×2 (stable dans beaucoup de règles)
  const block = new Uint8Array(32 * 32);
  block[15 * 32 + 15] = 1;
  block[15 * 32 + 16] = 1;
  block[16 * 32 + 15] = 1;
  block[16 * 32 + 16] = 1;
  defaultPatterns.push({
    id: 'default_block',
    name: 'Block 2×2',
    grid: block,
    width: 32,
    height: 32,
    created: Date.now()
  });
  
  // Blinker période 2 (oscillateur simple)
  const blinker = new Uint8Array(32 * 32);
  blinker[16 * 32 + 15] = 1;
  blinker[16 * 32 + 16] = 1;
  blinker[16 * 32 + 17] = 1;
  defaultPatterns.push({
    id: 'default_blinker',
    name: 'Blinker p2',
    grid: blinker,
    width: 32,
    height: 32,
    created: Date.now()
  });
  
  // Glider-like (pattern mobile)
  const glider = new Uint8Array(32 * 32);
  glider[15 * 32 + 16] = 1;
  glider[16 * 32 + 17] = 1;
  glider[17 * 32 + 15] = 1;
  glider[17 * 32 + 16] = 1;
  glider[17 * 32 + 17] = 1;
  defaultPatterns.push({
    id: 'default_glider',
    name: 'Glider-like',
    grid: glider,
    width: 32,
    height: 32,
    created: Date.now()
  });
  
  // Pattern random sparse (30 cellules aléatoires mais reproductible avec seed fixe)
  const random = new Uint8Array(32 * 32);
  // Utiliser positions fixes pour reproductibilité
  const positions = [
    [5,5], [8,12], [15,3], [22,18], [7,25], [19,9], [11,20], [28,7],
    [3,15], [17,28], [25,5], [9,17], [14,11], [21,23], [6,19], [27,14],
    [12,8], [18,22], [4,10], [23,16], [10,26], [16,4], [20,13], [13,21],
    [26,10], [8,24], [24,6], [11,15], [19,19], [15,27]
  ];
  positions.forEach(([x, y]) => {
    if (x < 32 && y < 32) {
      random[y * 32 + x] = 1;
    }
  });
  defaultPatterns.push({
    id: 'default_random',
    name: 'Random sparse',
    grid: random,
    width: 32,
    height: 32,
    created: Date.now()
  });
  
  return defaultPatterns;
}

/**
 * Retourne les patterns par défaut officiels pour tests automatiques
 * Ces patterns sont stables, codés en dur, et identiques à chaque appel
 * @returns {Array<Object>} Array de 4 patterns standard
 */
export function getDefaultPatterns() {
  const patterns = [];
  
  // Block 2×2 - Pattern stable
  const block = new Uint8Array(32 * 32);
  block[15 * 32 + 15] = 1;
  block[15 * 32 + 16] = 1;
  block[16 * 32 + 15] = 1;
  block[16 * 32 + 16] = 1;
  patterns.push({
    id: 'default_block',
    name: 'Block 2×2',
    grid: block,
    width: 32,
    height: 32,
    created: Date.now()
  });
  
  // Blinker période 2 - Oscillateur simple
  const blinker = new Uint8Array(32 * 32);
  blinker[16 * 32 + 15] = 1;
  blinker[16 * 32 + 16] = 1;
  blinker[16 * 32 + 17] = 1;
  patterns.push({
    id: 'default_blinker',
    name: 'Blinker p2',
    grid: blinker,
    width: 32,
    height: 32,
    created: Date.now()
  });
  
  // Glider-like - Pattern mobile potentiel
  const glider = new Uint8Array(32 * 32);
  glider[15 * 32 + 16] = 1;
  glider[16 * 32 + 17] = 1;
  glider[17 * 32 + 15] = 1;
  glider[17 * 32 + 16] = 1;
  glider[17 * 32 + 17] = 1;
  patterns.push({
    id: 'default_glider',
    name: 'Glider-like',
    grid: glider,
    width: 32,
    height: 32,
    created: Date.now()
  });
  
  // Pattern random sparse - Seed fixée pour reproductibilité
  const random = new Uint8Array(32 * 32);
  const positions = [
    [12, 10], [15, 8], [18, 12], [14, 16], [20, 14],
    [10, 20], [16, 22], [22, 18], [8, 15], [25, 10],
    [13, 24], [19, 8], [11, 18], [24, 22], [9, 12],
    [17, 20], [21, 15], [14, 9], [26, 16], [10, 25],
    [18, 6], [12, 28], [23, 12], [7, 17], [20, 24],
    [15, 11], [28, 20], [6, 22], [16, 7], [11, 14]
  ];
  positions.forEach(([y, x]) => {
    if (y >= 0 && y < 32 && x >= 0 && x < 32) {
      random[y * 32 + x] = 1;
    }
  });
  patterns.push({
    id: 'default_random',
    name: 'Random sparse',
    grid: random,
    width: 32,
    height: 32,
    created: Date.now()
  });
  
  return patterns;
}

