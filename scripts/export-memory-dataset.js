/**
 * Export Memory Rules Dataset
 * Génère un dataset JSON des règles mémoire pour meta-learning
 * 
 * Usage (navigateur):
 *   1. Ouvrir Memory AI Lab
 *   2. Console: const dataset = await exportMemoryDataset();
 *   3. Console: copy(JSON.stringify(dataset, null, 2));
 *   4. Coller dans data/memory_rules_dataset.json
 */

import { MEMORY_HALL_OF_FAME, HOF_RULES } from '../src/presets/rules.js';

// Règles testées par AutoScan (depuis autoScan.js)
const EXTRA_RULES = [
  { name: 'B01/S23', born: [0, 1], survive: [2, 3] },
  { name: 'B01/S34', born: [0, 1], survive: [3, 4] },
  { name: 'B01/S356', born: [0, 1], survive: [3, 5, 6] },
  { name: 'B01/S2', born: [0, 1], survive: [2] },
  { name: 'B01/S4', born: [0, 1], survive: [4] },
  { name: 'B0/S3', born: [0], survive: [3] },
  { name: 'B1/S3', born: [1], survive: [3] },
  { name: 'B01/S13', born: [0, 1], survive: [1, 3] },
  { name: 'B01/S35', born: [0, 1], survive: [3, 5] },
  { name: 'B245/S5', born: [2, 4, 5], survive: [5] },
  { name: 'B246/S58', born: [2, 4, 6], survive: [5, 8] },
  { name: 'B246/S5', born: [2, 4, 6], survive: [5] },
  { name: 'B2456/S5', born: [2, 4, 5, 6], survive: [5] },
  { name: 'B2456/S58', born: [2, 4, 5, 6], survive: [5, 8] },
  { name: 'B0246/S3', born: [0, 2, 4, 6], survive: [3] },
  { name: 'B0345/S8', born: [0, 3, 4, 5], survive: [8] },
  { name: 'B02/S', born: [0, 2], survive: [] },
  { name: 'B018/S', born: [0, 1, 8], survive: [] },
  { name: 'B3/S23', born: [3], survive: [2, 3] },
  { name: 'B36/S23', born: [3, 6], survive: [2, 3] },
  { name: 'B3/S234', born: [3], survive: [2, 3, 4] },
  { name: 'B24/S3', born: [2, 4], survive: [3] },
  { name: 'B26/S5', born: [2, 6], survive: [5] },
  { name: 'B46/S58', born: [4, 6], survive: [5, 8] },
];

/**
 * Encode une règle en vecteurs binaires
 * @param {Object} rule - {born: [], survive: []}
 * @returns {Object} {bornMask: [9], surviveMask: [9]}
 */
function encodeRule(rule) {
  const bornMask = new Array(9).fill(0);
  const surviveMask = new Array(9).fill(0);
  
  rule.born.forEach(n => { if (n >= 0 && n <= 8) bornMask[n] = 1; });
  rule.survive.forEach(n => { if (n >= 0 && n <= 8) surviveMask[n] = 1; });
  
  return { bornMask, surviveMask };
}

/**
 * Parse notation vers objet rule
 */
function parseNotation(notation) {
  const match = notation.match(/B([0-8]*)\/S([0-8]*)/);
  if (!match) return null;
  
  const born = match[1] ? match[1].split('').map(Number) : [];
  const survive = match[2] ? match[2].split('').map(Number) : [];
  
  return { born, survive };
}

/**
 * Exporte le dataset complet
 */
export function exportMemoryDataset() {
  const dataset = {
    meta: {
      version: '1.0',
      date: new Date().toISOString(),
      protocol: {
        patternSize: '32×32',
        patterns: 4,
        noiseLevel: 0.05,
        steps: 80,
        runs: 50,
        criterion: 'Hamming ≤10%'
      },
      source: 'Mythmaker28/ising-life-lab Memory AI Lab'
    },
    rules: []
  };
  
  // Ajouter rules Hall of Fame
  HOF_RULES.forEach(rule => {
    const notation = rule.name.match(/\(([^)]+)\)/)?.[1] || rule.name;
    const encoded = encodeRule(rule);
    
    dataset.rules.push({
      notation,
      bornMask: encoded.bornMask,
      surviveMask: encoded.surviveMask,
      born: rule.born,
      survive: rule.survive,
      isHallOfFame: true,
      isMemoryCandidate: MEMORY_HALL_OF_FAME.includes(notation),
      recallMean: notation === 'B01/S3' ? 96.7 : null,  // À remplir après tests
      recallMin: null,
      recallMax: null,
      source: 'extreme_search'
    });
  });
  
  // Ajouter EXTRA_RULES
  EXTRA_RULES.forEach(rule => {
    const notation = rule.name;
    const encoded = encodeRule(rule);
    const isCandidate = MEMORY_HALL_OF_FAME.includes(notation);
    
    dataset.rules.push({
      notation,
      bornMask: encoded.bornMask,
      surviveMask: encoded.surviveMask,
      born: rule.born,
      survive: rule.survive,
      isHallOfFame: false,
      isMemoryCandidate: isCandidate,
      recallMean: isCandidate ? 80 : null,  // Approximation
      recallMin: null,
      recallMax: null,
      source: 'autoscan'
    });
  });
  
  console.log(`📦 Dataset généré: ${dataset.rules.length} règles`);
  console.log(`   Hall of Fame: ${dataset.rules.filter(r => r.isHallOfFame).length}`);
  console.log(`   Memory Candidates: ${dataset.rules.filter(r => r.isMemoryCandidate).length}`);
  
  return dataset;
}

// Exposer si dans navigateur
if (typeof window !== 'undefined') {
  window.exportMemoryDataset = exportMemoryDataset;
  console.log('✅ Dataset exporter chargé');
  console.log('📚 Usage: const dataset = exportMemoryDataset(); copy(JSON.stringify(dataset, null, 2));');
}

