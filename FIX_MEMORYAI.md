# 🔧 FIX: MemoryAI is not defined

## ❌ Problème

```javascript
const memAI = MemoryAI.create(...)
// Uncaught ReferenceError: MemoryAI is not defined
```

---

## ✅ Solution Simple

### 1. Vérifier que tu es sur la bonne page

**MemoryAI est défini SEULEMENT sur**:
```
http://localhost:8001/experiments/memory-ai-lab/
```

**PAS disponible sur**:
- auto-memory-research (charge pas main.js complet)
- rule-predictor (page séparée)
- memory-storage-system (page séparée)

### 2. Hard Refresh

```
Ctrl + Shift + R
```

Le commit qui ajoute MemoryAI est: **669cb78**

---

## 🧪 Test Rapide

**URL**: `http://localhost:8001/experiments/memory-ai-lab/`

**Console**:
```javascript
// Check 1: MemoryAI existe?
typeof window.MemoryAI
// Expected: 'object'

typeof window.MemoryAI.create
// Expected: 'function'

// Check 2: Test complet
const memAI = MemoryAI.create()
const patterns = MemoryLab.getPatternsForTests()
memAI.store(patterns)

// Créer bruit (fonction addNoise existe dans le module mais pas window)
function addNoise(grid, rate) {
  const noisy = new Uint8Array(grid);
  for (let i = 0; i < noisy.length; i++) {
    if (Math.random() < rate) noisy[i] = 1 - noisy[i];
  }
  return noisy;
}

const noisy = addNoise(patterns[0], 0.05)
const result = memAI.recall(noisy)

console.log('Best:', result.best.rule, 'distance:', result.best.distance)
console.table(result.all)
```

**Expected**:
```javascript
Best: B01/S3 distance: 12
// Table avec 8 engines (7 CA + Hopfield)
```

---

## 🔍 Si Toujours Pas Défini

**Vérifier fichier**:
```bash
# Ligne 856 doit contenir:
# window.MemoryAI = { create: window.createMemoryAI };
```

**Dans console sur memory-ai-lab**:
```javascript
// Debug
console.log(typeof window.createMemoryAI)  // 'function'
console.log(typeof window.MemoryAI)         // 'object'
console.log(window.MemoryAI)                // { create: function }
```

**Si undefined**:
- Git pull pour être sûr d'avoir commit 669cb78
- Vérifier que experiments/memory-ai-lab/main.js a bien les lignes 820-856
- Serveur relancé depuis la bonne racine

---

## ✅ Snippet de Test Final

**Copier-coller sur**: `http://localhost:8001/experiments/memory-ai-lab/`

```javascript
// Test ultra-minimal
({
  MemoryAI: !!window.MemoryAI,
  createMemoryAI: !!window.createMemoryAI,
  MemoryLab: !!window.MemoryLab,
  CAMemoryEngine: !!window.CAMemoryEngine,
  HopfieldMemoryEngine: !!window.HopfieldMemoryEngine
})
// Expected: tous true
```

---

**Si tous true**: `MemoryAI.create()` devrait marcher  
**Si MemoryAI false**: Hard refresh ou vérifier commit

