# ☀️ DEMAIN MATIN - Tests en 5 Minutes

**Serveur**:
```bash
cd C:\Users\tommy\Documents\ising-v2-final
python -m http.server 8001
```

---

## ✅ Test 1: MemoryAI Multi-Engine (1 min)

**URL**: `http://localhost:8001/experiments/memory-ai-lab/`

```javascript
const memAI = MemoryAI.create()
const patterns = MemoryLab.getPatternsForTests()
memAI.store(patterns)

function addNoise(grid, rate) {
  const x = new Uint8Array(grid);
  for (let i = 0; i < x.length; i++) if (Math.random() < rate) x[i] = 1 - x[i];
  return x;
}

const result = memAI.recall(addNoise(patterns[0], 0.05))
console.log('Best:', result.best.rule)
console.table(result.all)
// Expected: 8 engines testés, best engine affiché
```

---

## ✅ Test 2: Engine Selector Demo (2 min)

**URL**: `http://localhost:8001/experiments/engine-selector-demo/`

**Actions**:
1. Click "Run Demo"
2. Attendre 20 secondes
3. Vérifier speedup affiché (6-8×)

---

## ✅ Test 3: Auto Memory Research (1 min)

**URL**: `http://localhost:8001/experiments/auto-memory-research/`

```javascript
!!window.MemoryCapacity  // true
await AutoMemoryResearch.suggest()
// Table avec candidates
```

---

## ✅ Test 4: Rule Predictor (1 min)

**URL**: `http://localhost:8001/experiments/rule-predictor/`

```javascript
predictor.scoreRule('B01/S3')  // ~90%
predictor.trainingStats        // 16 samples
```

---

## 🎯 Si Tout Passe

**Projet**: 99/100 ✅  
**Tag**: v2.0-complete ✅  
**Status**: Production-ready 🚀

---

## 📦 Docs Clés

- `PROJECT_FINAL_REPORT.md` - Résumé complet
- `TEST_ENGINE_SELECTOR.md` - Test meta-learner
- `START_HERE.md` - Quick ref

---

**5 minutes chrono. Si ça passe, le projet est terminé.** ⏱️

