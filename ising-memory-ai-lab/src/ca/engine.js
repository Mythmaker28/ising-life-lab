/**
 * CA Engine - Moteur CA Life-like torique optimisé
 * Utilise Uint8Array pour performance maximale
 */

export class CAEngine {
  constructor(width, height) {
    this.width = width;
    this.height = height;
    this.grid = this.createEmptyGrid();
  }

  createEmptyGrid() {
    return new Uint8Array(this.width * this.height);
  }

  step(grid, rule) {
    const newGrid = new Uint8Array(grid.length);
    
    for (let y = 0; y < this.height; y++) {
      for (let x = 0; x < this.width; x++) {
        const idx = y * this.width + x;
        const neighbors = this.countNeighbors(grid, x, y);
        const isAlive = grid[idx] === 1;
        
        if (isAlive) {
          newGrid[idx] = rule.survive.includes(neighbors) ? 1 : 0;
        } else {
          newGrid[idx] = rule.born.includes(neighbors) ? 1 : 0;
        }
      }
    }
    
    return newGrid;
  }

  countNeighbors(grid, x, y) {
    let count = 0;
    for (let dy = -1; dy <= 1; dy++) {
      for (let dx = -1; dx <= 1; dx++) {
        if (dx === 0 && dy === 0) continue;
        
        const nx = (x + dx + this.width) % this.width;
        const ny = (y + dy + this.height) % this.height;
        const idx = ny * this.width + nx;
        
        count += grid[idx];
      }
    }
    return count;
  }

  run(grid, rule, steps) {
    let current = grid;
    for (let i = 0; i < steps; i++) {
      current = this.step(current, rule);
    }
    return current;
  }

  randomGrid(density = 0.5) {
    const grid = new Uint8Array(this.width * this.height);
    for (let i = 0; i < grid.length; i++) {
      grid[i] = Math.random() < density ? 1 : 0;
    }
    return grid;
  }

  cloneGrid(grid) {
    return new Uint8Array(grid);
  }

  getPopulation(grid) {
    let count = 0;
    for (let i = 0; i < grid.length; i++) {
      count += grid[i];
    }
    return count;
  }
}




