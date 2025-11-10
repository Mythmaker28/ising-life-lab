export function createPatternItem(pattern, onDelete) {
  const item = document.createElement('div');
  item.className = 'pattern-item';
  item.dataset.patternId = pattern.id;
  
  const canvas = document.createElement('canvas');
  canvas.width = pattern.width * 4;
  canvas.height = pattern.height * 4;
  const ctx = canvas.getContext('2d');
  
  ctx.fillStyle = '#000000';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#00FF00';
  for (let y = 0; y < pattern.height; y++) {
    for (let x = 0; x < pattern.width; x++) {
      const idx = y * pattern.width + x;
      if (pattern.grid[idx] === 1) {
        ctx.fillRect(x * 4, y * 4, 4, 4);
      }
    }
  }
  
  const name = document.createElement('div');
  name.className = 'pattern-name';
  name.textContent = pattern.name;
  
  const info = document.createElement('div');
  info.className = 'pattern-info';
  info.textContent = `${pattern.width}×${pattern.height}`;
  
  const deleteBtn = document.createElement('button');
  deleteBtn.className = 'delete-btn';
  deleteBtn.textContent = '×';
  deleteBtn.onclick = () => onDelete(pattern.id);
  
  item.appendChild(canvas);
  item.appendChild(name);
  item.appendChild(info);
  item.appendChild(deleteBtn);
  
  return item;
}

export function createResultsTable(results) {
  const table = document.createElement('table');
  table.className = 'results-table';
  
  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');
  ['Pattern', 'Rule', 'Recall Rate', 'Status', 'Attractors', 'Coverage'].forEach(text => {
    const th = document.createElement('th');
    th.textContent = text;
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);
  table.appendChild(thead);
  
  const tbody = document.createElement('tbody');
  results.forEach(result => {
    const row = document.createElement('tr');
    const cells = [
      result.patternId,
      result.ruleId,
      `${(result.recallRate * 100).toFixed(1)}%`,
      result.status,
      result.attractors.length,
      `${(result.coverage * 100).toFixed(1)}%`
    ];
    
    cells.forEach((text, i) => {
      const td = document.createElement('td');
      if (i === 2) {
        td.textContent = text;
        td.style.fontWeight = 'bold';
        td.style.color = parseFloat(text) >= 60 ? '#00ff88' : parseFloat(text) >= 40 ? '#ffaa00' : '#ff4444';
      } else if (i === 3) {
        td.textContent = text;
        td.className = `status-${text.toLowerCase()}`;
      } else {
        td.textContent = text;
      }
      row.appendChild(td);
    });
    
    tbody.appendChild(row);
  });
  table.appendChild(tbody);
  
  return table;
}

export function createComparisonTable(hopfieldResults, caResults) {
  const table = document.createElement('table');
  table.className = 'results-table';
  
  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');
  ['Pattern', 'Hopfield Recall', 'CA Recall', 'Winner', 'Δ'].forEach(text => {
    const th = document.createElement('th');
    th.textContent = text;
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);
  table.appendChild(thead);
  
  const tbody = document.createElement('tbody');
  const caMap = new Map();
  caResults.forEach(r => caMap.set(r.patternId, r));
  
  hopfieldResults.forEach(hopResult => {
    const caResult = caMap.get(hopResult.patternId);
    if (!caResult) return;
    
    const row = document.createElement('tr');
    const hopRecall = hopResult.recallRate * 100;
    const caRecall = caResult.recallRate * 100;
    const delta = hopRecall - caRecall;
    const winner = delta > 5 ? 'Hopfield' : delta < -5 ? 'CA' : 'Tie';
    
    const cells = [
      hopResult.patternId,
      `${hopRecall.toFixed(1)}%`,
      `${caRecall.toFixed(1)}%`,
      winner,
      `${delta > 0 ? '+' : ''}${delta.toFixed(1)}%`
    ];
    
    cells.forEach((text, i) => {
      const td = document.createElement('td');
      if (i === 3) {
        td.textContent = text;
        td.className = text === 'Hopfield' ? 'status-ok' : text === 'CA' ? 'status-weak' : '';
        td.style.fontWeight = 'bold';
      } else if (i === 4) {
        td.textContent = text;
        td.style.color = delta > 0 ? '#00ff88' : delta < 0 ? '#ffaa00' : '#aaa';
        td.style.fontWeight = 'bold';
      } else {
        td.textContent = text;
      }
      row.appendChild(td);
    });
    
    tbody.appendChild(row);
  });
  
  table.appendChild(tbody);
  return table;
}

export function updateProgressBar(fillElement, textElement, percentage) {
  fillElement.style.width = `${percentage}%`;
  textElement.textContent = `${percentage.toFixed(1)}%`;
}

