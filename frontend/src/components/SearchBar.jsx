import React, { useState, useEffect, useRef } from 'react';
import './SearchBar.css';

export default function SearchBar({ nodes, onTeamSelect }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const searchRef = useRef(null);
  
  useEffect(() => {
    if (searchTerm.length < 2) {
      setResults([]);
      return;
    }
    
    const filtered = searchTeams(nodes, searchTerm);
    setResults(filtered.slice(0, 10)); // Limit to 10 results
    setShowResults(true);
  }, [searchTerm, nodes]);
  
  // Close results when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowResults(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);
  
  const searchTeams = (nodes, term) => {
    const lowerTerm = term.toLowerCase();
    
    return nodes
      .map(node => {
        // Search across all eras
        const matchingEras = node.eras.filter(era =>
          era.name.toLowerCase().includes(lowerTerm) ||
          era.uci_code?.toLowerCase().includes(lowerTerm)
        );
        
        if (matchingEras.length === 0) return null;
        
        return {
          node,
          primaryName: matchingEras[matchingEras.length - 1].name,
          allNames: [...new Set(matchingEras.map(e => e.name))],
          score: calculateRelevance(matchingEras, term)
        };
      })
      .filter(Boolean)
      .sort((a, b) => b.score - a.score);
  };
  
  const calculateRelevance = (eras, term) => {
    let score = 0;
    const lowerTerm = term.toLowerCase();
    
    eras.forEach(era => {
      const name = era.name.toLowerCase();
      if (name === lowerTerm) score += 100;
      else if (name.startsWith(lowerTerm)) score += 50;
      else if (name.includes(lowerTerm)) score += 25;
      
      if (era.uci_code?.toLowerCase() === lowerTerm) score += 100;
    });
    
    return score;
  };
  
  const handleSelect = (result) => {
    onTeamSelect(result.node);
    setSearchTerm('');
    setShowResults(false);
  };
  
  return (
    <div className="search-bar" ref={searchRef}>
      <input
        type="text"
        placeholder="Search teams..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        onFocus={() => results.length > 0 && setShowResults(true)}
      />
      {showResults && results.length > 0 && (
        <div className="search-results">
          {results.map((result, index) => (
            <div 
              key={result.node.id}
              className="search-result-item"
              onClick={() => handleSelect(result)}
            >
              <div className="result-name">{result.primaryName}</div>
              {result.allNames.length > 1 && (
                <div className="result-aliases">
                  Also known as: {result.allNames.filter(n => n !== result.primaryName).join(', ')}
                </div>
              )}
              <div className="result-meta">
                {result.node.founding_year}
                {result.node.dissolution_year ? ` - ${result.node.dissolution_year}` : ' - present'}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
