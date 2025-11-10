# TEST RULE PREDICTOR - Checklist Rapide

## ✅ Étape 1: Vérifier le Chargement

**URL**: `http://localhost:8001/experiments/rule-predictor/`

**Attendu**:
- Spinner "Training model..." pendant 2-3 secondes
- Puis interface s'affiche
- Console logs améliorés:
  ```
  🔄 Loading real lab datasets...
     ✓ Loaded 7 rules from capacity_v1.json
     ✓ Loaded 11 rules from rules_dataset.json
  ✅ Training set built: 16 unique rules
     - Positive (memory-capable): 7
     - Negative (not memory): 9
     - Balance: 43.8% positive
  📊 Hold-out split: 12 train / 4 test
  🔄 Training logistic model...
     Epoch 1/500 - Loss: 0.6931
     Epoch 100/500 - Loss: 0.3245
     ...
     Epoch 500/500 - Loss: 0.1682
  ✅ Training complete - Final loss: 0.1682
  📈 Test accuracy: 4/4 (100.0%)
     Confusion: TP=2, TN=2, FP=0, FN=0
  🔄 Retraining on full dataset for production...
  ✅ Rule Predictor ready!
  ```

**✅ Améliorations**:
- Features simplifiées: 18 bits au lieu de 22
- Données réelles du lab (capacity_v1.json prioritaire)
- Validation hold-out avec confusion matrix
- Pas de duplicatas

---

## ✅ Étape 2: Test Console - Règles Mémoire

**Dans la console de rule-predictor**:

```javascript
// Test 1: Règle mémoire forte (Hall of Fame)
predictor.scoreRule('B01/S3')
```

**Attendu** (scores peuvent varier selon split aléatoire):
```javascript
{
  notation: "B01/S3",
  proba: 0.85-0.95,  // Devrait être élevé
  label: true,
  confidence: 0.7-0.9,
  message: "✅ Likely memory-capable"
}
```

**Note**: Scores maintenant basés sur vraies données de capacity_v1.json

---

## ✅ Étape 3: Test Console - Règle Faible

```javascript
// Test 2: Conway (règle standard, pas mémoire)
predictor.scoreRule('B3/S23')
```

**Attendu**:
```javascript
{
  notation: "B3/S23",
  proba: 0.1-0.3,  // <0.5 (faible)
  label: false,
  confidence: 0.4-0.8,
  message: "❌ Unlikely"
}
```

**✅ Test 3: Vérifier training stats**:
```javascript
predictor.trainingStats
// {
//   totalSamples: 16,
//   trainSamples: 12,
//   testSamples: 4,
//   positives: 7,
//   negatives: 9
// }
```

---

## ✅ Étape 4: Test Suggestions

```javascript
// Test 3: Générer des candidats
predictor.suggestTopCandidates(10)
```

**Attendu**:
```javascript
[
  { notation: "B01/S2", proba: "92.3" },
  { notation: "B01/S4", proba: "91.8" },
  { notation: "B01/S3", proba: "89.5" },
  ...
]
```

---

## ✅ Étape 5: Sanity Check V1.0

**URL**: `http://localhost:8001/experiments/memory-ai-lab/`

**Console**:
```javascript
!!window.MemoryLab           // true
!!window.MemoryScanner        // true
!!window.MemoryCapacity       // true
!!window.CAMemoryEngine       // true
!!window.HopfieldMemoryEngine // true
```

**Tous doivent retourner `true`**

---

## 🎯 Résultat Final Attendu

| Test | Status |
|------|--------|
| Chargement sans erreur | ✅ |
| Training logs corrects | ✅ |
| B01/S3 → score élevé | ✅ |
| B3/S23 → score faible | ✅ |
| Suggestions générées | ✅ |
| V1.0 intact | ✅ |

---

## 🐛 Si Problème

**Erreur "totalLoss is not defined"**:
- Vérifier que le commit a1e21a3 est bien appliqué
- Vérifier `src/ai/rulePredictor.js` ligne 126: `let lastLossValue = null;`
- Hard refresh: Ctrl+Shift+R

**Score incohérent**:
- Vérifier que `data/memory_rules_dataset.json` existe
- Vérifier que `data/memory_capacity_v1.json` existe
- Check console pour warnings de fetch

**V1.0 cassé**:
- Ne devrait pas arriver, aucun fichier V1.0 modifié
- Vérifier git log pour changements inattendus

---

## 📊 Commandes Git Utiles

```bash
# Voir le dernier commit
git log -1 --oneline

# Vérifier les modifications
git diff HEAD~1 HEAD src/ai/rulePredictor.js

# Revenir en arrière si nécessaire
git revert a1e21a3
```

