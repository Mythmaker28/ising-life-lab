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

