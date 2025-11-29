
import { describe, it, expect } from 'vitest';
import { validateHexColor, getContrastColor, lightenColor } from '../../src/utils/colorUtils';

describe('colorUtils', () => {
  it('validates hex color', () => {
    expect(validateHexColor('#123ABC')).toBe('#123ABC');
    expect(validateHexColor('123ABC')).toBe('#4A90E2');
    expect(validateHexColor('#XYZ123')).toBe('#4A90E2');
  });

  it('gets contrast color', () => {
    expect(getContrastColor('#FFFFFF')).toBe('#000000');
    expect(getContrastColor('#000000')).toBe('#FFFFFF');
    // #4A90E2 has light luminance; black text provides better contrast with current algorithm
    expect(getContrastColor('#4A90E2')).toBe('#000000');
  });

  it('lightens color', () => {
    expect(lightenColor('#000000', 20)).toMatch(/^#([0-9A-F]{6})$/i);
    expect(lightenColor('#123456', 30)).toMatch(/^#([0-9A-F]{6})$/i);
  });
});
