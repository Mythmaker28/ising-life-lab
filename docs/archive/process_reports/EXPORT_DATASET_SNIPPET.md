# 📥 Export Dataset - Enrichir le Training Set

**Usage**: Après avoir validé de nouvelles règles avec Auto Memory Research

---

## 🎯 Objectif

Exporter les résultats validés au format JSON pour enrichir `data/memory_rules_dataset.json` ou créer un nouveau fichier de dataset.

---

## 📝 Snippet Console

### 1. Exporter Résultats Validés

**Sur**: `http://localhost:8001/experiments/auto-memory-research/`

```javascript
// Après avoir run le pipeline
await AutoMemoryResearch.runAll()

// Récupérer résultats
const { mlSuggestions, validatedResults } = AutoMemoryResearch.getResults()

// Formater pour dataset
const samples = validatedResults.map(r => ({
  notation: r.notation,
  bornMask: [...Array(9)].map((_, i) => r.notation.match(/B([0-8]*)/)[1]?.includes(String(i)) ? 1 : 0),
  surviveMask: [...Array(9)].map((_, i) => r.notation.match(/S([0-8]*)/)[1]?.includes(String(i)) ? 1 : 0),
  isMemoryCandidate: r.isMemoryLike,
  avgRecall: r.avgRecall,
  maxCapacity: r.maxCapacity,
  mlProba: r.mlProba,
  source: 'auto_research_v1'
}))

// Afficher JSON
console.log(JSON.stringify(samples, null, 2))

// OU copier dans presse-papier
copy(JSON.stringify(samples, null, 2))
```

---

### 2. Format de Sortie

**Exemple**:
```json
[
  {
    "notation": "B01/S3",
    "bornMask": [1,1,0,0,0,0,0,0,0],
    "surviveMask": [0,0,0,1,0,0,0,0,0],
    "isMemoryCandidate": true,
    "avgRecall": 100,
    "maxCapacity": 10,
    "mlProba": 0.895,
    "source": "auto_research_v1"
  },
  {
    "notation": "B01/S4",
    "bornMask": [1,1,0,0,0,0,0,0,0],
    "surviveMask": [0,0,0,0,1,0,0,0,0],
    "isMemoryCandidate": true,
    "avgRecall": 99,
    "maxCapacity": 10,
    "mlProba": 0.887,
    "source": "auto_research_v1"
  }
]
```

---

### 3. Enrichir Dataset Existant

**Méthode manuelle**:
1. Exécuter snippet ci-dessus
2. Copier JSON dans presse-papier
3. Ouvrir `data/memory_rules_dataset.json`
4. Ajouter nouvelles entrées dans `rules` array
5. Éviter duplicatas (check notation)
6. Sauvegarder

**Méthode automatique** (script Node):
```javascript
// scripts/enrich-dataset.js
import fs from 'fs';

const existing = JSON.parse(fs.readFileSync('data/memory_rules_dataset.json', 'utf8'));
const newSamples = [ /* coller résultats ici */ ];

// Fusionner sans duplicatas
const notations = new Set(existing.rules.map(r => r.notation));
const toAdd = newSamples.filter(s => !notations.has(s.notation));

existing.rules.push(...toAdd);
existing.meta.version = '1.1';
existing.meta.date = new Date().toISOString().split('T')[0];

fs.writeFileSync('data/memory_rules_dataset_v1.1.json', JSON.stringify(existing, null, 2));
console.log(`Added ${toAdd.length} new rules`);
```

---

### 4. Re-Trainer le Predictor

**Après enrichissement**:
```javascript
// Sur rule-predictor page
location.reload()  // Force reload pour charger nouveau dataset

// Vérifier
predictor.trainingStats.totalSamples
// Expected: 16 + N nouvelles règles
```

---

## 🔄 Workflow Complet

### Cycle de Découverte & Enrichissement

```
1. Rule Predictor
   ↓ suggest candidates
   
2. Auto Memory Research
   ↓ validate top 10
   
3. Export résultats validés
   ↓ copy JSON
   
4. Enrichir dataset
   ↓ add to memory_rules_dataset.json
   
5. Re-train predictor
   ↓ reload rule-predictor page
   
6. Repeat (accuracy improves)
```

**Itération**: Chaque cycle ajoute 5-10 règles validées au dataset

---

## 📊 Exemple Complet

### Scénario: Découvrir 5 Nouvelles Règles

**1. Run Auto Research**:
```javascript
await AutoMemoryResearch.runAll()
```

**2. Export résultats**:
```javascript
const { validatedResults } = AutoMemoryResearch.getResults()
const newRules = validatedResults.filter(r => r.isMemoryLike)
// Found 7 memory-capable rules

const samples = newRules.map(r => ({
  notation: r.notation,
  bornMask: [...Array(9)].map((_, i) => r.notation.match(/B([0-8]*)/)[1]?.includes(String(i)) ? 1 : 0),
  surviveMask: [...Array(9)].map((_, i) => r.notation.match(/S([0-8]*)/)[1]?.includes(String(i)) ? 1 : 0),
  isMemoryCandidate: true,
  avgRecall: r.avgRecall,
  maxCapacity: r.maxCapacity,
  mlProba: r.mlProba,
  source: 'auto_research_2025_11_08'
}))

copy(JSON.stringify(samples, null, 2))
```

**3. Enrichir dataset**:
- Ouvrir `data/memory_rules_dataset.json`
- Coller dans `rules` array
- Sauvegarder

**4. Re-train**:
- Reload `http://localhost:8001/experiments/rule-predictor/`
- Vérifier `predictor.trainingStats.totalSamples` a augmenté

**5. Vérifier accuracy**:
```javascript
const validation = predictor.validateKnown()
const accuracy = validation.filter(v => v.match).length / validation.length
console.log(`Accuracy: ${(accuracy * 100).toFixed(1)}%`)
```

---

## 🎯 Impact Attendu

### Après 3-5 Itérations

**Dataset**:
- 16 → 40+ règles
- Balance amélioré
- Plus de diversity

**Accuracy**:
- Test: 75-100% → 85-95% (plus stable)
- Confusion matrix plus équilibrée

**Suggestions**:
- Plus de true positives
- Moins de false positives
- Meilleures candidates

---

## ⚠️ Notes Importantes

### Éviter Duplicatas
Avant d'ajouter une règle:
```javascript
const existing = JSON.parse(await fetch('../../data/memory_rules_dataset.json').then(r => r.text()))
const notations = existing.rules.map(r => r.notation)
const newRule = 'B01/S35'

if (notations.includes(newRule)) {
  console.warn('Rule already in dataset')
} else {
  console.log('OK to add')
}
```

### Vérifier Qualité
Avant d'ajouter une règle au dataset:
- avgRecall ≥ 90% (critère strict)
- maxCapacity ≥ 10 (capacité suffisante)
- Testée avec protocole V1 complet

### Backup
```bash
# Avant modification
cp data/memory_rules_dataset.json data/memory_rules_dataset.json.backup
```

---

**Le snippet est prêt à l'emploi.** Copy-paste dans la console pour exporter. 📋

