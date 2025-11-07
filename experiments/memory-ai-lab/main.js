import { CAEngine } from './ca/engine.js';
import { CARenderer } from './viz/canvas.js';
import { HOF_RULES } from '../../src/presets/rules.js';
import { hashGrid, findDominantAttractors, addNoise, hammingDistance } from './memory/attractorUtils.js';
import { HopfieldNetwork } from './hopfield/hopfield.js';
import { createPatternItem, createResultsTable, createComparisonTable, updateProgressBar } from './viz/ui.js';

const CA_WIDTH = 64;
const CA_HEIGHT = 64;
const CA_CELL_SIZE = 8;

let engine, renderer, currentGrid, animationId = null, isRunning = false, stepCount = 0, lastTime = 0, fps = 0;
let patterns = [], patternCounter = 0;
let patternCanvas, patternCtx, patternGrid, patternWidth = 32, patternHeight = 32, patternCellSize = 8, isDrawing = false;

document.addEventListener('DOMContentLoaded', () => {
  engine = new CAEngine(CA_WIDTH, CA_HEIGHT);
  renderer = new CARenderer('caCanvas', CA_WIDTH, CA_HEIGHT, CA_CELL_SIZE);
  currentGrid = engine.randomGrid(0.3);
  setupTabs();
  setupCAPlayground();
  setupMemoryLab();
  setupHopfieldLab();
  renderer.render(currentGrid);
  updateMetrics();
});

function setupTabs() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.dataset.tab;
      tabButtons.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(targetTab).classList.add('active');
      if (isRunning) stopAnimation();
    });
  });
}

function setupCAPlayground() {
  const ruleSelect = document.getElementById('ruleSelect');
  HOF_RULES.forEach(rule => {
    const option = document.createElement('option');
    option.value = JSON.stringify({ born: rule.born, survive: rule.survive });
    option.textContent = rule.name;
    ruleSelect.appendChild(option);
  });
  document.getElementById('startBtn').addEventListener('click', startAnimation);
  document.getElementById('stopBtn').addEventListener('click', stopAnimation);
  document.getElementById('stepBtn').addEventListener('click', stepOnce);
  document.getElementById('randomBtn').addEventListener('click', randomize);
  document.getElementById('clearBtn').addEventListener('click', clearGrid);
}

function startAnimation() {
  if (isRunning) return;
  isRunning = true;
  lastTime = performance.now();
  stepCount = 0;
  function animate(currentTime) {
    if (!isRunning) return;
    const deltaTime = currentTime - lastTime;
    lastTime = currentTime;
    fps = deltaTime > 0 ? 1000 / deltaTime : 0;
    const ruleData = JSON.parse(document.getElementById('ruleSelect').value);
    currentGrid = engine.step(currentGrid, ruleData);
    renderer.render(currentGrid);
    stepCount++;
    updateMetrics();
    animationId = requestAnimationFrame(animate);
  }
  animationId = requestAnimationFrame(animate);
}

function stopAnimation() {
  isRunning = false;
  if (animationId !== null) {
    cancelAnimationFrame(animationId);
    animationId = null;
  }
}

function stepOnce() {
  stopAnimation();
  const ruleData = JSON.parse(document.getElementById('ruleSelect').value);
  currentGrid = engine.step(currentGrid, ruleData);
  renderer.render(currentGrid);
  stepCount++;
  updateMetrics();
}

function randomize() {
  stopAnimation();
  currentGrid = engine.randomGrid(0.3);
  renderer.render(currentGrid);
  stepCount = 0;
  updateMetrics();
}

function clearGrid() {
  stopAnimation();
  currentGrid = engine.createEmptyGrid();
  renderer.render(currentGrid);
  stepCount = 0;
  updateMetrics();
}

function updateMetrics() {
  const metricsEl = document.getElementById('caMetrics');
  if (metricsEl) {
    const population = engine.getPopulation(currentGrid);
    metricsEl.textContent = `FPS: ${fps.toFixed(1)} | Step: ${stepCount} | Population: ${population}`;
  }
}

function setupMemoryLab() {
  patternCanvas = document.getElementById('patternCanvas');
  if (!patternCanvas) return;
  patternCanvas.width = patternWidth * patternCellSize;
  patternCanvas.height = patternHeight * patternCellSize;
  patternCanvas.style.imageRendering = 'pixelated';
  patternCtx = patternCanvas.getContext('2d');
  patternGrid = new Uint8Array(patternWidth * patternHeight);
  
  patternCanvas.addEventListener('mousedown', (e) => { isDrawing = true; drawCell(e); });
  patternCanvas.addEventListener('mousemove', (e) => { if (isDrawing) drawCell(e); });
  patternCanvas.addEventListener('mouseup', () => { isDrawing = false; });
  patternCanvas.addEventListener('mouseleave', () => { isDrawing = false; });
  
  document.getElementById('addPatternBtn')?.addEventListener('click', addPattern);
  document.getElementById('clearPatternBtn')?.addEventListener('click', clearPattern);
  document.getElementById('runMemoryTestBtn')?.addEventListener('click', runMemoryTest);
  
  ['noiseSlider', 'stepsSlider', 'runsSlider'].forEach(id => {
    const slider = document.getElementById(id);
    if (slider) {
      slider.addEventListener('input', (e) => {
        const valueId = id.replace('Slider', 'Value');
        const valueEl = document.getElementById(valueId);
        if (valueEl) {
          valueEl.textContent = id === 'noiseSlider' ? parseFloat(e.target.value).toFixed(2) : e.target.value;
        }
      });
    }
  });
  
  populateRuleSelect('memoryRuleSelect');
  renderPattern();
}

function populateRuleSelect(selectId) {
  const select = document.getElementById(selectId);
  if (!select) return;
  HOF_RULES.forEach(rule => {
    const option = document.createElement('option');
    option.value = JSON.stringify({ born: rule.born, survive: rule.survive, name: rule.name });
    option.textContent = rule.name;
    select.appendChild(option);
  });
}

function drawCell(e) {
  const rect = patternCanvas.getBoundingClientRect();
  const x = Math.floor((e.clientX - rect.left) / patternCellSize);
  const y = Math.floor((e.clientY - rect.top) / patternCellSize);
  if (x < 0 || x >= patternWidth || y < 0 || y >= patternHeight) return;
  const idx = y * patternWidth + x;
  patternGrid[idx] = 1 - patternGrid[idx];
  renderPattern();
}

function renderPattern() {
  patternCtx.fillStyle = '#000000';
  patternCtx.fillRect(0, 0, patternCanvas.width, patternCanvas.height);
  patternCtx.strokeStyle = '#333';
  patternCtx.lineWidth = 1;
  for (let x = 0; x <= patternWidth; x++) {
    patternCtx.beginPath();
    patternCtx.moveTo(x * patternCellSize, 0);
    patternCtx.lineTo(x * patternCellSize, patternHeight * patternCellSize);
    patternCtx.stroke();
  }
  for (let y = 0; y <= patternHeight; y++) {
    patternCtx.beginPath();
    patternCtx.moveTo(0, y * patternCellSize);
    patternCtx.lineTo(patternWidth * patternCellSize, y * patternCellSize);
    patternCtx.stroke();
  }
  patternCtx.fillStyle = '#00FF00';
  for (let y = 0; y < patternHeight; y++) {
    for (let x = 0; x < patternWidth; x++) {
      const idx = y * patternWidth + x;
      if (patternGrid[idx] === 1) {
        patternCtx.fillRect(x * patternCellSize + 1, y * patternCellSize + 1, patternCellSize - 2, patternCellSize - 2);
      }
    }
  }
}

function addPattern() {
  let hasCells = false;
  for (let i = 0; i < patternGrid.length; i++) {
    if (patternGrid[i] === 1) { hasCells = true; break; }
  }
  if (!hasCells) { alert('Le pattern est vide !'); return; }
  
  const pattern = {
    id: `pattern_${patternCounter++}`,
    name: `Pattern ${patternCounter}`,
    grid: new Uint8Array(patternGrid),
    width: patternWidth,
    height: patternHeight,
    created: Date.now()
  };
  patterns.push(pattern);
  updatePatternsList();
  clearPattern();
}

function clearPattern() {
  patternGrid.fill(0);
  renderPattern();
}

function updatePatternsList() {
  const container = document.getElementById('patternsContainer');
  if (!container) return;
  container.innerHTML = '';
  patterns.forEach(pattern => {
    const item = createPatternItem(pattern, (id) => {
      patterns = patterns.filter(p => p.id !== id);
      updatePatternsList();
    });
    container.appendChild(item);
  });
}

async function runMemoryTest() {
  if (patterns.length === 0) { alert('Ajoutez au moins un pattern !'); return; }
  
  const ruleData = JSON.parse(document.getElementById('memoryRuleSelect').value);
  const noiseLevel = parseFloat(document.getElementById('noiseSlider').value);
  const steps = parseInt(document.getElementById('stepsSlider').value);
  const runs = parseInt(document.getElementById('runsSlider').value);
  
  const progressContainer = document.getElementById('progressContainer');
  const progressFill = document.getElementById('progressFill');
  const progressText = document.getElementById('progressText');
  progressContainer.style.display = 'block';
  
  const results = [];
  for (let i = 0; i < patterns.length; i++) {
    const pattern = patterns[i];
    const result = await testPattern(pattern, ruleData, { noiseLevel, steps, runs });
    results.push(result);
    const progress = ((i + 1) / patterns.length) * 100;
    updateProgressBar(progressFill, progressText, progress);
    await new Promise(resolve => setTimeout(resolve, 10));
  }
  
  displayResults(results);
  setTimeout(() => { progressContainer.style.display = 'none'; }, 1000);
}

async function testPattern(pattern, rule, { noiseLevel, steps, runs }) {
  const tempEngine = new CAEngine(pattern.width, pattern.height);
  const attractorCounts = new Map();
  
  for (let i = 0; i < runs; i++) {
    const noisy = addNoise(pattern.grid, noiseLevel);
    const final = tempEngine.run(noisy, rule, steps);
    const hash = hashGrid(final);
    attractorCounts.set(hash, (attractorCounts.get(hash) || 0) + 1);
  }
  
  const dominants = findDominantAttractors(attractorCounts, runs);
  const mainAttractor = dominants[0] || { count: 0, percentage: 0 };
  const coverage = dominants.reduce((sum, a) => sum + a.percentage, 0);
  
  return {
    patternId: pattern.id,
    ruleId: rule.name,
    totalRuns: runs,
    noiseLevel,
    steps,
    attractors: dominants,
    recallRate: mainAttractor.percentage / 100,
    coverage: coverage / 100,
    status: mainAttractor.percentage >= 70 ? 'OK' : mainAttractor.percentage >= 40 ? 'Weak' : 'Fail'
  };
}

function displayResults(results) {
  const container = document.getElementById('memoryResults');
  if (!container) return;
  container.innerHTML = '';
  if (results.length === 0) { container.textContent = 'Aucun résultat'; return; }
  
  const table = createResultsTable(results);
  container.appendChild(table);
  
  const summary = document.createElement('div');
  summary.style.marginTop = '20px';
  summary.style.padding = '15px';
  summary.style.background = '#1a1a1a';
  summary.style.borderRadius = '6px';
  const avgRecall = results.reduce((sum, r) => sum + r.recallRate, 0) / results.length;
  const avgCoverage = results.reduce((sum, r) => sum + r.coverage, 0) / results.length;
  summary.innerHTML = `
    <h4 style="color: #00ff88; margin-bottom: 10px;">Résumé Global</h4>
    <p><strong>Recall Rate moyen:</strong> ${(avgRecall * 100).toFixed(1)}%</p>
    <p><strong>Coverage moyen:</strong> ${(avgCoverage * 100).toFixed(1)}%</p>
    <p><strong>Patterns testés:</strong> ${results.length}</p>
  `;
  container.appendChild(summary);
}

function setupHopfieldLab() {
  populateRuleSelect('hopfieldRuleSelect');
  document.getElementById('runComparisonBtn')?.addEventListener('click', runComparison);
  const noiseSlider = document.getElementById('hopfieldNoiseSlider');
  const runsSlider = document.getElementById('hopfieldRunsSlider');
  if (noiseSlider) {
    noiseSlider.addEventListener('input', (e) => {
      document.getElementById('hopfieldNoiseValue').textContent = parseFloat(e.target.value).toFixed(2);
    });
  }
  if (runsSlider) {
    runsSlider.addEventListener('input', (e) => {
      document.getElementById('hopfieldRunsValue').textContent = e.target.value;
    });
  }
}

async function runComparison() {
  if (patterns.length === 0) { alert('Créez d\'abord des patterns dans Memory Lab !'); return; }
  
  const ruleData = JSON.parse(document.getElementById('hopfieldRuleSelect').value);
  const noiseLevel = parseFloat(document.getElementById('hopfieldNoiseSlider').value);
  const runs = parseInt(document.getElementById('hopfieldRunsSlider').value);
  
  const progressContainer = document.getElementById('hopfieldProgressContainer');
  const progressFill = document.getElementById('hopfieldProgressFill');
  const progressText = document.getElementById('hopfieldProgressText');
  progressContainer.style.display = 'block';
  
  const flatPatterns = patterns.map(p => p.grid);
  const networkSize = flatPatterns[0].length;
  const network = new HopfieldNetwork(networkSize);
  network.train(flatPatterns);
  
  const hopfieldResults = [];
  for (let i = 0; i < patterns.length; i++) {
    const pattern = patterns[i];
    let successCount = 0;
    for (let j = 0; j < runs; j++) {
      const noisy = addNoise(pattern.grid, noiseLevel);
      const recalled = network.recall(noisy, 100);
      const dist = hammingDistance(recalled, pattern.grid);
      const threshold = pattern.grid.length * 0.05;
      if (dist <= threshold) successCount++;
    }
    hopfieldResults.push({ patternId: pattern.id, recallRate: successCount / runs, model: 'Hopfield' });
    const progress = ((i + 1) / patterns.length) * 50;
    updateProgressBar(progressFill, progressText, progress);
    await new Promise(resolve => setTimeout(resolve, 10));
  }
  
  const caResults = [];
  for (let i = 0; i < patterns.length; i++) {
    const pattern = patterns[i];
    const tempEngine = new CAEngine(pattern.width, pattern.height);
    const attractorCounts = new Map();
    for (let j = 0; j < runs; j++) {
      const noisy = addNoise(pattern.grid, noiseLevel);
      const final = tempEngine.run(noisy, ruleData, 80);
      const hash = hashGrid(final);
      attractorCounts.set(hash, (attractorCounts.get(hash) || 0) + 1);
    }
    const dominants = findDominantAttractors(attractorCounts, runs);
    const mainAttractor = dominants[0] || { count: 0, percentage: 0 };
    caResults.push({ patternId: pattern.id, recallRate: mainAttractor.percentage / 100, model: 'CA' });
    const progress = 50 + ((i + 1) / patterns.length) * 50;
    updateProgressBar(progressFill, progressText, progress);
    await new Promise(resolve => setTimeout(resolve, 10));
  }
  
  displayComparison(hopfieldResults, caResults);
  setTimeout(() => { progressContainer.style.display = 'none'; }, 1000);
}

function displayComparison(hopfieldResults, caResults) {
  const container = document.getElementById('hopfieldResults');
  if (!container) return;
  container.innerHTML = '';
  if (hopfieldResults.length === 0 || caResults.length === 0) { container.textContent = 'Aucun résultat'; return; }
  
  const table = createComparisonTable(hopfieldResults, caResults);
  container.appendChild(table);
  
  const summary = document.createElement('div');
  summary.style.marginTop = '20px';
  summary.style.padding = '15px';
  summary.style.background = '#1a1a1a';
  summary.style.borderRadius = '6px';
  const avgHopfield = hopfieldResults.reduce((sum, r) => sum + r.recallRate, 0) / hopfieldResults.length;
  const avgCA = caResults.reduce((sum, r) => sum + r.recallRate, 0) / caResults.length;
  const delta = (avgHopfield - avgCA) * 100;
  summary.innerHTML = `
    <h4 style="color: #00ff88; margin-bottom: 10px;">Résumé Comparatif</h4>
    <p><strong>Hopfield Recall moyen:</strong> ${(avgHopfield * 100).toFixed(1)}%</p>
    <p><strong>CA Recall moyen:</strong> ${(avgCA * 100).toFixed(1)}%</p>
    <p><strong>Différence:</strong> ${delta > 0 ? '+' : ''}${delta.toFixed(1)}%</p>
    <p><strong>Gagnant:</strong> ${delta > 5 ? 'Hopfield' : delta < -5 ? 'CA' : 'Égalité'}</p>
  `;
  container.appendChild(summary);
}

