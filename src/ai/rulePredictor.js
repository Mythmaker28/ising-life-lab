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
  const features = new Float32Array(18);
  
  // Features 0-8: Born bits
  rule.born.forEach(n => { if (n >= 0 && n <= 8) features[n] = 1; });
  
  // Features 9-17: Survive bits
  rule.survive.forEach(n => { if (n >= 0 && n <= 8) features[9 + n] = 1; });
  
  return features;
}

export async function buildTrainingSet() {
  console.log('🔄 Loading real lab datasets...');
  
  const rulesMap = new Map(); // notation -> {features, label, sources, data}
  
  try {
    // Load memory_capacity_v1.json (highest confidence data)
    const resp1 = await fetch('../../data/memory_capacity_v1.json');
    const capacity = await resp1.json();
    
    capacity.results?.forEach(r => {
      if (r.model === 'CA') {
        const features = encodeRuleBS(r.rule);
        // Label: isMemoryLike = (maxCapacity >= 10 AND avgRecall >= 90)
        const isMemoryLike = r.maxCapacity >= 10 && r.avgRecall >= 90;
        rulesMap.set(r.rule, {
          features,
          label: isMemoryLike ? 1 : 0,
          sources: ['capacity_v1'],
          avgRecall: r.avgRecall,
          maxCapacity: r.maxCapacity
        });
      }
    });
    console.log(`   ✓ Loaded ${capacity.results?.filter(r => r.model === 'CA').length || 0} rules from capacity_v1.json`);
  } catch (e) {
    console.warn('   ⚠️ memory_capacity_v1.json not accessible:', e.message);
  }
  
  try {
    // Load memory_rules_dataset.json
    const resp2 = await fetch('../../data/memory_rules_dataset.json');
    const dataset = await resp2.json();
    
    dataset.rules?.forEach(r => {
      if (!rulesMap.has(r.notation)) {
        const features = encodeRuleBS(r.notation);
        // Use isMemoryCandidate as label
        rulesMap.set(r.notation, {
          features,
          label: r.isMemoryCandidate ? 1 : 0,
          sources: ['rules_dataset'],
          avgRecall: r.avgRecall,
          source: r.source
        });
      } else {
        // Already have this rule, just add source
        rulesMap.get(r.notation).sources.push('rules_dataset');
      }
    });
    console.log(`   ✓ Loaded ${dataset.rules?.length || 0} rules from rules_dataset.json`);
  } catch (e) {
    console.warn('   ⚠️ memory_rules_dataset.json not accessible:', e.message);
  }
  
  // Add known negative examples
  const knownNegatives = [
    'B3/S23',        // Conway (not memory)
    'B36/S23',       // HighLife (not memory)
    'B3678/S34678',  // Day & Night (chaotic)
    'B2/S',          // Seeds (no survive)
    'B1357/S1357'    // Replicator (explosive)
  ];
  
  knownNegatives.forEach(notation => {
    if (!rulesMap.has(notation)) {
      const features = encodeRuleBS(notation);
      rulesMap.set(notation, {
        features,
        label: 0,
        sources: ['known_negative']
      });
    }
  });
  
  // Build arrays
  const X = [];
  const y = [];
  const meta = [];
  
  rulesMap.forEach((data, notation) => {
    X.push(data.features);
    y.push(data.label);
    meta.push({
      notation,
      label: data.label,
      sources: data.sources,
      avgRecall: data.avgRecall,
      maxCapacity: data.maxCapacity
    });
  });
  
  const positives = y.filter(l => l === 1).length;
  const negatives = y.filter(l => l === 0).length;
  
  console.log(`✅ Training set built: ${X.length} unique rules`);
  console.log(`   - Positive (memory-capable): ${positives}`);
  console.log(`   - Negative (not memory): ${negatives}`);
  console.log(`   - Balance: ${(positives / X.length * 100).toFixed(1)}% positive`);
  
  return { X, y: new Float32Array(y), meta };
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
  
  let lastLossValue = null;
  
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
    
    lastLossValue = totalLoss / nSamples;
    
    if (epoch === 0 || (epoch + 1) % 100 === 0 || epoch === epochs - 1) {
      console.log(`   Epoch ${epoch + 1}/${epochs} - Loss: ${lastLossValue.toFixed(4)}`);
    }
  }
  
  if (lastLossValue !== null) {
    console.log(`✅ Training complete - Final loss: ${lastLossValue.toFixed(4)}`);
  } else {
    console.log('✅ Training complete - Final loss: n/a');
  }
  
  return {
    weights: w,
    bias: b,
    predictProba: (features) => forward(features),
    predictLabel: (features, threshold = 0.5) => forward(features) >= threshold
  };
}

export async function createRulePredictor(config = {}) {
  const { X, y, meta } = await buildTrainingSet();
  
  // Hold-out validation (80/20 split)
  const splitIdx = Math.floor(X.length * 0.8);
  const Xtrain = X.slice(0, splitIdx);
  const ytrain = y.slice(0, splitIdx);
  const Xtest = X.slice(splitIdx);
  const ytest = y.slice(splitIdx);
  
  console.log(`📊 Hold-out split: ${Xtrain.length} train / ${Xtest.length} test`);
  
  const model = trainLogisticModel(Xtrain, ytrain, config);
  
  // Validate on test set
  if (Xtest.length > 0) {
    let correct = 0;
    for (let i = 0; i < Xtest.length; i++) {
      const pred = model.predictLabel(Xtest[i]);
      if ((pred ? 1 : 0) === ytest[i]) correct++;
    }
    const accuracy = (correct / Xtest.length * 100).toFixed(1);
    console.log(`📈 Test accuracy: ${correct}/${Xtest.length} (${accuracy}%)`);
    
    // Show confusion matrix
    let tp = 0, tn = 0, fp = 0, fn = 0;
    for (let i = 0; i < Xtest.length; i++) {
      const pred = model.predictLabel(Xtest[i]) ? 1 : 0;
      const actual = ytest[i];
      if (pred === 1 && actual === 1) tp++;
      else if (pred === 0 && actual === 0) tn++;
      else if (pred === 1 && actual === 0) fp++;
      else fn++;
    }
    console.log(`   Confusion: TP=${tp}, TN=${tn}, FP=${fp}, FN=${fn}`);
  }
  
  // Retrain on full dataset for production
  console.log('🔄 Retraining on full dataset for production...');
  const finalModel = trainLogisticModel(X, y, config);
  
  return {
    scoreRule(notation) {
      try {
        const features = encodeRuleBS(notation);
        const proba = finalModel.predictProba(features);
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
            const proba = finalModel.predictProba(features);
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
          actualLabel: m.label,
          predictedLabel: score.label ? 1 : 0,
          match: (score.label ? 1 : 0) === m.label,
          sources: m.sources,
          avgRecall: m.avgRecall,
          maxCapacity: m.maxCapacity
        });
      });
      return validation;
    },
    
    model: finalModel,
    meta,
    trainingStats: {
      totalSamples: X.length,
      trainSamples: Xtrain.length,
      testSamples: Xtest.length,
      positives: y.filter(l => l === 1).length,
      negatives: y.filter(l => l === 0).length
    }
  };
}

