# Prochaines Étapes - Memory AI Lab

**Date**: 08/11/2025  
**Status**: ✅ Projet fonctionnel et stable  
**Branche**: memory-ai-lab

---

## ✅ Ce Qui Fonctionne Maintenant

### APIs Unifiées ✅

**Gestion des patterns centralisée:**
- `attractorUtils.getDefaultPatterns()` → 4 patterns reproductibles (single source of truth)
- `MemoryLab.getCurrentPatterns()` → Patterns dessinés dans l'UI (éphémères)
- **Logique unifiée**: Toutes les APIs (runBatchForHallOfFame, compareWithHallOfFame, scanMemoryCandidates) utilisent le même ordre de priorité:
  1. Patterns fournis explicitement (`options.patterns`)
  2. Patterns UI si disponibles
  3. Patterns par défaut reproductibles

### Tests Automatiques ✅

```javascript
// 1. Test Hall of Fame avec patterns UI si disponibles (~2-3 min)
const batch = await MemoryLab.runBatchForHallOfFame({ noiseLevel: 0.05, steps: 80, runs: 50 });
const comp = await HopfieldLab.compareWithHallOfFame({ noiseLevel: 0.05, runs: 50 });
const report = Reports.generateMarkdownReport(batch, comp);
console.log(report);

// 2. AutoScan pour découvrir candidates (~5-10 min)
await MemoryScanner.scanMemoryCandidates({ 
  noiseLevels: [0.01, 0.03, 0.05, 0.08],
  steps: 160,
  runs: 60
});
```

**Résultats attendus avec les 15 patterns UI:**
- Seeds 1.88 : recall ~60-80%
- B01/S3: recall ~85-95% (meilleure candidate)
- AutoScan devrait trouver 2-3 candidates avec ces 15 patterns

---

## 🚀 Prochaines Étapes Suggérées

### 1. Persistance des Patterns (Haute Priorité)

**Problème actuel:** Les patterns UI sont perdus au reload de la page.

**Solution proposée:**

#### A. LocalStorage (Simple, recommandé)

Ajouter dans `experiments/memory-ai-lab/main.js`:

```javascript
// Sauvegarder patterns dans localStorage
function savePatterns() {
  const patternsData = patterns.map(p => ({
    id: p.id,
    name: p.name,
    grid: Array.from(p.grid),  // Uint8Array → Array pour JSON
    width: p.width,
    height: p.height,
    created: p.created
  }));
  localStorage.setItem('memorylab_patterns', JSON.stringify(patternsData));
  console.log(`💾 ${patterns.length} patterns sauvegardés`);
}

// Charger patterns depuis localStorage
function loadPatterns() {
  try {
    const saved = localStorage.getItem('memorylab_patterns');
    if (saved) {
      const patternsData = JSON.parse(saved);
      patterns = patternsData.map(p => ({
        ...p,
        grid: new Uint8Array(p.grid)  // Array → Uint8Array
      }));
      patternCounter = Math.max(...patterns.map(p => parseInt(p.id.split('_')[1])), 0) + 1;
      updatePatternsList();
      console.log(`📂 ${patterns.length} patterns chargés depuis localStorage`);
      return true;
    }
  } catch (error) {
    console.warn('⚠️ Erreur lors du chargement des patterns:', error);
  }
  return false;
}

// Appeler dans init()
document.addEventListener('DOMContentLoaded', () => {
  // ... existing init code ...
  loadPatterns();  // Charger patterns sauvegardés
});

// Appeler savePatterns() après addPattern() et après suppression
```

**Avantages:**
- Simple à implémenter
- Pas de dépendance externe
- Patterns persistent entre sessions

#### B. Export/Import JSON

Ajouter boutons dans l'UI:
- "Export Patterns" → télécharge JSON
- "Import Patterns" → charge depuis fichier

#### C. Patterns Présets

Créer une bibliothèque de patterns intéressants:
```javascript
const PRESET_PATTERNS = {
  'glider': [...],
  'blinker': [...],
  'pulsar': [...],
  'pentadecathlon': [...],
  // etc.
};
```

---

### 2. Visualisation des Attracteurs (Moyenne Priorité)

**Objectif:** Comprendre visuellement où convergent les runs.

**Implémentation:**

```javascript
// Dans testPattern(), stocker les grilles finales
const attractorGrids = new Map();  // hash → grid
for (let i = 0; i < runs; i++) {
  const noisy = addNoise(pattern.grid, noiseLevel);
  const final = tempEngine.run(noisy, rule, steps);
  const hash = hashGrid(final);
  if (!attractorGrids.has(hash)) {
    attractorGrids.set(hash, final);
  }
  attractorCounts.set(hash, (attractorCounts.get(hash) || 0) + 1);
}

// Retourner les grilles des attracteurs dominants
return {
  // ... existing fields ...
  attractorGrids: dominants.map(a => ({
    hash: a.hash,
    grid: attractorGrids.get(a.hash),
    percentage: a.percentage
  }))
};
```

**UI:**
- Afficher les 3-4 attracteurs dominants sous forme de mini-canvas
- Permettre de voir vers quoi convergent les runs

---

### 3. Courbes Recall vs Noise (Recherche)

**Objectif:** Analyser la robustesse au bruit.

**Implémentation:**

```javascript
async function testRobustness(rule, patterns) {
  const noiseLevels = [0.00, 0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20];
  const results = [];
  
  for (const noise of noiseLevels) {
    const batch = await runBatchForPattern(rule, patterns, { 
      noiseLevel: noise,
      steps: 80,
      runs: 50
    });
    results.push({
      noise,
      recall: batch.avgRecallRate,
      coverage: batch.avgCoverage
    });
  }
  
  return results;
}
```

**Visualisation:**
- Graphique avec Noise (x-axis) vs Recall Rate (y-axis)
- Identifier le "breaking point" de chaque règle

---

### 4. Tests Multi-Pattern (Recherche Avancée)

**Objectif:** Tester les interférences entre patterns.

**Hypothèse:** Les CA peuvent stocker plusieurs patterns simultanément dans des régions différentes de l'espace des phases.

**Implémentation:**

```javascript
async function testMultiPattern(rule, patterns) {
  // Combiner plusieurs patterns dans la même grille
  const multiGrid = new Uint8Array(64 * 64);
  
  // Placer pattern 1 en haut-gauche
  // Placer pattern 2 en haut-droite
  // etc.
  
  // Ajouter bruit
  // Évoluer
  // Vérifier si les différentes régions convergent vers leurs patterns respectifs
}
```

---

### 5. Règles Hybrides CA-Hopfield (Recherche)

**Objectif:** Combiner les forces de CA (dynamiques émergentes) et Hopfield (recall direct).

**Idée:**
1. Entraîner un Hopfield sur patterns
2. Utiliser les poids Hopfield pour créer une règle CA paramétrée
3. Tester cette règle hybride

**Exemple conceptuel:**
```javascript
function createHybridRule(hopfieldWeights, patterns) {
  // Convertir les poids Hopfield en règles CA born/survive
  // Méthode 1: Seuillage des poids
  // Méthode 2: Apprentissage supervisé
  
  return { born: [...], survive: [...] };
}
```

---

### 6. Benchmarking & Comparaison Systématique

**Objectif:** Tableau comparatif complet de toutes les règles testées.

**Métriques à ajouter:**
- Temps de convergence (steps moyens avant stabilisation)
- Variance du recall entre patterns
- Robustesse multi-noise (aire sous la courbe recall/noise)
- Capacité de stockage (max patterns distincts)

**Implémentation:**

```javascript
const benchmark = {
  rule: 'B2456/S078',
  recall: 0.65,
  coverage: 0.92,
  attractors: 3.5,
  convergenceTime: 45,  // steps moyens
  variance: 0.12,       // variance recall entre patterns
  robustness: 0.78,     // score multi-noise
  capacity: 4           // patterns distincts stockables
};
```

---

### 7. Optimisation Performance

**Objectif:** Réduire le temps des tests lourds.

**Pistes:**
- Web Workers pour paralléliser les runs
- WASM pour moteur CA (10-50x plus rapide)
- Cache des attracteurs (si même rule + pattern déjà testé)
- Sampling intelligent (arrêt early si convergence détectée)

---

## 💡 Suggestions d'Amélioration UX

### 1. Indicateur de Progress Détaillé

Remplacer la simple progress bar par:
```
Test en cours: Seed_1.88a (règle 3/7)
Pattern: Glider-like (2/15)
Runs: 35/50 (70%)
Temps restant estimé: ~45s
```

### 2. Sauvegarde Automatique des Résultats

Après chaque batch test:
- Sauvegarder résultats dans localStorage
- Offrir "Download Results (JSON/CSV)" button
- Historique des tests avec timestamps

### 3. Comparaison Visuelle

Split-screen pour comparer:
- Pattern original
- Attractor dominant CA
- Attractor Hopfield
- Différence (heatmap)

### 4. Presets de Configuration

Boutons rapides:
- "Quick Test" (runs=10, steps=40)
- "Standard Test" (runs=50, steps=80)
- "Thorough Test" (runs=100, steps=160)
- "Robustness Test" (multi-noise)

---

## 🔬 Expériences Scientifiques Suggérées

### Expérience 1: Capacité de Stockage

**Question:** Combien de patterns distincts une règle CA peut-elle stocker?

**Protocole:**
1. Générer N patterns aléatoires
2. Pour chaque règle Hall of Fame:
   - Tester recall pour N=2, 4, 8, 16 patterns
   - Mesurer quand le recall commence à dégrader
3. Comparer avec capacité théorique Hopfield (0.138×N neurones)

### Expérience 2: Patterns Complexes

**Question:** Les CA sont-elles meilleures sur patterns distribués/complexes?

**Protocole:**
1. Créer patterns de complexité croissante:
   - Simple: block, blinker
   - Moyen: glider, toad
   - Complexe: spaceship, gun
2. Tester CA vs Hopfield sur chaque niveau
3. Voir si l'avantage Hopfield diminue avec la complexité

### Expérience 3: Dynamiques Temporelles

**Question:** Les attracteurs CA sont-ils des oscillateurs ou des stables?

**Protocole:**
1. Pour chaque attracteur dominant détecté:
   - Le réexécuter pendant 200 steps
   - Détecter la période (stable=1, oscillateur=2+, chaotique=>10)
2. Classifier les attracteurs par type
3. Voir si certaines règles favorisent les oscillateurs

---

## 📊 Résultats Attendus (avec 15 patterns UI)

Basé sur les logs visibles:

**Hall of Fame CA:**
- B2456/S078 (Seed_1.88a): recall ~0%, coverage ~0%, attractors ~0
- B2456/S068 (Seed_1.88b): recall ~0%, coverage ~0%, attractors ~0
- B246/S58: recall ~100%, coverage ~100%, attractors ~0
- B2456/S07: recall ~0%, coverage ~0%, attractors ~0
- B246/S5: recall ~0%, coverage ~0%, attractors ~0
- **B2456/S5 (Mythmaker_1)**: recall ~0%, coverage ~0%, attractors ~0
- **B01/S3 (Mythmaker_2)**: recall ~96.7%, coverage ~91.2%, attractors ~1 ✅

**Observations:**
- B01/S3 clairement la meilleure (>95% recall)
- B246/S58 aussi excellente (100% recall)
- Les Seeds montrent 0% car critère trop strict OU patterns UI non adaptés

**Recommandations:**
1. Vérifier les patterns UI (trop complexes?)
2. Tester Seeds avec patterns simples (block, blinker uniquement)
3. Augmenter maxDiffRatio à 0.15 pour Seeds
4. Les Seeds sont optimisées pour patterns aléatoires 64×64, pas patterns dessinés 32×32

---

## 🎯 Roadmap Court Terme

### Version 1.2 (1-2h de dev)

- [ ] **Persistance LocalStorage** pour patterns
  - savePatterns() / loadPatterns()
  - Auto-save après add/delete
  - Bouton "Clear All Patterns"

- [ ] **Export/Import JSON**
  - downloadPatterns()
  - importPatterns(file)
  - Format JSON standard

- [ ] **Presets de Patterns**
  - Bibliothèque 10-15 patterns classiques
  - Boutons "Load Preset: Glider", "Load Preset: Pulsar", etc.

### Version 1.3 (2-4h de dev)

- [ ] **Visualisation Attracteurs**
  - Afficher top 3-4 attracteurs dominants
  - Mini-canvas pour chaque
  - Clic pour voir détails

- [ ] **Progress Détaillé**
  - Règle en cours
  - Pattern en cours
  - Temps estimé restant

- [ ] **Historique des Tests**
  - Sauvegarder chaque batch test
  - Voir tests précédents
  - Comparer avec tests actuels

### Version 2.0 (Recherche)

- [ ] **Courbes Robustesse**
  - testRobustness() API
  - Graphiques recall vs noise
  - Identification breaking points

- [ ] **Tests Multi-Pattern**
  - Interférences entre patterns
  - Capacité de stockage
  - Comparaison avec Hopfield théorique

- [ ] **Règles Hybrides CA-Hopfield**
  - Apprendre règles CA depuis poids Hopfield
  - Tester ces règles hybrides
  - Publier résultats

---

## 🐛 Bugs Connus & Limitations

### 1. Seeds 1.88 montrent 0% recall

**Cause possible:**
- Critère trop strict (Hamming ≤ 10%)
- Patterns UI trop complexes/distribués
- Seeds optimisées pour grilles 64×64, pas 32×32

**Solutions:**
- Tester Seeds avec patterns simples uniquement
- Augmenter tolérance à 15-20% pour Seeds
- Ou accepter que Seeds ne sont pas adaptées aux petits patterns dessinés

### 2. Patterns non reproductibles entre runs

**Cause:** Patterns UI incluent des patterns "random" différents à chaque dessin.

**Solution:** Utiliser patterns par défaut pour tests officiels (déjà implémenté).

### 3. AutoScan long (5-10 min)

**Normal** pour 25 règles × 4 niveaux × 60 runs × 4 patterns.

**Optimisations possibles:**
- Réduire runs à 40 pour scan exploratoire
- Paralléliser avec Web Workers
- Caching des résultats intermédiaires

---

## 📝 Checklist Avant Fusion vers Main

- [ ] Les deux URLs fonctionnent sans erreur (Ising Life Lab + Memory AI Lab)
- [ ] Tous les boutons ont des handlers (aucun clic silencieux)
- [ ] API console documentée et fonctionnelle
- [ ] Documentation à jour (README, PRD, Quick Start)
- [ ] Pas de fichiers vides ou cassés
- [ ] Commits propres et descriptifs
- [ ] Tests manuels OK sur Chrome/Firefox

---

## 🎓 Contributions Futures

### Papier / Publication

**Titre suggéré:** "Memory Capacity of Life-like Cellular Automata: A Comparison with Hopfield Networks"

**Sections:**
1. Introduction (CA vs Hopfield pour mémoire)
2. Méthodologie (protocole de test, critères)
3. Hall of Fame (Seeds 1.88, B01/S3, etc.)
4. Résultats (recall rates, comparaisons)
5. Discussion (quand CA > Hopfield, pourquoi)
6. Conclusion (CA comme alternative aux réseaux de neurones)

### Dataset Public

Créer un dataset des résultats:
- 7 règles Hall of Fame × 100 patterns variés
- Multi-noise (5 niveaux)
- Format CSV + JSON
- Publier sur Zenodo/GitHub

### Outil Interactif

Version web publique:
- Hébergé sur GitHub Pages
- Interface complète
- Exemples de patterns
- Tutoriel intégré

---

## 🤝 Besoin d'Aide?

**Pour développement:**
- Issues sur GitHub
- Documentation dans `/docs`
- Code commenté

**Pour recherche:**
- Voir `memory-results-extreme.md` pour méthodologie
- PRD pour objectifs scientifiques
- Contact: [À remplir]

---

**Dernière mise à jour**: 08/11/2025  
**Version**: 1.1 (AutoScan implemented)  
**Prochaine version prévue**: 1.2 (Persistence)

