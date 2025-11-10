# Hypothèses et Choix de Conception

Ce document liste explicitement les **hypothèses**, **simplifications**, et **choix arbitraires** faits dans ce laboratoire. Transparence totale.

## 1. Hypothèses Scientifiques

### 1.1 Edge-of-Chaos et Computation

**Hypothèse**: Les systèmes opérant au "bord du chaos" présentent une capacité computationnelle maximale.

**Base**: Travaux de Langton (1990), Packard (1988), Mitchell et al. (1993).

**Limites**:
- Principalement démontré pour règles CA spécifiques (ex: règle 110)
- Définition de "edge-of-chaos" reste floue (multiple métriques possibles)
- Lien avec computation universelle pas toujours clair

**Notre position**: Nous utilisons cette hypothèse comme **guide heuristique**, pas comme vérité absolue. Les métriques sont conçues pour tester cette hypothèse, pas la confirmer a priori.

### 1.2 Quantification de la Mémoire

**Hypothèse**: Les attracteurs (points fixes, cycles limites) constituent une forme de "mémoire" dans les systèmes dynamiques.

**Justification**: Un système qui revient de manière fiable à un état (ou cycle d'états) "se souvient" de cet état.

**Limites**:
- Différent de la mémoire au sens information-théorique (capacité de stockage)
- Ne capture pas la mémoire non-Markovienne (histoire longue)
- Points fixes triviaux (tous 0, tous 1) ont mémoire maximale mais ne sont pas intéressants

**Notre approche**: `memory_score` pénalise les attracteurs triviaux et favorise cycles courts stables.

### 1.3 Analogie Ising ↔ Biologie

**Hypothèse (faible)**: Le modèle d'Ising classique capture certains aspects de systèmes biologiques (spins = états on/off de molécules/gènes).

**Base**: Modèles de Hopfield (réseaux neuronaux), modèles de régulation génétique (boolean networks).

**Limites majeures**:
- Biologie est continue, stochastique, hors-équilibre
- Pas de quantum (pour vrais qubits biologiques)
- Topologie de réseau simplifiée (grille régulière ≠ réseaux biologiques)

**Notre position**: Ising est un **modèle jouet** pour intuitions, pas une description réaliste de biologie.

## 2. Choix de Métriques

### 2.1 Valeurs "Optimales" pour Edge-of-Chaos

| Métrique | Valeur Optimale | Justification |
|----------|-----------------|---------------|
| Entropie | 0.5 | Compromis ordre/désordre |
| Sensibilité | 0.3 | Empirique (règles connues) |
| Mémoire | 0.5-0.7 | Attracteurs non-triviaux |
| Activité | 0.3 | Empirique (règles intéressantes) |

**Important**: Ces valeurs sont **heuristiques**, basées sur:
- Analyse de règles CA connues (30, 110, 150, etc.)
- Intuition physique (ni gelé ni chaotique)
- Ajustement empirique

**Elles peuvent être modifiées** selon le contexte scientifique.

### 2.2 Moyenne Géométrique pour Edge Score

**Choix**: $\text{edge\_score} = (T_1 \times T_2 \times T_3 \times T_4)^{1/4}$

**Alternative**: Moyenne arithmétique $(\frac{1}{4} \sum T_i)$ ou pondérée.

**Justification du choix**:
- Moyenne géométrique pénalise fortement les déséquilibres (si un terme = 0, score = 0)
- Force un "équilibre" entre les quatre dimensions
- Correspond à l'idée de "bord" (balance entre extrêmes)

**Limitation**: Très sensible aux termes faibles. Une règle excellente sur 3 dimensions mais nulle sur 1 aura score nul.

### 2.3 Normalisation des Entropies

**Choix**: Diviser par $\log_2(\text{max\_states})$ pour normaliser à $[0, 1]$.

**Alternatives**:
- Utiliser entropie absolue (bits)
- Normaliser par entropie de distribution uniforme empirique

**Justification**: Normalisation à $[0, 1]$ facilite comparaisons entre différents types de systèmes.

**Limitation**: Perd information sur échelle absolue.

## 3. Choix d'Implémentation

### 3.1 Conditions aux Bords

**Choix par défaut**: Périodiques (toroïdales)

**Alternatives**: Fixes, réflectives, ouvertes.

**Justification**:
- Périodiques minimisent artefacts de bord
- Cohérent avec physique statistique (thermodynamique limite)

**Limitation**: Ne correspond pas à systèmes biologiques réels (frontières ouvertes).

### 3.2 Tailles de Grille

**Défaut**: 100 (1D), 100×100 (2D)

**Justification**:
- Compromis vitesse/précision
- Suffisant pour capturer comportements génériques
- Comparable à littérature CA

**Limitation**: Effets de taille finie (finite-size effects) présents. Pour certaines règles, $N \to \infty$ nécessaire pour comportement asymptotique.

### 3.3 Durée d'Évolution

**Défaut**: 200-500 pas

**Justification**:
- Suffisant pour atteindre attracteurs simples (période < 100)
- Permet transient + régime stable
- Temps de calcul raisonnable

**Limitation**: Attracteurs très longs (période > 500) non détectés. Systèmes à convergence lente mal caractérisés.

### 3.4 Seed pour Initialisation

**Choix**: Initialisation aléatoire uniforme avec seed contrôlé

**Alternative**: Initialisation structurée (ex: seul pixel central actif)

**Justification**:
- Aléatoire = test robustesse à conditions initiales
- Seed = reproductibilité

**Limitation**: Comportement peut dépendre fortement de condition initiale (bassins d'attraction multiples).

## 4. Simplifications Algorithmiques

### 4.1 Détection de Cycles Simplifiée

**Méthode**: Comparaison exacte d'états (hashage)

**Limitation**: Ne détecte pas cycles "approchés" ou quasi-périodicité.

**Conséquence**: Peut rater comportements complexes (strange attractors discrets).

### 4.2 Lyapunov Discret

**Méthode**: $\lambda \approx \frac{1}{t} \log \frac{d_H(t)}{d_H(0)}$

**Limitation**: Pour systèmes discrets, divergence sature à $d_H = 0.5$. Exposant de Lyapunov mal défini.

**Notre approche**: Utilisé comme **proxy** de sensibilité, pas comme vraie mesure de chaos.

### 4.3 Estimation λ de Langton

**Méthode**: $\hat{\lambda} = \text{activity} \times (1 + \text{variability})$

**Statut**: **EXPÉRIMENTAL**. Heuristique non-validée.

**Justification**: Calcul exact nécessite table de règles complète (énumération coûteuse pour grandes tables).

**Limitation**: Corrélation avec vrai $\lambda$ non établie rigoureusement.

## 5. Hypothèses Computationnelles

### 5.1 Déterminisme des CA

**Hypothèse**: CA sont déterministes (même IC + règle → même évolution)

**Exception**: Ising (Monte Carlo stochastique), contrôlé par seed.

**Justification**: Reproductibilité.

### 5.2 Pas d'Interactions Non-Locales

**Hypothèse**: Voisinage local uniquement (Moore, von Neumann)

**Limitation**: Systèmes biologiques ont interactions long-range (diffusion, signalisation).

**Notre position**: Modèle simplifié. Extensions possibles (CA avec voisinage étendu).

### 5.3 États Discrets

**Hypothèse**: États binaires ($\{0, 1\}$) ou spins ($\{-1, +1\}$)

**Limitation**: Biologie est continue (concentrations, conformations).

**Extension possible**: CA multi-états ou continuous CA (nécessite refonte métriques).

## 6. Limites de Généralisation

### 6.1 Types de CA Supportés

**Actuellement**: Élémentaires (1D), Life-like (2D)

**Non-supportés**: Totalistic généraux, asynchrones, probabilistes, anisotropes

**Raison**: Complexité implémentation vs bénéfice incertain.

**Extensibilité**: Architecture permet ajout futur.

### 6.2 Métriques Binaires

**Limitation**: Toutes les métriques supposent états discrets.

**Systèmes continus**: Nécessitent adaptations (ex: entropie différentielle).

### 6.3 Dynamiques Hors-Équilibre

**Ising**: Implémentation actuelle = Monte Carlo thermodynamique (convergence vers équilibre).

**Limitation**: Pas de dynamiques ballistiques, réactives, etc.

## 7. Choix Non-Justifiés (Arbitraires)

Certains choix sont **arbitraires** (conventions):

1. **Logarithme base 2**: Convention (bits). Base $e$ (nats) aussi valide.

2. **Gaussiennes pour termes edge_score**: Forme de cloche intuitive. Autres fonctions (Lorentzienne, etc.) possibles.

3. **Poids égaux des 4 termes**: Moyenne géométrique non-pondérée. Pondération possible selon objectif.

4. **Seuils de période max (100)**: Arbitraire. Dépend du temps de calcul acceptable.

5. **Nombre de graines par défaut (3)**: Compromis statistique vs vitesse. Plus robuste avec 10+.

## 8. Incertitudes Théoriques

### 8.1 Définition Universelle d'Edge-of-Chaos

**Problème**: Pas de définition mathématique rigoureuse universellement acceptée.

**Approches existantes**:
- Paramètre $\lambda$ de Langton
- Exposant de Lyapunov $\approx 0$
- Maximisation capacité computationnelle (flou)
- Criticalité auto-organisée (SOC)

**Notre approche**: Métrique composite multi-dimensionnelle. **Expérimental**.

### 8.2 Lien Computation ↔ Edge-of-Chaos

**Théorème non-prouvé**: "Edge-of-chaos maximise computation"

**Contre-exemples possibles**: Règles chaotiques mais Turing-complètes ? Règles ordonnées avec computation ?

**Notre position**: Hypothèse de travail, à tester empiriquement.

## 9. Décisions de Design Justifiées

### 9.1 API sans État

**Choix**: Fonctions pures, pas de variables globales

**Justification**:
- Reproductibilité
- Parallélisabilité
- Facilité de test
- AI-friendly

**Coût**: Léger overhead (réinitialisation moteurs)

### 9.2 Séparation Core / Metrics / Search

**Choix**: Architecture modulaire

**Justification**:
- Testabilité indépendante
- Réutilisabilité (métriques applicables à autres systèmes)
- Clarté conceptuelle

### 9.3 Documentation Exhaustive

**Choix**: 4 documents détaillés (README_LAB, THEORETICAL_FOUNDATION, AI_AGENT_GUIDE, CONNECTIONS)

**Justification**:
- Transparence scientifique
- Accessibilité pour futurs utilisateurs (humains et IA)
- Traçabilité des choix

## 10. Révisions Futures Prévues

### Court Terme

- [ ] Calcul exact de $\lambda$ Langton pour CA élémentaires
- [ ] Tests unitaires complets (pytest)
- [ ] Validation sur règles CA connues (30, 110, etc.)

### Moyen Terme

- [ ] Support CA totalistic généraux
- [ ] Ising 3D
- [ ] Métriques pour systèmes continus
- [ ] Parallélisation native (Dask/Ray)

### Long Terme

- [ ] Intégration avec arrest-molecules
- [ ] Benchmarks sur données biologiques réelles
- [ ] Amélioration définition edge-of-chaos basée sur résultats empiriques

## Conclusion

Ce laboratoire fait des **choix explicites et transparents**. Certains sont solidement justifiés, d'autres sont heuristiques ou arbitraires. **Aucune prétention de vérité absolue**.

Les utilisateurs (humains ou IA) doivent **comprendre ces limites** et adapter les métriques à leurs contextes spécifiques.

**Principe fondamental**: Transparence > Perfection.

