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

### Memory AI Lab (Experimental)

Explore memory experiments with CA vs Hopfield networks:
```bash
python -m http.server 8001
# Then open http://localhost:8001/experiments/memory-ai-lab/index.html
```

Features:
- **CA Playground**: Test Hall of Fame rules (Seed_1.88a, Seed_1.88b, etc.)
- **Memory Lab**: Draw patterns, test memory recall with noise
- **Hopfield Comparison**: Compare CA memory vs classical Hopfield networks

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

