import React, { useState, useEffect } from 'react';
import { api } from '../api';
import './Products.css';

function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      const data = await api.getProducts();
      setProducts(data);
    } catch (error) {
      setMessage('Error loading products');
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = async (product) => {
    try {
      await api.addToCart(product.product_id, 1, product.price);
      setMessage(`Added ${product.name} to cart!`);
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error adding to cart');
    }
  };

  if (loading) return <div className="loading">Loading products...</div>;

  return (
    <div className="products">
      <h1>Products</h1>
      {message && <div className="message">{message}</div>}
      <div className="product-grid">
        {products.map(product => (
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
        ))}
      </div>
    </div>
  );
}

export default Products;
