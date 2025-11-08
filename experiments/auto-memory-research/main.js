import { createRulePredictor } from '../../src/ai/rulePredictor.js';

// State
let predictor = null;
let mlSuggestions = [];
let validatedResults = [];

// Initialize
async function init() {
  try {
    console.log('🤖 Initializing Auto Memory Researcher...');
    
    predictor = await createRulePredictor({ epochs: 500, learningRate: 0.1, lambda: 0.01 });
    
    document.getElementById('loading').style.display = 'none';
    document.getElementById('app').style.display = 'block';
    
    console.log('✅ Auto Memory Researcher ready!');
    console.log('💡 Usage:');
    console.log('  AutoMemoryResearch.suggest()');
    console.log('  AutoMemoryResearch.validate()');
    console.log('  AutoMemoryResearch.runAll()');
    
  } catch (error) {
    document.getElementById('loading').innerHTML = `
      <p style="color: #ff4444;">❌ Error initializing</p>
      <p>${error.message}</p>
    `;
    console.error('Error:', error);
  }
}

// Generate candidate rules and score with ML
async function generateMLSuggestions() {
  console.log('🔍 Step 1: Generating ML suggestions...');
  
  const step1 = document.getElementById('step1');
  const status1 = document.getElementById('status1');
  const btnSuggest = document.getElementById('btn-suggest');
  
  step1.classList.add('active');
  status1.style.display = 'block';
  status1.innerHTML = '<div class="spinner"></div> Generating candidates...';
  btnSuggest.disabled = true;
  
  try {
    // Generate candidate pool (small B/S subspace)
    const candidates = [];
    const bornSets = [
      [0], [1], [0,1], [2], [0,2], [1,2], [3], [0,3], [1,3],
      [4], [0,4], [1,4], [2,4], [4,6]
    ];
    const surviveSets = [
      [], [2], [3], [4], [5], [2,3], [3,4], [2,3,4], [1,3], [5,8], [4,5]
    ];
    
    bornSets.forEach(born => {
      surviveSets.forEach(survive => {
        const notation = `B${born.join('')}/S${survive.join('')}`;
        candidates.push(notation);
      });
    });
    
    console.log(`Generated ${candidates.length} candidate rules`);
    status1.innerHTML = `Scoring ${candidates.length} candidates with ML...`;
    
    // Score each with ML predictor
    mlSuggestions = [];
    for (const notation of candidates) {
      try {
        const score = predictor.scoreRule(notation);
        if (score.proba >= 0.5) {  // Keep promising ones
          mlSuggestions.push({
            notation,
            mlProba: score.proba,
            mlLabel: score.label,
            mlConfidence: score.confidence,
            message: score.message
          });
        }
      } catch (e) {
        // Skip invalid notations
      }
    }
    
    // Sort by probability
    mlSuggestions.sort((a, b) => b.mlProba - a.mlProba);
    
    console.log(`✅ Found ${mlSuggestions.length} promising rules (ML score ≥ 50%)`);
    
    status1.innerHTML = `✅ Found ${mlSuggestions.length} promising candidates`;
    step1.classList.remove('active');
    step1.classList.add('completed');
    
    // Update UI
    updateSummary();
    displayMLSuggestions();
    
    // Enable validation
    document.getElementById('btn-validate').disabled = false;
    
  } catch (error) {
    status1.innerHTML = `❌ Error: ${error.message}`;
    console.error('Error generating suggestions:', error);
  } finally {
    btnSuggest.disabled = false;
  }
}

// Validate top rules with Memory Capacity
async function validateTopRules() {
  console.log('🧪 Step 2: Validating top rules...');
  
  const step2 = document.getElementById('step2');
  const status2 = document.getElementById('status2');
  const btnValidate = document.getElementById('btn-validate');
  
  step2.classList.add('active');
  status2.style.display = 'block';
  btnValidate.disabled = true;
  
  try {
    // Take top 10 rules
    const topRules = mlSuggestions.slice(0, 10).map(s => s.notation);
    console.log(`Validating ${topRules.length} rules:`, topRules);
    
    validatedResults = [];
    
    for (let i = 0; i < topRules.length; i++) {
      const ruleNotation = topRules[i];
      status2.innerHTML = `Testing ${i + 1}/${topRules.length}: ${ruleNotation}...`;
      
      try {
        const result = await validateRule(ruleNotation);
        const mlData = mlSuggestions.find(s => s.notation === ruleNotation);
        
        validatedResults.push({
          notation: ruleNotation,
          mlProba: mlData.mlProba,
          avgRecall: result.avgRecall,
          maxCapacity: result.maxCapacity,
          isMemoryLike: result.avgRecall >= 90 && result.maxCapacity >= 5,
          mlPredictedMemory: mlData.mlProba >= 0.8,
          match: (mlData.mlProba >= 0.8 && result.avgRecall >= 90) || 
                 (mlData.mlProba < 0.8 && result.avgRecall < 90)
        });
        
        console.log(`✓ ${ruleNotation}: recall=${result.avgRecall}%, capacity=${result.maxCapacity}`);
        
      } catch (e) {
        console.warn(`Failed to validate ${ruleNotation}:`, e.message);
      }
    }
    
    const truePositives = validatedResults.filter(r => r.isMemoryLike).length;
    const accuracy = validatedResults.filter(r => r.match).length / validatedResults.length;
    
    console.log(`✅ Validation complete: ${truePositives}/${validatedResults.length} true memory rules`);
    console.log(`📊 ML accuracy: ${(accuracy * 100).toFixed(1)}%`);
    
    status2.innerHTML = `✅ Validated ${validatedResults.length} rules`;
    step2.classList.remove('active');
    step2.classList.add('completed');
    
    // Update UI
    updateSummary();
    displayValidationResults();
    
    // Enable export
    document.getElementById('btn-export').disabled = false;
    document.getElementById('step3').classList.add('completed');
    document.getElementById('status3').style.display = 'block';
    document.getElementById('status3').innerHTML = `✅ Pipeline complete! Accuracy: ${(accuracy * 100).toFixed(1)}%`;
    
  } catch (error) {
    status2.innerHTML = `❌ Error: ${error.message}`;
    console.error('Error validating rules:', error);
  } finally {
    btnValidate.disabled = false;
  }
}

// Validate a single rule using Memory Capacity protocol
async function validateRule(ruleNotation) {
  // Import CAMemoryEngine
  const { CAMemoryEngine } = await import('../../src/memory/caMemoryEngine.js');
  const { getDefaultPatterns } = await import('../memory-ai-lab/memory/attractorUtils.js');
  
  const patterns = getDefaultPatterns().slice(0, 5);  // Use 5 test patterns
  const noiseLevels = [0.03, 0.05, 0.08];
  const runs = 15;
  
  const engine = CAMemoryEngine.create({
    rule: ruleNotation,
    width: 32,
    height: 32,
    steps: 80
  });
  
  engine.store(patterns);
  
  let totalSuccesses = 0;
  let totalTests = 0;
  let maxSuccessfulCapacity = 0;
  
  // Test different capacities
  for (let capacity = 3; capacity <= 10; capacity += 2) {
    const testPatterns = patterns.slice(0, Math.min(capacity, patterns.length));
    
    for (const noiseLevel of noiseLevels) {
      let successes = 0;
      
      for (let run = 0; run < runs; run++) {
        for (const pattern of testPatterns) {
          const noisy = applyNoise(pattern, noiseLevel);
          const result = engine.recall(noisy, { steps: 80, maxDiffRatio: 0.1 });
          if (result.success) successes++;
          totalTests++;
        }
      }
      
      totalSuccesses += successes;
      const recallRate = successes / (testPatterns.length * runs);
      
      if (recallRate >= 0.9 && testPatterns.length > maxSuccessfulCapacity) {
        maxSuccessfulCapacity = testPatterns.length;
      }
    }
  }
  
  const avgRecall = (totalSuccesses / totalTests) * 100;
  
  return {
    rule: ruleNotation,
    avgRecall: Math.round(avgRecall),
    maxCapacity: maxSuccessfulCapacity
  };
}

// Apply noise to a pattern
function applyNoise(grid, rate) {
  const noisy = new Uint8Array(grid);
  for (let i = 0; i < noisy.length; i++) {
    if (Math.random() < rate) {
      noisy[i] = 1 - noisy[i];
    }
  }
  return noisy;
}

// Update summary cards
function updateSummary() {
  document.getElementById('summary').style.display = 'grid';
  document.getElementById('total-candidates').textContent = mlSuggestions.length;
  document.getElementById('ml-promising').textContent = mlSuggestions.filter(s => s.mlProba >= 0.8).length;
  document.getElementById('validated').textContent = validatedResults.length;
  document.getElementById('true-positives').textContent = validatedResults.filter(r => r.isMemoryLike).length;
}

// Display ML suggestions table
function displayMLSuggestions() {
  const container = document.getElementById('tables-container');
  
  const html = `
    <h3 style="color: #00ff88; margin: 20px 0 10px 0;">ML Suggestions (Top 20)</h3>
    <table>
      <thead>
        <tr>
          <th>Rank</th>
          <th>Rule</th>
          <th>ML Probability</th>
          <th>Confidence</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        ${mlSuggestions.slice(0, 20).map((s, i) => `
          <tr>
            <td>${i + 1}</td>
            <td><code>${s.notation}</code></td>
            <td class="${s.mlProba >= 0.8 ? 'high-score' : s.mlProba >= 0.6 ? 'medium-score' : 'low-score'}">
              ${(s.mlProba * 100).toFixed(1)}%
            </td>
            <td>${(s.mlConfidence * 100).toFixed(0)}%</td>
            <td>
              ${s.mlLabel ? 
                '<span class="badge badge-success">Likely Memory</span>' : 
                '<span class="badge badge-warning">Borderline</span>'}
            </td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
  
  container.innerHTML = html;
}

// Display validation results
function displayValidationResults() {
  const container = document.getElementById('tables-container');
  
  const html = `
    <h3 style="color: #00ff88; margin: 20px 0 10px 0;">ML Suggestions (Top 20)</h3>
    <table>
      <thead>
        <tr>
          <th>Rank</th>
          <th>Rule</th>
          <th>ML Score</th>
          <th>Confidence</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        ${mlSuggestions.slice(0, 20).map((s, i) => `
          <tr>
            <td>${i + 1}</td>
            <td><code>${s.notation}</code></td>
            <td class="${s.mlProba >= 0.8 ? 'high-score' : s.mlProba >= 0.6 ? 'medium-score' : 'low-score'}">
              ${(s.mlProba * 100).toFixed(1)}%
            </td>
            <td>${(s.mlConfidence * 100).toFixed(0)}%</td>
            <td>
              ${s.mlLabel ? 
                '<span class="badge badge-success">Likely</span>' : 
                '<span class="badge badge-warning">Borderline</span>'}
            </td>
          </tr>
        `).join('')}
      </tbody>
    </table>
    
    <h3 style="color: #00ff88; margin: 30px 0 10px 0;">Validation Results (Top 10 Tested)</h3>
    <table>
      <thead>
        <tr>
          <th>Rule</th>
          <th>ML Predicted</th>
          <th>Actual Recall</th>
          <th>Max Capacity</th>
          <th>Result</th>
          <th>Match</th>
        </tr>
      </thead>
      <tbody>
        ${validatedResults.map(r => `
          <tr>
            <td><code>${r.notation}</code></td>
            <td class="${r.mlProba >= 0.8 ? 'high-score' : 'medium-score'}">
              ${(r.mlProba * 100).toFixed(1)}%
            </td>
            <td class="${r.avgRecall >= 90 ? 'high-score' : r.avgRecall >= 70 ? 'medium-score' : 'low-score'}">
              ${r.avgRecall}%
            </td>
            <td>${r.maxCapacity}</td>
            <td>
              ${r.isMemoryLike ? 
                '<span class="badge badge-success">✓ Memory</span>' : 
                '<span class="badge badge-danger">✗ Not Memory</span>'}
            </td>
            <td>
              ${r.match ? '✓' : '✗'}
            </td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
  
  container.innerHTML = html;
}

// Export results
function exportResults() {
  const data = {
    timestamp: new Date().toISOString(),
    mlSuggestions: mlSuggestions.slice(0, 20),
    validatedResults,
    summary: {
      totalCandidates: mlSuggestions.length,
      mlPromising: mlSuggestions.filter(s => s.mlProba >= 0.8).length,
      validated: validatedResults.length,
      trueMemory: validatedResults.filter(r => r.isMemoryLike).length,
      accuracy: validatedResults.length > 0 ? 
        (validatedResults.filter(r => r.match).length / validatedResults.length * 100).toFixed(1) : 0
    }
  };
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `auto-memory-research-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
  
  console.log('📥 Results exported');
}

// Run full pipeline
async function runAll() {
  console.log('🚀 Running full auto-research pipeline...');
  await generateMLSuggestions();
  await new Promise(resolve => setTimeout(resolve, 1000));  // Brief pause
  await validateTopRules();
  console.log('✅ Pipeline complete!');
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
  init();
  
  document.getElementById('btn-suggest')?.addEventListener('click', generateMLSuggestions);
  document.getElementById('btn-validate')?.addEventListener('click', validateTopRules);
  document.getElementById('btn-export')?.addEventListener('click', exportResults);
});

// Expose API
window.AutoMemoryResearch = {
  suggest: generateMLSuggestions,
  validate: validateTopRules,
  runAll,
  getResults: () => ({ mlSuggestions, validatedResults }),
  predictor
};

console.log('🤖 Auto Memory Research module loaded');

