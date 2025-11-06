/**
 * Canvas rendering and UI controls for cellular automata visualization.
 * Handles animation loop, user interactions, and real-time updates.
 */

import { createGrid, randomizeGrid } from '../core/caGrid.js';
import { step } from '../core/caStep.js';
import { RULES } from '../presets/rules.js';
import { getBasicMetrics } from '../metrics/metrics.js';
import { totalEnergy } from '../energy/localEnergyStub.js';

// Global state
let grid = null;
let currentRule = RULES[0];
let animationId = null;
let cellSize = 8; // pixels per cell
let lastStepTime = 0;
let speedMultiplier = 1.0; // 0.1x to 3x

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
  
  // Get canvas context
  ctx = canvas.getContext('2d');
  
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
  
  if (gliderBtn) {
    gliderBtn.addEventListener('click', () => {
      if (grid) {
        // Clear grid
        const width = grid[0].length;
        const height = grid.length;
        grid = createGrid(width, height, 0);
        
        // Draw glider pattern (Conway's Life glider)
        // Position: center-ish, with bounds checking
        const centerX = Math.floor(width / 2);
        const centerY = Math.floor(height / 2);
        
        // Glider pattern (5 cells) - correct Conway's Life glider
        // Pattern (relative to center):
        //   . . .
        //   . . X
        //   X . X
        //   . X X
        // Ensure we're within bounds
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
 * Alive cells = black, dead cells = white.
 * Auto-centers the grid if it doesn't fill the entire canvas.
 * 
 * @param {Array<Array<0|1>>} gridToRender - Grid to draw
 */
function render(gridToRender) {
  if (!ctx || !canvas) {
    console.error('Cannot render: canvas or context not initialized');
    return;
  }
  
  const height = gridToRender.length;
  const width = gridToRender[0].length;
  
  // Clear canvas
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  // Calculate offset to center the grid
  const gridWidth = width * cellSize;
  const gridHeight = height * cellSize;
  const offsetX = Math.floor((canvas.width - gridWidth) / 2);
  const offsetY = Math.floor((canvas.height - gridHeight) / 2);
  
  // Draw cells
  ctx.fillStyle = '#000000';
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      if (gridToRender[y][x] === 1) {
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

/**
 * Updates the metrics display.
 * Updates every frame, but could be throttled for performance.
 * 
 * @param {Array<Array<0|1>>} gridToMeasure - Grid to analyze
 */
function updateMetrics(gridToMeasure) {
  if (!metricsDiv) {
    console.error('Cannot update metrics: metricsDiv not initialized');
    return;
  }
  
  const metrics = getBasicMetrics(gridToMeasure);
  const energy = totalEnergy(gridToMeasure);
  metricsDiv.textContent = 
    `Density: ${metrics.density.toFixed(3)}, ` +
    `Entropy: ${metrics.entropy.toFixed(3)} bits, ` +
    `Population: ${metrics.population}, ` +
    `Energy: ${energy.toFixed(0)}`;
}

/**
 * Starts the animation loop.
 * Uses speed multiplier to control step frequency.
 * Speed: 0.1x = slow, 1.0x = normal, 3.0x = fast
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
      
      // Update metrics every step
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

