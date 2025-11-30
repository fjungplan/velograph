import * as d3 from 'd3';

export class OptimizedRenderer {
  constructor(svg, performanceMonitor) {
    this.svg = svg;
    this.monitor = performanceMonitor;
    this.renderQueue = [];
    this.isRendering = false;
  }

  queueRender(renderFn) {
    this.renderQueue.push(renderFn);
    if (!this.isRendering) {
      this.processQueue();
    }
  }

  processQueue() {
    if (this.renderQueue.length === 0) {
      this.isRendering = false;
      return;
    }
    this.isRendering = true;
    requestAnimationFrame(() => {
      const startTime = this.monitor.startTiming('render');
      while (this.renderQueue.length > 0) {
        const renderFn = this.renderQueue.shift();
        renderFn();
      }
      this.monitor.endTiming('render', startTime);
      this.isRendering = false;
    });
  }

  renderWithLOD(nodes, links, scale) {
    const useLowDetail = nodes.length > 100 || scale < 0.8;
    if (useLowDetail) {
      this.renderLowDetail(nodes, links);
    } else {
      this.renderHighDetail(nodes, links);
    }
  }

  renderLowDetail(_nodes, _links) {
    const g = d3.select(this.svg).select('g');
    g.selectAll('.node text').style('display', 'none');
    g.selectAll('.node rect').attr('fill', (d) => {
      const sponsors = d?.eras?.[d.eras.length - 1]?.sponsors || [];
      return sponsors[0]?.color || '#4A90E2';
    });
  }

  renderHighDetail(_nodes, _links) {
    const g = d3.select(this.svg).select('g');
    g.selectAll('.node text').style('display', null);
    // Gradients are assumed to be defined by JerseyRenderer
  }

  renderToCanvas(canvas, nodes, links, transform) {
    const ctx = canvas.getContext('2d');
    const { x, y, k: scale } = transform;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(scale, scale);

    links.forEach((link) => {
      ctx.beginPath();
      ctx.moveTo(link.sourceX, link.sourceY);
      ctx.lineTo(link.targetX, link.targetY);
      ctx.strokeStyle = link.type === 'SPIRITUAL_SUCCESSION' ? '#999' : '#333';
      ctx.lineWidth = 2 / scale;
      ctx.stroke();
    });

    nodes.forEach((node) => {
      ctx.fillStyle = node.eras?.[node.eras.length - 1]?.sponsors?.[0]?.color || '#4A90E2';
      ctx.fillRect(node.x, node.y, node.width, node.height);
      ctx.strokeStyle = '#333';
      ctx.lineWidth = 2 / scale;
      ctx.strokeRect(node.x, node.y, node.width, node.height);
    });

    ctx.restore();
  }
}
