console.log('⏳ Chargement Memory AI Lab...');

import { CAEngine } from './ca/engine.js';
import { CARenderer } from './viz/canvas.js';
import { HOF_RULES } from '../../src/presets/rules.js';
import { hashGrid, findDominantAttractors, addNoise, hammingDistance, isRecallSuccess, getDefaultPatterns } from './memory/attractorUtils.js';
import { HopfieldNetwork } from './hopfield/hopfield.js';
import { createPatternItem, createResultsTable, createComparisonTable, updateProgressBar } from './viz/ui.js';
import { CAMemoryEngine } from '../../src/memory/caMemoryEngine.js';
import { HopfieldMemoryEngine } from '../../src/memory/hopfieldMemoryEngine.js';

console.log('✓ Imports chargés');

const CA_WIDTH = 64;
const CA_HEIGHT = 64;
const CA_CELL_SIZE = 8;

let engine, renderer, currentGrid, animationId = null, isRunning = false, stepCount = 0, lastTime = 0, fps = 0;
let patterns = [], patternCounter = 0;
let patternCanvas, patternCtx, patternGrid, patternWidth = 32, patternHeight = 32, patternCellSize = 8, isDrawing = false;

// === Persistence localStorage ===
const STORAGE_KEY = 'memorylab_patterns_v1';

function savePatternsToLocalStorage() {
  try {
    const patternsData = patterns.map(p => ({
      id: p.id,
      name: p.name,
      grid: Array.from(p.grid),
      width: p.width,
      height: p.height,
      created: p.created
    }));
    localStorage.setItem(STORAGE_KEY, JSON.stringify(patternsData));
    console.log(`💾 ${patterns.length} patterns sauvegardés`);
  } catch (error) {
    console.warn('⚠️ Impossible de sauvegarder les patterns:', error);
  }
}

function loadPatternsFromLocalStorage() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      const patternsData = JSON.parse(saved);
      patterns = patternsData.map(p => ({
        ...p,
        grid: new Uint8Array(p.grid)
      }));
      patternCounter = Math.max(...patterns.map(p => parseInt(p.id.replace(/\D/g, '')) || 0), 0) + 1;
      console.log(`📂 ${patterns.length} patterns restaurés depuis localStorage`);
      return true;
    }
  } catch (error) {
    console.warn('⚠️ Unable to load saved patterns:', error);
  }
  return false;
}

/**
 * Retourne les patterns UI actuels
 * @returns {Array} Patterns dessinés par l'utilisateur
 */
function getCurrentPatterns() {
  return patterns;
}

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
  
  // Charger patterns sauvegardés après init UI
  if (loadPatternsFromLocalStorage()) {
    updatePatternsList();
  }
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
  if (!patternCanvas) {
    console.warn('⚠️ Pattern canvas introuvable');
    return;
  }
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
  updateTestButtonsState(); // Désactiver les boutons si pas de patterns
  
  // Bouton AutoScan
  const autoScanBtn = document.getElementById('runAutoScanBtn');
  if (autoScanBtn) {
    autoScanBtn.addEventListener('click', async () => {
      if (!window.MemoryScanner || !window.MemoryScanner.scanMemoryCandidates) {
        console.error('❌ MemoryScanner non disponible (autoScan.js non chargé)');
        alert('⚠️ Module AutoScan non chargé. Rechargez la page.');
        return;
      }
      autoScanBtn.disabled = true;
      const originalText = autoScanBtn.textContent;
      autoScanBtn.textContent = 'Running AutoScan...';
      try {
        console.log('🚀 Lancement AutoScan...');
        const result = await window.MemoryScanner.scanMemoryCandidates({
          noiseLevels: [0.01, 0.03, 0.05, 0.08],
          steps: 160,
          runs: 60
        });
        console.log('🎯 AutoScan terminé. Candidates:', result.candidates || result);
        autoScanBtn.textContent = originalText;
      } catch (error) {
        console.error('❌ Erreur AutoScan:', error);
        alert('Erreur lors du scan. Consultez la console (F12) pour plus de détails.');
        autoScanBtn.textContent = 'AutoScan failed (voir console)';
      } finally {
        autoScanBtn.disabled = false;
      }
    });
  }
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
  savePatternsToLocalStorage();
  console.log(`✓ Pattern ${pattern.name} ajouté (${patterns.length} patterns total)`);
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
      updateTestButtonsState();
      savePatternsToLocalStorage();
    });
    container.appendChild(item);
  });
  updateTestButtonsState();
}

function updateTestButtonsState() {
  const runMemoryBtn = document.getElementById('runMemoryTestBtn');
  const runComparisonBtn = document.getElementById('runComparisonBtn');
  
  if (runMemoryBtn) {
    runMemoryBtn.disabled = patterns.length === 0;
    runMemoryBtn.title = patterns.length === 0 ? 'Ajoutez au moins un pattern avant de lancer le test' : '';
  }
  
  if (runComparisonBtn) {
    runComparisonBtn.disabled = patterns.length === 0;
    runComparisonBtn.title = patterns.length === 0 ? 'Ajoutez au moins un pattern avant de lancer la comparaison' : '';
  }
}

async function runMemoryTest() {
  if (patterns.length === 0) { 
    alert('⚠️ Ajoutez au moins un pattern avant de lancer le test !'); 
    return; 
  }
  
  const ruleSelect = document.getElementById('memoryRuleSelect');
  if (!ruleSelect || !ruleSelect.value) {
    console.error('❌ Sélecteur de règle introuvable');
    return;
  }
  
  try {
    const ruleData = JSON.parse(ruleSelect.value);
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
  } catch (error) {
    console.error('❌ Erreur lors du test de mémoire:', error);
    alert('Erreur lors du test. Consultez la console (F12) pour plus de détails.');
    const progressContainer = document.getElementById('progressContainer');
    if (progressContainer) progressContainer.style.display = 'none';
  }
}

async function testPattern(pattern, rule, { noiseLevel, steps, runs, maxDiffRatio = 0.1 }) {
  const tempEngine = new CAEngine(pattern.width, pattern.height);
  const attractorCounts = new Map();
  let successCount = 0;
  
  for (let i = 0; i < runs; i++) {
    const noisy = addNoise(pattern.grid, noiseLevel);
    const final = tempEngine.run(noisy, rule, steps);
    const hash = hashGrid(final);
    attractorCounts.set(hash, (attractorCounts.get(hash) || 0) + 1);
    
    // Vérifier si le recall est un succès (tolérance 10%)
    if (isRecallSuccess(pattern.grid, final, maxDiffRatio)) {
      successCount++;
    }
  }
  
  const dominants = findDominantAttractors(attractorCounts, runs);
  const mainAttractor = dominants[0] || { count: 0, percentage: 0 };
  const coverage = dominants.reduce((sum, a) => sum + a.percentage, 0);
  const recallRate = successCount / runs;
  
  return {
    patternId: pattern.id,
    ruleId: rule.name,
    totalRuns: runs,
    noiseLevel,
    steps,
    attractors: dominants,
    recallRate: recallRate,
    coverage: coverage / 100,
    status: recallRate >= 0.7 ? 'OK' : recallRate >= 0.4 ? 'Weak' : 'Fail'
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
  if (patterns.length === 0) { 
    alert('⚠️ Créez d\'abord des patterns dans Memory Lab !'); 
    return; 
  }
  
  try {
  
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
  } catch (error) {
    console.error('❌ Erreur lors de la comparaison:', error);
    alert('Erreur lors de la comparaison. Consultez la console (F12) pour plus de détails.');
    const progressContainer = document.getElementById('hopfieldProgressContainer');
    if (progressContainer) progressContainer.style.display = 'none';
  }
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

// ========== API Publique pour tests automatiques ==========

async function runBatchForHallOfFame(options = {}) {
  const { noiseLevel = 0.05, steps = 80, runs = 50, patterns: testPatterns = null, maxDiffRatio = 0.1 } = options;
  
  let patternsToTest = testPatterns;
  
  // Logique unifiée de sélection des patterns
  if (!patternsToTest || patternsToTest.length === 0) {
    if (patterns.length > 0) {
      patternsToTest = patterns;
      console.log(`✓ Utilisation de ${patterns.length} patterns depuis Memory Lab UI`);
    } else {
      // Fallback: patterns par défaut centralisés
      patternsToTest = getDefaultPatterns();
      console.log(`✓ Utilisation de ${patternsToTest.length} patterns par défaut (reproductibles)`);
    }
  }
  console.log(`🧪 Lancement batch Hall of Fame: ${HOF_RULES.length} règles × ${patternsToTest.length} patterns × ${runs} runs`);
  
  const results = [];
  for (const rule of HOF_RULES) {
    const ruleData = { born: rule.born, survive: rule.survive, name: rule.name };
    const ruleResults = [];
    
    for (const pattern of patternsToTest) {
      const result = await testPattern(pattern, ruleData, { noiseLevel, steps, runs, maxDiffRatio });
      ruleResults.push(result);
    }
    
    const avgRecall = ruleResults.reduce((sum, r) => sum + r.recallRate, 0) / ruleResults.length;
    const avgCoverage = ruleResults.reduce((sum, r) => sum + r.coverage, 0) / ruleResults.length;
    const avgAttractors = ruleResults.reduce((sum, r) => sum + r.attractors.length, 0) / ruleResults.length;
    
    const notation = rule.name.match(/\(([^)]+)\)/)?.[1] || rule.name;
    
    results.push({
      rule: rule.name.replace('🏆 ', ''),
      notation: notation,
      avgRecallRate: avgRecall,
      avgCoverage: avgCoverage,
      avgAttractors: avgAttractors,
      patternsResults: ruleResults
    });
    
    console.log(`✓ ${notation}: recall=${(avgRecall * 100).toFixed(1)}%, coverage=${(avgCoverage * 100).toFixed(1)}%, attractors=${avgAttractors.toFixed(1)}`);
  }
  
  console.log('✅ Batch Hall of Fame terminé');
  console.table(results.map(r => ({
    Règle: r.rule,
    'Recall (%)': (r.avgRecallRate * 100).toFixed(1),
    'Coverage (%)': (r.avgCoverage * 100).toFixed(1),
    'Attracteurs': r.avgAttractors.toFixed(1)
  })));
  
  return results;
}

async function compareWithHallOfFame(options = {}) {
  const { noiseLevel = 0.05, runs = 50, patterns: testPatterns = null, maxDiffRatio = 0.1 } = options;
  
  let patternsToTest = testPatterns;
  
  // Logique unifiée de sélection des patterns
  if (!patternsToTest || patternsToTest.length === 0) {
    if (patterns.length > 0) {
      patternsToTest = patterns;
      console.log(`✓ Utilisation de ${patterns.length} patterns depuis Memory Lab UI`);
    } else {
      // Fallback: patterns par défaut centralisés
      patternsToTest = getDefaultPatterns();
      console.log(`✓ Utilisation de ${patternsToTest.length} patterns par défaut (reproductibles)`);
    }
  }
  
  console.log(`🧪 Comparaison Hopfield vs Hall of Fame: ${HOF_RULES.length} règles × ${patternsToTest.length} patterns`);
  
  // Entraîner Hopfield
  const flatPatterns = patternsToTest.map(p => p.grid);
  const networkSize = flatPatterns[0].length;
  const network = new HopfieldNetwork(networkSize);
  network.train(flatPatterns);
  
  // Test Hopfield (même critère de succès que CA)
  const hopfieldResults = [];
  for (const pattern of patternsToTest) {
    let successCount = 0;
    for (let j = 0; j < runs; j++) {
      const noisy = addNoise(pattern.grid, noiseLevel);
      const recalled = network.recall(noisy, 100);
      if (isRecallSuccess(pattern.grid, recalled, maxDiffRatio)) {
        successCount++;
      }
    }
    hopfieldResults.push({
      patternId: pattern.id,
      recallRate: successCount / runs
    });
  }
  
  const hopfieldAvg = hopfieldResults.reduce((sum, r) => sum + r.recallRate, 0) / hopfieldResults.length;
  console.log(`✓ Hopfield: recall moyen=${(hopfieldAvg * 100).toFixed(1)}%`);
  
  // Test chaque règle CA (même critère de succès que Hopfield)
  const comparisons = [];
  for (const rule of HOF_RULES) {
    const ruleData = { born: rule.born, survive: rule.survive, name: rule.name };
    const caResults = [];
    
    for (const pattern of patternsToTest) {
      const tempEngine = new CAEngine(pattern.width, pattern.height);
      let successCount = 0;
      
      for (let j = 0; j < runs; j++) {
        const noisy = addNoise(pattern.grid, noiseLevel);
        const final = tempEngine.run(noisy, ruleData, 80);
        
        if (isRecallSuccess(pattern.grid, final, maxDiffRatio)) {
          successCount++;
        }
      }
      
      caResults.push({
        patternId: pattern.id,
        recallRate: successCount / runs
      });
    }
    
    const caAvg = caResults.reduce((sum, r) => sum + r.recallRate, 0) / caResults.length;
    const delta = (caAvg - hopfieldAvg) * 100;
    
    const notation = rule.name.match(/\(([^)]+)\)/)?.[1] || rule.name;
    
    comparisons.push({
      rule: rule.name.replace('🏆 ', ''),
      notation: notation,
      hopfieldRecall: hopfieldAvg,
      caRecall: caAvg,
      delta: delta,
      winner: delta > 5 ? 'CA' : delta < -5 ? 'Hopfield' : 'Tie'
    });
    
    console.log(`✓ ${notation}: CA=${(caAvg * 100).toFixed(1)}% vs Hopfield=${(hopfieldAvg * 100).toFixed(1)}% (Δ${delta > 0 ? '+' : ''}${delta.toFixed(1)}%)`);
  }
  
  console.log('✅ Comparaison terminée');
  console.table(comparisons.map(c => ({
    Règle: c.notation,
    'CA (%)': (c.caRecall * 100).toFixed(1),
    'Hopfield (%)': (c.hopfieldRecall * 100).toFixed(1),
    'Δ (%)': c.delta.toFixed(1),
    Gagnant: c.winner
  })));
  
  return { hopfield: hopfieldResults, comparisons };
}

function generateMarkdownReport(batchResults, comparisonResults) {
  if (!batchResults || batchResults.length === 0) {
    console.error('❌ Pas de résultats batch. Lancez runBatchForHallOfFame() d\'abord.');
    return '';
  }
  
  const numPatterns = batchResults[0]?.patternsResults?.length || patterns.length || 'N/A';
  
  let md = `# Memory AI Lab - Résultats automatiques\n\n`;
  md += `**Date**: ${new Date().toLocaleString('fr-FR')}\n\n`;
  md += `**Méthodologie**:\n`;
  md += `- Patterns testés: ${numPatterns}\n`;
  md += `- Runs par pattern: 50\n`;
  md += `- Noise level: 0.05\n`;
  md += `- Steps: 80\n`;
  md += `- Critère de succès: Distance de Hamming ≤ 10% de la taille\n\n`;
  
  md += `## Résultats Hall of Fame (CA)\n\n`;
  md += `| Règle | Notation | Recall Rate | Coverage | Attracteurs | Status |\n`;
  md += `|-------|----------|-------------|----------|-------------|--------|\n`;
  
  batchResults.forEach(r => {
    const status = r.avgRecallRate >= 0.7 ? '✅ OK' : r.avgRecallRate >= 0.4 ? '⚠️ Weak' : '❌ Fail';
    md += `| ${r.rule.replace('🏆 ', '')} | ${r.notation} | ${(r.avgRecallRate * 100).toFixed(1)}% | ${(r.avgCoverage * 100).toFixed(1)}% | ${r.avgAttractors.toFixed(1)} | ${status} |\n`;
  });
  
  if (comparisonResults) {
    md += `\n## Comparaison CA vs Hopfield\n\n`;
    md += `| Règle | CA Recall | Hopfield Recall | Δ | Gagnant |\n`;
    md += `|-------|-----------|-----------------|---|----------|\n`;
    
    comparisonResults.comparisons.forEach(c => {
      md += `| ${c.notation} | ${(c.caRecall * 100).toFixed(1)}% | ${(c.hopfieldRecall * 100).toFixed(1)}% | ${c.delta > 0 ? '+' : ''}${c.delta.toFixed(1)}% | ${c.winner} |\n`;
    });
    
    md += `\n**Conclusion**: `;
    const caWins = comparisonResults.comparisons.filter(c => c.winner === 'CA').length;
    const hopWins = comparisonResults.comparisons.filter(c => c.winner === 'Hopfield').length;
    if (hopWins > caWins) {
      md += `Hopfield supérieur dans la majorité des cas (${hopWins}/${HOF_RULES.length} règles).\n`;
    } else if (caWins > hopWins) {
      md += `CA supérieur dans la majorité des cas (${caWins}/${HOF_RULES.length} règles).\n`;
    } else {
      md += `Performance équivalente entre CA et Hopfield.\n`;
    }
  }
  
  md += `\n## Règle recommandée\n\n`;
  const best = batchResults.reduce((max, r) => r.avgRecallRate > max.avgRecallRate ? r : max);
  md += `**${best.rule}** (${best.notation}) - Meilleur recall rate: ${(best.avgRecallRate * 100).toFixed(1)}%\n\n`;
  md += `Cette règle présente le meilleur taux de rappel moyen sur l'ensemble des patterns testés.\n`;
  
  return md;
}

// Helper: patterns pour tests (UI ou defaults)
function getPatternsForTests() {
  return patterns.length > 0 ? patterns : getDefaultPatterns();
}

// Exposer l'API globalement
window.MemoryLab = {
  runBatchForHallOfFame,
  getCurrentPatterns: () => patterns,
  getPatternsForTests,
  patterns: () => patterns,
  HOF_RULES: () => HOF_RULES
};

window.HopfieldLab = {
  compareWithHallOfFame,
  patterns: () => patterns
};

window.Reports = {
  generateMarkdownReport
};

// Exposer memory engines
window.CAMemoryEngine = CAMemoryEngine;
window.HopfieldMemoryEngine = HopfieldMemoryEngine;

console.log('%c✅ Memory AI Lab chargé', 'color: #00ff88; font-weight: bold; font-size: 14px');
console.log('%c📚 API disponible:', 'color: #00ff88; font-weight: bold');
console.log('%c  MemoryLab.runBatchForHallOfFame(options)', 'color: #88ffaa');
console.log('%c  HopfieldLab.compareWithHallOfFame(options)', 'color: #88ffaa');
console.log('%c  Reports.generateMarkdownReport(batch, comp)', 'color: #88ffaa');
console.log('%c  MemoryScanner.scanMemoryCandidates(options)', 'color: #00aaff');
console.log('');
console.log('%c🎯 FULL PIPELINE (copier-coller):', 'color: #ffaa00; font-weight: bold; font-size: 13px');
console.log(`%c// 1) Test Hall of Fame
const batch = await MemoryLab.runBatchForHallOfFame({ noiseLevel: 0.05, steps: 80, runs: 50 });
const comp = await HopfieldLab.compareWithHallOfFame({ noiseLevel: 0.05, runs: 50 });
const report = Reports.generateMarkdownReport(batch, comp);
console.log(report);

// 2) AutoScan candidates
const scan = await MemoryScanner.scanMemoryCandidates({ noiseLevels: [0.01, 0.03, 0.05, 0.08], steps: 160, runs: 60 });
console.log("🏆 Candidates mémoire finales:", scan.candidates);
console.table(scan.candidates);`, 'color: #aaffaa; font-family: monospace;');
console.log('');
console.log('%c💾 Patterns persistés via localStorage. Vos patterns sont sauvegardés automatiquement.', 'color: #aaffaa; font-style: italic');
console.log('%c🏆 Memory Candidates: B01/S3, B01/S23, B01/S34, B01/S2, B01/S4, B01/S13, B46/S58', 'color: #ffaa00');

// Vérification que l'API est bien exposée
if (typeof window.MemoryLab !== 'undefined' && typeof window.HopfieldLab !== 'undefined' && typeof window.Reports !== 'undefined') {
  console.log('%c✓ API correctement exposée au window', 'color: #00ff88');
  console.log('%c  Accès: window.MemoryLab, window.HopfieldLab, window.Reports', 'color: #88ffaa');
} else {
  console.error('❌ Erreur: API non exposée correctement');
}

