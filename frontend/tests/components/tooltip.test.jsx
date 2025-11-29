import { describe, it, expect, beforeEach } from 'vitest';
import { JSDOM } from 'jsdom';
import React from 'react';
import { render } from '@testing-library/react';
import Tooltip from '../../src/components/Tooltip';

describe('Tooltip component', () => {
  let dom;
  beforeEach(() => {
    dom = new JSDOM('<!DOCTYPE html><html><body></body></html>');
    global.document = dom.window.document;
    global.window = dom.window;
  });

  it('renders nothing when not visible', () => {
    const { container } = render(<Tooltip content={<div>Hi</div>} position={{ x: 0, y: 0 }} visible={false} />);
    expect(container.querySelector('.timeline-tooltip')).toBeNull();
  });

  it('renders content when visible', () => {
    const { container } = render(<Tooltip content={<div className="payload">Hi</div>} position={{ x: 10, y: 10 }} visible={true} />);
    const tooltip = container.querySelector('.timeline-tooltip');
    expect(tooltip).not.toBeNull();
    expect(container.querySelector('.payload')).not.toBeNull();
  });
});
