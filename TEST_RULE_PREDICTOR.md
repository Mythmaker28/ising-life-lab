# TEST RULE PREDICTOR - Checklist Rapide

## ✅ Étape 1: Vérifier le Chargement

**URL**: `http://localhost:8001/experiments/rule-predictor/`

**Attendu**:
- Spinner "Training model..." pendant 2-3 secondes
- Puis interface s'affiche
- Console logs:
  ```
  🔄 Loading training datasets...
  ✅ Training set built: 25 samples
  🔄 Training logistic model...
     Epoch 1/500 - Loss: 0.6931
     Epoch 100/500 - Loss: 0.3245
     ...
     Epoch 500/500 - Loss: 0.1682
  ✅ Training complete - Final loss: 0.1682
  ✅ Rule Predictor ready!
  📊 Validation accuracy: XX.X%
  ```

**❌ Si erreur "totalLoss is not defined"**: Le correctif n'a pas été appliqué correctement

---

## ✅ Étape 2: Test Console - Règles Mémoire

**Dans la console de rule-predictor**:

```javascript
// Test 1: Règle mémoire forte (Hall of Fame)
await predictor.scoreRule('B01/S3')
```

**Attendu**:
```javascript
{
  notation: "B01/S3",
  proba: 0.8956,  // >0.8
  label: true,
  confidence: 0.7912,
  message: "✅ Likely memory-capable"
}
```

---

## ✅ Étape 3: Test Console - Règle Faible

```javascript
// Test 2: Conway (règle standard, pas mémoire)
await predictor.scoreRule('B3/S23')
```

**Attendu**:
```javascript
{
  notation: "B3/S23",
  proba: 0.2134,  // <0.5
  label: false,
  confidence: 0.5732,
  message: "❌ Unlikely"
}
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

