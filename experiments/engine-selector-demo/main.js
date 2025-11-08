import { createMemoryAI } from '../../src/memory/memoryAI.js';
import { getDefaultPatterns } from '../memory-ai-lab/memory/attractorUtils.js';

let memAI = null;
let patterns = null;

function addNoise(grid, rate) {
  const noisy = new Uint8Array(grid);
  for (let i = 0; i < noisy.length; i++) {
    if (Math.random() < rate) noisy[i] = 1 - noisy[i];
  }
  return noisy;
}

async function runDemo() {
  const btn = document.getElementById('btn-demo');
  const status = document.getElementById('status');
  
  btn.disabled = true;
  status.style.display = 'block';
  status.textContent = '🔄 Initializing MemoryAI with selector...';
  
  try {
    // Create with selector
    patterns = getDefaultPatterns();
    memAI = createMemoryAI({ width: 32, height: 32, steps: 80, useSelector: true });
    memAI.store(patterns);
    
    status.textContent = '⏳ Training selector (15s)...';
    await new Promise(r => setTimeout(r, 15000));
    
    // Test
    status.textContent = '🧪 Testing recall...';
    const noisy = addNoise(patterns[0], 0.08);
    
    const t1 = performance.now();
    const resultAll = memAI.recall(noisy);
    const t2 = performance.now();
    
    const t3 = performance.now();
    const resultPred = memAI.recall(noisy, { usePrediction: true, patternIndex: 0 });
    const t4 = performance.now();
    
    const timeAll = t2 - t1;
    const timePred = t4 - t3;
    const speedup = (timeAll / timePred).toFixed(1);
    
    status.innerHTML = `
✅ Demo complete!<br>
Without prediction: ${timeAll.toFixed(1)}ms (tested ${resultAll.all.length} engines)<br>
With prediction: ${timePred.toFixed(1)}ms (tested ${resultPred.all.length} engine)<br>
Speedup: ${speedup}×<br>
Best engine: ${resultPred.best.rule}
    `;
    
    console.log('Without prediction:', resultAll);
    console.log('With prediction:', resultPred);
    console.log(`Speedup: ${speedup}×`);
    
  } catch (error) {
    status.innerHTML = `❌ Error: ${error.message}`;
    console.error(error);
  } finally {
    btn.disabled = false;
  }
}

async function runBenchmark() {
  const btn = document.getElementById('btn-benchmark');
  const status = document.getElementById('status');
  const metricsDiv = document.getElementById('metrics');
  const resultsDiv = document.getElementById('results');
  
  btn.disabled = true;
  status.style.display = 'block';
  status.textContent = '🔄 Running benchmark...';
  
  try {
    patterns = getDefaultPatterns();
    memAI = createMemoryAI({ width: 32, height: 32, steps: 80, useSelector: true });
    memAI.store(patterns);
    
    status.textContent = '⏳ Training selector...';
    await new Promise(r => setTimeout(r, 15000));
    
    // Benchmark
    const samples = 100;
    let timeWithout = 0;
    let timeWith = 0;
    let correct = 0;
    
    for (let i = 0; i < samples; i++) {
      status.textContent = `🧪 Testing ${i + 1}/${samples}...`;
      
      const pi = Math.floor(Math.random() * patterns.length);
      const noisy = addNoise(patterns[pi], 0.05 + Math.random() * 0.05);
      
      const t1 = performance.now();
      const r1 = memAI.recall(noisy);
      timeWithout += performance.now() - t1;
      
      const t2 = performance.now();
      const r2 = memAI.recall(noisy, { usePrediction: true, patternIndex: pi });
      timeWith += performance.now() - t2;
      
      if (r1.best.rule === r2.best.rule) correct++;
    }
    
    const speedup = (timeWithout / timeWith).toFixed(1);
    const accuracy = (correct / samples * 100).toFixed(1);
    
    // Update UI
    metricsDiv.style.display = 'grid';
    document.getElementById('metric-speedup').textContent = speedup + '×';
    document.getElementById('metric-accuracy').textContent = accuracy + '%';
    document.getElementById('metric-samples').textContent = samples;
    
    // Global wins table
    const wins = memAI.selector.globalWins;
    const html = `
      <h3 style="color: #00ff88; margin: 20px 0 10px;">Engine Performance</h3>
      <table>
        <thead>
          <tr>
            <th>Engine</th>
            <th>Wins</th>
            <th>Win Rate</th>
          </tr>
        </thead>
        <tbody>
          ${Object.entries(wins).sort((a,b) => b[1] - a[1]).map(([engine, count]) => {
            const total = Object.values(wins).reduce((s,c) => s + c, 0);
            const rate = (count / total * 100).toFixed(1);
            return `
              <tr>
                <td><code>${engine}</code></td>
                <td class="${count > total * 0.2 ? 'high' : count > total * 0.1 ? 'medium' : 'low'}">${count}</td>
                <td>${rate}%</td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    `;
    
    resultsDiv.innerHTML = html;
    
    status.innerHTML = `✅ Benchmark complete!<br>Speedup: ${speedup}×, Accuracy: ${accuracy}%`;
    
    console.log('Benchmark results:', {
      speedup,
      accuracy,
      samples,
      wins
    });
    
  } catch (error) {
    status.innerHTML = `❌ Error: ${error.message}`;
    console.error(error);
  } finally {
    btn.disabled = false;
  }
}

document.getElementById('btn-demo')?.addEventListener('click', runDemo);
document.getElementById('btn-benchmark')?.addEventListener('click', runBenchmark);

console.log('🎯 Engine Selector Demo loaded');
console.log('💡 Click "Run Demo" for quick test or "Run Benchmark" for full analysis');

