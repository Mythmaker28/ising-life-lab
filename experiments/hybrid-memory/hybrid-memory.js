import { CAMemoryEngine } from '../../src/memory/caMemoryEngine.js';
import { HopfieldMemoryEngine } from '../../src/memory/hopfieldMemoryEngine.js';
import { getDefaultPatterns } from '../memory-ai-lab/memory/attractorUtils.js';

const MEMORY_HALL_OF_FAME = ['B01/S3', 'B01/S23', 'B01/S34', 'B01/S2', 'B01/S4', 'B01/S13', 'B46/S58'];

let engines = {};
let patterns = [];
let logEl, initBtn, testBtn, benchmarkBtn;

document.addEventListener('DOMContentLoaded', () => {
  logEl = document.getElementById('log');
  initBtn = document.getElementById('initBtn');
  testBtn = document.getElementById('testBtn');
  benchmarkBtn = document.getElementById('benchmarkBtn');
  
  initBtn.addEventListener('click', initEngines);
  testBtn.addEventListener('click', testNoisyRecall);
  benchmarkBtn.addEventListener('click', benchmarkAll);
});

function log(msg, type = '') {
  const div = document.createElement('div');
  div.className = type;
  div.textContent = msg;
  logEl.appendChild(div);
  logEl.scrollTop = logEl.scrollHeight;
}

async function initEngines() {
  initBtn.disabled = true;
  log('🔧 Initialisation des engines...');
  
  patterns = getDefaultPatterns().map(p => p.grid);
  log(`✓ ${patterns.length} patterns chargés`);
  
  engines = {};
  MEMORY_HALL_OF_FAME.forEach(rule => {
    engines[rule] = CAMemoryEngine.create({ rule, width: 32, height: 32, steps: 80 });
    engines[rule].store(patterns);
  });
  
  engines.Hopfield = HopfieldMemoryEngine.create({ width: 32, height: 32 });
  engines.Hopfield.store(patterns);
  
  log(`✓ ${Object.keys(engines).length} engines initialisés (7 CA + Hopfield)`);
  testBtn.disabled = false;
  benchmarkBtn.disabled = false;
}

function testNoisyRecall() {
  log('\n🧪 Test avec bruit 5%...');
  const noisy = new Uint8Array(patterns[0]);
  for (let i = 0; i < noisy.length; i++) {
    if (Math.random() < 0.05) noisy[i] = 1 - noisy[i];
  }
  
  Object.entries(engines).forEach(([name, engine]) => {
    const result = engine.recall(noisy);
    const msg = `${name}: ${result.success ? '✅' : '❌'} distance=${result.distance}`;
    log(msg, result.success ? 'success' : 'fail');
  });
}

async function benchmarkAll() {
  benchmarkBtn.disabled = true;
  log('\n📊 Benchmark (noise 0.01, 0.05, 0.08)...');
  
  const noises = [0.01, 0.05, 0.08];
  const runs = 10;
  
  for (const [name, engine] of Object.entries(engines)) {
    const results = [];
    
    for (const noise of noises) {
      let success = 0;
      for (let r = 0; r < runs; r++) {
        const noisy = new Uint8Array(patterns[0]);
        for (let i = 0; i < noisy.length; i++) {
          if (Math.random() < noise) noisy[i] = 1 - noisy[i];
        }
        const out = engine.recall(noisy);
        if (out.success) success++;
      }
      results.push({ noise, recall: (success / runs * 100).toFixed(0) });
    }
    
    log(`${name}: ${results.map(r => `${r.recall}%@${r.noise}`).join(', ')}`);
  }
  
  benchmarkBtn.disabled = false;
  log('✅ Benchmark terminé');
}

window.HybridMemory = { initEngines, testNoisyRecall, benchmarkAll };
log('✅ Hybrid Memory System chargé');
log('💡 Cliquez "Initialize Engines" pour commencer');

