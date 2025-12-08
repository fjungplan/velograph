import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './HamburgerMenu.css';

export default function HamburgerMenu() {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleMenuItemClick = (path) => {
    setIsOpen(false);
    navigate(path);
  };

  return (
    <div className="hamburger-menu" ref={menuRef}>
      <button
        className="hamburger-button"
        onClick={() => setIsOpen(!isOpen)}
        title="Navigation"
        aria-label="Toggle navigation menu"
      >
        <span className="hamburger-icon">
          <span></span>
          <span></span>
          <span></span>
        </span>
      </button>

      {isOpen && (
        <div className="hamburger-dropdown">
          <button className="menu-item" onClick={() => handleMenuItemClick('/')}>
            Timeline
          </button>
          <button className="menu-item" onClick={() => handleMenuItemClick('/about')}>
            About
          </button>
          <button className="menu-item" onClick={() => handleMenuItemClick('/imprint')}>
            Impressum / Legal
          </button>
        </div>
      )}
    </div>
  );
}
