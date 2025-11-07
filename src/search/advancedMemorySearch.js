/**
 * Advanced memory rule search with genetic algorithm approach.
 * Mutates best rules and evolves population over generations.
 */

import { RULES } from '../presets/rules.js';
import { createGrid, randomizeGrid } from '../core/caGrid.js';
import { scanAttractors } from '../memory/attractorScan.js';

/**
 * Parses rule born/survive to sets.
 */
function parseRule(rule) {
  return {
    bornSet: new Set(rule.born),
    surviveSet: new Set(rule.survive)
  };
}

/**
 * Formats born/survive sets to B.../S... notation.
 */
function formatRule(bornSet, surviveSet) {
  const b = Array.from(bornSet).sort((a, b) => a - b).join('');
  const s = Array.from(surviveSet).sort((a, b) => a - b).join('');
  return `B${b}/S${s}`;
}

/**
 * Mutates a rule by adding/removing values from born/survive.
 */
function mutateRule(baseRule, intensity = 1) {
  const { bornSet, surviveSet } = parseRule(baseRule);
  const nums = [0, 1, 2, 3, 4, 5, 6, 7, 8];
  
  // Apply mutations
  for (let i = 0; i < intensity; i++) {
    // Mutate born
    if (Math.random() < 0.5 && bornSet.size > 0) {
      // Remove
      const toRemove = Array.from(bornSet)[Math.floor(Math.random() * bornSet.size)];
      bornSet.delete(toRemove);
    } else {
      // Add
      const toAdd = nums[Math.floor(Math.random() * nums.length)];
      bornSet.add(toAdd);
    }
    
    // Mutate survive
    if (Math.random() < 0.5 && surviveSet.size > 0) {
      // Remove
      const toRemove = Array.from(surviveSet)[Math.floor(Math.random() * surviveSet.size)];
      surviveSet.delete(toRemove);
    } else {
      // Add
      const toAdd = nums[Math.floor(Math.random() * nums.length)];
      surviveSet.add(toAdd);
    }
  }
  
  const born = Array.from(bornSet).sort((a, b) => a - b);
  const survive = Array.from(surviveSet).sort((a, b) => a - b);
  const notation = formatRule(bornSet, surviveSet);
  
  return {
    name: `Evo ${notation}`,
    born,
    survive
  };
}

/**
 * Evaluates memory behavior using multiple test patterns.
 */
async function evaluateMemory(rule, options) {
  const runs = options.runs || 40;
  const steps = options.steps || 80;
  const noise = options.noise || 0.05;
  
  // Test with multiple patterns
  const patterns = [
    createSmallCluster(),
    createRandomPattern(),
    createCross()
  ];
  
  const allDominants = [];
  const allCoverages = [];
  
  for (const pattern of patterns) {
    const report = scanAttractors(rule, pattern, { runs, steps, noise, maxAttractors: 10 });
    allDominants.push(report.dominantCount || 0);
    const coverage = report.attractors.reduce((sum, a) => sum + a.frequency, 0);
    allCoverages.push(coverage);
  }
  
  // Aggregate
  const avgDominant = allDominants.reduce((a, b) => a + b, 0) / allDominants.length;
  const avgCoverage = allCoverages.reduce((a, b) => a + b, 0) / allCoverages.length;
  
  // Classify
  let ruleClass = 'chaotic';
  let memoryScore = 0;
  
  if (avgDominant === 0) {
    ruleClass = 'chaotic';
  } else if (avgDominant <= 1.5 && avgCoverage > 0.95) {
    ruleClass = 'frozen';
    memoryScore = 0.1;
  } else if (avgDominant >= 2 && avgDominant <= 10 && avgCoverage >= 0.7) {
    ruleClass = 'memory-like';
    const targetCount = 4;
    const countPenalty = Math.abs(avgDominant - targetCount);
    memoryScore = avgCoverage / (1 + countPenalty * 0.3);
  } else if (avgDominant > 10) {
    ruleClass = 'chaotic';
  } else {
    ruleClass = 'weak-memory';
    memoryScore = avgCoverage * 0.5;
  }
  
  return {
    rule,
    dominantCount: Math.round(avgDominant),
    coverage: avgCoverage,
    memoryScore,
    class: ruleClass
  };
}

// Helper: create test patterns
function createSmallCluster() {
  const grid = createGrid(32, 32, 0);
  const cx = 16, cy = 16;
  grid[cy][cx] = 1;
  grid[cy][cx+1] = 1;
  grid[cy+1][cx] = 1;
  grid[cy+1][cx+1] = 1;
  grid[cy-1][cx] = 1;
  return grid;
}

function createRandomPattern() {
  const grid = createGrid(32, 32, 0);
  randomizeGrid(grid, 0.25);
  return grid;
}

function createCross() {
  const grid = createGrid(32, 32, 0);
  const cx = 16, cy = 16;
  for (let i = -3; i <= 3; i++) {
    grid[cy][cx + i] = 1;
    grid[cy + i][cx] = 1;
  }
  return grid;
}

/**
 * Evolves memory rules using genetic algorithm approach.
 */
export async function evolveMemoryRules({
  baseRules = [],
  populationSize = 40,
  generations = 3,
  runs = 40,
  steps = 80,
  noise = 0.05,
  topK = 10
} = {}) {
  
  console.log('🧬 Starting advanced memory rule evolution...');
  console.log(`   Population: ${populationSize}, Generations: ${generations}, Runs: ${runs}`);
  
  // Build initial population
  if (baseRules.length === 0) {
    baseRules = RULES.filter(r => {
      const name = r.name || '';
      return name.startsWith('Mythmaker_') || name.startsWith('Mahee_') || 
             name.startsWith('Tommy_') || name.startsWith('Discovery_');
    });
  }
  
  let population = [...baseRules];
  
  // Add mutations
  for (let i = 0; i < populationSize / 2; i++) {
    const base = baseRules[Math.floor(Math.random() * baseRules.length)];
    population.push(mutateRule(base, Math.floor(Math.random() * 2) + 1));
  }
  
  // Add randoms
  while (population.length < populationSize) {
    population.push(generateRandomRule());
  }
  
  let allResults = [];
  
  // Evolve over generations
  for (let gen = 0; gen < generations; gen++) {
    console.log(`\n🔄 Generation ${gen + 1}/${generations}...`);
    
    const genResults = [];
    
    for (let i = 0; i < population.length; i++) {
      if (i % 20 === 0) {
        console.log(`   Evaluating ${i}/${population.length}...`);
      }
      
      const rule = population[i];
      const evaluation = await evaluateMemory(rule, { runs, steps, noise });
      genResults.push(evaluation);
    }
    
    // Sort by memoryScore
    genResults.sort((a, b) => b.memoryScore - a.memoryScore);
    
    // Keep all results
    allResults = allResults.concat(genResults);
    
    // Build next generation from top performers
    if (gen < generations - 1) {
      const topPerformers = genResults.slice(0, populationSize / 2);
      population = [...topPerformers.map(r => r.rule)];
      
      // Mutate top performers
      for (let i = 0; i < populationSize / 2; i++) {
        const base = topPerformers[Math.floor(Math.random() * topPerformers.length)].rule;
        population.push(mutateRule(base, 1));
      }
    }
  }
  
  // Final selection
  const memoryLike = allResults.filter(r => r.class === 'memory-like');
  const weakMemory = allResults.filter(r => r.class === 'weak-memory');
  const chaotic = allResults.filter(r => r.class === 'chaotic');
  const frozen = allResults.filter(r => r.class === 'frozen');
  
  memoryLike.sort((a, b) => b.memoryScore - a.memoryScore);
  
  const topRules = memoryLike.slice(0, topK);
  
  console.log('');
  console.log('🏆 Evolution complete!');
  console.log(`   Tested: ${allResults.length} rules`);
  console.log(`   Memory-like: ${memoryLike.length}`);
  console.log(`   Weak-memory: ${weakMemory.length}`);
  console.log(`   Chaotic: ${chaotic.length}`);
  console.log(`   Frozen: ${frozen.length}`);
  console.log('');
  console.log(`Top ${topRules.length} memory rules:`);
  console.table(topRules.map(r => ({
    name: r.rule.name,
    born: r.rule.born.join(''),
    survive: r.rule.survive.join(''),
    class: r.class,
    dominantCount: r.dominantCount,
    coverage: (r.coverage * 100).toFixed(1) + '%',
    memoryScore: r.memoryScore.toFixed(3)
  })));
  
  return {
    top: topRules,
    stats: {
      tested: allResults.length,
      memoryLike: memoryLike.length,
      weakMemory: weakMemory.length,
      chaotic: chaotic.length,
      frozen: frozen.length
    }
  };
}

// Simple random rule generator
function generateRandomRule() {
  const born = [];
  const survive = [];
  
  for (let i = 0; i <= 8; i++) {
    if (Math.random() < 0.3) born.push(i);
    if (Math.random() < 0.3) survive.push(i);
  }
  
  return {
    name: `Random B${born.join('')}/S${survive.join('')}`,
    born,
    survive
  };
}

