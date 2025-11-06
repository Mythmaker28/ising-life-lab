# Ising Life Lab

A minimal sandbox exploring Life-like cellular automata, Ising-style energies, and energy-based models.

**Status**: Working V1 - all files have content, application is functional.

## Quick Start

1. Clone repository
2. Open `public/index.html` in modern browser via HTTP server:
   ```bash
   python -m http.server 8000
   # Then open http://localhost:8000/public/index.html
   ```
3. Select rule, click Randomize, click Start

## Features

- **5+ Life-like CA rules** (Conway, HighLife, Day & Night, Seeds, Replicator)
- **Real-time visualization** with play/pause/step controls
- **Speed control** (0.1x to 3x)
- **Live metrics**: density, entropy, population, energy
- **Energy stub**: placeholder for pseudo-Ising Hamiltonians
- **Glider preset**: quick demo of Conway's Life glider

## Architecture

- `/src/core/`: Grid logic and CA engine
- `/src/presets/`: Predefined rulesets
- `/src/viz/`: Canvas rendering and UI
- `/src/metrics/`: Complexity measurements
- `/src/energy/`: Local energy functions (extensible)

## Extending

Add new rules in `src/presets/rules.js`:

```javascript
{ name: "MyRule (B3/S23)", born: [3], survive: [2,3] }
```

## Roadmap

- [ ] Pattern detection (gliders, oscillators)
- [ ] Learn energy functions approximating CA dynamics
- [ ] Rule search for edge-of-chaos regimes
- [ ] Connect to Hopfield networks / Ising machines
- [ ] Energy visualization (color heatmap)

## License

MIT

