/**
 * Canvas rendering and UI controls for cellular automata visualization.
 * Handles animation loop, user interactions, and real-time updates.
 * V2: adds energy view, pattern detection, metrics graph, next rule button.
 */

import { createGrid, randomizeGrid } from '../core/caGrid.js';
import { step } from '../core/caStep.js';
import { RULES } from '../presets/rules.js';
import { getBasicMetrics } from '../metrics/metrics.js';
import { totalEnergy, localEnergy } from '../energy/localEnergyStub.js';

// Global state
let grid = null;
let currentRule = RULES[0];
let animationId = null;
let cellSize = 8; // pixels per cell
let lastStepTime = 0;
let speedMultiplier = 1.0; // 0.1x to 3x
let generationCount = 0;

// Metrics history for graphing (max 200 points)
let historyDensity = [];
let historyEnergy = [];
const MAX_HISTORY = 200;

// Pattern detection
let previousStates = new Map();
let detectedPattern = '';

// Interesting rules indices for Next Rule button
const INTERESTING_RULES = [0, 1, 2, 5, 6, 7]; // Conway, HighLife, Day&Night, Mythmaker, Mahee, Tommy
let currentInterestingIndex = 0;

// DOM elements (will be initialized in init())
let canvas = null;
let ctx = null;
let ruleSelect = null;
let startBtn = null;
let stopBtn = null;
let stepBtn = null;
let randomBtn = null;
let clearBtn = null;
let gliderBtn = null;
let speedRange = null;
let speedValue = null;
let metricsDiv = null;
let energyViewCheckbox = null;
let nextRuleBtn = null;
let metricsGraph = null;
let metricsGraphCtx = null;

/**
 * Initializes the grid and UI.
 */
function init() {
  // Get DOM elements (must be done after DOM is ready)
  canvas = document.getElementById('canvas');
  ruleSelect = document.getElementById('ruleSelect');
  startBtn = document.getElementById('startBtn');
  stopBtn = document.getElementById('stopBtn');
  stepBtn = document.getElementById('stepBtn');
  randomBtn = document.getElementById('randomBtn');
  clearBtn = document.getElementById('clearBtn');
  gliderBtn = document.getElementById('gliderBtn');
  speedRange = document.getElementById('speedRange');
  speedValue = document.getElementById('speedValue');
  metricsDiv = document.getElementById('metrics');
  energyViewCheckbox = document.getElementById('energyView');
  nextRuleBtn = document.getElementById('nextRuleBtn');
  metricsGraph = document.getElementById('metricsGraph');
  
  // Check for missing elements
  if (!canvas) {
    console.error('Missing element: canvas');
    return;
  }
  if (!ruleSelect) {
    console.error('Missing element: ruleSelect');
    return;
  }
  if (!startBtn || !stopBtn || !stepBtn || !randomBtn || !clearBtn) {
    console.error('Missing button elements');
    return;
  }
  if (!metricsDiv) {
    console.error('Missing element: metrics');
    return;
  }
  
  // Get canvas contexts
  ctx = canvas.getContext('2d');
  if (metricsGraph) {
    metricsGraphCtx = metricsGraph.getContext('2d');
  }
  
  // Debug: verify RULES is loaded
  console.log('RULES loaded:', RULES.length, 'rules');
  
  // Populate rule dropdown
  RULES.forEach((rule, index) => {
    const option = document.createElement('option');
    option.value = index;
    option.textContent = rule.name;
    ruleSelect.appendChild(option);
  });
  
  // Set default to Conway (first rule)
  ruleSelect.value = 0;
  currentRule = RULES[0];
  
  // Create initial grid (100x75 cells)
  const width = 100;
  const height = 75;
  
  // Auto-compute cell size to fit canvas
  cellSize = Math.min(
    Math.floor(canvas.width / width),
    Math.floor(canvas.height / height)
  );
  
  // Create initial grid and randomize
  grid = createGrid(width, height, 0);
  randomizeGrid(grid, 0.25);
  
  // Render initial state
  render(grid);
  updateMetrics(grid);
  
  // Set up event listeners
  ruleSelect.addEventListener('change', () => {
    currentRule = RULES[parseInt(ruleSelect.value)];
    console.log('Rule changed to:', currentRule.name);
    render(grid);
    updateMetrics(grid);
  });
  
  if (speedRange) {
    speedRange.addEventListener('input', (e) => {
      speedMultiplier = parseFloat(e.target.value);
      if (speedValue) {
        speedValue.textContent = speedMultiplier.toFixed(1) + 'x';
      }
    });
  }
  
  startBtn.addEventListener('click', () => {
    console.log('Start button clicked');
    startAnimation();
  });
  stopBtn.addEventListener('click', () => {
    console.log('Stop button clicked');
    stopAnimation();
  });
  stepBtn.addEventListener('click', () => {
    console.log('Step button clicked');
    if (grid) {
      grid = step(grid, currentRule);
      render(grid);
      updateMetrics(grid);
    }
  });
  
  randomBtn.addEventListener('click', () => {
    console.log('Randomize button clicked');
    if (grid) {
      randomizeGrid(grid, 0.25);
      render(grid);
      updateMetrics(grid);
    }
  });
  
  if (nextRuleBtn) {
    nextRuleBtn.addEventListener('click', () => {
      currentInterestingIndex = (currentInterestingIndex + 1) % INTERESTING_RULES.length;
      const ruleIndex = INTERESTING_RULES[currentInterestingIndex];
      ruleSelect.value = ruleIndex;
      currentRule = RULES[ruleIndex];
      console.log('Next rule:', currentRule.name);
      render(grid);
      updateMetrics(grid);
    });
  }
  
  if (gliderBtn) {
    gliderBtn.addEventListener('click', () => {
      if (grid) {
        // Clear grid
        const width = grid[0].length;
        const height = grid.length;
        grid = createGrid(width, height, 0);
        
        // Draw glider pattern (Conway's Life glider)
        const centerX = Math.floor(width / 2);
        const centerY = Math.floor(height / 2);
        
        // Glider pattern (5 cells)
        if (centerY > 0 && centerX < width - 1) {
          grid[centerY - 1][centerX + 1] = 1;
        }
        if (centerX > 0 && centerX < width - 1) {
          grid[centerY][centerX - 1] = 1;
          grid[centerY][centerX + 1] = 1;
        }
        if (centerY < height - 1 && centerX < width - 1) {
          grid[centerY + 1][centerX] = 1;
          grid[centerY + 1][centerX + 1] = 1;
        }
        
        render(grid);
        updateMetrics(grid);
      }
    });
  }
  
  clearBtn.addEventListener('click', () => {
    if (grid) {
      const width = grid[0].length;
      const height = grid.length;
      grid = createGrid(width, height, 0);
      render(grid);
      updateMetrics(grid);
    }
  });
}

/**
 * Renders the grid to canvas.
 * Normal mode: alive = black, dead = white.
 * Energy view mode: color-coded by local energy (green = stable, red = unstable).
 */
function render(gridToRender) {
  if (!ctx || !canvas) {
    console.error('Cannot render: canvas or context not initialized');
    return;
  }
  
  const height = gridToRender.length;
  const width = gridToRender[0].length;
  const isEnergyView = energyViewCheckbox && energyViewCheckbox.checked;
  
  // Clear canvas
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  // Calculate offset to center the grid
  const gridWidth = width * cellSize;
  const gridHeight = height * cellSize;
  const offsetX = Math.floor((canvas.width - gridWidth) / 2);
  const offsetY = Math.floor((canvas.height - gridHeight) / 2);
  
  // Draw cells
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const cell = gridToRender[y][x];
      
      if (isEnergyView) {
        // Energy view: color-code by local energy
        const energy = localEnergy(gridToRender, x, y);
        
        if (cell === 1) {
          // Alive cell: hue based on energy (green=stable, red=unstable)
          const hue = Math.max(0, 120 - Math.min(energy * 30, 120));
          ctx.fillStyle = `hsl(${hue}, 100%, 50%)`;
          ctx.fillRect(
            offsetX + x * cellSize,
            offsetY + y * cellSize,
            cellSize,
            cellSize
          );
        } else {
          // Dead cell: light color if has energy
          if (energy > 0) {
            ctx.fillStyle = `rgba(255, 200, 200, 0.3)`;
            ctx.fillRect(
              offsetX + x * cellSize,
              offsetY + y * cellSize,
              cellSize,
              cellSize
            );
          }
        }
      } else {
        // Normal view: black for alive
        if (cell === 1) {
          ctx.fillStyle = '#000000';
          ctx.fillRect(
            offsetX + x * cellSize,
            offsetY + y * cellSize,
            cellSize,
            cellSize
          );
        }
      }
    }
  }
}

/**
 * Updates the metrics display with pattern detection.
 * Tracks metrics history for graphing and detects oscillating patterns.
 */
function updateMetrics(gridToMeasure) {
  if (!metricsDiv) {
    console.error('Cannot update metrics: metricsDiv not initialized');
    return;
  }
  
  generationCount++;
  
  const metrics = getBasicMetrics(gridToMeasure);
  const energy = totalEnergy(gridToMeasure);
  
  // Update metrics history for graphing
  historyDensity.push(metrics.density);
  historyEnergy.push(energy);
  if (historyDensity.length > MAX_HISTORY) {
    historyDensity.shift();
    historyEnergy.shift();
  }
  
  // Simple pattern detection: check if we've seen this state before
  const gridHash = gridToMeasure.map(row => row.join('')).join('|');
  
  if (previousStates.has(gridHash)) {
    const previousGen = previousStates.get(gridHash);
    const period = generationCount - previousGen;
    if (period > 0) {
      detectedPattern = ` (oscillator period ${period})`;
    }
  } else {
    previousStates.set(gridHash, generationCount);
    detectedPattern = '';
  }
  
  // Clear old states if map gets too large (keep last 100)
  if (previousStates.size > 100) {
    const keysToDelete = Array.from(previousStates.keys()).slice(0, previousStates.size - 100);
    keysToDelete.forEach(key => previousStates.delete(key));
  }
  
  metricsDiv.textContent = 
    `Density: ${metrics.density.toFixed(3)}, ` +
    `Entropy: ${metrics.entropy.toFixed(3)} bits, ` +
    `Population: ${metrics.population}, ` +
    `Energy: ${energy.toFixed(0)}${detectedPattern}`;
  
  // Draw metrics graph
  drawMetricsGraph();
}

/**
 * Draws the metrics evolution graph (density and energy over time).
 */
function drawMetricsGraph() {
  if (!metricsGraphCtx || !metricsGraph) {
    return;
  }
  
  const width = metricsGraph.width;
  const height = metricsGraph.height;
  const ctx = metricsGraphCtx;
  
  // Clear canvas
  ctx.fillStyle = '#f9f9f9';
  ctx.fillRect(0, 0, width, height);
  
  if (historyDensity.length < 2) {
    return; // Need at least 2 points to draw
  }
  
  const numPoints = historyDensity.length;
  const xStep = width / (MAX_HISTORY - 1);
  const xOffset = width - (numPoints - 1) * xStep;
  
  // Find max energy for scaling
  const maxEnergy = Math.max(...historyEnergy, 1);
  
  // Draw density line (blue)
  ctx.strokeStyle = '#2196F3';
  ctx.lineWidth = 2;
  ctx.beginPath();
  for (let i = 0; i < numPoints; i++) {
    const x = xOffset + i * xStep;
    const y = height - (historyDensity[i] * height * 0.9);
    if (i === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  }
  ctx.stroke();
  
  // Draw energy line (red, rescaled)
  ctx.strokeStyle = '#f44336';
  ctx.lineWidth = 2;
  ctx.beginPath();
  for (let i = 0; i < numPoints; i++) {
    const x = xOffset + i * xStep;
    const normalizedEnergy = historyEnergy[i] / maxEnergy;
    const y = height - (normalizedEnergy * height * 0.9);
    if (i === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  }
  ctx.stroke();
  
  // Draw legend
  ctx.font = '12px monospace';
  ctx.fillStyle = '#2196F3';
  ctx.fillText('Density', 10, 15);
  ctx.fillStyle = '#f44336';
  ctx.fillText('Energy', 10, 30);
}

/**
 * Starts the animation loop.
 */
function startAnimation() {
  if (animationId) return; // Already running
  
  lastStepTime = performance.now();
  
  function loop(currentTime) {
    if (!grid) {
      animationId = null;
      return;
    }
    
    // Calculate time delta and apply speed multiplier
    const deltaTime = currentTime - lastStepTime;
    const baseInterval = 100; // 100ms base interval (10 steps/sec at 1.0x)
    const targetInterval = baseInterval / speedMultiplier;
    
    if (deltaTime >= targetInterval) {
      grid = step(grid, currentRule);
      render(grid);
      updateMetrics(grid);
      
      lastStepTime = currentTime;
    }
    
    animationId = requestAnimationFrame(loop);
  }
  
  animationId = requestAnimationFrame(loop);
}

/**
 * Stops the animation loop.
 */
function stopAnimation() {
  if (animationId) {
    cancelAnimationFrame(animationId);
    animationId = null;
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
