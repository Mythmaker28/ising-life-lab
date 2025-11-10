# Fondements Théoriques et Définitions Mathématiques

Ce document définit **précisément** les métriques utilisées dans Ising Life Lab. Aucun nombre mystique, aucune "boîte noire".

## 1. Automates Cellulaires (CA)

### 1.1 Définition

Un automate cellulaire est un tuple $(L, S, N, f)$ où:
- $L$: Lattice (grille) de dimension $d$ (ici $d=1$ ou $d=2$)
- $S$: Ensemble fini d'états (ici $S = \{0, 1\}$)
- $N$: Voisinage (ex: von Neumann, Moore)
- $f: S^{|N|} \to S$: Fonction de transition locale

### 1.2 Règles Élémentaires (1D)

Pour $d=1$ avec voisinage $\{-1, 0, +1\}$:
- Nombre de configurations: $2^3 = 8$
- Nombre de règles: $2^8 = 256$

**Encodage de Wolfram**: Une règle $R \in [0, 255]$ est représentée en binaire:

$$R = \sum_{i=0}^{7} b_i \cdot 2^i$$

où $b_i = f(i_2, i_1, i_0)$ et $(i_2, i_1, i_0)$ est la représentation binaire de $i$.

**Exemple: Règle 30**
- Binaire: `00011110`
- Table:
  ```
  111 110 101 100 011 010 001 000
   0   0   0   1   1   1   1   0
  ```

### 1.3 Règles Life-like (2D)

Voisinage de Moore (8 voisins). Une règle est définie par:
- $B \subseteq \{0, 1, ..., 8\}$: conditions de naissance
- $S \subseteq \{0, 1, ..., 8\}$: conditions de survie

**Notation**: B{birth}/S{survival}

**Exemple: Conway's Life = B3/S23**
- Une cellule morte naît si exactement 3 voisins vivants
- Une cellule vivante survit si 2 ou 3 voisins vivants

**Encodage**: $R = \sum_{b \in B} 2^b + \sum_{s \in S} 2^{s+9}$

## 2. Modèle d'Ising

### 2.1 Hamiltonien

$$H = -J \sum_{\langle i,j \rangle} s_i s_j - h \sum_i s_i$$

où:
- $s_i \in \{-1, +1\}$: spins
- $J$: constante de couplage ($J > 0$ ferromagnétique)
- $h$: champ magnétique externe
- $\langle i,j \rangle$: paires de voisins

### 2.2 Dynamiques de Monte Carlo

**Glauber (heat bath)**:

$$P(\text{flip}) = \frac{1}{1 + e^{\beta \Delta E}}$$

**Metropolis**:

$$P(\text{flip}) = \min(1, e^{-\beta \Delta E})$$

où $\beta = 1/(k_B T)$ et $\Delta E = E_{\text{après}} - E_{\text{avant}} = 2 H_{\text{local}}$.

### 2.3 Transition de Phase

Pour Ising 2D, transition de phase à température critique:

$$T_c \approx \frac{2J}{k_B \ln(1 + \sqrt{2})} \approx 2.269 J/k_B$$

## 3. Métriques Quantitatives

### 3.1 Entropie de Shannon

Pour un ensemble d'états $\{x_1, ..., x_n\}$:

$$H(X) = -\sum_{x \in \mathcal{X}} p(x) \log_2 p(x)$$

**Implémentation**: `isinglab/metrics/entropy.py::shannon_entropy`

- États binaires: $H \in [0, 1]$ bit
- $H = 0$: tous les bits identiques (ordre maximal)
- $H = 1$: distribution uniforme $p(0) = p(1) = 0.5$

### 3.2 Entropie Spatiale

Basée sur les blocs $k \times k$ (ici $k=2$ par défaut):

$$H_{\text{spatial}} = -\sum_{b \in \text{blocks}} p(b) \log_2 p(b)$$

Normalisée par $\log_2(\min(2^{k^2}, N_{\text{blocks}}))$.

**Interprétation**:
- $H_{\text{spatial}} \approx 0$: motifs répétitifs (cristal)
- $H_{\text{spatial}} \approx 1$: haute diversité de motifs

### 3.3 Sensibilité (Distance de Hamming)

Pour deux états $s_1, s_2 \in \{0,1\}^N$:

$$d_H(s_1, s_2) = \frac{1}{N} \sum_{i=1}^N \mathbb{1}[s_1^{(i)} \neq s_2^{(i)}]$$

**Sensibilité aux conditions initiales**:

$$\text{sensitivity}(t) = \mathbb{E}[d_H(s_t, s'_t)]$$

où $s'_0$ est une perturbation de $s_0$ ($\epsilon N$ bits flippés, $\epsilon \ll 1$).

**Implémentation**: `isinglab/metrics/sensitivity.py::hamming_sensitivity`

### 3.4 Exposant de Lyapunov (Discret)

$$\lambda = \lim_{t \to \infty} \frac{1}{t} \log \frac{d_H(s_t, s'_t)}{d_H(s_0, s'_0)}$$

**Interprétation**:
- $\lambda < 0$: comportement stable (attracteur)
- $\lambda \approx 0$: edge-of-chaos
- $\lambda > 0$: chaos (divergence exponentielle)

**Implémentation**: `isinglab/metrics/sensitivity.py::lyapunov_exponent`

**Limitation**: Pour systèmes discrets, $\lambda$ est une approximation. La divergence sature à $d_H = 0.5$.

### 3.5 Score de Mémoire

**Détection de Cycle**:

Un cycle de période $p$ existe si $\exists t_0, p > 0$ tel que:

$$s_{t_0} = s_{t_0 + p} = s_{t_0 + 2p} = ...$$

**Score de Mémoire**:

$$\text{memory\_score} = \text{stability} \times (1 - 0.5 \cdot \text{period\_penalty}) \times (0.5 + 0.5 \cdot \text{convergence})$$

où:
- $\text{stability} = 1 - \frac{t_{\text{transient}}}{t_{\text{total}}}$
- $\text{period\_penalty} = \min(p / p_{\max}, 1)$
- $\text{convergence} = 1 - \frac{t_{\text{transient}}}{t_{\text{total}}}$

**Valeurs**:
- $\text{memory\_score} = 1$: point fixe immédiat
- $\text{memory\_score} \approx 0.5-0.7$: cycle limite stable
- $\text{memory\_score} \approx 0$: comportement chaotique, pas d'attracteur

**Implémentation**: `isinglab/metrics/memory.py::memory_score`

### 3.6 Niveau d'Activité

$$\text{activity} = \frac{1}{N} \sum_{i=1}^N s_i$$

Pour $s_i \in \{0, 1\}$: fraction de 1s.  
Pour $s_i \in \{-1, +1\}$: mappé à $[0, 1]$ via $(s_i + 1)/2$.

### 3.7 Score Edge-of-Chaos (Composite)

$$\text{edge\_score} = \left( T_{\text{entropy}} \times T_{\text{sensitivity}} \times T_{\text{memory}} \times T_{\text{activity}} \right)^{1/4}$$

où chaque terme $T_x$ est une fonction en cloche (gaussienne) centrée sur une valeur "optimale":

**Terme d'Entropie**:

$$T_{\text{entropy}} = \exp\left( -\frac{(H_{\text{norm}} - \mu_H)^2}{2\sigma_H^2} \right)$$

avec $\mu_H = 0.5$, $\sigma_H = 0.2$ (élargi de 0.1 pour accepter plus de variabilité).

**Terme de Sensibilité**:

$$T_{\text{sensitivity}} = \exp\left( -\frac{(\text{sens} - \mu_s)^2}{2\sigma_s^2} \right)$$

avec $\mu_s = 0.3$, $\sigma_s = 0.15$.

**Terme de Mémoire**:

$$T_{\text{memory}} = \exp\left( -\frac{(m - \mu_m)^2}{2\sigma_m^2} \right)$$

avec $\mu_m = 0.5$, $\sigma_m = 0.25$. Utilise gaussienne (comme autres termes) pour éviter d'annuler règles chaotiques ($m=0$).

**Terme d'Activité**:

$$T_{\text{activity}} = \exp\left( -\frac{(a - \mu_a)^2}{2\sigma_a^2} \right)$$

avec $\mu_a = 0.3$, $\sigma_a = 0.2$.

**Justification de la moyenne géométrique**:

La racine 4ème de produit (moyenne géométrique) assure qu'**aucun** terme ne peut être ignoré. Si un seul terme est nul, le score final est nul. Cela force un équilibre entre les quatre dimensions.

**Implémentation**: `isinglab/metrics/edge_score.py::edge_of_chaos_score`

### 3.8 Paramètre λ de Langton

**Définition théorique**: Pour une règle CA avec table de transition $f$:

$$\lambda = \frac{|Q - Q_{\text{quiescent}}|}{|Q|}$$

où $Q$ est l'ensemble de toutes les transitions et $Q_{\text{quiescent}}$ les transitions vers l'état quiescent.

**Empiriquement**: $\lambda \approx 0.45-0.55$ correspond à edge-of-chaos.

**Estimation dynamique**:

Puisque calculer $\lambda$ exactement nécessite la table de règles complète, nous **estimons**:

$$\hat{\lambda} = \text{activity} \times (1 + \text{variability})$$

où $\text{variability} = \sigma(\text{activity}(t))$.

**Note**: Cette estimation est **heuristique**. Pour une analyse rigoureuse, il faut analyser la table de règles.

**Implémentation**: `isinglab/metrics/edge_score.py::lambda_parameter_estimate`

**STATUS**: EXPERIMENTAL. Marqué comme approximation dans la documentation.

## 4. Justification des Valeurs "Optimales"

### 4.1 Pourquoi Entropie = 0.5?

L'edge-of-chaos n'est ni ordre parfait ($H=0$) ni désordre maximal ($H=1$). La valeur $0.5$ est un compromis empirique basé sur:

- Règle 110 (Turing-complète): $H \approx 0.4-0.6$
- Règle 30 (chaotique): $H \approx 0.8-1.0$
- Règle 0 (ordre): $H \approx 0$

### 4.2 Pourquoi Sensibilité = 0.3?

- Trop faible ($< 0.1$): système gelé, pas de propagation d'information
- Trop élevée ($> 0.5$): chaos, information non-conservable
- Optimal ($\approx 0.2-0.4$): propagation + stabilité partielle

### 4.3 Pourquoi Mémoire = 0.4-0.7?

- $m = 1$ (point fixe immédiat): trivial, pas intéressant
- $m \approx 0.5-0.7$ (cycle court): comportement répétitif mais non-trivial
- $m \approx 0$ (pas d'attracteur): pas de "mémoire" extractable

### 4.4 Pourquoi Activité = 0.3?

Empiriquement:
- Règles intéressantes ont souvent $20-40\%$ de cellules actives
- Trop bas ($< 0.1$): la plupart meurt rapidement
- Trop haut ($> 0.5$): saturation, peu de structure

**Important**: Ces valeurs sont des **guides heuristiques**, pas des vérités absolues. Elles peuvent être ajustées selon le contexte scientifique.

## 5. Limitations et Incertitudes

### 5.1 Finite-Size Effects

Toutes les métriques dépendent de la taille de grille $N$. Pour $N$ petit:
- Entropie sous-estimée
- Cycles artificiels dus aux conditions aux bords
- Sensibilité peut saturer rapidement

**Recommandation**: $N \geq 100$ pour 1D, $N \times N \geq 50 \times 50$ pour 2D.

### 5.2 Finite-Time Effects

Les métriques convergent avec le temps $T$:
- Attracteurs longs nécessitent $T$ grand
- Exposant de Lyapunov: convergence lente

**Recommandation**: $T \geq 200$ pour analyse, $T \geq 500$ pour mémoire.

### 5.3 Stochasticité (Ising)

Le modèle d'Ising est **stochastique**. Les métriques fluctuent entre runs.

**Solution**: Moyenner sur $n_{\text{seeds}} \geq 3$ seeds différents.

### 5.4 λ de Langton Approximatif

Notre estimation de $\lambda$ est **heuristique**. Pour un calcul exact:

$$\lambda_{\text{exact}} = \frac{1}{2^{|N|}} \sum_{\text{configs}} \mathbb{1}[f(\text{config}) \neq \text{quiescent}]$$

ce qui nécessite énumération exhaustive ($2^8 = 256$ pour CA élémentaires, faisable, mais $2^9$ pour Life-like, plus coûteux).

**TODO**: Implémenter calcul exact pour règles élémentaires.

## 6. Connexion avec la Théorie

### 6.1 Classes de Wolfram

Wolfram (1984) classifie les CA en 4 classes:

| Classe | Comportement | Métriques Typiques |
|--------|--------------|-------------------|
| I | Uniformité | $H \approx 0$, $m \approx 1$ |
| II | Structures simples | $H \approx 0.2-0.4$, $m \approx 0.6-0.8$ |
| III | Chaos | $H \approx 0.8-1.0$, $\lambda > 0$ |
| IV | Complexité (edge-of-chaos) | $H \approx 0.4-0.6$, $\lambda \approx 0$, $m \approx 0.4-0.6$ |

Notre `edge_score` vise à maximiser Classe IV.

### 6.2 Transition de Phase Ising

À $T = T_c$:
- Longueur de corrélation diverge: $\xi \to \infty$
- Fluctuations critiques (edge-of-chaos naturel)
- Sensibilité maximale aux conditions initiales

Notre framework devrait détecter $T_c$ via pic de `edge_score`.

**Validation possible**: Scanner $T \in [1.5, 3.0]$ pour Ising 2D, vérifier pic à $T \approx 2.27$.

## 7. Références Mathématiques

1. **Shannon, C. E.** (1948). "A Mathematical Theory of Communication". *Bell System Technical Journal*.

2. **Ott, E.** (2002). "Chaos in Dynamical Systems". Cambridge University Press.

3. **Langton, C. G.** (1990). "Computation at the edge of chaos: Phase transitions and emergent computation". *Physica D*, 42(1-3), 12-37.

4. **Packard, N. H.** (1988). "Adaptation toward the edge of chaos". *Dynamic Patterns in Complex Systems*, 293-301.

5. **Cipra, B. A.** (1987). "An introduction to the Ising model". *American Mathematical Monthly*, 94(10), 937-959.

6. **Wolfram, S.** (2002). "A New Kind of Science". Wolfram Media.

## 8. Formules Récapitulatives

| Métrique | Formule | Plage | Optimal (edge) |
|----------|---------|-------|----------------|
| Entropie Shannon | $-\sum p_i \log_2 p_i$ | $[0, 1]$ | $\approx 0.5$ |
| Sensibilité | $\mathbb{E}[d_H(s_t, s'_t)]$ | $[0, 0.5]$ | $\approx 0.3$ |
| Mémoire | $(1 - t_{\text{trans}}/T)(1 - 0.5p/p_{\max})...$ | $[0, 1]$ | $\approx 0.5-0.7$ |
| Activité | $\frac{1}{N}\sum s_i$ | $[0, 1]$ | $\approx 0.3$ |
| Edge Score | $(T_H T_s T_m T_a)^{1/4}$ | $[0, 1]$ | $\approx 1$ |

**Transparence**: Toutes les formules sont implémentées telles quelles dans le code. Pas de normalisation cachée.

