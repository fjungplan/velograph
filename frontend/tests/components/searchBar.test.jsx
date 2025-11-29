import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SearchBar from '../../src/components/SearchBar';

describe('SearchBar', () => {
  const mockNodes = [
    {
      id: '1',
      founding_year: 2010,
      dissolution_year: null,
      eras: [
        { name: 'Team Sky', uci_code: 'SKY' },
        { name: 'Team Ineos', uci_code: 'IGD' }
      ]
    },
    {
      id: '2',
      founding_year: 2005,
      dissolution_year: 2019,
      eras: [
        { name: 'Astana Pro Team', uci_code: 'AST' }
      ]
    },
    {
      id: '3',
      founding_year: 2015,
      dissolution_year: null,
      eras: [
        { name: 'Team Jumbo-Visma', uci_code: 'TJV' },
        { name: 'Visma-Lease a Bike', uci_code: 'TVL' }
      ]
    }
  ];

  it('renders search input', () => {
    const mockOnTeamSelect = vi.fn();
    render(<SearchBar nodes={mockNodes} onTeamSelect={mockOnTeamSelect} />);
    
    const input = screen.getByPlaceholderText('Search teams...');
    expect(input).toBeDefined();
  });

  it('does not show results for searches less than 2 characters', async () => {
    const mockOnTeamSelect = vi.fn();
    render(<SearchBar nodes={mockNodes} onTeamSelect={mockOnTeamSelect} />);
    
    const input = screen.getByPlaceholderText('Search teams...');
    fireEvent.change(input, { target: { value: 'T' } });
    
    await waitFor(() => {
      const results = document.querySelector('.search-results');
      expect(results).toBeNull();
    });
  });

  it('shows search results for valid query', async () => {
    const mockOnTeamSelect = vi.fn();
    render(<SearchBar nodes={mockNodes} onTeamSelect={mockOnTeamSelect} />);
    
    const input = screen.getByPlaceholderText('Search teams...');
    fireEvent.change(input, { target: { value: 'Team' } });
    
    await waitFor(() => {
      const results = screen.getByText('Team Ineos');
      expect(results).toBeDefined();
    });
  });

  it('searches across all eras', async () => {
    const mockOnTeamSelect = vi.fn();
    render(<SearchBar nodes={mockNodes} onTeamSelect={mockOnTeamSelect} />);
    
    const input = screen.getByPlaceholderText('Search teams...');
    fireEvent.change(input, { target: { value: 'Sky' } });
    
    await waitFor(() => {
      // Should find the node even though "Sky" appears in an older era
      // Shows the latest matching era name (Team Sky)
      const results = screen.getByText('Team Sky');
      expect(results).toBeDefined();
    });
  });

  it('searches by UCI code', async () => {
    const mockOnTeamSelect = vi.fn();
    render(<SearchBar nodes={mockNodes} onTeamSelect={mockOnTeamSelect} />);
    
    const input = screen.getByPlaceholderText('Search teams...');
    fireEvent.change(input, { target: { value: 'AST' } });
    
    await waitFor(() => {
      const results = screen.getByText('Astana Pro Team');
      expect(results).toBeDefined();
    });
  });

  it('ranks exact matches higher', async () => {
    const mockOnTeamSelect = vi.fn();
    const { container } = render(<SearchBar nodes={mockNodes} onTeamSelect={mockOnTeamSelect} />);
    
    const input = screen.getByPlaceholderText('Search teams...');
    fireEvent.change(input, { target: { value: 'Team Ineos' } });
    
    await waitFor(() => {
      const results = container.querySelectorAll('.search-result-item');
      expect(results.length).toBeGreaterThan(0);
      // First result should be exact match
      expect(results[0].textContent).toContain('Team Ineos');
    });
  });

  it('calls onTeamSelect when result is clicked', async () => {
    const mockOnTeamSelect = vi.fn();
    render(<SearchBar nodes={mockNodes} onTeamSelect={mockOnTeamSelect} />);
    
    const input = screen.getByPlaceholderText('Search teams...');
    fireEvent.change(input, { target: { value: 'Ineos' } });
    
    await waitFor(() => {
      const result = screen.getByText('Team Ineos');
      fireEvent.click(result.closest('.search-result-item'));
      
      expect(mockOnTeamSelect).toHaveBeenCalledWith(
        expect.objectContaining({ id: '1' })
      );
    });
  });

  it('clears search term after selection', async () => {
    const mockOnTeamSelect = vi.fn();
    render(<SearchBar nodes={mockNodes} onTeamSelect={mockOnTeamSelect} />);
    
    const input = screen.getByPlaceholderText('Search teams...');
    fireEvent.change(input, { target: { value: 'Ineos' } });
    
    await waitFor(() => {
      const result = screen.getByText('Team Ineos');
      fireEvent.click(result.closest('.search-result-item'));
    });
    
    expect(input.value).toBe('');
  });

  it('shows dissolution year in metadata', async () => {
    const mockOnTeamSelect = vi.fn();
    render(<SearchBar nodes={mockNodes} onTeamSelect={mockOnTeamSelect} />);
    
    const input = screen.getByPlaceholderText('Search teams...');
    fireEvent.change(input, { target: { value: 'Astana' } });
    
    await waitFor(() => {
      const meta = screen.getByText('2005 - 2019');
      expect(meta).toBeDefined();
    });
  });

  it('shows "present" for active teams', async () => {
    const mockOnTeamSelect = vi.fn();
    render(<SearchBar nodes={mockNodes} onTeamSelect={mockOnTeamSelect} />);
    
    const input = screen.getByPlaceholderText('Search teams...');
    fireEvent.change(input, { target: { value: 'Ineos' } });
    
    await waitFor(() => {
      const meta = screen.getByText('2010 - present');
      expect(meta).toBeDefined();
    });
  });

  it('limits results to 10', async () => {
    const manyNodes = Array.from({ length: 20 }, (_, i) => ({
      id: `${i}`,
      founding_year: 2000 + i,
      dissolution_year: null,
      eras: [{ name: `Team ${i}`, uci_code: `T${i}` }]
    }));
    
    const mockOnTeamSelect = vi.fn();
    const { container } = render(<SearchBar nodes={manyNodes} onTeamSelect={mockOnTeamSelect} />);
    
    const input = screen.getByPlaceholderText('Search teams...');
    fireEvent.change(input, { target: { value: 'Team' } });
    
    await waitFor(() => {
      const results = container.querySelectorAll('.search-result-item');
      expect(results.length).toBeLessThanOrEqual(10);
    });
  });
});
