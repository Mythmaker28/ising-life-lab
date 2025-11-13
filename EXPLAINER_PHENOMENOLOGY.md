# Phénoménologie Computationnelle : Le "Photoshop des Qualia"

## Vue d'ensemble

Ce document explique la théorie et l'implémentation du moteur d'oscillateurs de phase comme modèle computationnel des états phénoménologiques.

**Hypothèse centrale** : Les états de conscience altérés peuvent être modélisés comme des champs d'oscillateurs couplés, dont les défauts topologiques quantifient la fragmentation/unification perceptuelle.

---

## 1. Fondements théoriques

### 1.1 Modèle de Kuramoto

Le modèle de Kuramoto décrit la synchronisation d'oscillateurs couplés :

$$\frac{d\theta_i}{dt} = \omega_i + \sum_{j} K_{ij} \sin(\theta_j - \theta_i) + \eta_i(t)$$

**Composantes** :
- $\theta_i \in [0, 2\pi)$ : Phase de l'oscillateur $i$
- $\omega_i$ : Fréquence naturelle
- $K_{ij}$ : Force de couplage (peut être multi-échelle)
- $\eta_i(t)$ : Bruit stochastique

### 1.2 Paramètre d'ordre

La cohérence globale est mesurée par le paramètre d'ordre complexe :

$$r e^{i\psi} = \frac{1}{N} \sum_{j=1}^{N} e^{i\theta_j}$$

**Interprétation** :
- $r \approx 1$ : Synchronisation complète (uniformité)
- $r \approx 0$ : Phases désordonnées (fragmentation)

### 1.3 Défauts topologiques

Les défauts sont des singularités du champ de phase. Le **Winding Number** mesure la charge topologique :

$$W = \frac{1}{2\pi} \oint_{\partial \Omega} \nabla\theta \cdot d\mathbf{l}$$

**Types de défauts** :
- $W = +1$ : Vortex
- $W = -1$ : Anti-vortex
- $W = 0$ : Pas de défaut

**Dynamique** :
- Les paires vortex/anti-vortex peuvent s'**annihiler** (fusion)
- Les défauts peuvent être **créés** par instabilités
- La **densité de défauts** caractérise le régime

---

## 2. Hypothèse phénoménologique

### 2.1 Carte conceptuelle

| État phénoménologique | Paramètre d'ordre $r$ | Densité de défauts | Dynamique |
|----------------------|----------------------|-------------------|-----------|
| **5-MeO-DMT** : Uniformité | $r > 0.9$ | $< 0.001$ | Annihilation rapide |
| **N,N-DMT** : Fragmentation | $r < 0.3$ | $> 0.05$ | Défauts persistants |
| **LSD** : Flux géométrique | $0.5 < r < 0.7$ | $\sim 0.02$ | Oscillations |
| **Salvia** : Dissociation | Variable | Haute | Clusters isolés |

### 2.2 Métriques de valence

**Metric 1 : Taux d'annihilation**

$$\text{Annihilation Rate} = -\frac{d}{dt}(\text{#défauts})$$

- **Positif** : Convergence vers uniformité (5-MeO-DMT)
- **Proche de zéro** : Défauts stables (DMT)
- **Négatif** : Fragmentation croissante (stress, chaos)

**Metric 2 : Potentiel d'annihilation**

$$V_{\text{ann}} = \sum_{i,j : q_i q_j < 0} \frac{1}{|\mathbf{r}_i - \mathbf{r}_j| + \epsilon}$$

Mesure la proximité de paires vortex/anti-vortex prêtes à fusionner.

---

## 3. Architecture du moteur

### 3.1 Multi-Kernel

Contrairement au Kuramoto classique (couplage uniforme), notre moteur implémente **trois échelles de couplage** :

```python
K_effective = K1 * kernel_short_range + K2 * kernel_mid_range + K3 * kernel_long_range
```

**Interprétation** :
- **K1** (court-range) : Synchronisation locale, lisse les défauts
- **K2** (mid-range) : Compétition si $K_2 < 0$, génère des structures
- **K3** (long-range) : Ordre global

**Signature DMT** : $K_1 > 0$, $K_2 < 0$, $K_3 \approx 0$
→ Synchronisation locale + compétition mid-range = fragmentation stable

**Signature 5-MeO** : $K_1 \gg 0$, $K_2 = K_3 = 0$
→ Uniformisation pure

### 3.2 Annealing

Le paramètre `annealing_rate` contrôle la réduction temporelle du bruit :

$$\sigma(t) = \sigma_0 \exp(-\gamma t)$$

**Effet** : Permet au système de "geler" dans un état stable après une phase d'exploration.

### 3.3 Projection Map

La classe `ProjectionMap` permet de mapper un espace 3D virtuel (sphère, cube) sur la grille 2D de simulation.

**Usage** : Moduler spatialement les couplages pour créer des patterns géométriques :

```python
pmap = ProjectionMap(grid_shape=(256, 256), projection='stereographic')
distance_to_pole = pmap.compute_geodesic_distance([0, 0, 1])
K1_modulated = K1_base * exp(-distance_to_pole / sigma)
```

**Applications** :
- **Rotation de l'axe** : Génération de patterns géométriques (Salvia)
- **Spots gaussiens** : Zones de cohérence locale

---

## 4. Contrôle holonomique

### 4.1 Concept

Au lieu de fixer des paramètres statiques, on définit des **trajectoires** dans l'espace de configuration. Les boucles fermées permettent de calculer la **Phase de Berry**, une quantité géométrique invariante.

### 4.2 Strokes préfabriqués

**Stroke "5meo_basic"** :
- Boucle simple avec $K_1$ fort constant
- Annealing progressif
- Effet : Uniformisation

**Stroke "dmt_chaos"** :
- Oscillations entre kernels compétitifs
- Pas d'annealing
- Effet : Fragmentation persistante

**Stroke "salvia_geometry"** :
- Rotation du centre de projection sur la sphère
- Génération de patterns géométriques

### 4.3 Phase de Berry (TODO)

La phase géométrique le long d'une trajectoire fermée $C$ est :

$$\gamma = i \oint_C \langle \psi(\mathbf{R}) | \nabla_{\mathbf{R}} \psi(\mathbf{R}) \rangle \cdot d\mathbf{R}$$

où $|\psi(\mathbf{R})\rangle$ est l'état du système aux paramètres $\mathbf{R}$.

**Implémentation future** : Nécessite de définir l'espace de Hilbert approprié.

---

## 5. Validation expérimentale

### 5.1 Critères de succès

**Test 1 : Convergence 5-MeO**
- Après 500 steps avec `5meo_uniformity.json`
- $r_{\text{final}} > 0.9$
- Réduction des défauts > 80%

**Test 2 : Persistance DMT**
- Après 1000 steps avec `dmt_fragmentation.json`
- $r_{\text{final}} < 0.4$
- Densité de défauts stable (variation < 50%)

### 5.2 Résultats (voir `pheno_photoshop_demo.ipynb`)

Les simulations confirment les hypothèses :
- Configuration 5-MeO → annihilation rapide des défauts
- Configuration DMT → défauts persistants, système fragmenté

---

## 6. Connexion à l'Atlas physique

### 6.1 Bridge futur

L'objectif final est de connecter les paramètres du moteur aux paramètres physiques de l'Atlas :

| Paramètre moteur | Paramètre physique Atlas | Mécanisme proposé |
|------------------|-------------------------|-------------------|
| $K_1$ (couplage court-range) | Température locale | Fluctuations thermiques |
| $K_2$ (compétition mid-range) | Champs électromagnétiques | Couplages non-locaux |
| $\omega_i$ (fréquences) | Pression | Modes vibrationnels |
| Annealing | Gradient de refroidissement | Cinétique de transition |

### 6.2 Recherche de régimes

Utiliser le moteur comme **proxy** pour explorer l'espace de configuration de l'Atlas :

1. Définir une métrique cible (ex: $r \approx 0.95$, défauts $< 0.001$)
2. Optimiser les paramètres du moteur pour atteindre la cible
3. Mapper les paramètres optimisés vers l'Atlas via le bridge
4. Valider expérimentalement

---

## 7. Limitations et extensions

### 7.1 Limitations actuelles

1. **Pas de dynamique temporelle réelle** : Le $dt$ est arbitraire
2. **Phase de Berry non implémentée** : Placeholder uniquement
3. **Bridge Atlas manquant** : Connexion théorique seulement
4. **2D uniquement** : Pas de géométrie 3D native

### 7.2 Extensions proposées

1. **Couplage aux réseaux neuronaux** : Les oscillateurs représentent des populations neuronales
2. **Métriques avancées** : Entropie de von Neumann, complexité de Kolmogorov
3. **Optimisation automatique** : Recherche de strokes optimaux via RL
4. **Validation clinique** : Comparaison avec données EEG/fMRI

---

## 8. Guide d'utilisation

### 8.1 Quick Start

```python
from isinglab.oscillators import KuramotoXYEngine, MultiKernelConfig
from isinglab.analysis import detect_vortices

# Créer le moteur
config = MultiKernelConfig(k1_strength=2.0, k1_range=1, annealing_rate=0.5)
engine = KuramotoXYEngine(shape=(256, 256), config=config)
engine.reset()

# Simuler
for _ in range(1000):
    engine.step()

# Analyser
phase_field = engine.get_phase_field()
metrics = detect_vortices(phase_field)

print(f"Défauts : {metrics.n_defects}, r = {engine.get_order_parameter()[0]:.3f}")
```

### 8.2 Charger un preset

```python
import json

with open('presets/pheno/5meo_uniformity.json') as f:
    preset = json.load(f)

kc = preset['kernel_config']
config = MultiKernelConfig(**kc)
engine = KuramotoXYEngine(shape=tuple(preset['engine_config']['grid_shape']), config=config)
```

### 8.3 Contrôle holonomique

```python
from isinglab.control import StrokeLibrary

stroke = StrokeLibrary.get_stroke("dmt_chaos")

for t in np.linspace(0, 1, 100):
    params = stroke.interpolate(t)
    # Appliquer les paramètres au moteur (interface à implémenter)
```

---

## 9. Références théoriques

1. **Kuramoto, Y.** (1984). _Chemical Oscillations, Waves, and Turbulence_. Springer.
2. **Strogatz, S.H.** (2000). From Kuramoto to Crawford: exploring the onset of synchronization. _Physica D_, 143(1-4), 1-20.
3. **Mermin, N.D.** (1979). The topological theory of defects in ordered media. _Reviews of Modern Physics_, 51(3), 591.
4. **Berry, M.V.** (1984). Quantal phase factors accompanying adiabatic changes. _Proc. Royal Soc. London A_, 392(1802), 45-57.
5. **Carhart-Harris, R.L. et al.** (2014). The entropic brain: a theory of conscious states. _Frontiers in Human Neuroscience_, 8, 20.

---

## 10. Conclusion

Le moteur d'oscillateurs de phase fournit un **cadre quantitatif** pour modéliser la phénoménologie des états altérés. Les défauts topologiques émergent comme **marqueur robuste** de la fragmentation perceptuelle.

**Next steps** :
1. Implémenter la Phase de Berry
2. Créer le bridge Atlas
3. Validation clinique

**Status actuel** : Prototype fonctionnel, prêt pour exploration et extension.

---

_Document généré le 2025-11-13 dans le cadre du projet ising-life-lab._

