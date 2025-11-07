# Memory AI Lab - Architecture

## Vue d'ensemble

Le Memory AI Lab est une page expérimentale autonome située dans `experiments/memory-ai-lab/` qui permet de tester et comparer les capacités de mémoire des règles CA du Hall of Fame avec les réseaux de Hopfield classiques.

## Structure

```
experiments/memory-ai-lab/
├── index.html          # Page principale avec 3 onglets
├── styles.css          # Styles (thème sombre)
├── main.js             # Point d'entrée et orchestration
├── ca/
│   └── engine.js       # Moteur CA torique optimisé
├── memory/
│   └── attractorUtils.js   # Utilitaires: hash, bruit, distance Hamming, attracteurs
├── hopfield/
│   └── hopfield.js     # Réseau de Hopfield binaire (règle de Hebb)
└── viz/
    ├── canvas.js       # Renderer Canvas pour CA
    └── ui.js           # Composants UI (tableaux, progress bars)
```

## Réutilisation du code existant

- **Hall of Fame rules**: Importées depuis `../../src/presets/rules.js`
- **Pas de duplication**: Les règles sont maintenues en un seul endroit
- **Module ES6**: Imports relatifs standards

## Fonctionnalités

### 1. CA Playground

- Grille 64×64 avec règles du Hall of Fame uniquement
- Contrôles: Start, Stop, Step, Random, Clear
- Métriques temps réel: FPS, Step, Population
- Sélecteur de règles avec les 7 règles du Hall of Fame

### 2. Memory Lab

#### Éditeur de patterns
- Canvas 32×32 éditable au clic
- Grille visible pour faciliter le dessin
- Boutons Add Pattern et Clear

#### Tests de mémoire
- Configuration:
  - Règle (Hall of Fame)
  - Noise Level (0-0.3, défaut 0.05)
  - Steps (10-200, défaut 80)
  - Runs (10-100, défaut 50)
  
- Processus:
  1. Pour chaque pattern sauvegardé
  2. Pour chaque run:
     - Ajouter du bruit au pattern
     - Évoluer avec la règle CA pendant N steps
     - Calculer le hash de l'état final
  3. Détecter les attracteurs dominants (≥5% des runs)
  4. Calculer recall rate (% vers attracteur dominant) et coverage (% vers attracteurs ≥5%)

#### Résultats
- Tableau avec: Pattern, Rule, Recall Rate, Status, Attractors, Coverage
- Status: OK (≥70%), Weak (40-70%), Fail (<40%)
- Résumé global: moyennes et nombre de patterns testés

### 3. Hopfield Comparison

#### Entraînement
- Réseau de Hopfield binaire (0/1)
- Règle de Hebb: w_ij = (1/N) Σ(2p_i - 1)(2p_j - 1)
- Entraîné sur tous les patterns du Memory Lab

#### Test et comparaison
- Même protocole que Memory Lab pour CA
- Pour Hopfield: rappel asynchrone (max 100 itérations)
- Succès si distance de Hamming < 5% de la taille du pattern
- Tableau comparatif: Pattern, Hopfield Recall, CA Recall, Winner, Δ
- Résumé: moyennes et identification du gagnant

## Workflow utilisateur

1. **Lancer le serveur**:
   ```bash
   cd ising-life-lab  # racine du repo
   python -m http.server 8001
   ```

2. **Accéder à Memory AI Lab**:
   ```
   http://localhost:8001/experiments/memory-ai-lab/index.html
   ```

3. **Tester la mémoire**:
   - Onglet Memory Lab
   - Dessiner 2-3 patterns simples (glider, blinker, etc.)
   - Cliquer "Add Pattern" après chaque
   - Configurer: Noise 0.05, Steps 80, Runs 50
   - Cliquer "Run Memory Test"
   - Observer recall rate et attracteurs

4. **Comparer avec Hopfield**:
   - Onglet Hopfield Comparison
   - Cliquer "Run Comparison"
   - Observer quel modèle a le meilleur recall rate

## Performance

- CA step: < 5ms pour 64×64
- Memory test (3 patterns × 50 runs): < 30s
- Hopfield recall: < 100ms par pattern
- Interface fluide, pas de blocage UI

## Limites

- Patterns limités à 32×32 pour des raisons de performance
- Tous les patterns doivent avoir la même taille pour Hopfield
- Seeds aléatoires non fixées → variance dans les résultats (±5%)

## Prochaines étapes

- Support de patterns de tailles variables
- Export/import de patterns au format JSON
- Visualisation des attracteurs dominants
- Tests avec patterns plus complexes
- Analyse de la robustesse au bruit (courbe recall rate vs noise level)

