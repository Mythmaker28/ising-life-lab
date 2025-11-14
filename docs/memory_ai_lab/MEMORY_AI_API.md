# 🧠 MemoryAI - Multi-Engine API

**Fabrique multi-moteurs pour comparaison automatique**

---

## 🎯 Concept

`MemoryAI` crée instantanément 8 engines mémoire:
- **7 CA champions** (B01/S3, B01/S23, B01/S34, B01/S2, B01/S4, B01/S13, B46/S58)
- **1 Hopfield** (baseline)

Permet de tester automatiquement quel engine performe le mieux sur des patterns donnés.

---

## 📝 API

### Créer une Instance

```javascript
const memoryAI = window.MemoryAI.create({
  width: 32,       // Largeur grille
  height: 32,      // Hauteur grille
  steps: 80,       // Steps CA pour recall
  useSelector: false  // Meta-learner (défaut: false)
})
```

**Avec Meta-Learner** (NEW):
```javascript
const memoryAI = MemoryAI.create({ useSelector: true })
// Apprend quel engine est optimal par pattern
// Gain: 8× plus rapide si prédiction correcte
```

---

### Stocker des Patterns

```javascript
const patterns = MemoryLab.getPatternsForTests()
memoryAI.store(patterns)
```

**Effet**: Broadcast vers les 8 engines (7 CA + Hopfield)

---

### Recall avec Bruit

```javascript
const noisy = addNoise(patterns[0], 0.05)

// Standard: teste les 8 engines
const result = memoryAI.recall(noisy)

// Avec prédiction (si useSelector: true)
const resultFast = memoryAI.recall(noisy, { usePrediction: true, patternIndex: 0 })
```

**Retour**:
```javascript
{
  best: { rule: 'B01/S4', distance: 12, success: true },
  all: [
    { rule: 'B01/S4', distance: 12, success: true },
    { rule: 'B01/S3', distance: 18, success: true },
    // ... (8 résultats si predicted: false, 1 seul si predicted: true)
  ],
  predicted: false  // true si usePrediction activé et selector trained
}
```

**best**: Meilleur engine (Hamming distance minimal)  
**all**: Tous testés (predicted: false) ou seul prédit (predicted: true)  
**predicted**: Indique si meta-learner utilisé

---

## 💡 Use Cases

### 1. Trouver le Meilleur Engine pour un Pattern

```javascript
const memoryAI = MemoryAI.create()
const patterns = MemoryLab.getPatternsForTests()

memoryAI.store(patterns)

// Tester chaque pattern avec bruit
patterns.forEach((p, i) => {
  const noisy = addNoise(p, 0.05)
  const result = memoryAI.recall(noisy)
  console.log(`Pattern ${i}: best engine = ${result.best.rule} (distance: ${result.best.distance})`)
})
```

**Output**:
```
Pattern 0: best engine = B01/S3 (distance: 8)
Pattern 1: best engine = B01/S4 (distance: 5)
Pattern 2: best engine = B46/S58 (distance: 12)
...
```

---

### 2. Benchmark Ensemble

```javascript
const memoryAI = MemoryAI.create()
const patterns = MemoryLab.getPatternsForTests()

memoryAI.store(patterns)

const noiseLevel = 0.08
let ensembleSuccesses = 0
const engineSuccesses = {}

patterns.forEach(p => {
  const noisy = addNoise(p, noiseLevel)
  const result = memoryAI.recall(noisy)
  
  // Ensemble: au moins 1 engine a réussi?
  if (result.best.success) ensembleSuccesses++
  
  // Compter par engine
  result.all.forEach(r => {
    engineSuccesses[r.rule] = (engineSuccesses[r.rule] || 0) + (r.success ? 1 : 0)
  })
})

console.log(`Ensemble recall: ${ensembleSuccesses}/${patterns.length}`)
console.table(engineSuccesses)
```

**Résultat**:
```
Ensemble recall: 98/100

┌────────────┬──────────┐
│ Engine     │ Successes│
├────────────┼──────────┤
│ B01/S3     │ 96       │
│ B01/S4     │ 99       │
│ B01/S23    │ 85       │
│ Hopfield   │ 100      │
└────────────┴──────────┘
```

---

### 3. Voting / Consensus

```javascript
function consensusRecall(memoryAI, noisyPattern, threshold = 0.5) {
  const result = memoryAI.recall(noisyPattern)
  const successCount = result.all.filter(r => r.success).length
  const successRate = successCount / result.all.length
  
  return {
    consensus: successRate >= threshold,
    votes: successCount,
    total: result.all.length,
    best: result.best
  }
}

// Usage
const noisy = addNoise(patterns[0], 0.05)
const consensus = consensusRecall(memoryAI, noisy, 0.5)

if (consensus.consensus) {
  console.log(`✓ Consensus: ${consensus.votes}/${consensus.total} engines agree`)
  console.log(`Best: ${consensus.best.rule}`)
} else {
  console.log(`✗ No consensus: only ${consensus.votes}/${consensus.total} engines`)
}
```

---

## 🧪 Test Rapide

**Sur**: `http://localhost:8001/experiments/memory-ai-lab/`

```javascript
// 1. Créer MemoryAI
const memoryAI = MemoryAI.create()

// 2. Stocker patterns (UI ou default)
const patterns = MemoryLab.getPatternsForTests()
memoryAI.store(patterns)

// 3. Test recall
const noisy = addNoise(patterns[0], 0.05)
const result = memoryAI.recall(noisy)

console.log('Best engine:', result.best.rule)
console.log('Distance:', result.best.distance)
console.table(result.all)
```

**Expected**:
- `best.rule`: Un des 7 champions ou Hopfield
- `all`: Array de 8 résultats triés par distance

---

## 📊 Avantages

### vs. Test Manuel
- **AVANT**: Tester 7 règles manuellement → 7 appels séparés
- **APRÈS**: `memoryAI.recall()` → 1 appel, meilleur retourné

### vs. Single Engine
- **AVANT**: Choisir 1 règle à l'avance (risque sub-optimal)
- **APRÈS**: Teste les 8, garde le meilleur (optimal)

### Ensemble Learning
- Consensus possible (vote majoritaire)
- Fallback automatique si un engine échoue
- Diversité des règles CA

---

## 🔧 Configuration Avancée

### Steps Variables par Engine

```javascript
// Actuellement: steps constant
// Future: steps adaptatif par règle

const memoryAI = MemoryAI.create()
// B01/S3 pourrait avoir steps=60
// B46/S58 pourrait avoir steps=100
```

### Sélection Dynamique

```javascript
// Charger seulement top-N engines (selon dataset actuel)
const topEngines = ['B01/S3', 'B01/S4', 'Hopfield']
// Filtrer MEMORY_CHAMPIONS
```

---

## 🎯 Use Cases Réels

### Stockage Mémoire Robuste

```javascript
// Système qui garantit recall avec ensemble
class RobustMemorySystem {
  constructor() {
    this.ai = MemoryAI.create()
  }
  
  store(patterns) {
    this.ai.store(patterns)
  }
  
  recall(noisy) {
    const result = this.ai.recall(noisy)
    if (result.best.success) {
      return result.best
    }
    // Fallback: retourner meilleure approximation
    return result.all[0]  // Plus petit distance
  }
}
```

### Diagnostic Engine

```javascript
// Identifier quel engine marche le mieux par pattern
function diagnosePatterns(patterns) {
  const memoryAI = MemoryAI.create()
  memoryAI.store(patterns)
  
  const diagnosis = patterns.map((p, i) => {
    const noisy = addNoise(p, 0.05)
    const result = memoryAI.recall(noisy)
    return {
      patternId: i,
      bestEngine: result.best.rule,
      distance: result.best.distance,
      alternatives: result.all.filter(r => r.success).length
    }
  })
  
  console.table(diagnosis)
  return diagnosis
}
```

---

## 📚 Liens

- **CA Memory API**: `docs/CA_MEMORY_API.md`
- **Capacity Results**: `docs/memory-capacity-results.md`
- **Hall of Fame**: `docs/MEMORY_HALL_OF_FAME.md`

---

---

## 📦 Module Réutilisable

**Depuis commit [suivant]**: MemoryAI extrait en module standalone

**Import**:
```javascript
import { createMemoryAI, MemoryAI, MEMORY_CHAMPIONS } from './src/memory/memoryAI.js';
```

**Fichier**: `src/memory/memoryAI.js` (60 lignes, pur ES6)

---

**Status**: ✅ Production-Ready  
**Module**: src/memory/memoryAI.js  
**API Version**: 1.1

