import { useEffect, useRef } from 'react';
import './Tooltip.css';

export default function Tooltip({ content, position, visible }) {
  const tooltipRef = useRef(null);

  useEffect(() => {
    if (visible && tooltipRef.current && position) {
      const tooltip = tooltipRef.current;
      const rect = tooltip.getBoundingClientRect();

      let x = position.x + 15;
      let y = position.y - 10;

      if (x + rect.width > window.innerWidth) {
        x = position.x - rect.width - 15;
      }
      if (y + rect.height > window.innerHeight) {
        y = window.innerHeight - rect.height - 10;
      }

      tooltip.style.left = `${x}px`;
      tooltip.style.top = `${y}px`;
    }
  }, [position, visible]);

  if (!visible || !content) return null;

  return (
    <div ref={tooltipRef} className="timeline-tooltip">
      {content}
    </div>
  );
}
