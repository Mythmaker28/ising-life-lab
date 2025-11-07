# Quick Start - Memory AI Lab

## 🚀 Lancement en 30 secondes

### 1. Démarrer le serveur

```bash
cd C:\Users\tommy\Documents\ising-v2-final
python -m http.server 8001
```

### 2. Ouvrir Memory AI Lab

```
http://localhost:8001/experiments/memory-ai-lab/index.html
```

### 3. Lancer les tests automatiques

**Ouvrir la console** (F12) et copier-coller:

```javascript
const batch = await MemoryLab.runBatchForHallOfFame({ noiseLevel: 0.05, steps: 80, runs: 50 });
const comp = await HopfieldLab.compareWithHallOfFame({ noiseLevel: 0.05, runs: 50 });
const report = Reports.generateMarkdownReport(batch, comp);
console.log(report);
```

**C'est tout!** Les tests utilisent automatiquement 4 patterns par défaut si vous n'en avez pas dessiné.

---

## 📊 Ce qui se passe

1. **`runBatchForHallOfFame()`**: Teste les 7 règles du Hall of Fame
   - Chaque règle testée sur 4 patterns × 50 runs = 200 simulations par règle
   - Calcule recall rate, coverage, nombre d'attracteurs
   - Affiche un tableau récapitulatif dans la console

2. **`compareWithHallOfFame()`**: Compare CA vs Hopfield
   - Entraîne un réseau Hopfield sur les patterns
   - Teste le recall avec bruit pour Hopfield et chaque règle CA
   - Compare avec le même critère de succès (Distance de Hamming ≤ 10%)

3. **`generateMarkdownReport()`**: Génère un rapport
   - Format Markdown prêt à coller dans `memory-ai-lab-results.md`
   - Tables avec toutes les métriques
   - Conclusion automatique sur le gagnant

---

## 🎨 Tests avec patterns personnalisés

Si vous voulez tester avec vos propres patterns:

1. **Aller dans l'onglet "Memory Lab"**
2. **Dessiner 2-3 patterns** dans le canvas 32×32
3. **Cliquer "Add Pattern"** après chaque
4. **Lancer les tests** (même commande console que ci-dessus)

Les tests utiliseront automatiquement VOS patterns au lieu des patterns par défaut.

---

## 📈 Interpréter les résultats

### Recall Rate

- **≥70%** : ✅ OK - La règle a une bonne mémoire
- **40-70%** : ⚠️ Weak - Mémoire modérée
- **<40%** : ❌ Fail - Mémoire faible

### Coverage

Pourcentage de runs qui convergent vers un attracteur dominant (≥5% des runs).
- **≥90%** : Très stable
- **70-90%** : Stable
- **<70%** : Comportement chaotique

### Attracteurs

Nombre moyen d'attracteurs dominants détectés.
- **2-4** : Idéal pour la mémoire (multiple stable states)
- **1** : Trop stable (frozen)
- **>6** : Trop chaotique

### CA vs Hopfield

- **Δ > +5%** : CA meilleur que Hopfield
- **Δ < -5%** : Hopfield meilleur que CA
- **-5% à +5%** : Performances équivalentes

---

## 🔧 Options avancées

```javascript
// Tester avec plus de runs pour plus de précision
const batch = await MemoryLab.runBatchForHallOfFame({ runs: 100 });

// Augmenter le bruit
const batch = await MemoryLab.runBatchForHallOfFame({ noiseLevel: 0.1 });

// Changer le critère de succès (20% de tolérance au lieu de 10%)
const batch = await MemoryLab.runBatchForHallOfFame({ maxDiffRatio: 0.2 });

// Utiliser des patterns spécifiques
const myPatterns = [/* vos patterns */];
const batch = await MemoryLab.runBatchForHallOfFame({ patterns: myPatterns });
```

---

## 🆘 Troubleshooting

### "MemoryLab is not defined"

- Rechargez la page avec Ctrl+Shift+R (vider le cache)
- Vérifiez que vous êtes sur `http://localhost:8001/experiments/memory-ai-lab/index.html`
- Vérifiez dans la console que vous voyez: "✅ Memory AI Lab chargé"

### Les tests ne démarrent pas

- Vérifiez que le serveur est bien lancé: `python -m http.server 8001`
- Vérifiez qu'il n'y a pas d'erreurs 404 dans la console Network tab
- Essayez de taper `MemoryLab` dans la console - ça doit montrer un objet

### Scores à 0% partout

- Normal si les patterns sont trop complexes ou les règles trop chaotiques
- Essayez avec des patterns plus simples (block 2×2, blinker)
- Essayez d'augmenter `maxDiffRatio` à 0.15 ou 0.2

---

## 📚 Accès direct aux APIs

```javascript
// Voir les patterns chargés
MemoryLab.patterns()

// Voir les règles Hall of Fame
MemoryLab.HOF_RULES()
```

