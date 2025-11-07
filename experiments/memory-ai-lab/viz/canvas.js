export class CARenderer {
  constructor(canvasId, width, height, cellSize = 8) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) throw new Error(`Canvas ${canvasId} not found`);
    this.ctx = this.canvas.getContext('2d', { alpha: false });
    this.width = width;
    this.height = height;
    this.cellSize = cellSize;
    this.canvas.width = width * cellSize;
    this.canvas.height = height * cellSize;
    this.canvas.style.imageRendering = 'pixelated';
  }
  
  render(grid) {
    const { ctx, width, height, cellSize } = this;
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    ctx.fillStyle = '#00FF00';
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const idx = y * width + x;
        if (grid[idx] === 1) {
          ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
        }
      }
    }
  }
  
  clear() {
    const { ctx } = this;
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  }
}

