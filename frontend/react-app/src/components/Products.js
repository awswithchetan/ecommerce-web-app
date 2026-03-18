import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { useCart } from '../CartContext';
import './Products.css';

function Products({ user, onSignInClick }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const { refreshCartCount } = useCart();

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const data = await api.getProducts();
      setProducts(data);
    } catch (error) {
      setMessage('Error loading products');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      loadProducts();
      return;
    }
    setIsSearching(true);
    setLoading(true);
    try {
      const data = await api.searchProducts(searchQuery);
      setProducts(data);
    } catch (error) {
      setMessage('Error searching products');
    } finally {
      setLoading(false);
      setIsSearching(false);
    }
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    loadProducts();
  };

  const handleAddToCart = async (product) => {
    if (!user) {
      onSignInClick();
      return;
    }
    try {
      await api.addToCart(product.product_id, 1, product.price);
      setMessage(`Added ${product.name} to cart!`);
      refreshCartCount();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error adding to cart');
    }
  };

  if (loading) return <div className="loading">Loading products...</div>;

  return (
    <div className="products">
      <form className="search-bar" onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Search products..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <button type="submit">Search</button>
        {searchQuery && (
          <button type="button" onClick={handleClearSearch}>Clear</button>
        )}
      </form>

      {message && <div className="message">{message}</div>}

      <div className="product-grid">
        {products.length === 0 ? (
          <div className="no-results">No products found</div>
        ) : (
          products.map(product => (
            <div key={product.product_id} className="product-card">
              <img src={product.image_url} alt={product.name} />
              <h3>{product.name}</h3>
              <p>{product.description}</p>
              <div className="product-footer">
                <span className="price">${product.price}</span>
                <span className="stock">Stock: {product.stock}</span>
              </div>
              <button onClick={() => handleAddToCart(product)}>
                Add to Cart
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Products;
