/**
 * Automatic search for Life-like rules with memory behavior.
 * Tests rules against attractor convergence criteria.
 */

import { createGrid, randomizeGrid } from '../core/caGrid.js';
import { generateRandomRule } from './ruleExplorer.js';
import { scanAttractors } from '../memory/attractorScan.js';

/**
 * Tests a rule for memory behavior using multiple test patterns.
 * @param {Object} rule - Rule to test
 * @param {Object} options - { runs, steps, noise }
 * @returns {Object} { rule, dominantCount, dominantCoverage, memoryScore, type }
 */
function evaluateMemoryBehavior(rule, options = {}) {
  const runs = options.runs || 40;
  const steps = options.steps || 80;
  const noise = options.noise || 0.05;
  
  // Create a simple test pattern (e.g., small cluster)
  const testGrid = createGrid(32, 32, 0);
  // Add a small centered pattern
  const cx = 16, cy = 16;
  testGrid[cy][cx] = 1;
  testGrid[cy][cx+1] = 1;
  testGrid[cy+1][cx] = 1;
  testGrid[cy+1][cx+1] = 1;
  testGrid[cy-1][cx] = 1;
  
  // Scan attractors
  const report = scanAttractors(rule, testGrid, {
    runs,
    steps,
    noise,
    maxAttractors: 10
  });
  
  const dominantCount = report.dominantCount || 0;
  const dominantCoverage = report.attractors.reduce((sum, a) => sum + a.frequency, 0);
  
  // Classify and score
  let type = 'chaotic';
  let memoryScore = 0;
  
  if (dominantCount === 0) {
    type = 'chaotic';
    memoryScore = 0;
  } else if (dominantCount === 1 && dominantCoverage > 0.95) {
    type = 'frozen';
    memoryScore = 0.1; // Very low score for trivial convergence
  } else if (dominantCount >= 2 && dominantCount <= 10 && dominantCoverage >= 0.7) {
    type = 'memory-like';
    // Score favors 3-6 attractors with high coverage
    const targetCount = 4;
    const countPenalty = Math.abs(dominantCount - targetCount);
    memoryScore = dominantCoverage / (1 + countPenalty * 0.3);
  } else if (dominantCount > 10) {
    type = 'chaotic';
    memoryScore = 0.2; // Low score for too many attractors
  } else {
    type = 'weak-memory';
    memoryScore = dominantCoverage * 0.5;
  }
  
  return {
    rule,
    dominantCount,
    dominantCoverage,
    memoryScore,
    type
  };
}

/**
 * Scans many random rules for memory behavior.
 * @param {Object} options - { candidates, runs, steps, noise }
 * @returns {Array} Sorted array of memory rule candidates
 */
export async function scanForMemoryRules(options = {}) {
  const candidates = options.candidates || 40;
  const runs = options.runs || 40;
  const steps = options.steps || 80;
  const noise = options.noise || 0.05;
  
  console.log('🧠 Starting memory rule search...');
  console.log(`   Candidates: ${candidates}, Runs: ${runs}, Steps: ${steps}, Noise: ${noise}`);
  
  const results = [];
  
  for (let i = 0; i < candidates; i++) {
    if (i % 10 === 0 && i > 0) {
      console.log(`   Progress: ${i}/${candidates}...`);
    }
    
    const rule = generateRandomRule();
    const evaluation = evaluateMemoryBehavior(rule, { runs, steps, noise });
    results.push(evaluation);
  }
  
  // Filter and sort
  const memoryLikeRules = results.filter(r => r.type === 'memory-like');
  const weakMemoryRules = results.filter(r => r.type === 'weak-memory');
  const chaoticRules = results.filter(r => r.type === 'chaotic');
  const frozenRules = results.filter(r => r.type === 'frozen');
  
  // Sort by memoryScore
  memoryLikeRules.sort((a, b) => b.memoryScore - a.memoryScore);
  
  console.log('');
  console.log('🎯 Memory Rule Search Results:');
  console.log(`   Memory-like: ${memoryLikeRules.length}`);
  console.log(`   Weak memory: ${weakMemoryRules.length}`);
  console.log(`   Chaotic: ${chaoticRules.length}`);
  console.log(`   Frozen: ${frozenRules.length}`);
  console.log('');
  
  if (memoryLikeRules.length > 0) {
    const topRules = memoryLikeRules.slice(0, 5);
    console.log('🏆 Top 5 memory-like rules:');
    console.table(topRules.map(r => ({
      name: r.rule.name,
      born: r.rule.born.join(''),
      survive: r.rule.survive.join(''),
      type: r.type,
      dominantCount: r.dominantCount,
      coverage: (r.dominantCoverage * 100).toFixed(1) + '%',
      memoryScore: r.memoryScore.toFixed(3)
    })));
    
    // Generate promotion snippet
    console.log('');
    console.log('📋 Code snippet for promoting top rules:');
    topRules.forEach((r, i) => {
      console.log(`  { name: "Memory_${i+1} (B${r.rule.born.join('')}/S${r.rule.survive.join('')})", born: [${r.rule.born.join(', ')}], survive: [${r.rule.survive.join(', ')}] },`);
    });
  } else {
    console.log('❌ No memory-like rules found. Try different parameters or increase candidates.');
  }
  
  return {
    memoryLike: memoryLikeRules,
    weakMemory: weakMemoryRules,
    chaotic: chaoticRules,
    frozen: frozenRules
  };
}

