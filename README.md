# Ising Life Lab

A minimal sandbox exploring Life-like cellular automata, Ising-style energies, and energy-based models.

**Status**: V2 - Working with rule discovery, energy visualization, and automatic analysis.

## Quick Start

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

### Memory Storage System (Phase 2 ✅)

**URL**: http://localhost:8001/experiments/memory-storage-system/

Multi-engine parallel comparison (7 CA + Hopfield).

**Features**:
- Test 7 CA rules + Hopfield simultaneously
- Visual pattern grid
- Configurable noise testing (0-20%)
- Real-time performance metrics
- Batch testing across all patterns

### Hybrid Memory Demo

**URL**: http://localhost:8001/experiments/hybrid-memory/

Simple demo using factorized memory engines.

### 🧠 Rule Predictor AI (Phase 3 ✅)

**URL**: http://localhost:8001/experiments/rule-predictor/

ML-powered prediction of memory-capable CA rules.

**Features**:
- Logistic regression trained on validated datasets
- Predict memory score (0-100%) for any B/S rule
- Auto-suggest top 20 promising candidates
- Validation table (predicted vs actual)
- Links to Memory AI Lab for testing

**No external libs** - Pure vanilla JS ML implementation.

### 🤖 Auto Memory Researcher (Phase 4 ✅)

**URL**: http://localhost:8001/experiments/auto-memory-research/

Integrated ML-guided rule discovery and validation pipeline.

**Features**:
- Automated candidate generation and ML scoring
- Real-time validation with Memory Capacity protocol
- Compare ML predictions vs. actual performance
- Export results as JSON
- Full pipeline automation with `AutoMemoryResearch.runAll()`

**Perfect integration** - Uses all existing primitives without breaking changes.

### 🎯 Engine Selector Demo (Phase 5 ✅)

**URL**: http://localhost:8001/experiments/engine-selector-demo/

Meta-learner that predicts optimal memory engine per pattern.

**Features**:
- Learns from MemoryAI.recall() results (8 engines × patterns)
- Predicts best engine before testing (8× faster)
- Quick demo + full benchmark (100 samples)
- Performance metrics: speedup, accuracy, win distribution

**Meta-learning** - Optimizes engine selection for 80-95% accuracy with 6-8× speedup.

## Features

### Core CA Engine
- **13 Life-like CA rules** including classics (Conway, HighLife, Day & Night, Seeds, Replicator)
- **Custom rules**: Mythmaker, Mahee, Tommy
- **Promoted rules**: 5 automatically discovered high-scoring rules (Mythmaker_1/2, Mahee_1, Tommy_1/2)
- **Real-time visualization** with play/pause/step controls
- **Speed control** (0.1x to 3x)

### Advanced Features
- **Energy view** (checkbox): color heatmap showing local energy (green=stable, red=unstable)
- **Live metrics**: density, entropy, population, energy
- **Real-time graph**: density and energy evolution over time
- **Pattern detection**: automatic oscillator period detection
- **Rule Explorer**: "Discover rules" button finds interesting Life-like rules automatically
- **Random rule**: generate random Life-like rules on demand
- **Next rule**: cycle through interesting rules

### Developer Tools
- `IsingAnalysis` exposed to console for rule analysis
- Batch analysis of discovered and promoted rules
- `generatePromotionCode()` to identify top candidates

## Architecture

- `/src/core/`: Grid logic and CA engine
- `/src/presets/`: Predefined rulesets (including Hall of Fame)
- `/src/viz/`: Canvas rendering and UI
- `/src/metrics/`: Complexity measurements
- `/src/energy/`: Local energy functions (extensible)
- `/src/search/`: Rule discovery and exploration
- `/src/memory/`: Memory analysis and attractor detection
- `/src/experiments/`: Analysis utilities for discovered rules
- `/experiments/memory-ai-lab/`: Standalone Memory AI Lab (branch: memory-ai-lab)

## Promoted Rules

The following rules were discovered via the automatic Rule Explorer and promoted based on high scores (1.82-1.88), measured by entropy, density balance, and variation:

- **Mythmaker_1 (B2456/S5)**: Complex rule with high score (~1.88)
- **Mythmaker_2 (B01/S3)**: Clean period-2 oscillator
- **Mahee_1 (B0345/S8)**: Complex patterns with good stability
- **Tommy_1 (B1245/S)**: Seeds-like with interesting dynamics
- **Tommy_2 (B018/S)**: Elegant period-2 oscillator

These rules are excellent candidates for studying:
- Energy landscapes and stability
- Pattern formation and memory
- Edge-of-chaos behavior
- Ising-style Hamiltonian learning

## Extending

### Add custom rules
Edit `src/presets/rules.js`:
```javascript
{ name: "MyRule (B3/S23)", born: [3], survive: [2,3] }
```

### Discover new rules
Click "Discover rules" to automatically find interesting rules, or use the console:
```javascript
await IsingAnalysis.analyzeFoundRules({ runs: 10, steps: 80 });
IsingAnalysis.generatePromotionCode(5);
```

## Roadmap

- [ ] Pattern detection (gliders, oscillators)
- [ ] Learn energy functions approximating CA dynamics
- [ ] Rule search for edge-of-chaos regimes
- [ ] Connect to Hopfield networks / Ising machines
- [ ] Energy visualization (color heatmap)

## License

MIT

