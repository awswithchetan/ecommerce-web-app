import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

function Navbar({ signOut, user }) {
  const displayName = user?.signInDetails?.loginId || user?.username || 'User';
  
  return (
    <nav className="navbar">
      <div className="nav-brand">
        <Link to="/">eCommerce Store</Link>
      </div>
      <div className="nav-links">
        <Link to="/">Products</Link>
        <Link to="/cart">Cart</Link>
        <Link to="/orders">Orders</Link>
        {user && (
          <div className="user-info">
            <span className="user-name">{displayName}</span>
            <button onClick={signOut} className="signout-btn">Sign Out</button>
          </div>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
