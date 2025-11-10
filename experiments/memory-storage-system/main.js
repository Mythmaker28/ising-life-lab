import { CAMemoryEngine } from '../../src/memory/caMemoryEngine.js';
import { HopfieldMemoryEngine } from '../../src/memory/hopfieldMemoryEngine.js';
import { getDefaultPatterns } from '../memory-ai-lab/memory/attractorUtils.js';

const MEMORY_HALL_OF_FAME = ['B01/S3', 'B01/S23', 'B01/S34', 'B01/S2', 'B01/S4', 'B01/S13', 'B46/S58'];

let engines = [];
let patterns = [];
let consoleEl, initBtn, refreshBtn, recallBtn, batchBtn;

// ========== Helpers ==========

function log(msg, type = '') {
  const div = document.createElement('div');
  div.className = type;
  div.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
  consoleEl.appendChild(div);
  consoleEl.scrollTop = consoleEl.scrollHeight;
  console.log(msg);
}

async function getBasePatterns() {
  try {
    if (window.MemoryLab?.getPatternsForTests) {
      const p = window.MemoryLab.getPatternsForTests();
      if (p?.length > 0) {
        log(`✓ ${p.length} patterns depuis MemoryLab`, 'success');
        return p.map(x => x.grid || x);
      }
    }
  } catch (e) {
    log(`⚠️ MemoryLab non accessible: ${e.message}`, 'warn');
  }
  
  log('✓ Génération patterns par défaut', 'success');
  return getDefaultPatterns().map(p => p.grid);
}

function applyNoise(pattern, noiseLevel) {
  const noisy = new Uint8Array(pattern);
  for (let i = 0; i < noisy.length; i++) {
    if (Math.random() < noiseLevel) noisy[i] = 1 - noisy[i];
  }
  return noisy;
}

function hammingDistance(a, b) {
  let diff = 0;
  for (let i = 0; i < Math.min(a.length, b.length); i++) {
    if (a[i] !== b[i]) diff++;
  }
  return diff / a.length;
}

function renderPatternMini(pattern, canvas) {
  const size = Math.sqrt(pattern.length);
  const cellSize = canvas.width / size;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#000';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#00ff00';
  for (let i = 0; i < pattern.length; i++) {
    if (pattern[i]) {
      const x = (i % size) * cellSize;
      const y = Math.floor(i / size) * cellSize;
      ctx.fillRect(x, y, cellSize, cellSize);
    }
  }
}

// ========== Main Logic ==========

async function initEngines() {
  initBtn.disabled = true;
  initBtn.textContent = 'Initializing...';
  log('🔧 Initialisation du système...', 'success');
  
  const statusEl = document.getElementById('initStatus');
  statusEl.textContent = 'Loading patterns...';
  
  patterns = await getBasePatterns();
  
  document.getElementById('patternCount').textContent = `${patterns.length} patterns`;
  updatePatternGrid();
  
  const caCheckboxes = document.querySelectorAll('.ca-checkbox:checked');
  const hopfieldChecked = document.getElementById('hopfield-checkbox').checked;
  
  engines = [];
  statusEl.textContent = 'Initializing engines...';
  
  for (const checkbox of caCheckboxes) {
    const rule = checkbox.value;
    const t0 = performance.now();
    const engine = CAMemoryEngine.create({ rule, width: 32, height: 32, steps: 80 });
    engine.store(patterns);
    const duration = performance.now() - t0;
    
    engines.push({ type: 'CA', name: rule, engine });
    log(`✓ ${rule} init (${duration.toFixed(1)}ms)`, 'success');
  }
  
  if (hopfieldChecked) {
    const t0 = performance.now();
    const engine = HopfieldMemoryEngine.create({ width: 32, height: 32 });
    engine.store(patterns);
    const duration = performance.now() - t0;
    
    engines.push({ type: 'Hopfield', name: 'Hopfield', engine });
    log(`✓ Hopfield init (${duration.toFixed(1)}ms)`, 'success');
  }
  
  statusEl.textContent = `✅ ${engines.length} engines ready`;
  populatePatternSelect();
  recallBtn.disabled = false;
  batchBtn.disabled = false;
  refreshBtn.disabled = false;
  initBtn.textContent = 'Initialize Storage';
  initBtn.disabled = false;
  
  log(`🎉 Système prêt: ${engines.length} engines, ${patterns.length} patterns`, 'success');
}

function updatePatternGrid() {
  const grid = document.getElementById('patternGrid');
  grid.innerHTML = '';
  
  patterns.forEach((p, i) => {
    const canvas = document.createElement('canvas');
    canvas.className = 'pattern-mini';
    canvas.width = 60;
    canvas.height = 60;
    canvas.title = `Pattern ${i+1}`;
    renderPatternMini(p, canvas);
    grid.appendChild(canvas);
  });
}

function populatePatternSelect() {
  const select = document.getElementById('patternSelect');
  select.innerHTML = '';
  patterns.forEach((_, i) => {
    const opt = document.createElement('option');
    opt.value = i;
    opt.textContent = `Pattern ${i+1}`;
    select.appendChild(opt);
  });
}

async function testRecall() {
  recallBtn.disabled = true;
  log('\n🧪 Test recall avec bruit...');
  
  const idx = parseInt(document.getElementById('patternSelect').value);
  const noise = parseFloat(document.getElementById('noiseSlider').value) / 100;
  const sourcePattern = patterns[idx];
  
  const noisyPattern = applyNoise(sourcePattern, noise);
  log(`Pattern ${idx+1} avec ${(noise*100).toFixed(0)}% bruit`);
  
  const tbody = document.querySelector('#resultsTable tbody');
  tbody.innerHTML = '';
  
  for (const {name, engine} of engines) {
    const t0 = performance.now();
    try {
      const result = engine.recall(noisyPattern);
      const duration = performance.now() - t0;
      const recalled = result.final || result.recalled;
      const distance = hammingDistance(recalled, sourcePattern);
      const success = distance < 0.1;
      
      const row = tbody.insertRow();
      row.innerHTML = `
        <td>${name}</td>
        <td class="${success ? 'success' : 'fail'}">${success ? '✓' : '✗'}</td>
        <td>${(distance * 100).toFixed(1)}%</td>
        <td>${result.stepsUsed || '?'}</td>
        <td>${duration.toFixed(1)}</td>
      `;
      
      log(`${name}: ${success ? '✓' : '✗'} dist=${(distance*100).toFixed(1)}%`);
    } catch (e) {
      const row = tbody.insertRow();
      row.innerHTML = `<td>${name}</td><td colspan="4" class="fail">Error: ${e.message}</td>`;
      log(`${name}: Error - ${e.message}`, 'error');
    }
  }
  
  recallBtn.disabled = false;
}

async function batchTest() {
  batchBtn.disabled = true;
  log('\n📊 Batch test sur tous les patterns...');
  
  const noise = parseFloat(document.getElementById('noiseSlider').value) / 100;
  const stats = engines.map(e => ({ name: e.name, successes: 0, totalDist: 0 }));
  
  for (let i = 0; i < patterns.length; i++) {
    const noisyPattern = applyNoise(patterns[i], noise);
    
    for (let j = 0; j < engines.length; j++) {
      try {
        const result = engines[j].engine.recall(noisyPattern);
        const recalled = result.final || result.recalled;
        const distance = hammingDistance(recalled, patterns[i]);
        stats[j].totalDist += distance;
        if (distance < 0.1) stats[j].successes++;
      } catch (e) {
        log(`Error on ${engines[j].name}: ${e.message}`, 'error');
      }
    }
  }
  
  log('\n🎯 Résultats batch:');
  stats.forEach(s => {
    const avgDist = (s.totalDist / patterns.length * 100).toFixed(1);
    const successRate = (s.successes / patterns.length * 100).toFixed(0);
    log(`${s.name}: ${successRate}% success, avg dist=${avgDist}%`);
  });
  
  batchBtn.disabled = false;
}

// ========== Init ==========

document.addEventListener('DOMContentLoaded', async () => {
  consoleEl = document.getElementById('consoleLog');
  initBtn = document.getElementById('initBtn');
  refreshBtn = document.getElementById('refreshBtn');
  recallBtn = document.getElementById('recallBtn');
  batchBtn = document.getElementById('batchBtn');
  
  initBtn.addEventListener('click', initEngines);
  recallBtn.addEventListener('click', testRecall);
  batchBtn.addEventListener('click', batchTest);
  refreshBtn.addEventListener('click', async () => {
    patterns = await getBasePatterns();
    updatePatternGrid();
    populatePatternSelect();
  });
  
  document.getElementById('noiseSlider').addEventListener('input', (e) => {
    document.getElementById('noiseValue').textContent = `${e.target.value}%`;
  });
  
  log('✅ Memory Storage System chargé');
  log('💡 Sélectionnez engines puis cliquez "Initialize Storage"');
  
  // Self-test
  log('\n🔬 Self-test...');
  console.assert(typeof CAMemoryEngine !== 'undefined', 'CAMemoryEngine OK');
  console.assert(typeof HopfieldMemoryEngine !== 'undefined', 'HopfieldMemoryEngine OK');
  log('✓ APIs disponibles');
});

window.MemoryStorage = { initEngines, testRecall, batchTest };

