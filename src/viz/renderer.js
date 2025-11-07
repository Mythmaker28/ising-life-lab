/**
 * Canvas rendering and UI controls for cellular automata visualization.
 * Handles animation loop, user interactions, and real-time updates.
 * V2: adds energy view, pattern detection, metrics graph, next rule button.
 */

import { createGrid, randomizeGrid } from '../core/caGrid.js';
import { step } from '../core/caStep.js';
import { RULES, HOF_RULES } from '../presets/rules.js';
import { getBasicMetrics } from '../metrics/metrics.js';
import { totalEnergy, localEnergy } from '../energy/localEnergyStub.js';
import { exploreRules } from '../search/ruleExplorer.js';
import { analyzeRule, analyzeFoundRules, analyzePromotedRules, generatePromotionCode } from '../experiments/ruleAnalysis.js';
import { initMemoryLab } from '../memory/memoryLab.js';
import { getRuleByName, scanAttractors } from '../memory/attractorScan.js';
import { scanForMemoryRules } from '../search/memoryRuleSearch.js';
import { evolveMemoryRules, extremeMemorySearch } from '../search/advancedMemorySearch.js';

// Expose analysis functions to console for dev/research use
if (typeof window !== 'undefined') {
  window.IsingAnalysis = {
    ...(window.IsingAnalysis || {}),
    analyzeRule, 
    analyzeFoundRules, 
    analyzePromotedRules,
    generatePromotionCode,
    scanAttractors,
    scanForMemoryRules,
    evolveMemoryRules,
    extremeMemorySearch,
    getRuleByName,
    RULES 
  };
  console.log('✅ IsingAnalysis exposed with', Object.keys(window.IsingAnalysis).length, 'functions');
}

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

// Next Rule button: cycles through interesting rules (predefined + found)
let currentInterestingIndex = 0;

/**
 * Gets indices of interesting rules (predefined + promoted + any Found rules)
 */
function getInterestingRuleIndices() {
  const indices = [];
  
  // Add all predefined and promoted rules (everything except "Found:" and "Random")
  RULES.forEach((rule, index) => {
    const name = rule.name || '';
    if (!name.startsWith('Found:') && !name.startsWith('Random') && !name.startsWith('Auto')) {
      indices.push(index);
    }
  });
  
  // Add any "Found:" rules
  RULES.forEach((rule, index) => {
    if (rule.name.startsWith('Found:') && !indices.includes(index)) {
      indices.push(index);
    }
  });
  
  return indices;
}

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
let randomRuleBtn = null;
let discoverRulesBtn = null;
let searchMemoryBtn = null;
let deepMemoryBtn = null;
let extremeSearchBtn = null;
let discoverSummary = null;
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
  randomRuleBtn = document.getElementById('randomRuleBtn');
  discoverRulesBtn = document.getElementById('discoverRulesBtn');
  searchMemoryBtn = document.getElementById('searchMemoryBtn');
  deepMemoryBtn = document.getElementById('deepMemoryBtn');
  extremeSearchBtn = document.getElementById('extremeSearchBtn');
  discoverSummary = document.getElementById('discoverSummary');
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
  console.log('RULES loaded:', RULES.length, 'rules + HOF:', HOF_RULES.length);
  
  // Combine HOF + RULES for unified access
  const allRules = [...HOF_RULES, ...RULES];
  
  // Populate rule dropdown with Hall of Fame first
  const hofGroup = document.createElement('optgroup');
  hofGroup.label = '🏆 Hall of Fame (Top Memory Rules)';
  HOF_RULES.forEach((rule, index) => {
    const option = document.createElement('option');
    option.value = index;
    option.textContent = rule.name;
    hofGroup.appendChild(option);
  });
  ruleSelect.appendChild(hofGroup);
  
  // Then add all other rules
  const otherGroup = document.createElement('optgroup');
  otherGroup.label = 'All Rules';
  RULES.forEach((rule, index) => {
    const option = document.createElement('option');
    option.value = HOF_RULES.length + index;
    option.textContent = rule.name;
    otherGroup.appendChild(option);
  });
  ruleSelect.appendChild(otherGroup);
  
  // Update global RULES reference to combined list
  RULES.length = 0;
  RULES.push(...allRules);
  
  // Set default to first HOF rule (Seed_1.88a)
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
      const interestingRules = getInterestingRuleIndices();
      currentInterestingIndex = (currentInterestingIndex + 1) % interestingRules.length;
      const ruleIndex = interestingRules[currentInterestingIndex];
      ruleSelect.value = ruleIndex;
      currentRule = RULES[ruleIndex];
      console.log('Next rule:', currentRule.name);
      render(grid);
      updateMetrics(grid);
    });
  }
  
  if (randomRuleBtn) {
    randomRuleBtn.addEventListener('click', () => {
      const newRule = generateRandomRule();
      RULES.push(newRule);
      
      // Add to dropdown
      const option = document.createElement('option');
      option.value = RULES.length - 1;
      option.textContent = newRule.name;
      ruleSelect.appendChild(option);
      
      // Select it
      ruleSelect.value = RULES.length - 1;
      currentRule = newRule;
      console.log('Random rule generated:', newRule.name);
      render(grid);
      updateMetrics(grid);
    });
  }
  
  if (discoverRulesBtn) {
    discoverRulesBtn.addEventListener('click', () => {
      // Disable button during search
      discoverRulesBtn.disabled = true;
      discoverRulesBtn.textContent = 'Searching...';
      
      if (discoverSummary) {
        discoverSummary.textContent = 'Exploring 30 random rules...';
        discoverSummary.className = 'visible';
      }
      
      // Run exploration after small delay to update UI
      setTimeout(() => {
        try {
          console.log('🔍 Starting rule exploration (30 candidates)...');
          const results = exploreRules(30, { width: 40, height: 40, steps: 60 });
          
          if (results.length === 0) {
            // No interesting rules found
            if (discoverSummary) {
              discoverSummary.textContent = 'No interesting rules found. Try again!';
            }
            console.log('❌ No complex rules passed the criteria.');
          } else {
            // Log results
            console.log(`✅ Found ${results.length} interesting rules:`);
            console.table(results.map(r => ({
              name: r.rule.name,
              born: r.rule.born.join(''),
              survive: r.rule.survive.join(''),
              type: r.type,
              score: r.score.toFixed(3),
              densityFinal: r.densityFinal.toFixed(3),
              entropyMean: r.entropyMean.toFixed(3),
              variationMean: r.variationMean.toFixed(3),
              period: r.period || '-'
            })));
            
            // Add rules to RULES if not duplicate
            let addedCount = 0;
            results.forEach(result => {
              const rule = result.rule;
              
              // Check if rule already exists
              const exists = RULES.some(r => 
                JSON.stringify(r.born) === JSON.stringify(rule.born) &&
                JSON.stringify(r.survive) === JSON.stringify(rule.survive)
              );
              
              if (!exists) {
                // Rename to "Found: ..." with type and score
                const typeLabel = result.type === 'oscillating' ? `osc.p${result.period}` : result.type;
                rule.name = `Found: B${rule.born.join('')}/S${rule.survive.join('')} [${typeLabel}, ${result.score.toFixed(2)}]`;
                RULES.push(rule);
                
                // Add to dropdown
                const option = document.createElement('option');
                option.value = RULES.length - 1;
                option.textContent = rule.name;
                ruleSelect.appendChild(option);
                
                addedCount++;
              }
            });
            
            if (addedCount > 0) {
              if (discoverSummary) {
                discoverSummary.textContent = `✓ Found ${addedCount} interesting rule${addedCount > 1 ? 's' : ''}! Check dropdown for "Found: B.../S..." entries.`;
              }
              console.log(`➕ Added ${addedCount} new rule${addedCount > 1 ? 's' : ''} to the selector.`);
            } else {
              if (discoverSummary) {
                discoverSummary.textContent = `Found ${results.length} rule${results.length > 1 ? 's' : ''} (already in list).`;
              }
              console.log('ℹ️ All found rules already exist in selector.');
            }
          }
        } catch (error) {
          console.error('❌ Error while searching rules:', error);
          if (discoverSummary) {
            discoverSummary.textContent = 'Error while searching rules (see console).';
          }
        } finally {
          // Always re-enable button
          discoverRulesBtn.disabled = false;
          discoverRulesBtn.textContent = 'Discover rules';
        }
      }, 50);
    });
  }
  
  if (searchMemoryBtn) {
    searchMemoryBtn.addEventListener('click', async () => {
      if (!window.IsingAnalysis || !window.IsingAnalysis.scanForMemoryRules) {
        console.error('❌ scanForMemoryRules not available');
        return;
      }
      
      searchMemoryBtn.disabled = true;
      searchMemoryBtn.textContent = 'Scanning...';
      
      try {
        const result = await window.IsingAnalysis.scanForMemoryRules({
          candidates: 40,
          runs: 40,
          steps: 80,
          noise: 0.05
        });
        
        console.log('');
        console.log('📊 Memory search complete!');
        console.log(`   Memory-like: ${result.memoryLike.length}`);
        console.log(`   Weak-memory: ${result.weakMemory.length}`);
        console.log(`   Chaotic: ${result.chaotic.length}`);
        console.log(`   Frozen: ${result.frozen.length}`);
      } catch (error) {
        console.error('❌ Error during memory search:', error);
      } finally {
        searchMemoryBtn.disabled = false;
        searchMemoryBtn.textContent = 'Search memory rules';
      }
    });
  }
  
  if (deepMemoryBtn) {
    deepMemoryBtn.addEventListener('click', async () => {
      if (!window.IsingAnalysis || !window.IsingAnalysis.evolveMemoryRules) {
        console.error('❌ evolveMemoryRules not available');
        return;
      }
      
      deepMemoryBtn.disabled = true;
      deepMemoryBtn.textContent = 'Evolving...';
      
      try {
        const result = await window.IsingAnalysis.evolveMemoryRules({
          populationSize: 60,
          generations: 4,
          runs: 40,
          steps: 90,
          noise: 0.05,
          topK: 20
        });
        
        console.log('');
        console.log('🎯 Deep memory evolution complete!');
        console.table(result.top.slice(0, 5));
      } catch (error) {
        console.error('❌ Error during deep search:', error);
      } finally {
        deepMemoryBtn.disabled = false;
        deepMemoryBtn.textContent = 'Deep memory search';
      }
    });
  }
  
  if (extremeSearchBtn) {
    extremeSearchBtn.addEventListener('click', async () => {
      if (!window.IsingAnalysis || !window.IsingAnalysis.extremeMemorySearch) {
        console.error('❌ extremeMemorySearch not available');
        return;
      }
      
      extremeSearchBtn.disabled = true;
      extremeSearchBtn.textContent = 'Extreme running...';
      
      if (discoverSummary) {
        discoverSummary.textContent = 'Running extreme search (2-5 min)...';
        discoverSummary.className = 'visible';
      }
      
      try {
        const result = await window.IsingAnalysis.extremeMemorySearch({
          populationSize: 200,
          generations: 8,
          runsPerRule: 60
        });
        
        if (discoverSummary) {
          const top3 = result.top.slice(0, 3).map(r => 
            `B${r.rule.born.join('')}/S${r.rule.survive.join('')}`
          ).join(', ');
          discoverSummary.textContent = `✅ Top extreme memory rules: ${top3} (see console)`;
        }
        
        console.log('');
        console.log('🎊 EXTREME SEARCH COMPLETE - Check memory-results-extreme.md');
      } catch (error) {
        console.error('❌ Error during extreme search:', error);
        if (discoverSummary) {
          discoverSummary.textContent = 'Error during extreme search (see console)';
        }
      } finally {
        extremeSearchBtn.disabled = false;
        extremeSearchBtn.textContent = 'Extreme search';
      }
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
  
  // Initialize Memory Lab
  initMemoryLab();
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

/**
 * Generates a random Life-like rule.
 * Born and survive are random subsets of {0..8}.
 * @returns {Object} Rule object with name, born, survive
 */
function generateRandomRule() {
  const born = [];
  const survive = [];
  
  // Randomly select numbers for born (probability 0.3 for each)
  for (let i = 0; i <= 8; i++) {
    if (Math.random() < 0.3) {
      born.push(i);
    }
  }
  
  // Randomly select numbers for survive (probability 0.3 for each)
  for (let i = 0; i <= 8; i++) {
    if (Math.random() < 0.3) {
      survive.push(i);
    }
  }
  
  // Format name
  const bornStr = born.join('');
  const surviveStr = survive.join('');
  const name = `Random (B${bornStr}/S${surviveStr})`;
  
  return {
    name: name,
    born: born,
    survive: survive
  };
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
