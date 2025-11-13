# ✅ TEST ENGINE SELECTOR - Meta-Learner

**Commit**: [current]  
**Fichiers**: `src/ai/engineSelector.js`, `src/memory/memoryAI.js`

---

## 🧪 Test Unique (1 snippet)

**URL**: `http://localhost:8001/experiments/memory-ai-lab/`

**Après hard refresh (Ctrl+Shift+R)**:

```javascript
// 1. Créer MemoryAI avec selector activé
const patterns = MemoryLab.getPatternsForTests().map(p => p.grid || p);
const memAI = MemoryAI.create({ width: 32, height: 32, steps: 80, useSelector: true });

// 2. Store (déclenche training async)
memAI.store(patterns);

// 3. Attendre training (~10-15 secondes pour 10 samples × patterns.length)
await new Promise(r => setTimeout(r, 15000));

// 4. Test recall
const addNoise = (grid, rate) => {
  const x = new Uint8Array(grid);
  for (let i = 0; i < x.length; i++) if (Math.random() < rate) x[i] = 1 - x[i];
  return x;
};

const base = patterns[0];
const noisy = addNoise(base, 0.08);

// Sans prédiction (teste les 8)
console.log('SANS prédiction:', memAI.recall(noisy));

// Avec prédiction (teste 1 seul)
console.log('AVEC prédiction:', memAI.recall(noisy, { usePrediction: true, patternIndex: 0 }));
```

---

## ✅ Expected Results

**Sans prédiction**:
```javascript
{
  best: { rule: 'B01/S4', distance: 12, success: true },
  all: [
    { rule: 'B01/S4', distance: 12, success: true },
    { rule: 'B01/S3', distance: 18, success: true },
    // ... 8 résultats
  ],
  predicted: false
}
```

**Avec prédiction**:
```javascript
{
  best: { rule: 'B01/S4', distance: 12, success: true },
  all: [
    { rule: 'B01/S4', distance: 12, success: true }
    // 1 seul résultat (engine prédit)
  ],
  predicted: true
}
```

**Gain**: 8× plus rapide si prédiction correcte

---

## 🔍 Debug

**Console logs attendus**:
```
🧠 Training EngineSelector...
✅ EngineSelector trained {
  globalWins: {B01/S3: 45, B01/S4: 67, Hopfield: 23, ...},
  mappedPatterns: 8,
  totalSamples: 80
}
```

**Checks**:
```javascript
// Vérifier que selector existe
memAI.selector
// Expected: EngineSelector instance

memAI.selector.trained
// Expected: true (après training)

memAI.selector.bestGlobal()
// Expected: 'B01/S4' ou similaire (engine le plus gagnant)

memAI.selector.suggestForPattern(0)
// Expected: 'B01/S3' ou null si pas de mapping clair
```

---

## ⚡ Performance

**Test 100 patterns**:
- Sans selector: 100 × 8 = 800 engine recalls (~2 min)
- Avec selector: 100 × 1 = 100 engine recalls (~15s) + training overhead
- **Net gain: ~80-85% temps économisé**

---

## 🐛 Si Problème

**"EngineSelector is not defined"**:
- Hard refresh
- Vérifier commit appliqué
- Check `typeof window.EngineSelector` → 'function'

**Training never completes**:
- Vérifier patterns non-empty
- Check console pour errors async
- Réduire samplesPerPattern à 5

**Prediction toujours false**:
- Vérifier `memAI.selector.trained === true`
- Attendre 15s après store()
- Check `memAI.useSelector === true`

---

**Doc complète**: `docs/MEMORY_AI_API.md` (mis à jour avec useSelector)

