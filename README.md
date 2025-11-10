# Ising Life Lab

**Un laboratoire expérimental pour automates cellulaires et systèmes de type Ising**

## Vue d'ensemble

Ce dépôt fournit un environnement propre et reproductible pour:
- Explorer les dynamiques d'automates cellulaires (CA) et systèmes de type Ising
- Découvrir et caractériser des règles "edge-of-chaos" (bord du chaos)
- Quantifier les comportements de type mémoire et attracteurs
- Permettre à des agents IA de rechercher et évaluer des règles systématiquement

## Structure du dépôt

```
ising-life-lab/
├── src/
│   ├── core/          # Dynamiques de base CA/Ising
│   ├── memory/        # Détection d'attracteurs et comportements mémoire
│   ├── energy/        # Fonctionnelles d'énergie, Lyapunov, entropie
│   ├── search/        # Recherche et évolution de règles CA
│   └── viz/           # Visualisation (frontend web)
├── isinglab/          # API Python pour analyse et recherche
├── experiments/       # Configurations reproductibles
├── outputs/           # Résultats de scans
└── docs/              # Documentation théorique et guides
```

## Démarrage rapide

### Installation et Test (Smoke Test)

```bash
# 1. Créer environnement virtuel (recommandé)
python -m venv venv

# 2. Activer (Windows PowerShell)
.\venv\Scripts\activate.ps1
# OU (Windows CMD)
venv\Scripts\activate.bat
# OU (Linux/Mac)
source venv/bin/activate

# 3. Installer dépendances
pip install -r requirements.txt

# 4. Installer package en mode développement
pip install -e .

# 5. Tester avec scan rapide (~30 secondes)
python -m isinglab.scan_rules --config experiments/scan_quick.yaml
```

**✅ Succès attendu**: Création de `outputs/quick/scan_results.csv` et `outputs/quick/top_rules.json`

### Scans Complets

```bash
# Scan exhaustif 256 règles élémentaires (~2-5 min)
python -m isinglab.scan_rules --config experiments/scan_default.yaml

# Scan focalisé mémoire (steps=500, ~5-10 min)
python -m isinglab.scan_rules --config experiments/scan_memory_focused.yaml
```

**Résultats sauvegardés dans:**
- `outputs/scan_results.csv` - Toutes les métriques pour toutes les règles
- `outputs/top_rules.json` - Top N règles classées par critère

### Utiliser l'API Python

```python
from isinglab.api import evaluate_rule

metrics = evaluate_rule(
    rule=30,  # Règle de Wolfram
    grid_size=(100, 100),
    steps=200,
    seed=42
)

print(f"Edge score: {metrics['edge_score']:.3f}")
print(f"Memory score: {metrics['memory_score']:.3f}")
```

### Visualisation interactive

```bash
npm start
```

Ouvre un navigateur sur `http://localhost:3000` pour explorer visuellement les règles.

## Documentation

- [**README_LAB.md**](docs/README_LAB.md) - Guide complet du laboratoire
- [**THEORETICAL_FOUNDATION.md**](docs/THEORETICAL_FOUNDATION.md) - Fondements mathématiques des métriques
- [**AI_AGENT_GUIDE.md**](docs/AI_AGENT_GUIDE.md) - Guide pour agents IA autonomes
- [**CONNECTIONS.md**](docs/CONNECTIONS.md) - Liens avec autres projets (qubits biologiques, arrest-molecules)

## Principes de conception

1. **Reproductibilité totale** - Tous les résultats sont reproductibles avec seeds
2. **Traçabilité** - Chaque métrique est définie mathématiquement
3. **Modularité** - Composants indépendants et testables
4. **Transparence** - Pas de "boîtes noires" ou de nombres mystiques
5. **AI-friendly** - API simple sans état global

## Licence

MIT License - Voir [LICENSE](LICENSE) pour détails.

## Citation

Si vous utilisez ce laboratoire dans vos recherches, veuillez citer:

```bibtex
@software{ising_life_lab,
  title = {Ising Life Lab: Experimental Framework for CA and Ising Systems},
  author = {Mythmaker28},
  year = {2025},
  url = {https://github.com/Mythmaker28/ising-life-lab}
}
```

