# Exemple Canonique de Scan Output

## Configuration (experiments/scan_default.yaml)

```yaml
rule_range: [0, 255]
ca_type: "elementary"
grid_size: [100]
steps: 200
seed: 42
n_seeds: 3
output_dir: "outputs"
top_n: 20
metric: "edge_score"
verbose: true
```

## Commande

```bash
python -m isinglab.scan_rules --config experiments/scan_default.yaml
```

## Outputs Générés

### 1. outputs/scan_results.csv

**Format**: CSV avec headers

**Colonnes** (14 total):
1. `entropy` - Entropie de Shannon de l'état final
2. `spatial_entropy` - Entropie des blocs spatiaux (2×2)
3. `sensitivity` - Sensibilité aux conditions initiales (Hamming)
4. `memory_score` - Score de mémoire (attracteurs)
5. `edge_score` - Score composite edge-of-chaos ⭐
6. `activity` - Niveau d'activité (densité de 1s)
7. `attractor_type` - Type: "fixed", "cycle", "chaotic", "quasi-periodic"
8. `attractor_period` - Période du cycle (0 si pas de cycle)
9. `attractor_stability` - Fraction de temps dans attracteur
10. `lambda_estimate` - Estimation λ de Langton (EXPERIMENTAL)
11. `rule` - Numéro de règle
12. `grid_size` - Dimensions grille
13. `steps` - Nombre de pas d'évolution
14. `seed` - Seed utilisé (ou seed de base si n_seeds>1)

**Exemple de ligne**:
```
rule,edge_score,memory_score,entropy,sensitivity,activity,attractor_type,...
110,0.2396,0.0000,0.9988,0.3000,0.52,chaotic,...
```

### 2. outputs/top_rules.json

**Format**: JSON array of objects

**Structure**:
```json
[
  {
    "rule": 20,
    "edge_score": 0.5440,
    "memory_score": 0.7389,
    "entropy": 0.7219,
    "spatial_entropy": 0.3626,
    "sensitivity": 0.0640,
    "activity": 0.2,
    "attractor_type": "cycle",
    "attractor_period": 50,
    "attractor_stability": 0.9901,
    "lambda_estimate": 0.2068,
    "grid_size": [100],
    "steps": 200,
    "seed": 42
  },
  ...
]
```

**Tri**: Par `metric` spécifié dans config (défaut: `edge_score`)

**Nombre**: `top_n` règles (défaut: 20)

## Reproductibilité

**Garantie**: Même commande → mêmes résultats

**Contrôles**:
- `seed` fixe les ICs
- `steps` fixe la durée
- `grid_size` fixe la taille
- `n_seeds` contrôle le nombre d'échantillons

**Moyennage** (si `n_seeds > 1`):
- Métriques numériques: moyenne ± std
- `attractor_type`: mode (plus fréquent)
- Colonnes ajoutées: `*_std` pour chaque métrique

## Cas d'Usage

### 1. Trouver les règles edge-of-chaos

```python
import pandas as pd

df = pd.read_csv('outputs/scan_results.csv')
edge_rules = df[df['edge_score'] > 0.4].sort_values('edge_score', ascending=False)
print(f"Trouvé {len(edge_rules)} règles avec edge_score > 0.4")
print(edge_rules[['rule', 'edge_score', 'memory_score', 'sensitivity']].head(10))
```

### 2. Analyser les attracteurs

```python
# Règles avec cycles longs
cycles = df[(df['attractor_type'] == 'cycle') & (df['attractor_period'] > 10)]
print(f"{len(cycles)} règles avec cycles longs (>10)")

# Règles chaotiques
chaotic = df[df['attractor_type'] == 'chaotic']
print(f"{len(chaotic)} règles chaotiques")
```

### 3. Exporter pour analyse externe

```python
# Format pour ML/analyse
import json

with open('outputs/top_rules.json') as f:
    top = json.load(f)

# Extraire features pour clustering
features = [[r['entropy'], r['sensitivity'], r['memory_score']] for r in top]
```

## Limitations Documentées

1. **Lambda estimate**: EXPERIMENTAL - Heuristique, pas calcul exact
2. **Finite-size effects**: Grilles petites (<50) peuvent donner résultats biaisés
3. **Finite-time**: `steps` < 500 peut ne pas capturer attracteurs longs
4. **Stochasticité**: `n_seeds=1` donne un seul échantillon (variance non capturée)

## Validation Recommandée

Après chaque scan, vérifier:
1. Distribution de `edge_score`: doit être bimodale (pics à ~0 et ~0.3-0.6)
2. Règles classiques (30, 110, 150) dans top 30% si `steps >= 200`
3. Pas de NaN/Inf dans les métriques
4. `attractor_period` < `steps` (si cycle détecté)

## Commande de Vérification Rapide

```bash
python -c "
import pandas as pd
df = pd.read_csv('outputs/scan_results.csv')
print(f'Total rules: {len(df)}')
print(f'Mean edge_score: {df[\"edge_score\"].mean():.3f}')
print(f'Max edge_score: {df[\"edge_score\"].max():.3f}')
print(f'Rules with edge>0.3: {(df[\"edge_score\"]>0.3).sum()}')
print(f'Chaotic rules: {(df[\"attractor_type\"]==\"chaotic\").sum()}')
"
```

