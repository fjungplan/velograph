/**
 * Determine which nodes are visible in current viewport
 */
export class ViewportManager {
  constructor(width, height) {
    this.width = width;
    this.height = height;
    this.padding = 100; // Extra padding for smooth scrolling
  }

  getVisibleNodes(nodes, transform) {
    const { x, y, k: scale } = transform;

    const viewLeft = -x / scale;
    const viewRight = (this.width - x) / scale;
    const viewTop = -y / scale;
    const viewBottom = (this.height - y) / scale;

    return nodes.filter((node) => {
      const nodeRight = node.x + node.width;
      const nodeBottom = node.y + node.height;

      return !(
        nodeRight < viewLeft - this.padding ||
        node.x > viewRight + this.padding ||
        nodeBottom < viewTop - this.padding ||
        node.y > viewBottom + this.padding
      );
    });
  }

  getVisibleLinks(links, visibleNodeIds) {
    return links.filter(
      (link) => visibleNodeIds.has(link.source) || visibleNodeIds.has(link.target)
    );
  }
}
