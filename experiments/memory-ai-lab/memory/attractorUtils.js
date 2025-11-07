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

