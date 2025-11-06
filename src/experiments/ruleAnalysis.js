/**
 * Advanced analysis module for cellular automata rules.
 * Provides batch analysis of discovered rules with statistical aggregation.
 */

import { RULES } from '../presets/rules.js';
import { evaluateRule } from '../search/ruleExplorer.js';

/**
 * Analyzes a single rule with multiple random seeds.
 * Runs the rule multiple times and aggregates statistics.
 * 
 * @param {Object} rule - Rule to analyze
 * @param {Object} options - { runs, steps, width, height }
 * @returns {Object} { summary, details }
 */
export async function analyzeRule(rule, {
  runs = 20,
  steps = 80,
  width = 50,
  height = 50
} = {}) {
  const results = [];

  for (let i = 0; i < runs; i++) {
    // Use evaluateRule as simulation engine
    const evalResult = evaluateRule(rule, { steps, width, height });
    results.push(evalResult);
  }

  // Aggregate metrics
  const count = results.length;
  const avg = key => results.reduce((s, r) => s + (r[key] || 0), 0) / count;
  
  // Count types
  const typeCounts = {};
  for (const r of results) {
    typeCounts[r.type] = (typeCounts[r.type] || 0) + 1;
  }

  const summary = {
    name: rule.name || 'unnamed',
    born: rule.born.join(''),
    survive: rule.survive.join(''),
    runs,
    avgScore: avg('score'),
    avgDensityFinal: avg('densityFinal'),
    avgEntropyMean: avg('entropyMean'),
    avgVariationMean: avg('variationMean'),
    types: typeCounts
  };

  console.log('📊 Analysis for rule:', summary.name);
  console.table([summary]);
  
  return { summary, details: results };
}

/**
 * Analyzes all "Found:" rules in batch.
 * Useful for comparing discovered rules.
 * 
 * @param {Object} options - Analysis options
 * @returns {Array} Array of summaries sorted by avgScore
 */
export async function analyzeFoundRules(options = {}) {
  const foundRules = RULES.filter(r => (r.name || '').startsWith('Found:'));

  if (foundRules.length === 0) {
    console.warn('⚠️ No "Found:" rules in RULES.');
    return [];
  }

  console.log(`🔬 Starting batch analysis of ${foundRules.length} found rules...`);
  
  const allSummaries = [];
  for (let i = 0; i < foundRules.length; i++) {
    const rule = foundRules[i];
    console.log(`  Analyzing ${i + 1}/${foundRules.length}: ${rule.name}`);
    const { summary } = await analyzeRule(rule, options);
    allSummaries.push(summary);
  }

  // Sort by avgScore descending
  allSummaries.sort((a, b) => b.avgScore - a.avgScore);

  console.log('=== Batch analysis of Found rules ===');
  console.table(allSummaries);

  return allSummaries;
}

/**
 * Analyzes all promoted rules (Mythmaker_X, Mahee_X, Tommy_X).
 * 
 * @param {Object} options - Analysis options
 * @returns {Array} Array of summaries
 */
export async function analyzePromotedRules(options = {}) {
  const promoted = RULES.filter(r => {
    const name = r.name || '';
    return name.startsWith('Mythmaker_') || name.startsWith('Mahee_') || name.startsWith('Tommy_');
  });

  if (promoted.length === 0) {
    console.warn('⚠️ No promoted rules found.');
    return [];
  }

  console.log(`🔬 Analyzing ${promoted.length} promoted rules...`);
  
  const summaries = [];
  for (const rule of promoted) {
    const { summary } = await analyzeRule(rule, options);
    summaries.push(summary);
  }

  console.log('=== Analysis of promoted rules ===');
  console.table(summaries);

  return summaries;
}

/**
 * Generates promotion code for top discovered rules.
 * Use this to copy-paste into rules.js
 * 
 * @param {number} topN - Number of top rules to promote (default: 5)
 */
export function generatePromotionCode(topN = 5) {
  const foundRules = RULES.filter(r => (r.name || '').startsWith('Found:'));
  
  if (foundRules.length === 0) {
    console.warn('⚠️ No "Found:" rules to promote.');
    return;
  }
  
  // Extract scores from names like "Found: B.../S... [type, 1.84]"
  const rulesWithScores = foundRules.map(rule => {
    const match = rule.name.match(/\[([^,]+),\s*([0-9.]+)\]/);
    const score = match ? parseFloat(match[2]) : 0;
    const type = match ? match[1] : 'unknown';
    return { rule, score, type };
  });
  
  // Sort by score
  rulesWithScores.sort((a, b) => b.score - a.score);
  
  // Take top N
  const topRules = rulesWithScores.slice(0, topN);
  
  console.log('🏆 Top', topN, 'rules to promote:');
  console.table(topRules.map((r, i) => ({
    rank: i + 1,
    name: r.rule.name,
    born: r.rule.born.join(''),
    survive: r.rule.survive.join(''),
    type: r.type,
    score: r.score
  })));
  
  // Generate code
  let code = '\n// --- Promoted discovered rules ---\n';
  topRules.forEach((r, i) => {
    const suffix = i + 1;
    const ruleName = r.type.includes('osc') ? `Mythmaker_osc_${suffix}` : `Mythmaker_${suffix}`;
    code += `  {\n`;
    code += `    name: "${ruleName} (B${r.rule.born.join('')}/S${r.rule.survive.join('')})",\n`;
    code += `    born: [${r.rule.born.join(', ')}],\n`;
    code += `    survive: [${r.rule.survive.join(', ')}]\n`;
    code += `  },\n`;
  });
  
  console.log('📋 Copy this code and paste into src/presets/rules.js after the base rules:');
  console.log(code);
  
  return code;
}

