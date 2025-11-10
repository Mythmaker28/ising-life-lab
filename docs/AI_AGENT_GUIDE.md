# Guide pour Agents IA Autonomes

Ce document explique comment un agent IA (futur ou existant) peut utiliser Ising Life Lab de manière autonome pour explorer, rechercher, et caractériser des règles CA/Ising.

## ⚡ Quick Start pour Agents IA

**3 fonctions essentielles**, toutes dans `isinglab.api`:

```python
from isinglab.api import evaluate_rule, evaluate_batch, quick_scan

# 1. Évaluer UNE règle
metrics = evaluate_rule(
    rule=110,              # Int (CA) ou Dict (Ising)
    grid_size=(100,),      # Tuple: (width,) pour 1D, (h, w) pour 2D
    steps=200,             # Nombre de pas de temps
    seed=42                # Seed pour reproductibilité
)
# Returns: Dict avec keys: edge_score, memory_score, entropy, sensitivity, ...

# 2. Évaluer PLUSIEURS règles (avec moyennage optionnel)
results = evaluate_batch(
    rules=[30, 110, 150],  # List[int] ou List[Dict]
    grid_size=(100,),
    steps=200,
    seed=42,
    n_seeds=3              # Moyenne sur 3 ICs différents
)
# Returns: List[Dict], un dict par règle

# 3. Scan RAPIDE d'une plage
results = quick_scan(
    rule_range=(0, 255),   # (min, max) inclusive
    grid_size=(50,),       # Plus petit = plus rapide
    steps=100,             # Moins de steps = plus rapide
    seed=42
)
# Returns: List[Dict], trié par edge_score décroissant
```

**Garanties**:
- ✅ Déterministe (même seed → mêmes résultats)
- ✅ Pas d'état global (parallélisable)
- ✅ JSON-serializable (tous les dicts/listes/nombres)
- ✅ Validation d'entrée (erreurs claires si paramètres invalides)

## Philosophie de Conception

Le laboratoire est conçu selon les principes suivants pour faciliter l'utilisation par des agents:

1. **Sans état global**: Chaque fonction est pure ou explicitement paramétrée
2. **Reproductibilité totale**: Chaque résultat est reproductible via seeds
3. **API simple**: Une seule fonction principale (`evaluate_rule`)
4. **Format standard**: Entrées/sorties en JSON/YAML/CSV
5. **Parallélisable**: Aucune dépendance entre évaluations de règles

## Interface Principale

### 1. Évaluation d'une Règle Unique

```python
from isinglab.api import evaluate_rule

metrics = evaluate_rule(
    rule=110,              # ID de règle (int) ou params Ising (dict)
    grid_size=(100, 100),  # Dimensions de grille
    steps=200,             # Pas de temps
    seed=42,               # Seed reproductible
    ca_type="elementary",  # Type de CA
    boundary="periodic",   # Conditions aux bords
    return_history=False   # Inclure historique complet?
)

# metrics est un dict avec:
# - entropy, spatial_entropy, sensitivity, memory_score
# - edge_score (composite)
# - activity, attractor_type, attractor_period
# - lambda_estimate
# - metadata: rule, grid_size, steps, seed
```

**Garanties**:
- **Déterministe**: Même `(rule, grid_size, steps, seed)` → même `metrics`
- **Rapide**: ~0.1-1s par évaluation (dépend de grid_size, steps)
- **Pas d'effets secondaires**: Aucune modification de fichiers, variables globales

### 2. Évaluation en Batch

```python
from isinglab.api import evaluate_batch

rules = [30, 54, 110, 150]
results = evaluate_batch(
    rules=rules,
    grid_size=(100,),
    steps=200,
    seed=42,
    n_seeds=3  # Moyenne sur 3 seeds
)

# results est une List[Dict], un dict par règle
for r in results:
    print(f"Règle {r['rule']}: edge={r['edge_score']:.3f}")
```

**Avantages**:
- Moins d'overhead d'import
- Moyennage automatique sur plusieurs seeds
- Format uniforme (même avec n_seeds > 1)

## Énumération Systématique de l'Espace des Règles

### CA Élémentaires (1D)

**Espace complet**: 256 règles (règles 0-255)

```python
# Scan exhaustif
results = []
for rule in range(256):
    metrics = evaluate_rule(rule, grid_size=(100,), steps=200, seed=42)
    results.append(metrics)

# Sauvegarder
import pandas as pd
df = pd.DataFrame(results)
df.to_csv("all_elementary_ca.csv", index=False)
```

**Estimation de temps**: ~25-250 secondes (selon CPU)

### CA Life-like (2D)

**Espace**: $2^{18} = 262,144$ règles (théoriquement)

**Problème**: Trop grand pour scan exhaustif.

**Solutions**:

1. **Échantillonnage aléatoire**:

```python
import random
random.seed(42)

sample_rules = random.sample(range(262144), k=1000)
results = evaluate_batch(sample_rules, grid_size=(50, 50), steps=300, seed=42)
```

2. **Recherche guidée** (voir section suivante)

### Règles Ising

**Espace**: Continu (J, h, T)

**Stratégie**: Grid search ou échantillonnage

```python
import numpy as np

J_values = np.linspace(0.5, 2.0, 10)
T_values = np.linspace(1.0, 4.0, 20)

results = []
for J in J_values:
    for T in T_values:
        rule = {"J": J, "h": 0.0, "T": T, "dynamics": "glauber"}
        metrics = evaluate_rule(
            rule=rule,
            grid_size=(50, 50),
            steps=500,
            seed=42
        )
        results.append(metrics)
```

## Recherche Guidée et Optimisation

### Recherche Évolutionnaire

```python
from isinglab.search import EvolutionarySearch

def fitness(rule, **kwargs):
    """Fonction de fitness personnalisée."""
    metrics = evaluate_rule(rule, **kwargs)
    # Exemple: optimiser edge_score * memory_score
    return metrics["edge_score"] * metrics["memory_score"]

searcher = EvolutionarySearch(
    population_size=50,
    mutation_rate=0.1,
    seed=42
)

result = searcher.run(
    fitness_func=fitness,
    n_generations=100,
    rule_type="elementary",
    grid_size=(100,),
    steps=200,
    seed=42
)

print(f"Meilleure règle: {result['best_rule']}")
print(f"Fitness: {result['best_fitness']:.4f}")
```

### Recherche Bayésienne (Externe)

Pour des agents utilisant Bayesian Optimization:

```python
from skopt import gp_minimize

def objective(params):
    """Fonction objectif pour skopt."""
    rule = int(params[0])
    metrics = evaluate_rule(rule, grid_size=(100,), steps=200, seed=42)
    # Minimiser négation (skopt minimise)
    return -metrics["edge_score"]

result = gp_minimize(
    objective,
    [(0, 255)],  # Espace de recherche
    n_calls=100,
    random_state=42
)

best_rule = int(result.x[0])
```

## Stockage et Récupération des Résultats

### Format de Stockage Recommandé

**CSV pour données tabulaires**:

```python
import pandas as pd

# Sauvegarder
df = pd.DataFrame(results)
df.to_csv("scan_results.csv", index=False)

# Charger
df = pd.read_csv("scan_results.csv")
top_rules = df.sort_values("edge_score", ascending=False).head(10)
```

**JSON pour métadonnées riches**:

```python
import json

# Sauvegarder une règle spécifique avec historique
metrics = evaluate_rule(110, grid_size=(100,), steps=200, seed=42, return_history=True)

# Convertir numpy arrays en listes pour JSON
metrics_serializable = {
    k: v.tolist() if hasattr(v, 'tolist') else v
    for k, v in metrics.items()
}

with open("rule_110_analysis.json", "w") as f:
    json.dump(metrics_serializable, f, indent=2)
```

### Base de Données (pour scans massifs)

```python
import sqlite3
import json

# Créer DB
conn = sqlite3.connect("ca_rules.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS rules (
    rule INTEGER PRIMARY KEY,
    ca_type TEXT,
    edge_score REAL,
    memory_score REAL,
    entropy REAL,
    sensitivity REAL,
    attractor_type TEXT,
    full_metrics TEXT
)
""")

# Insérer résultats
for metrics in results:
    cursor.execute("""
    INSERT OR REPLACE INTO rules VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        metrics["rule"],
        "elementary",
        metrics["edge_score"],
        metrics["memory_score"],
        metrics["entropy"],
        metrics["sensitivity"],
        metrics["attractor_type"],
        json.dumps(metrics)
    ))

conn.commit()

# Requêtes
cursor.execute("SELECT rule, edge_score FROM rules WHERE edge_score > 0.5 ORDER BY edge_score DESC")
top_rules = cursor.fetchall()
```

## Parallélisation

### Multiprocessing (Local)

```python
from multiprocessing import Pool
from functools import partial

def eval_wrapper(rule, **kwargs):
    return evaluate_rule(rule, **kwargs)

# Préparer fonction partielle
eval_func = partial(eval_wrapper, grid_size=(100,), steps=200, seed=42)

# Paralléliser
with Pool(processes=8) as pool:
    results = pool.map(eval_func, range(256))
```

### Dask (Distributed)

```python
import dask
from dask.distributed import Client

client = Client()  # Connecter au cluster Dask

# Créer tâches lazy
lazy_results = [
    dask.delayed(evaluate_rule)(rule, grid_size=(100,), steps=200, seed=42)
    for rule in range(256)
]

# Exécuter
results = dask.compute(*lazy_results)
```

### Ray (Scalable)

```python
import ray

ray.init()

@ray.remote
def eval_remote(rule, **kwargs):
    return evaluate_rule(rule, **kwargs)

# Lancer tâches
futures = [eval_remote.remote(rule, grid_size=(100,), steps=200, seed=42) 
           for rule in range(256)]

# Récupérer résultats
results = ray.get(futures)
```

## Stratégies de Recherche Recommandées

### 1. Exploration Initiale (Budget Limité)

**Objectif**: Vue d'ensemble rapide

```python
from isinglab.api import quick_scan

# Scan rapide avec paramètres réduits
results = quick_scan(
    rule_range=(0, 255),
    grid_size=(50,),
    steps=100,
    seed=42
)

# Identifier régions intéressantes
import pandas as pd
df = pd.DataFrame(results)
promising = df[df["edge_score"] > 0.3]["rule"].tolist()
```

### 2. Approfondissement (Budget Moyen)

**Objectif**: Caractérisation précise des règles prometteuses

```python
# Réévaluer avec paramètres plus longs et multiples seeds
detailed_results = evaluate_batch(
    rules=promising,
    grid_size=(200,),
    steps=500,
    seed=42,
    n_seeds=10
)
```

### 3. Recherche Ciblée (Budget Élevé)

**Objectif**: Trouver règles optimales pour critère spécifique

```python
from isinglab.search import EvolutionarySearch

searcher = EvolutionarySearch(population_size=100, seed=42)

# Définir fitness complexe
def custom_fitness(rule, **kwargs):
    m = evaluate_rule(rule, **kwargs)
    # Exemple: edge-of-chaos avec mémoire élevée
    return m["edge_score"] * (m["memory_score"] ** 0.5)

result = searcher.run(
    fitness_func=custom_fitness,
    n_generations=200,
    rule_type="elementary",
    grid_size=(150,),
    steps=300,
    seed=42
)
```

## Détection de Patterns dans les Résultats

### Clustering de Règles

```python
from sklearn.cluster import KMeans
import numpy as np

# Extraire features
df = pd.DataFrame(results)
features = df[["entropy", "sensitivity", "memory_score", "activity"]].values

# Clustering
kmeans = KMeans(n_clusters=5, random_state=42)
df["cluster"] = kmeans.fit_predict(features)

# Analyser clusters
for cluster_id in range(5):
    cluster_rules = df[df["cluster"] == cluster_id]["rule"].tolist()
    print(f"Cluster {cluster_id}: {len(cluster_rules)} règles")
    print(f"  Exemple: {cluster_rules[:5]}")
```

### Analyse de Corrélations

```python
# Corrélations entre métriques
corr = df[["entropy", "spatial_entropy", "sensitivity", "memory_score", "edge_score"]].corr()
print(corr)

# Visualiser
import seaborn as sns
import matplotlib.pyplot as plt

sns.heatmap(corr, annot=True, cmap="coolwarm")
plt.savefig("metric_correlations.png")
```

## Logging et Traçabilité

### Enregistrement des Expériences

```python
import datetime
import json

experiment_log = {
    "timestamp": datetime.datetime.now().isoformat(),
    "experiment_id": "scan_elementary_001",
    "config": {
        "rule_range": [0, 255],
        "grid_size": (100,),
        "steps": 200,
        "n_seeds": 3,
        "seed": 42
    },
    "results_summary": {
        "n_rules": len(results),
        "mean_edge_score": df["edge_score"].mean(),
        "max_edge_score": df["edge_score"].max(),
        "best_rule": int(df.loc[df["edge_score"].idxmax(), "rule"])
    },
    "output_files": [
        "outputs/scan_results.csv",
        "outputs/top_rules.json"
    ]
}

with open("experiment_log.json", "w") as f:
    json.dump(experiment_log, f, indent=2)
```

## Gestion des Erreurs

```python
def safe_evaluate(rule, **kwargs):
    """Wrapper avec gestion d'erreurs."""
    try:
        return evaluate_rule(rule, **kwargs)
    except Exception as e:
        print(f"Erreur pour règle {rule}: {e}")
        return {
            "rule": rule,
            "error": str(e),
            "edge_score": 0.0,
            "memory_score": 0.0,
            # Valeurs par défaut pour éviter crash
        }

# Utiliser dans scans robustes
results = [safe_evaluate(r, grid_size=(100,), steps=200, seed=42) 
           for r in range(256)]
```

## Exemple: Agent de Recherche Complet

```python
class CAExplorerAgent:
    """Agent autonome pour exploration CA."""
    
    def __init__(self, output_dir="agent_outputs", seed=42):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.seed = seed
        self.explored_rules = set()
        self.results_db = []
    
    def explore_rule(self, rule):
        """Évaluer une règle et stocker résultats."""
        if rule in self.explored_rules:
            return None
        
        metrics = evaluate_rule(
            rule=rule,
            grid_size=(100,),
            steps=200,
            seed=self.seed
        )
        
        self.explored_rules.add(rule)
        self.results_db.append(metrics)
        
        return metrics
    
    def find_interesting_rules(self, n_samples=100, threshold=0.4):
        """Rechercher règles intéressantes par échantillonnage."""
        import random
        random.seed(self.seed)
        
        candidates = [r for r in range(256) if r not in self.explored_rules]
        sample = random.sample(candidates, min(n_samples, len(candidates)))
        
        interesting = []
        for rule in sample:
            metrics = self.explore_rule(rule)
            if metrics["edge_score"] > threshold:
                interesting.append((rule, metrics["edge_score"]))
        
        return sorted(interesting, key=lambda x: x[1], reverse=True)
    
    def save_results(self):
        """Sauvegarder tous les résultats."""
        df = pd.DataFrame(self.results_db)
        df.to_csv(self.output_dir / "explored_rules.csv", index=False)
        
        print(f"Sauvegardé {len(self.results_db)} résultats")
    
    def run(self, budget=100):
        """Exécuter exploration avec budget limité."""
        print(f"Démarrage exploration (budget: {budget} évaluations)")
        
        # Phase 1: Échantillonnage initial
        interesting = self.find_interesting_rules(n_samples=budget // 2)
        print(f"Trouvé {len(interesting)} règles intéressantes")
        
        # Phase 2: Affiner autour des règles intéressantes
        for rule, score in interesting[:5]:
            # Explorer voisinage (flip 1 bit)
            for bit in range(8):
                neighbor = rule ^ (1 << bit)
                if neighbor not in self.explored_rules:
                    self.explore_rule(neighbor)
        
        # Sauvegarder
        self.save_results()
        
        # Rapport
        df = pd.DataFrame(self.results_db)
        best = df.loc[df["edge_score"].idxmax()]
        print(f"\nMeilleure règle: {int(best['rule'])}")
        print(f"Edge score: {best['edge_score']:.4f}")

# Utiliser l'agent
agent = CAExplorerAgent(seed=42)
agent.run(budget=100)
```

## Ressources et Support

- **Documentation complète**: `docs/README_LAB.md`
- **Fondements théoriques**: `docs/THEORETICAL_FOUNDATION.md`
- **Code source**: `isinglab/` (Python bien commenté)
- **Exemples**: `experiments/` (configs YAML reproductibles)

Pour questions ou bugs, ouvrir une issue GitHub.

