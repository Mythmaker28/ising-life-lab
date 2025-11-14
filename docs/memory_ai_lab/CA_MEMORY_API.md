# CA Memory Engine API

API commune pour mémoire CA et Hopfield.

## Import

```javascript
import { CAMemoryEngine } from './src/memory/caMemoryEngine.js';
import { HopfieldMemoryEngine } from './src/memory/hopfieldMemoryEngine.js';
```

## API Commune

### CAMemoryEngine

```javascript
const engine = new CAMemoryEngine(32, 32);
engine.store(patterns, { rule: { born: [0,1], survive: [3] }, steps: 80 });
const result = engine.recall(noisyPattern, { steps: 80, maxDiffRatio: 0.1 });
// result: { recalled, success, distance, ratio, stepsUsed }
```

### HopfieldMemoryEngine

```javascript
const hop = new HopfieldMemoryEngine(1024);
hop.store(patterns);
const result = hop.recall(noisyPattern, { maxSteps: 100, maxDiffRatio: 0.1 });
// result: { recalled, success, distance, ratio, stepsUsed }
```

## Méthodes

- `store(patterns, options)`: Stocker patterns
- `recall(noisyPattern, options)`: Rappeler pattern
- `score(original, recalled, maxDiffRatio)`: Évaluer qualité

## Exposition Globale

Dans Memory AI Lab:
```javascript
window.CAMemoryEngine
window.HopfieldMemoryEngine
```

