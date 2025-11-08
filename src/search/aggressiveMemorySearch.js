/**
 * Aggressive memory rule search to beat the 1.88 seeds.
 * Double scoring: complexScore (visual dynamics) + memoryScore (attractors).
 */

import { createGrid, randomizeGrid } from '../core/caGrid.js';
import { step } from '../core/caStep.js';
import { getBasicMetrics } from '../metrics/metrics.js';
import { scanAttractors } from '../memory/attractorScan.js';

/**
 * Calculates complexScore (dynamics/entropy based).
 */
function calculateComplexScore(rule, { runs = 30, steps = 100 } = {}) {
  const results = [];
  
  for (let i = 0; i < runs; i++) {
    const grid = createGrid(50, 50, 0);
    randomizeGrid(grid, 0.25);
    
    const entropies = [];
    const densities = [];
    let variations = 0;
    let prevPop = 0;
    
    for (let s = 0; s < steps; s++) {
      const metrics = getBasicMetrics(grid);
      entropies.push(metrics.entropy);
      densities.push(metrics.density);
      
      if (s > 0 && metrics.population !== prevPop) {
        variations++;
      }
      prevPop = metrics.population;
      
      grid = step(grid, rule);
    }
    
    const avgEntropy = entropies.reduce((a, b) => a + b, 0) / entropies.length;
    const avgDensity = densities.reduce((a, b) => a + b, 0) / densities.length;
    const variationRate = variations / steps;
    
    results.push({ avgEntropy, avgDensity, variationRate });
  }
  
  // Aggregate
  const entropy = results.reduce((s, r) => s + r.avgEntropy, 0) / results.length;
  const density = results.reduce((s, r) => s + r.avgDensity, 0) / results.length;
  const variation = results.reduce((s, r) => s + r.variationRate, 0) / results.length;
  
  // Complex score: high entropy + good variation + density not extreme
  const complexScore = entropy + 0.5 * variation + 0.3 * (1 - Math.abs(density - 0.3));
  
  return complexScore;
}

/**
 * Calculates memoryScore using multi-pattern attractor scanning.
 */
async function calculateMemoryScore(rule, { runs = 80, steps = 100, noiseLevels = [0.03, 0.05, 0.08, 0.12] } = {}) {
  const patterns = [
    createPattern('cluster'),
    createPattern('random'),
    createPattern('cross'),
    createPattern('block')
  ];
  
  const allScores = [];
  
  for (const noise of noiseLevels) {
    for (const pattern of patterns) {
      const report = scanAttractors(rule, pattern, { runs, steps, noise, maxAttractors: 10 });
      
      const dominantCount = report.dominantCount || 0;
      const coverage = report.attractors.reduce((sum, a) => sum + a.frequency, 0);
      
      if (dominantCount >= 2 && dominantCount <= 10 && coverage >= 0.7) {
        const targetCount = 4;
        const countPenalty = Math.abs(dominantCount - targetCount);
        const score = coverage / (1 + countPenalty * 0.3);
        allScores.push(score);
      } else {
        allScores.push(0);
      }
    }
  }
  
  // Average across all noise/pattern combinations
  return allScores.reduce((a, b) => a + b, 0) / allScores.length;
}

// Pattern generators
function createPattern(type) {
  const grid = createGrid(32, 32, 0);
  const cx = 16, cy = 16;
  
  switch (type) {
    case 'cluster':
      for (let dy = -2; dy <= 2; dy++) {
        for (let dx = -2; dx <= 2; dx++) {
          if (Math.abs(dx) + Math.abs(dy) <= 3) {
            grid[cy + dy][cx + dx] = 1;
          }
        }
      }
      break;
    case 'random':
      randomizeGrid(grid, 0.25);
      break;
    case 'cross':
      for (let i = -4; i <= 4; i++) {
        grid[cy][cx + i] = 1;
        grid[cy + i][cx] = 1;
      }
      break;
    case 'block':
      for (let dy = 0; dy < 6; dy++) {
        for (let dx = 0; dx < 6; dx++) {
          grid[cy - 3 + dy][cx - 3 + dx] = 1;
        }
      }
      break;
  }
  
  return grid;
}

/**
 * Mutates a rule aggressively (1-3 changes).
 */
function mutateRule(baseRule, intensity = 2) {
  const bornSet = new Set(baseRule.born);
  const surviveSet = new Set(baseRule.survive);
  const nums = [0, 1, 2, 3, 4, 5, 6, 7, 8];
  
  for (let i = 0; i < intensity; i++) {
    // Born mutation
    if (Math.random() < 0.5 && bornSet.size > 0) {
      const toRemove = Array.from(bornSet)[Math.floor(Math.random() * bornSet.size)];
      bornSet.delete(toRemove);
    } else {
      const toAdd = nums[Math.floor(Math.random() * nums.length)];
      bornSet.add(toAdd);
    }
    
    // Survive mutation
    if (Math.random() < 0.5 && surviveSet.size > 0) {
      const toRemove = Array.from(surviveSet)[Math.floor(Math.random() * surviveSet.size)];
      surviveSet.delete(toRemove);
    } else {
      const toAdd = nums[Math.floor(Math.random() * nums.length)];
      surviveSet.add(toAdd);
    }
  }
  
  const born = Array.from(bornSet).sort((a, b) => a - b);
  const survive = Array.from(surviveSet).sort((a, b) => a - b);
  
  return {
    name: `Mut B${born.join('')}/S${survive.join('')}`,
    born,
    survive
  };
}

/**
 * Ultra-aggressive search to beat Seed_1.88 baseline.
 */
export async function aggressiveSearch({
  populationSize = 400,
  generations = 10,
  runsPerRule = 80,
  steps = 100,
  noiseLevels = [0.03, 0.05, 0.08, 0.12],
  seedRules = []
} = {}) {
  
  console.log('🔥 ========== AGGRESSIVE SEARCH TO BEAT 1.88 ==========');
  console.log(`   Population: ${populationSize} | Generations: ${generations}`);
  console.log(`   Runs/rule: ${runsPerRule} | Steps: ${steps}`);
  
  const startTime = performance.now();
  
  // Reference scores (Seed_1.88a)
  const REF_COMPLEX = 1.88;
  const REF_MEMORY = 1.42;
  
  console.log(`   Baseline: complexScore=${REF_COMPLEX}, memoryScore=${REF_MEMORY}`);
  console.log('');
  
  // Seeds
  const seeds = [
    { name: 'Seed_1.88a', born: [2, 4, 5, 6], survive: [0, 7, 8] },
    { name: 'Seed_1.88b', born: [2, 4, 5, 6], survive: [0, 6, 8] },
    { name: 'Evo B246/S58', born: [2, 4, 6], survive: [5, 8] },
    { name: 'Evo B2456/S07', born: [2, 4, 5, 6], survive: [0, 7] },
    { name: 'Evo B246/S5', born: [2, 4, 6], survive: [5] },
    { name: 'Mythmaker_1', born: [2, 4, 5, 6], survive: [5] }
  ];
  
  let population = [...seeds];
  let champions = [];
  
  // Heavy mutations around seeds
  for (let i = 0; i < populationSize / 2; i++) {
    const base = seeds[Math.floor(Math.random() * seeds.length)];
    population.push(mutateRule(base, Math.floor(Math.random() * 3) + 1));
  }
  
  // Fill with randoms
  while (population.length < populationSize) {
    population.push(generateRandomRule());
  }
  
  // Evolution
  for (let gen = 0; gen < generations; gen++) {
    console.log(`\n🧬 Gen ${gen + 1}/${generations}...`);
    
    const genResults = [];
    
    for (let i = 0; i < population.length; i++) {
      if (i % 100 === 0) {
        console.log(`   ${i}/${population.length}`);
        await new Promise(resolve => setTimeout(resolve, 0));
      }
      
      const rule = population[i];
      
      // Double scoring
      const complexScore = calculateComplexScore(rule, { runs: 30, steps: 100 });
      const memoryScore = await calculateMemoryScore(rule, { runs: runsPerRule, steps, noiseLevels });
      
      // Combined score
      const combinedScore = complexScore * 0.4 + memoryScore * 0.6;
      
      genResults.push({
        rule,
        complexScore,
        memoryScore,
        combinedScore
      });
    }
    
    // Filter: only rules better than baseline
    const betterThanBaseline = genResults.filter(r => 
      r.complexScore >= REF_COMPLEX || r.memoryScore >= REF_MEMORY + 0.05
    );
    
    if (betterThanBaseline.length > 0) {
      console.log(`   ✨ Found ${betterThanBaseline.length} candidates better than baseline!`);
      champions = champions.concat(betterThanBaseline);
    }
    
    // Next generation: focus on best performers
    genResults.sort((a, b) => b.combinedScore - a.combinedScore);
    const elite = genResults.slice(0, Math.floor(populationSize * 0.15));
    
    population = [...elite.map(r => r.rule)];
    
    // Aggressive mutations
    for (let i = 0; i < populationSize * 0.7; i++) {
      const base = elite[Math.floor(Math.random() * elite.length)].rule;
      population.push(mutateRule(base, Math.floor(Math.random() * 4) + 1));
    }
    
    while (population.length < populationSize) {
      population.push(generateRandomRule());
    }
  }
  
  // Final ranking
  champions.sort((a, b) => b.combinedScore - a.combinedScore);
  
  const elapsed = ((performance.now() - startTime) / 1000 / 60).toFixed(1);
  
  console.log('');
  console.log('=' .repeat(70));
  console.log('🎯 AGGRESSIVE SEARCH COMPLETE');
  console.log(`   Time: ${elapsed} min | Champions: ${champions.length}`);
  console.log('=' .repeat(70));
  
  if (champions.length === 0) {
    console.log('');
    console.log('❌ No rules beat the 1.88 baseline after', populationSize * generations, 'evaluations');
    console.log('   Seeds B2456/S078 & B2456/S068 remain supreme.');
    return { champions: [], verdict: 'baseline_unbeaten' };
  }
  
  const top5 = champions.slice(0, 5);
  
  console.log('');
  console.log('🏆 TOP 5 CHAMPIONS (beating baseline):');
  console.table(top5.map((r, i) => ({
    rank: i + 1,
    name: r.rule.name,
    born: r.rule.born.join(''),
    survive: r.rule.survive.join(''),
    complexScore: r.complexScore.toFixed(3),
    memoryScore: r.memoryScore.toFixed(3),
    combined: r.combinedScore.toFixed(3),
    verdict: r.memoryScore > REF_MEMORY ? 'BETTER' : 'comparable'
  })));
  
  return {
    champions: top5,
    verdict: top5[0].memoryScore > REF_MEMORY ? 'new_champion' : 'comparable',
    stats: {
      tested: populationSize * generations,
      betterThanBaseline: champions.length
    }
  };
}

function generateRandomRule() {
  const born = [];
  const survive = [];
  
  for (let i = 0; i <= 8; i++) {
    if (Math.random() < 0.3) born.push(i);
    if (Math.random() < 0.3) survive.push(i);
  }
  
  return {
    name: `Rand B${born.join('')}/S${survive.join('')}`,
    born,
    survive
  };
}


