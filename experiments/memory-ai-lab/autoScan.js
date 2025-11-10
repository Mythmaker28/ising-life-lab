/**
 * AutoScan - Exploration automatique de candidates mémoire
 */

console.log('⏳ Chargement AutoScan...');

import { CAEngine } from './ca/engine.js';
import { hashGrid, findDominantAttractors, addNoise, isRecallSuccess, getDefaultPatterns } from './memory/attractorUtils.js';

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

// Patterns par défaut maintenant centralisés dans attractorUtils.js

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
 * Pré-filtre les règles avec le ML predictor (optionnel)
 */
async function preFilterWithML(rules, threshold = 0.3) {
  try {
    const { createRulePredictor } = await import('../../src/ai/rulePredictor.js');
    console.log('🧠 Pré-filtrage ML activé...');
    
    const predictor = await createRulePredictor();
    const scored = [];
    
    rules.forEach(rule => {
      const notation = `B${rule.born.join('')}/S${rule.survive.join('')}`;
      try {
        const score = predictor.scoreRule(notation);
        if (score.proba >= threshold) {
          scored.push({
            ...rule,
            mlScore: score.proba,
            mlLabel: score.label
          });
        }
      } catch (e) {
        // Skip invalid rules
      }
    });
    
    console.log(`   ✂️ ML filter: ${rules.length} → ${scored.length} rules (threshold: ${(threshold * 100).toFixed(0)}%)`);
    return scored;
    
  } catch (e) {
    console.warn('   ⚠️ ML pre-filter unavailable, using all candidates');
    return rules;
  }
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
    patterns: providedPatterns = null,
    useMLFilter = false,
    mlThreshold = 0.3
  } = options;
  
  console.log('🔍 AutoScan - Recherche de candidates mémoire');
  console.log(`📊 Config: ${EXTRA_RULES.length} règles × ${noiseLevels.length} niveaux de bruit × ${runs} runs`);
  
  // Optional ML pre-filtering
  let rulesToTest = EXTRA_RULES;
  if (useMLFilter) {
    rulesToTest = await preFilterWithML(EXTRA_RULES, mlThreshold);
  }
  
  // Logique unifiée de sélection des patterns (alignée avec MemoryLab)
  let patternsToTest = providedPatterns;
  
  if (!patternsToTest || patternsToTest.length === 0) {
    // Essayer d'utiliser les patterns UI de MemoryLab
    if (window.MemoryLab && typeof window.MemoryLab.getCurrentPatterns === 'function') {
      const uiPatterns = window.MemoryLab.getCurrentPatterns();
      if (uiPatterns && uiPatterns.length > 0) {
        patternsToTest = uiPatterns;
        console.log(`✓ Utilisation de ${patternsToTest.length} patterns depuis Memory Lab UI`);
      }
    }
    
    // Fallback: patterns par défaut centralisés
    if (!patternsToTest || patternsToTest.length === 0) {
      patternsToTest = getDefaultPatterns();
      console.log(`✓ Utilisation de ${patternsToTest.length} patterns par défaut (reproductibles)`);
    }
  } else {
    console.log(`✓ Utilisation de ${patternsToTest.length} patterns fournis explicitement`);
  }
  
  const results = [];
  let ruleIndex = 0;
  
  for (const rule of rulesToTest) {
    ruleIndex++;
    console.log(`[${ruleIndex}/${rulesToTest.length}] Test de ${rule.name}...`);
    
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

