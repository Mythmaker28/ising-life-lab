/**
 * AutoScan - Exploration automatique de candidates mémoire
 */

console.log('⏳ Chargement AutoScan...');

import { CAEngine } from './ca/engine.js';
import { hashGrid, findDominantAttractors, addNoise, isRecallSuccess } from './memory/attractorUtils.js';

// Règles à explorer (voisinage de B01/S3 + variations Hall of Fame)
const EXTRA_RULES = [
  // Voisinage de B01/S3 (Mythmaker_2)
  { name: 'B01/S23', born: [0, 1], survive: [2, 3] },
  { name: 'B01/S34', born: [0, 1], survive: [3, 4] },
  { name: 'B01/S356', born: [0, 1], survive: [3, 5, 6] },
  { name: 'B01/S2', born: [0, 1], survive: [2] },
  { name: 'B01/S4', born: [0, 1], survive: [4] },
  { name: 'B0/S3', born: [0], survive: [3] },
  { name: 'B1/S3', born: [1], survive: [3] },
  { name: 'B01/S13', born: [0, 1], survive: [1, 3] },
  { name: 'B01/S35', born: [0, 1], survive: [3, 5] },
  
  // Variations autour des Seeds
  { name: 'B245/S5', born: [2, 4, 5], survive: [5] },
  { name: 'B246/S58', born: [2, 4, 6], survive: [5, 8] },
  { name: 'B246/S5', born: [2, 4, 6], survive: [5] },
  { name: 'B2456/S5', born: [2, 4, 5, 6], survive: [5] },
  { name: 'B2456/S58', born: [2, 4, 5, 6], survive: [5, 8] },
  
  // Exploration minimale survive
  { name: 'B0246/S3', born: [0, 2, 4, 6], survive: [3] },
  { name: 'B0345/S8', born: [0, 3, 4, 5], survive: [8] },
  { name: 'B02/S', born: [0, 2], survive: [] },
  { name: 'B018/S', born: [0, 1, 8], survive: [] },
  
  // Oscillateurs potentiels
  { name: 'B3/S23', born: [3], survive: [2, 3] },
  { name: 'B36/S23', born: [3, 6], survive: [2, 3] },
  { name: 'B3/S234', born: [3], survive: [2, 3, 4] },
  
  // Exploration born restreint
  { name: 'B24/S3', born: [2, 4], survive: [3] },
  { name: 'B26/S5', born: [2, 6], survive: [5] },
  { name: 'B46/S58', born: [4, 6], survive: [5, 8] },
];

// Patterns par défaut pour tests
function createDefaultPatterns() {
  const defaultPatterns = [];
  
  // Block 2×2
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
    height: 32
  });
  
  // Blinker période 2
  const blinker = new Uint8Array(32 * 32);
  blinker[16 * 32 + 15] = 1;
  blinker[16 * 32 + 16] = 1;
  blinker[16 * 32 + 17] = 1;
  defaultPatterns.push({
    id: 'default_blinker',
    name: 'Blinker p2',
    grid: blinker,
    width: 32,
    height: 32
  });
  
  // Glider-like
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
    height: 32
  });
  
  // Pattern random sparse
  const random = new Uint8Array(32 * 32);
  for (let i = 0; i < 30; i++) {
    const x = Math.floor(Math.random() * 32);
    const y = Math.floor(Math.random() * 32);
    random[y * 32 + x] = 1;
  }
  defaultPatterns.push({
    id: 'default_random',
    name: 'Random sparse',
    grid: random,
    width: 32,
    height: 32
  });
  
  return defaultPatterns;
}

/**
 * Teste une règle sur un pattern avec un niveau de bruit donné
 */
async function testRuleOnPattern(rule, pattern, { noiseLevel, steps, runs, maxDiffRatio }) {
  const engine = new CAEngine(pattern.width, pattern.height);
  const attractorCounts = new Map();
  let successCount = 0;
  
  for (let i = 0; i < runs; i++) {
    const noisy = addNoise(pattern.grid, noiseLevel);
    const final = engine.run(noisy, rule, steps);
    const hash = hashGrid(final);
    attractorCounts.set(hash, (attractorCounts.get(hash) || 0) + 1);
    
    if (isRecallSuccess(pattern.grid, final, maxDiffRatio)) {
      successCount++;
    }
  }
  
  const dominants = findDominantAttractors(attractorCounts, runs);
  const mainAttractor = dominants[0] || { count: 0, percentage: 0 };
  const coverage = dominants.reduce((sum, a) => sum + a.percentage, 0) / 100;
  const recallRate = successCount / runs;
  
  return {
    recallRate,
    coverage,
    attractors: dominants.length,
    dominantPercentage: mainAttractor.percentage
  };
}

/**
 * Scanne les règles candidates avec plusieurs niveaux de bruit
 */
export async function scanMemoryCandidates(options = {}) {
  const {
    noiseLevels = [0.01, 0.03, 0.05, 0.08],
    steps = 160,
    runs = 60,
    minRecall = 70,
    minCoverage = 40,
    maxDiffRatio = 0.1,
    patterns = null
  } = options;
  
  console.log('🔍 AutoScan - Recherche de candidates mémoire');
  console.log(`📊 Config: ${EXTRA_RULES.length} règles × ${noiseLevels.length} niveaux de bruit × ${runs} runs`);
  
  // Utiliser patterns fournis ou générer par défaut
  const patternsToTest = patterns || createDefaultPatterns();
  console.log(`✓ Utilisation de ${patternsToTest.length} patterns de test`);
  
  const results = [];
  let ruleIndex = 0;
  
  for (const rule of EXTRA_RULES) {
    ruleIndex++;
    console.log(`[${ruleIndex}/${EXTRA_RULES.length}] Test de ${rule.name}...`);
    
    const perNoise = [];
    
    for (const nl of noiseLevels) {
      const noiseResults = [];
      
      for (const pattern of patternsToTest) {
        const result = await testRuleOnPattern(rule, pattern, {
          noiseLevel: nl,
          steps,
          runs,
          maxDiffRatio
        });
        noiseResults.push(result);
      }
      
      // Moyennes pour ce niveau de bruit
      const avgRecall = noiseResults.reduce((sum, r) => sum + r.recallRate, 0) / noiseResults.length;
      const avgCoverage = noiseResults.reduce((sum, r) => sum + r.coverage, 0) / noiseResults.length;
      const avgAttractors = noiseResults.reduce((sum, r) => sum + r.attractors, 0) / noiseResults.length;
      
      perNoise.push({
        noise: nl,
        recall: avgRecall * 100,
        coverage: avgCoverage * 100,
        attractors: avgAttractors
      });
    }
    
    // Évaluer si candidate mémoire
    const okLowNoise = perNoise.filter(p =>
      p.noise <= 0.05 &&
      p.recall >= minRecall &&
      p.coverage >= minCoverage &&
      p.attractors >= 0.5
    );
    
    const okMedNoise = perNoise.find(p =>
      p.noise >= 0.08 && p.recall >= 40
    );
    
    const isCandidate = okLowNoise.length >= 2 && !!okMedNoise;
    
    results.push({
      rule: rule.name,
      notation: rule.name,
      perNoise,
      isCandidate,
      avgRecall: perNoise.reduce((sum, p) => sum + p.recall, 0) / perNoise.length,
      minRecall: Math.min(...perNoise.map(p => p.recall)),
      maxRecall: Math.max(...perNoise.map(p => p.recall))
    });
    
    if (isCandidate) {
      console.log(`  ✅ ${rule.name} - CANDIDATE (recall: ${okLowNoise[0].recall.toFixed(1)}%-${okLowNoise[okLowNoise.length - 1].recall.toFixed(1)}%)`);
    } else {
      console.log(`  ○ ${rule.name} - Non candidate (max recall: ${Math.max(...perNoise.map(p => p.recall)).toFixed(1)}%)`);
    }
  }
  
  const candidates = results.filter(r => r.isCandidate);
  
  console.log('');
  console.log('🎯 === RÉSULTAT FINAL ===');
  console.log(`📊 Règles testées: ${EXTRA_RULES.length}`);
  console.log(`✅ Candidates trouvées: ${candidates.length}`);
  
  if (candidates.length > 0) {
    console.log('');
    console.log('🏆 CANDIDATES MÉMOIRE:');
    console.table(candidates.map(c => ({
      Règle: c.rule,
      'Recall Min (%)': c.minRecall.toFixed(1),
      'Recall Max (%)': c.maxRecall.toFixed(1),
      'Recall Moy (%)': c.avgRecall.toFixed(1)
    })));
  } else {
    console.log('⚠️ Aucune nouvelle candidate trouvée avec ces critères.');
  }
  
  console.log('');
  console.log('📋 Toutes les règles testées:');
  console.table(results.map(r => ({
    Règle: r.rule,
    'Recall Moy (%)': r.avgRecall.toFixed(1),
    'Min (%)': r.minRecall.toFixed(1),
    'Max (%)': r.maxRecall.toFixed(1),
    Candidate: r.isCandidate ? '✅' : '○'
  })));
  
  return { results, candidates };
}

// Exposer l'API globalement
if (typeof window !== 'undefined') {
  window.MemoryScanner = {
    scanMemoryCandidates,
    EXTRA_RULES: () => EXTRA_RULES
  };
  console.log('✅ AutoScan chargé');
  console.log('📚 API: MemoryScanner.scanMemoryCandidates({ noiseLevels: [0.01, 0.03, 0.05, 0.08], steps: 160, runs: 60 })');
}

export { scanMemoryCandidates, EXTRA_RULES };

