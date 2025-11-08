/**
 * Enrichissement automatique du dataset
 * Utilise AutoMemoryResearch pour valider nouvelles règles
 */

// À exécuter dans console de auto-memory-research après validation

export async function enrichDatasetFromResults() {
  if (!window.AutoMemoryResearch) {
    throw new Error('AutoMemoryResearch not available. Run on auto-memory-research page.');
  }
  
  const { validatedResults } = window.AutoMemoryResearch.getResults();
  
  if (!validatedResults || validatedResults.length === 0) {
    console.warn('No validated results. Run AutoMemoryResearch.runAll() first.');
    return null;
  }
  
  // Filter only high-quality results
  const newSamples = validatedResults
    .filter(r => r.avgRecall > 0)  // Has been tested
    .map(r => ({
      notation: r.notation,
      bornMask: parseBornMask(r.notation),
      surviveMask: parseSurviveMask(r.notation),
      isMemoryCandidate: r.isMemoryLike,
      avgRecall: r.avgRecall,
      maxCapacity: r.maxCapacity,
      mlProba: r.mlProba,
      source: `auto_research_${new Date().toISOString().split('T')[0]}`,
      validated: new Date().toISOString()
    }));
  
  const dataset = {
    meta: {
      version: '1.1',
      date: new Date().toISOString().split('T')[0],
      addedRules: newSamples.length,
      source: 'Auto Memory Research validation'
    },
    newRules: newSamples
  };
  
  console.log(`📥 Generated ${newSamples.length} new samples for dataset`);
  console.log(JSON.stringify(dataset, null, 2));
  
  // Copy to clipboard if available
  if (navigator.clipboard) {
    await navigator.clipboard.writeText(JSON.stringify(dataset, null, 2));
    console.log('✅ Copied to clipboard');
  }
  
  return dataset;
}

function parseBornMask(notation) {
  const match = notation.match(/B([0-8]*)/);
  const born = match && match[1] ? match[1].split('').map(Number) : [];
  return [...Array(9)].map((_, i) => born.includes(i) ? 1 : 0);
}

function parseSurviveMask(notation) {
  const match = notation.match(/S([0-8]*)/);
  const survive = match && match[1] ? match[1].split('').map(Number) : [];
  return [...Array(9)].map((_, i) => survive.includes(i) ? 1 : 0);
}

// Expose
if (typeof window !== 'undefined') {
  window.enrichDatasetFromResults = enrichDatasetFromResults;
}

console.log('📦 Dataset enrichment script loaded');
console.log('💡 Usage: await enrichDatasetFromResults()');

