/**
 * Rule Predictor - ML-based memory prediction
 * Logistic regression pour prédire si une règle CA sera memory-capable
 */

export function parseRuleNotation(notation) {
  const match = notation.match(/B([0-8]*)\/S([0-8]*)/);
  if (!match) throw new Error(`Invalid notation: ${notation}`);
  return {
    born: match[1] ? match[1].split('').map(Number) : [],
    survive: match[2] ? match[2].split('').map(Number) : []
  };
}

export function encodeRuleBS(notation) {
  const rule = parseRuleNotation(notation);
  const features = new Float32Array(22);
  
  // Features 0-8: Born bits
  rule.born.forEach(n => { if (n >= 0 && n <= 8) features[n] = 1; });
  
  // Features 9-17: Survive bits
  rule.survive.forEach(n => { if (n >= 0 && n <= 8) features[9 + n] = 1; });
  
  // Features dérivées
  features[18] = rule.born.length / 9;  // Densité Born
  features[19] = rule.survive.length / 9;  // Densité Survive
  features[20] = (rule.born.includes(0) || rule.born.includes(1)) ? 1 : 0;  // B0 ou B1
  features[21] = (rule.survive.includes(2) && rule.survive.includes(3)) ? 1 : 0;  // S2 ET S3
  
  return features;
}

export async function buildTrainingSet() {
  console.log('🔄 Loading training datasets...');
  
  const rules = [];
  const labels = [];
  const meta = [];
  
  try {
    // Charger memory_rules_dataset.json
    const resp1 = await fetch('../../data/memory_rules_dataset.json');
    const data1 = await resp1.json();
    
    data1.rules?.forEach(r => {
      rules.push(encodeRuleBS(r.notation));
      labels.push(r.isMemoryCandidate ? 1 : 0);
      meta.push({ notation: r.notation, source: 'dataset' });
    });
  } catch (e) {
    console.warn('⚠️ memory_rules_dataset.json non accessible:', e.message);
  }
  
  try {
    // Charger memory_capacity_v1.json
    const resp2 = await fetch('../../data/memory_capacity_v1.json');
    const data2 = await resp2.json();
    
    data2.results?.forEach(r => {
      if (r.model === 'CA') {
        const features = encodeRuleBS(r.rule);
        // Éviter duplicata
        const exists = meta.some(m => m.notation === r.rule);
        if (!exists) {
          rules.push(features);
          labels.push((r.avgRecall >= 90 && r.maxCapacity >= 10) ? 1 : 0);
          meta.push({ notation: r.rule, source: 'capacity' });
        }
      }
    });
  } catch (e) {
    console.warn('⚠️ memory_capacity_v1.json non accessible:', e.message);
  }
  
  // Ajouter exemples négatifs connus
  const negatives = ['B3/S23', 'B36/S23', 'B3678/S34678', 'B2/S', 'B1357/S1357'];
  negatives.forEach(notation => {
    rules.push(encodeRuleBS(notation));
    labels.push(0);
    meta.push({ notation, source: 'known_negative' });
  });
  
  const positives = labels.filter(l => l === 1).length;
  const negativeCount = labels.filter(l => l === 0).length;
  
  console.log(`✅ Training set built: ${rules.length} samples`);
  console.log(`   - Positive: ${positives}`);
  console.log(`   - Negative: ${negativeCount}`);
  
  return { X: rules, y: new Float32Array(labels), meta };
}

export function trainLogisticModel(X, y, config = {}) {
  const {
    epochs = 500,
    learningRate = 0.1,
    lambda = 0.01  // L2 regularization
  } = config;
  
  const nFeatures = X[0].length;
  const nSamples = X.length;
  
  // Initialize weights
  const w = new Float32Array(nFeatures);
  for (let i = 0; i < nFeatures; i++) {
    w[i] = (Math.random() - 0.5) * 0.1;
  }
  let b = 0;
  
  function sigmoid(z) {
    return 1 / (1 + Math.exp(-z));
  }
  
  function forward(features) {
    let z = b;
    for (let i = 0; i < nFeatures; i++) {
      z += w[i] * features[i];
    }
    return sigmoid(z);
  }
  
  // Gradient descent
  console.log('🔄 Training logistic model...');
  
  for (let epoch = 0; epoch < epochs; epoch++) {
    let totalLoss = 0;
    const dw = new Float32Array(nFeatures);
    let db = 0;
    
    // Forward + backward
    for (let i = 0; i < nSamples; i++) {
      const pred = forward(X[i]);
      const error = pred - y[i];
      
      // Loss (BCE)
      const loss = -y[i] * Math.log(pred + 1e-15) - (1 - y[i]) * Math.log(1 - pred + 1e-15);
      totalLoss += loss;
      
      // Gradients
      for (let j = 0; j < nFeatures; j++) {
        dw[j] += error * X[i][j];
      }
      db += error;
    }
    
    // L2 regularization
    for (let j = 0; j < nFeatures; j++) {
      totalLoss += lambda * w[j] * w[j];
    }
    
    // Update
    for (let j = 0; j < nFeatures; j++) {
      w[j] -= learningRate * (dw[j] / nSamples + 2 * lambda * w[j]);
    }
    b -= learningRate * (db / nSamples);
    
    if (epoch % 100 === 0) {
      console.log(`   Epoch ${epoch}/${epochs} - Loss: ${(totalLoss / nSamples).toFixed(4)}`);
    }
  }
  
  console.log(`✅ Training complete - Final loss: ${(totalLoss / nSamples).toFixed(4)}`);
  
  return {
    weights: w,
    bias: b,
    predictProba: (features) => forward(features),
    predictLabel: (features, threshold = 0.5) => forward(features) >= threshold
  };
}

export async function createRulePredictor(config = {}) {
  const { X, y, meta } = await buildTrainingSet();
  const model = trainLogisticModel(X, y, config);
  
  return {
    scoreRule(notation) {
      try {
        const features = encodeRuleBS(notation);
        const proba = model.predictProba(features);
        const label = proba >= 0.5;
        const confidence = Math.abs(proba - 0.5) * 2;  // 0-1
        
        return {
          notation,
          proba,
          label,
          confidence,
          message: label ? '✅ Likely memory-capable' : '❌ Unlikely'
        };
      } catch (e) {
        return { notation, error: e.message };
      }
    },
    
    suggestTopCandidates(limit = 20) {
      console.log('🔍 Generating candidate rules...');
      const candidates = [];
      
      // Generate plausible rules
      // B0X/SY, B1X/SY where X,Y are subsets
      const bornBases = [[0], [1], [0,1], [2], [0,2], [1,2], [4], [0,1,4], [2,4], [4,6]];
      const surviveBases = [[], [2], [3], [4], [5], [2,3], [3,4], [2,3,4], [5,8]];
      
      bornBases.forEach(born => {
        surviveBases.forEach(survive => {
          const notation = `B${born.join('')}/S${survive.join('')}`;
          
          // Skip if already in training set
          const known = meta.some(m => m.notation === notation);
          if (known) return;
          
          try {
            const features = encodeRuleBS(notation);
            const proba = model.predictProba(features);
            candidates.push({ notation, proba: (proba * 100).toFixed(1) });
          } catch (e) {}
        });
      });
      
      // Sort and limit
      candidates.sort((a, b) => parseFloat(b.proba) - parseFloat(a.proba));
      console.log(`✓ Generated ${candidates.length} candidates`);
      
      return candidates.slice(0, limit);
    },
    
    validateKnown() {
      const validation = [];
      meta.forEach(m => {
        const score = this.scoreRule(m.notation);
        validation.push({
          notation: m.notation,
          predicted: score.proba,
          label: score.label ? 1 : 0
        });
      });
      return validation;
    },
    
    model,
    meta
  };
}

