/**
 * Memory Lab UI: interactive pattern drawing and attractor scanning.
 */

import { createGrid, randomizeGrid } from '../core/caGrid.js';
import { RULES } from '../presets/rules.js';
import { getRuleByName, scanAttractors } from './attractorScan.js';

// Memory Lab state
let memoryGrid = null;
let memoryWidth = 32;
let memoryHeight = 32;
let cellSize = 8;

// DOM elements
let memoryCanvas = null;
let memoryCtx = null;
let memoryRuleSelect = null;
let memoryNoise = null;
let memoryNoiseValue = null;
let memorySteps = null;
let memoryRuns = null;
let memoryClearBtn = null;
let memoryRandomBtn = null;
let memoryScanBtn = null;
let memoryResults = null;

/**
 * Initializes the Memory Lab UI.
 */
export function initMemoryLab() {
  // Get DOM elements
  memoryCanvas = document.getElementById('memoryCanvas');
  memoryRuleSelect = document.getElementById('memoryRuleSelect');
  memoryNoise = document.getElementById('memoryNoise');
  memoryNoiseValue = document.getElementById('memoryNoiseValue');
  memorySteps = document.getElementById('memorySteps');
  memoryRuns = document.getElementById('memoryRuns');
  memoryClearBtn = document.getElementById('memoryClearBtn');
  memoryRandomBtn = document.getElementById('memoryRandomBtn');
  memoryScanBtn = document.getElementById('memoryScanBtn');
  memoryResults = document.getElementById('memoryResults');
  
  if (!memoryCanvas || !memoryRuleSelect || !memoryScanBtn) {
    console.log('Memory Lab elements not found, skipping initialization.');
    return;
  }
  
  memoryCtx = memoryCanvas.getContext('2d');
  cellSize = memoryCanvas.width / memoryWidth;
  
  // Initialize grid
  memoryGrid = createGrid(memoryWidth, memoryHeight, 0);
  
  // Populate rule select with promoted rules
  const promotedRules = RULES.filter(r => {
    const name = r.name || '';
    return name.startsWith('Mythmaker_') || name.startsWith('Mahee_') || name.startsWith('Tommy_');
  });
  
  promotedRules.forEach(rule => {
    const option = document.createElement('option');
    option.value = rule.name;
    option.textContent = rule.name;
    memoryRuleSelect.appendChild(option);
  });
  
  // Render initial state
  renderMemoryGrid();
  
  // Event listeners
  memoryCanvas.addEventListener('click', (e) => {
    const rect = memoryCanvas.getBoundingClientRect();
    const x = Math.floor((e.clientX - rect.left) / cellSize);
    const y = Math.floor((e.clientY - rect.top) / cellSize);
    
    if (x >= 0 && x < memoryWidth && y >= 0 && y < memoryHeight) {
      memoryGrid[y][x] = 1 - memoryGrid[y][x]; // Toggle
      renderMemoryGrid();
    }
  });
  
  if (memoryNoise && memoryNoiseValue) {
    memoryNoise.addEventListener('input', (e) => {
      memoryNoiseValue.textContent = parseFloat(e.target.value).toFixed(2);
    });
  }
  
  if (memoryClearBtn) {
    memoryClearBtn.addEventListener('click', () => {
      memoryGrid = createGrid(memoryWidth, memoryHeight, 0);
      renderMemoryGrid();
    });
  }
  
  if (memoryRandomBtn) {
    memoryRandomBtn.addEventListener('click', () => {
      randomizeGrid(memoryGrid, 0.2);
      renderMemoryGrid();
    });
  }
  
  if (memoryScanBtn) {
    memoryScanBtn.addEventListener('click', runMemoryTest);
  }
  
  console.log('✅ Memory Lab initialized');
}

/**
 * Renders the memory grid to canvas.
 */
function renderMemoryGrid() {
  if (!memoryCtx || !memoryCanvas) return;
  
  // Clear
  memoryCtx.fillStyle = '#ffffff';
  memoryCtx.fillRect(0, 0, memoryCanvas.width, memoryCanvas.height);
  
  // Draw grid lines (light gray)
  memoryCtx.strokeStyle = '#e0e0e0';
  memoryCtx.lineWidth = 1;
  for (let x = 0; x <= memoryWidth; x++) {
    memoryCtx.beginPath();
    memoryCtx.moveTo(x * cellSize, 0);
    memoryCtx.lineTo(x * cellSize, memoryCanvas.height);
    memoryCtx.stroke();
  }
  for (let y = 0; y <= memoryHeight; y++) {
    memoryCtx.beginPath();
    memoryCtx.moveTo(0, y * cellSize);
    memoryCtx.lineTo(memoryCanvas.width, y * cellSize);
    memoryCtx.stroke();
  }
  
  // Draw cells
  memoryCtx.fillStyle = '#000000';
  for (let y = 0; y < memoryHeight; y++) {
    for (let x = 0; x < memoryWidth; x++) {
      if (memoryGrid[y][x] === 1) {
        memoryCtx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
      }
    }
  }
}

/**
 * Runs the memory test (attractor scan).
 */
function runMemoryTest() {
  if (!memoryRuleSelect || !memoryResults) return;
  
  const ruleName = memoryRuleSelect.value;
  const rule = getRuleByName(ruleName);
  
  if (!rule) {
    memoryResults.innerHTML = '<p style="color: red;">Rule not found!</p>';
    return;
  }
  
  // Check if pattern is not empty
  const population = memoryGrid.reduce((sum, row) => 
    sum + row.reduce((s, cell) => s + cell, 0), 0
  );
  
  if (population === 0) {
    memoryResults.innerHTML = '<p style="color: orange;">Draw a pattern first!</p>';
    return;
  }
  
  // Get parameters
  const noise = memoryNoise ? parseFloat(memoryNoise.value) : 0.1;
  const steps = memorySteps ? parseInt(memorySteps.value) : 80;
  const runs = memoryRuns ? parseInt(memoryRuns.value) : 40;
  
  // Disable button
  memoryScanBtn.disabled = true;
  memoryScanBtn.textContent = 'Scanning...';
  memoryResults.innerHTML = '<p>Running attractor scan...</p>';
  
  // Run scan after delay to update UI
  setTimeout(() => {
    try {
      const report = scanAttractors(rule, memoryGrid, {
        runs,
        steps,
        noise,
        maxAttractors: 6
      });
      
      // Display results
      let html = `<h3>Results</h3>`;
      html += `<p><b>Rule:</b> ${report.ruleName} | <b>Runs:</b> ${report.runs} | <b>Noise:</b> ${(report.noise * 100).toFixed(0)}% | <b>Attractors found:</b> ${report.totalAttractors}</p>`;
      
      if (report.attractors.length === 0) {
        html += '<p>No stable attractors detected.</p>';
      } else {
        html += '<table style="border-collapse: collapse; margin: 10px 0; font-family: monospace; font-size: 12px;">';
        html += '<tr><th style="border: 1px solid #ccc; padding: 5px;">#</th><th style="border: 1px solid #ccc; padding: 5px;">Frequency</th><th style="border: 1px solid #ccc; padding: 5px;">Count</th><th style="border: 1px solid #ccc; padding: 5px;">Pattern</th></tr>';
        
        report.attractors.slice(0, 3).forEach((attr, i) => {
          html += '<tr>';
          html += `<td style="border: 1px solid #ccc; padding: 5px;">${i + 1}</td>`;
          html += `<td style="border: 1px solid #ccc; padding: 5px;">${(attr.frequency * 100).toFixed(1)}%</td>`;
          html += `<td style="border: 1px solid #ccc; padding: 5px;">${attr.count}</td>`;
          html += `<td style="border: 1px solid #ccc; padding: 5px;"><canvas id="attractorCanvas${i}" width="64" height="64"></canvas></td>`;
          html += '</tr>';
        });
        
        html += '</table>';
      }
      
      memoryResults.innerHTML = html;
      
      // Draw attractor samples
      report.attractors.slice(0, 3).forEach((attr, i) => {
        const canvas = document.getElementById(`attractorCanvas${i}`);
        if (canvas) {
          const ctx = canvas.getContext('2d');
          const w = attr.sampleGrid[0].length;
          const h = attr.sampleGrid.length;
          const cs = 64 / Math.max(w, h);
          
          ctx.fillStyle = '#ffffff';
          ctx.fillRect(0, 0, 64, 64);
          ctx.fillStyle = '#000000';
          
          for (let y = 0; y < h; y++) {
            for (let x = 0; x < w; x++) {
              if (attr.sampleGrid[y][x] === 1) {
                ctx.fillRect(x * cs, y * cs, cs, cs);
              }
            }
          }
        }
      });
      
    } catch (error) {
      console.error('Error during memory test:', error);
      memoryResults.innerHTML = '<p style="color: red;">Error during scan (see console)</p>';
    } finally {
      memoryScanBtn.disabled = false;
      memoryScanBtn.textContent = 'Run memory test';
    }
  }, 50);
}

