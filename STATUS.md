# Ising-Life-Lab — Status

**Version** : P5 (Geometric Control Validation)  
**Date** : 2025-11-13  
**État** : ✅ Production-Ready

---

## Statut Actuel

Le repo est dans un état **stable et fonctionnel** après validation P5.

### Résultats P5 (Contrôle Géométrique Quantique)

- **360 configurations testées** sur 180 systèmes quantiques biologiques
- **P4 (Geometric Loop) : 100% de victoires** vs P3 (Dynamic Ramp)
- **Amélioration moyenne : +83,9%** de robustesse
- **Publication en préparation** (preprint arXiv)

### Structure du Repo

```
ising-life-lab/
├── isinglab/              # Package Python principal
├── data/atlas_*/          # Atlas de systèmes quantiques
├── scripts/               # Scripts d'exécution
├── tests/                 # Suite de tests (141 pass)
├── docs/                  # Documentation core
├── examples/              # Démos et notebooks
└── results/               # Résultats expérimentaux
```

### Démarrage Rapide

```bash
# Installation
pip install -e .

# Tests
pytest tests/ -q

# Exemple P5
python run_atlas_batch_p5.py
```

**➡️ Voir [QUICKSTART_P5.md](QUICKSTART_P5.md) pour guide complet**

---

## Tests

- **141 tests passent** (12 skipped - CA historiques archivés)
- **Suite complète** : oscillateurs, Atlas, Pareto, holonomie

```bash
pytest tests/ -v
```

---

## Documentation

| Doc | Description |
|-----|-------------|
| [README.md](README.md) | Vue d'ensemble + résultats P5 |
| [QUICKSTART_P5.md](QUICKSTART_P5.md) | Guide utilisateur 15 min |
| [CHANGELOG.md](CHANGELOG.md) | Historique des versions |
| [docs/THEORETICAL_FOUNDATION.md](docs/THEORETICAL_FOUNDATION.md) | Bases théoriques |
| [docs/BRIDGE_*.md](docs/) | Ponts vers autres repos |

---

## Maintenance

**Branches** :
- `main` : Branche stable (HEAD actuel)

**Prochain agent** : Voir [docs/AI_AGENT_GUIDE.md](docs/AI_AGENT_GUIDE.md)

**Nettoyage** : Rapports de processus archivés dans `docs/archive/process_reports/`


