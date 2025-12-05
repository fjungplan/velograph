import { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './UserMenu.css';

export default function UserMenu() {
  const { user, logout, isAdmin, canEdit, needsModeration } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (!user) return null;

  const handleLogout = () => {
    logout();
    setIsOpen(false);
  };

  const handleMenuItemClick = () => {
    setIsOpen(false);
  };

  return (
    <div className="user-menu" ref={menuRef}>
      <button
        className="user-avatar"
        onClick={() => setIsOpen(!isOpen)}
        title={user.display_name || user.email}
      >
        {user.avatar_url ? (
          <img src={user.avatar_url} alt={user.display_name} />
        ) : (
          <div className="avatar-placeholder">
            {user.display_name?.[0] || user.email[0]}
          </div>
        )}
      </button>

      {isOpen && (
        <div className="user-menu-dropdown">
          <div className="user-info">
            <div className="user-name">{user.display_name || user.email}</div>
            <div className="user-role">
              {isAdmin() && <span className="badge admin">Admin</span>}
              {needsModeration() && <span className="badge new">New User</span>}
              {canEdit() && !isAdmin() && !needsModeration() && (
                <span className="badge trusted">Trusted</span>
              )}
              {!canEdit() && !isAdmin() && (
                <span className="badge guest">Guest</span>
              )}
            </div>
            <div className="user-stats">
              {user.approved_edits_count} edits approved
            </div>
          </div>

          <div className="menu-divider" />

          {canEdit() && (
            <>
              <button className="menu-item" onClick={handleMenuItemClick}>
                My Edits
              </button>
              <div className="menu-divider" />
            </>
          )}

          {isAdmin() && (
            <>
              <button className="menu-item" onClick={handleMenuItemClick}>
                Moderation Queue
              </button>
              <button className="menu-item" onClick={handleMenuItemClick}>
                Admin Panel
              </button>
              <div className="menu-divider" />
            </>
          )}

          <button className="menu-item logout" onClick={handleLogout}>
            Sign Out
          </button>
        </div>
      )}
    </div>
  );
}
