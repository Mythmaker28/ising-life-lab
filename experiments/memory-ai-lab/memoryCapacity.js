/**
 * Memory Capacity Benchmark
 * Tests memory capacity across multiple pattern counts and noise levels
 */

console.log('⏳ Chargement MemoryCapacity...');

import { CAEngine } from './ca/engine.js';
import { MEMORY_HALL_OF_FAME } from '../../src/presets/rules.js';
import { addNoise, isRecallSuccess, hashGrid, findDominantAttractors } from './memory/attractorUtils.js';
import { HopfieldNetwork } from './hopfield/hopfield.js';

/**
 * Génère N patterns simples reproductibles
 */
function generateSimplePatterns(count, size = 32) {
  const patterns = [];
  for (let i = 0; i < count; i++) {
    const grid = new Uint8Array(size * size);
    // Pattern simple: petit bloc à position déterministe
    const offsetX = 10 + (i % 3) * 8;
    const offsetY = 10 + Math.floor(i / 3) * 8;
    
    // Bloc 3×3
    for (let dy = 0; dy < 3; dy++) {
      for (let dx = 0; dx < 3; dx++) {
        const x = offsetX + dx;
        const y = offsetY + dy;
        if (x < size && y < size) {
          grid[y * size + x] = 1;
        }
      }
    }
    
    patterns.push({
      id: `capacity_${i}`,
      name: `Pattern ${i+1}`,
      grid,
      width: size,
      height: size
    });
  }
  return patterns;
}

/**
 * Teste une règle CA sur N patterns
 */
async function testCACapacity(rule, patterns, { noiseLevel, steps, runs, maxDiffRatio }) {
  const engine = new CAEngine(patterns[0].width, patterns[0].height);
  let successCount = 0;
  const totalTests = patterns.length * runs;
  
  for (const pattern of patterns) {
    for (let i = 0; i < runs; i++) {
      const noisy = addNoise(pattern.grid, noiseLevel);
      const final = engine.run(noisy, rule, steps);
      if (isRecallSuccess(pattern.grid, final, maxDiffRatio)) {
        successCount++;
      }
    }
  }
  
  return successCount / totalTests;
}

/**
 * Teste Hopfield sur N patterns
 */
async function testHopfieldCapacity(patterns, { noiseLevel, runs, maxDiffRatio }) {
  const networkSize = patterns[0].grid.length;
  const network = new HopfieldNetwork(networkSize);
  const flatPatterns = patterns.map(p => p.grid);
  network.train(flatPatterns);
  
  let successCount = 0;
  const totalTests = patterns.length * runs;
  
  for (const pattern of patterns) {
    for (let i = 0; i < runs; i++) {
      const noisy = addNoise(pattern.grid, noiseLevel);
      const recalled = network.recall(noisy, 100);
      if (isRecallSuccess(pattern.grid, recalled, maxDiffRatio)) {
        successCount++;
      }
    }
  }
  
  return successCount / totalTests;
}

/**
 * Suite complète de benchmarks de capacité mémoire
 */
export async function runFullSuite(options = {}) {
  const {
    rules = MEMORY_HALL_OF_FAME,
    patternConfigs = [
      { size: 32, count: 3 },
      { size: 32, count: 5 },
      { size: 32, count: 10 }
    ],
    noiseLevels = [0.01, 0.03, 0.05, 0.08],
    steps = 80,
    runs = 40,
    maxDiffRatio = 0.1
  } = options;
  
  console.log('🧪 MemoryCapacity - Full Suite Benchmark');
  console.log(`📊 ${rules.length + 1} modèles × ${patternConfigs.length} configs × ${noiseLevels.length} noise levels`);
  
  const results = [];
  
  // Tester chaque règle CA
  for (const ruleNotation of rules) {
    console.log(`\nTest de ${ruleNotation}...`);
    const rule = parseNotation(ruleNotation);
    const ruleResults = [];
    
    for (const config of patternConfigs) {
      const patterns = generateSimplePatterns(config.count, config.size);
      
      for (const noise of noiseLevels) {
        const recall = await testCACapacity(rule, patterns, {
          noiseLevel: noise,
          steps,
          runs,
          maxDiffRatio
        });
        
        ruleResults.push({
          patternCount: config.count,
          noise,
          recall: recall * 100
        });
      }
    }
    
    // Trouver capacité max (recall ≥90%)
    const capacityConfigs = patternConfigs.map(cfg => ({
      count: cfg.count,
      avgRecall: ruleResults
        .filter(r => r.patternCount === cfg.count)
        .reduce((sum, r) => sum + r.recall, 0) / noiseLevels.length
    }));
    
    const maxCapacity = capacityConfigs.filter(c => c.avgRecall >= 90).pop();
    
    results.push({
      rule: ruleNotation,
      model: 'CA',
      maxCapacity: maxCapacity ? maxCapacity.count : '<3',
      avgRecall: capacityConfigs.reduce((sum, c) => sum + c.avgRecall, 0) / capacityConfigs.length,
      details: ruleResults
    });
    
    console.log(`  ✓ ${ruleNotation}: capacity=${maxCapacity ? maxCapacity.count : '<3'}, avgRecall=${results[results.length-1].avgRecall.toFixed(1)}%`);
  }
  
  // Tester Hopfield
  console.log(`\nTest de Hopfield...`);
  const hopfieldResults = [];
  
  for (const config of patternConfigs) {
    const patterns = generateSimplePatterns(config.count, config.size);
    
    for (const noise of noiseLevels) {
      const recall = await testHopfieldCapacity(patterns, {
        noiseLevel: noise,
        runs,
        maxDiffRatio
      });
      
      hopfieldResults.push({
        patternCount: config.count,
        noise,
        recall: recall * 100
      });
    }
  }
  
  const hopfieldCapacityConfigs = patternConfigs.map(cfg => ({
    count: cfg.count,
    avgRecall: hopfieldResults
      .filter(r => r.patternCount === cfg.count)
      .reduce((sum, r) => sum + r.recall, 0) / noiseLevels.length
  }));
  
  const hopfieldMaxCapacity = hopfieldCapacityConfigs.filter(c => c.avgRecall >= 90).pop();
  
  results.push({
    rule: 'Hopfield',
    model: 'Hopfield',
    maxCapacity: hopfieldMaxCapacity ? hopfieldMaxCapacity.count : '<3',
    avgRecall: hopfieldCapacityConfigs.reduce((sum, c) => sum + c.avgRecall, 0) / hopfieldCapacityConfigs.length,
    details: hopfieldResults
  });
  
  console.log(`  ✓ Hopfield: capacity=${hopfieldMaxCapacity ? hopfieldMaxCapacity.count : '<3'}, avgRecall=${results[results.length-1].avgRecall.toFixed(1)}%`);
  
  console.log('\n🎯 === RÉSULTATS CAPACITY ===');
  console.table(results.map(r => ({
    Règle: r.rule,
    Modèle: r.model,
    'Max Capacity': r.maxCapacity,
    'Recall Moy (%)': r.avgRecall.toFixed(1)
  })));
  
  return { byRule: results, raw: { patternConfigs, noiseLevels } };
}

/**
 * Parse notation B/S
 */
function parseNotation(notation) {
  const match = notation.match(/B([0-8]+)\/S([0-8]*)/);
  if (!match) throw new Error(`Invalid notation: ${notation}`);
  
  const born = match[1].split('').map(Number);
  const survive = match[2] ? match[2].split('').map(Number) : [];
  
  return { born, survive, name: notation };
}

// Exposer l'API
if (typeof window !== 'undefined') {
  window.MemoryCapacity = {
    runFullSuite
  };
  console.log('✅ MemoryCapacity chargé');
  console.log('📚 API: MemoryCapacity.runFullSuite({ rules, patternConfigs, noiseLevels, steps, runs })');
}

