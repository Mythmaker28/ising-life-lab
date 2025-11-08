import { createRulePredictor, parseRuleNotation } from '../../src/ai/rulePredictor.js';

let predictor = null;

async function init() {
  try {
    predictor = await createRulePredictor({ epochs: 500, learningRate: 0.1, lambda: 0.01 });
    
    document.getElementById('loading').style.display = 'none';
    document.getElementById('app').style.display = 'block';
    
    console.log('✅ Rule Predictor ready!');
    console.log('💡 Usage:');
    console.log('  predictor.scoreRule("B01/S3")');
    console.log('  predictor.suggestTopCandidates(20)');
    
    window.predictor = predictor;
    
    // Remplir validation table
    fillValidationTable();
    
  } catch (error) {
    document.getElementById('loading').innerHTML = `
      <p style="color: #ff4444;">❌ Error loading predictor</p>
      <p>${error.message}</p>
    `;
    console.error('Error:', error);
  }
}

function fillValidationTable() {
  const tbody = document.querySelector('#validationTable tbody');
  tbody.innerHTML = '';
  
  const validation = predictor.validateKnown();
  
  validation.forEach(v => {
    const row = tbody.insertRow();
    const predicted = v.predicted >= 0.5 ? 1 : 0;
    const match = predicted === v.label;
    
    row.innerHTML = `
      <td>${v.notation}</td>
      <td class="${predicted ? 'likely' : 'unlikely'}">${(v.predicted * 100).toFixed(0)}%</td>
      <td>${v.label ? '✅' : '❌'}</td>
      <td>${match ? '✓' : '✗'}</td>
    `;
  });
  
  const accuracy = validation.filter(v => (v.predicted >= 0.5 ? 1 : 0) === v.label).length / validation.length;
  console.log(`📊 Validation accuracy: ${(accuracy * 100).toFixed(1)}%`);
}

function predictRule() {
  const input = document.getElementById('ruleInput');
  const notation = input.value.trim();
  
  if (!notation) {
    input.classList.add('invalid');
    return;
  }
  
  try {
    parseRuleNotation(notation);  // Validate
    input.classList.remove('invalid');
    
    const score = predictor.scoreRule(notation);
    
    if (score.error) {
      showPrediction(`❌ Error: ${score.error}`, 0, 0);
      return;
    }
    
    showPrediction(score.message, score.proba, score.confidence);
    
    console.log('Prediction:', score);
    
  } catch (e) {
    input.classList.add('invalid');
    showPrediction(`❌ Invalid notation: ${e.message}`, 0, 0);
  }
}

function showPrediction(message, proba, confidence) {
  const result = document.getElementById('predictionResult');
  result.innerHTML = `
    <div class="proba">${(proba * 100).toFixed(1)}%</div>
    <div style="margin: 10px 0; font-size: 1.2em;">${message}</div>
    <div style="color: #aaa;">Confidence: ${(confidence * 100).toFixed(0)}%</div>
    <div class="confidence-bar">
      <div class="confidence-fill" style="width: ${confidence * 100}%"></div>
    </div>
  `;
}

function suggestCandidates() {
  const btn = document.getElementById('suggestBtn');
  btn.disabled = true;
  btn.textContent = 'Generating...';
  
  setTimeout(() => {
    const candidates = predictor.suggestTopCandidates(20);
    
    const container = document.getElementById('suggestions');
    const table = document.createElement('table');
    table.innerHTML = `
      <thead>
        <tr>
          <th>Rule</th>
          <th>Score</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        ${candidates.map(c => `
          <tr>
            <td>${c.notation}</td>
            <td class="likely">${c.proba}%</td>
            <td><a href="../memory-ai-lab/index.html?rule=${encodeURIComponent(c.notation)}" target="_blank">Test in Lab →</a></td>
          </tr>
        `).join('')}
      </tbody>
    `;
    
    container.innerHTML = '';
    container.appendChild(table);
    
    btn.disabled = false;
    btn.textContent = 'Suggest Top 20 Candidates';
    
    console.log('💡 Top candidates:', candidates.slice(0, 5));
    
  }, 100);
}

// Setup
document.addEventListener('DOMContentLoaded', () => {
  init();
  
  document.getElementById('predictBtn')?.addEventListener('click', predictRule);
  document.getElementById('suggestBtn')?.addEventListener('click', suggestCandidates);
  document.getElementById('ruleInput')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') predictRule();
  });
});

