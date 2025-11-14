# Guide du Laboratoire Ising Life Lab

## Vue d'ensemble

Le **Ising Life Lab** est un environnement expérimental rigoureux pour l'exploration systématique des automates cellulaires (CA) et des systèmes de type Ising. Ce laboratoire permet de:

1. **Simuler** des dynamiques CA et Ising de manière déterministe et reproductible
2. **Mesurer** quantitativement les propriétés émergentes (entropie, sensibilité, mémoire)
3. **Rechercher** des règles présentant des comportements spécifiques (edge-of-chaos, mémoire)
4. **Analyser** les régimes dynamiques de manière transparente et traçable

## Architecture du Laboratoire

### Modules Principaux

```
isinglab/
├── core/              # Moteurs de simulation
│   ├── ca_engine.py   # Automates cellulaires (1D/2D)
│   └── ising_engine.py # Modèle d'Ising classique
│
├── metrics/           # Métriques quantitatives
│   ├── entropy.py     # Entropie de Shannon, spatiale, temporelle
│   ├── sensitivity.py # Exposant de Lyapunov, distance de Hamming
│   ├── memory.py      # Détection d'attracteurs, score de mémoire
│   └── edge_score.py  # Score composé "edge-of-chaos"
│
├── search/            # Outils de recherche
│   ├── scanner.py     # Scan systématique d'espaces de règles
│   └── evolutionary.py # Recherche évolutionnaire/génétique
│
└── api.py            # API simple pour agents IA
```

### Principe de Fonctionnement

1. **Initialisation déterministe**: Chaque simulation utilise un seed pour garantir la reproductibilité
2. **Évolution**: Le système évolue selon des règles CA ou Ising spécifiées
3. **Mesure**: Des métriques quantitatives sont calculées sur l'historique des états
4. **Scoring**: Un score composite évalue la "qualité" de la règle selon les critères choisis

## Utilisation Pratique

### 1. Évaluer une Règle Unique

```python
from isinglab.api import evaluate_rule

# Évaluer la règle 30 de Wolfram (automate élémentaire)
metrics = evaluate_rule(
    rule=30,
    grid_size=(100,),  # 1D, largeur 100
    steps=200,
    seed=42
)

print(f"Edge-of-chaos score: {metrics['edge_score']:.3f}")
print(f"Memory score: {metrics['memory_score']:.3f}")
print(f"Entropy: {metrics['entropy']:.3f}")
print(f"Type d'attracteur: {metrics['attractor_type']}")
```

### 2. Scanner un Espace de Règles

```bash
# Scan exhaustif des 256 règles élémentaires
python -m isinglab.scan_rules --config experiments/scan_default.yaml

# Scan rapide (exploration préliminaire)
python -m isinglab.scan_rules --config experiments/scan_quick.yaml

# Scan focalisé sur la mémoire
python -m isinglab.scan_rules --config experiments/scan_memory_focused.yaml
```

**Résultats produits:**
- `outputs/scan_results.csv`: Toutes les métriques pour toutes les règles
- `outputs/top_rules.json`: Top 20 règles selon le critère choisi

### 3. Recherche Évolutionnaire

```python
from isinglab.search import EvolutionarySearch, edge_fitness

# Créer chercheur évolutionnaire
searcher = EvolutionarySearch(
    population_size=50,
    mutation_rate=0.1,
    seed=42
)

# Optimiser pour edge-of-chaos
result = searcher.run(
    fitness_func=edge_fitness,
    n_generations=100,
    rule_type="elementary",
    grid_size=(100,),
    steps=200,
    seed=42
)

print(f"Meilleure règle trouvée: {result['best_rule']}")
print(f"Fitness: {result['best_fitness']:.3f}")
```

### 4. Analyse d'un Modèle d'Ising

```python
from isinglab.api import evaluate_rule

# Évaluer un système d'Ising 2D
metrics = evaluate_rule(
    rule={
        "J": 1.0,      # Couplage ferromagnétique
        "h": 0.0,      # Champ externe nul
        "T": 2.27,     # Température critique
        "dynamics": "glauber"
    },
    grid_size=(50, 50),
    steps=500,
    seed=42
)

print(f"Magnétisation: {metrics['activity']:.3f}")
print(f"Edge score: {metrics['edge_score']:.3f}")
```

## Configuration des Expériences

Les fichiers YAML dans `experiments/` permettent de configurer les scans de manière reproductible.

**Structure d'un fichier de configuration:**

```yaml
# experiments/custom_scan.yaml
rule_range: [0, 255]     # Règles à scanner
ca_type: "elementary"    # Type de CA
grid_size: [100]         # Dimensions de la grille
steps: 200               # Nombre de pas d'évolution
seed: 42                 # Seed pour reproductibilité
n_seeds: 3               # Répétitions avec seeds différents
output_dir: "outputs"    # Dossier de sortie
top_n: 20                # Nombre de top règles à sauvegarder
metric: "edge_score"     # Métrique de classement
verbose: true            # Affichage détaillé
```

## Plugger de Nouvelles Fonctions de Scoring

### Créer une Métrique Personnalisée

```python
# Dans votre code
def custom_metric(history, **kwargs):
    """
    Métrique personnalisée basée sur l'historique.
    
    Args:
        history: Liste d'états (np.ndarray)
        
    Returns:
        Score numérique (float)
    """
    # Exemple: ratio d'activité moyenne sur écart-type
    from isinglab.metrics.entropy import activity_level
    activities = [activity_level(state) for state in history]
    
    mean_act = np.mean(activities)
    std_act = np.std(activities)
    
    if std_act == 0:
        return 0.0
    
    return mean_act / std_act

# L'utiliser dans un scan
from isinglab.api import evaluate_rule

def custom_fitness(rule, **eval_kwargs):
    metrics = evaluate_rule(rule, **eval_kwargs, return_history=True)
    history = metrics['history']
    return custom_metric(history)

# Recherche évolutionnaire avec métrique custom
from isinglab.search import EvolutionarySearch

searcher = EvolutionarySearch(population_size=30, seed=42)
result = searcher.run(
    fitness_func=custom_fitness,
    n_generations=50,
    rule_type="elementary",
    grid_size=(100,),
    steps=200
)
```

### Modifier le Score Edge-of-Chaos

Le score edge-of-chaos est défini dans `isinglab/metrics/edge_score.py`. Vous pouvez:

1. Ajuster les poids des termes (entropie, sensibilité, mémoire, activité)
2. Changer les valeurs "cibles" optimales
3. Utiliser une autre fonction de combinaison

**Exemple de modification:**

```python
# Dans isinglab/metrics/edge_score.py

def edge_of_chaos_score_v2(history, sensitivity, memory, ...):
    """Version modifiée privilégiant la mémoire."""
    
    entropy_term = compute_entropy_term(history)
    sensitivity_term = compute_sensitivity_term(sensitivity)
    memory_term = memory ** 0.5  # Réduire pénalité mémoire élevée
    activity_term = compute_activity_term(history)
    
    # Pondération différente: mémoire compte double
    score = (entropy_term * sensitivity_term * memory_term**2 * activity_term) ** 0.2
    
    return score
```

## Utilisation par des Agents IA

Le laboratoire est conçu pour être utilisable par des agents autonomes. Voir [AI_AGENT_GUIDE.md](AI_AGENT_GUIDE.md) pour:

- API sans état
- Énumération systématique des règles
- Parallélisation des évaluations
- Format de stockage des résultats

## Garanties

### Reproductibilité

- **Tous** les résultats sont reproductibles avec le même seed
- Les calculs sont **déterministes** (sauf Ising stochastique, contrôlé par seed)
- Pas d'état global: chaque évaluation est indépendante

### Traçabilité

- Chaque métrique a une **définition mathématique explicite** (voir [THEORETICAL_FOUNDATION.md](THEORETICAL_FOUNDATION.md))
- Pas de "nombres magiques" non justifiés
- Les formules de scoring sont **transparentes** et modifiables

### Performance

- Implémentation NumPy optimisée
- Grilles jusqu'à 500×500 en temps raisonnable
- Scans parallélisables (via `evaluate_batch`)

## Limitations Actuelles

1. **Règles CA limitées**: Implémentation actuelle supporte élémentaires et Life-like. Les règles totalistiques générales nécessitent une extension.

2. **Ising 2D uniquement**: Le moteur Ising actuel est 2D. Pour 3D, adapter `IsingEngine`.

3. **Estimation λ approximative**: Le paramètre λ de Langton est **estimé** à partir des dynamiques, pas calculé directement depuis la table de règles (nécessite analyse combinatoire).

4. **Métriques continues**: Pour les systèmes continus (pas discrets), adapter les métriques (actuellement binaires/spin).

## Exemples de Questions Scientifiques

Le laboratoire permet d'explorer:

1. **Quelles règles CA présentent un comportement edge-of-chaos?**
   - Scanner avec `metric: "edge_score"`
   - Analyser corrélations entre métriques

2. **Existe-t-il des règles avec mémoire parfaite mais non-triviales?**
   - Scanner avec `metric: "memory_score"`
   - Filtrer `attractor_type != "fixed"`

3. **Quelle est la distribution des exposants de Lyapunov dans l'espace des règles?**
   - Extraire `sensitivity` de tous les scans
   - Histogramme et analyse statistique

4. **Les règles réversibles sont-elles toujours edge-of-chaos?**
   - Identifier règles réversibles
   - Comparer leurs distributions de métriques

## Support et Développement

Pour questions, bugs ou contributions:
- Issues GitHub: [github.com/Mythmaker28/ising-life-lab/issues](https://github.com/Mythmaker28/ising-life-lab/issues)
- Voir [CONTRIBUTING.md] pour guidelines de contribution (TODO)

## Références

- Langton, C. G. (1990). "Computation at the edge of chaos"
- Wolfram, S. (2002). "A New Kind of Science"
- Packard, N. H. (1988). "Adaptation toward the edge of chaos"
- Ising, E. (1925). "Beitrag zur Theorie des Ferromagnetismus"

