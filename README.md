# Ising Life Lab

**Un laboratoire expérimental dual pour automates cellulaires et systèmes de type Ising**

Ce dépôt contient **deux environnements complémentaires**:

1. **Python `isinglab`** (analyse quantitative, recherche systématique, API pour agents IA)
2. **JavaScript Memory Lab** (visualisation interactive, exploration en temps réel)

---

## 🐍 Python `isinglab` - Analyse Quantitative

### Vue d'ensemble

Environnement reproductible pour:
- Explorer les dynamiques d'automates cellulaires (CA) et systèmes de type Ising
- Découvrir et caractériser des règles "edge-of-chaos" (bord du chaos)
- Quantifier les comportements de type mémoire et attracteurs
- Permettre à des agents IA de rechercher et évaluer des règles systématiquement

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

### Documentation Python

- [**README_LAB.md**](docs/README_LAB.md) - Guide complet du laboratoire
- [**THEORETICAL_FOUNDATION.md**](docs/THEORETICAL_FOUNDATION.md) - Fondements mathématiques des métriques
- [**AI_AGENT_GUIDE.md**](docs/AI_AGENT_GUIDE.md) - Guide pour agents IA autonomes
- [**CONNECTIONS.md**](docs/CONNECTIONS.md) - Liens avec autres projets (qubits biologiques, arrest-molecules)
- [**ATLAS_INTEGRATION_GUIDE.md**](docs/ATLAS_INTEGRATION_GUIDE.md) - 🆕 Intégration Biological Qubits Atlas

### 🔬 Intégration Biological Qubits Atlas (Nouveau)

Le package `isinglab` peut maintenant charger et analyser des systèmes réels du [Biological Qubits Atlas](https://github.com/Mythmaker28/Quantum-Sensors-Qubits-in-Biology) :

**Systèmes supportés** :
- ✅ **180 systèmes optiques** (fluorescent proteins : GCaMP, ASAP, dLight, etc.)
- ✅ **10 spin qubits** (NV centers, SiC defects, SiV, P1, etc.)
- ✅ **8 nuclear spins** (¹³C, ³¹P, ¹⁴N, ²⁹Si dans diamond/silicon)
- ✅ **8 radical pairs** (Cryptochrome, photolyase, PSII, etc.)

**Workflow typique** :
```python
from isinglab.data_bridge import load_optical_systems, map_system_properties
from isinglab.mapping_profiles import get_target_profile_for_system
from isinglab.pipelines import run_regime_search

# 1. Charger systèmes Atlas (READ-ONLY)
df = load_optical_systems(tier="curated")  # 180 curated systems
df_mapped = map_system_properties(df)

# 2. Générer profil cible (HEURISTIQUE)
profile = get_target_profile_for_system(
    modality="optical",
    temperature_regime="physiological",
    coherence_class="long"
)

# 3. Rechercher régimes CA/Ising
results_df, top_rules = run_regime_search(target_profile=profile)
print(f"Top rule: {top_rules[0]['rule']}")
```

**⚠️ DISCLAIMERS** : Mappings = analogies conceptuelles, PAS prédictions quantiques. Voir [docs/ATLAS_INTEGRATION_GUIDE.md](docs/ATLAS_INTEGRATION_GUIDE.md)

---

## 🌐 JavaScript Memory Lab - Visualisation Interactive

### Quick Start

1. Clone repository
2. Open `public/index.html` in modern browser via HTTP server:
   ```bash
   python -m http.server 8001
   # Then open http://localhost:8001/public/index.html
   ```
3. Select rule, click Randomize, click Start

### Memory AI Lab (V1.0 ✅)

**URL**: http://localhost:8001/experiments/memory-ai-lab/index.html

Test and compare CA vs Hopfield memory capabilities.

**Features**:
- **CA Playground**: 7 Hall of Fame rules
- **Memory Lab**: Draw patterns (localStorage persistence)
- **Hopfield Comparison**: Fair benchmarking
- **AutoScan**: Discover memory candidates
- **5 APIs**: MemoryLab, HopfieldLab, Reports, MemoryScanner, MemoryCapacity

**Results**: 7 validated memory rules (B01/S3 champion 96-99% recall)

See `docs/QUICK_START_MEMORY_AI_LAB.md`

### Autres Expériences JavaScript

- **Memory Storage System** (Phase 2): http://localhost:8001/experiments/memory-storage-system/
- **Rule Predictor AI** (Phase 3): http://localhost:8001/experiments/rule-predictor/
- **Auto Memory Researcher** (Phase 4): http://localhost:8001/experiments/auto-memory-research/
- **Engine Selector Demo** (Phase 5): http://localhost:8001/experiments/engine-selector-demo/
- **Project Dashboard**: http://localhost:8001/experiments/dashboard/

### Features JavaScript

#### Core CA Engine
- **13 Life-like CA rules** including classics (Conway, HighLife, Day & Night, Seeds, Replicator)
- **Custom rules**: Mythmaker, Mahee, Tommy
- **Promoted rules**: 5 automatically discovered high-scoring rules (Mythmaker_1/2, Mahee_1, Tommy_1/2)
- **Real-time visualization** with play/pause/step controls
- **Speed control** (0.1x to 3x)

#### Advanced Features
- **Energy view** (checkbox): color heatmap showing local energy (green=stable, red=unstable)
- **Live metrics**: density, entropy, population, energy
- **Real-time graph**: density and energy evolution over time
- **Pattern detection**: automatic oscillator period detection
- **Rule Explorer**: "Discover rules" button finds interesting Life-like rules automatically
- **Random rule**: generate random Life-like rules on demand
- **Next rule**: cycle through interesting rules

---

## 📁 Structure du dépôt

```
ising-life-lab/
├── isinglab/           # 🐍 Python API pour analyse quantitative
│   ├── api.py          # API publique (evaluate_rule, evaluate_batch, quick_scan)
│   ├── core/           # Dynamiques de base CA/Ising
│   ├── metrics/        # Métriques quantitatives (entropy, sensitivity, memory, edge_score)
│   ├── search/         # Recherche et évolution de règles
│   └── scan_rules.py   # CLI principal
├── src/                # 🌐 JavaScript modules pour visualisation
│   ├── core/           # Grid logic and CA engine
│   ├── memory/         # Memory Lab, Hopfield, attractor detection
│   ├── viz/            # Canvas rendering and UI
│   ├── metrics/        # Complexity measurements
│   ├── energy/         # Local energy functions
│   ├── search/         # Rule discovery and exploration
│   └── experiments/    # Analysis utilities
├── experiments/        # Configurations reproductibles (Python YAML + JavaScript demos)
│   ├── scan_*.yaml     # Python experiment configs
│   ├── memory-ai-lab/  # Standalone Memory AI Lab
│   ├── rule-predictor/ # ML-powered rule prediction
│   └── [autres expériences JS]
├── public/             # Entry points pour applications web
│   └── index.html      # Interface principale JavaScript
├── outputs/            # Résultats de scans (Python)
└── docs/               # Documentation théorique et guides
```

---

## 🧬 Principes de conception

1. **Reproductibilité totale** - Tous les résultats sont reproductibles avec seeds
2. **Traçabilité** - Chaque métrique est définie mathématiquement
3. **Modularité** - Composants indépendants et testables
4. **Transparence** - Pas de "boîtes noires" ou de nombres mystiques
5. **AI-friendly** - API simple sans état global
6. **Complémentarité** - Python pour l'analyse rigoureuse, JavaScript pour l'exploration intuitive

---

## 📜 Licence

MIT License - Voir [LICENSE](LICENSE) pour détails.

---

## 📖 Citation

Si vous utilisez ce laboratoire dans vos recherches, veuillez citer:

```bibtex
@software{ising_life_lab,
  title = {Ising Life Lab: Dual Framework for CA and Ising Systems},
  author = {Mythmaker28},
  year = {2025},
  url = {https://github.com/Mythmaker28/ising-life-lab}
}
```
