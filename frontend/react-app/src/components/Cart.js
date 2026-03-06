import React, { useState, useEffect } from 'react';
import { api } from '../api';
import './Cart.css';

function Cart() {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadCart();
  }, []);

  const loadCart = async () => {
    try {
      const data = await api.getCart();
      setCart(data);
    } catch (error) {
      setMessage('Error loading cart');
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (productId) => {
    try {
      await api.removeFromCart(productId);
      setMessage('Item removed');
      loadCart();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error removing item');
    }
  };

  const handleCheckout = async () => {
    if (!cart?.items?.length) {
      setMessage('Cart is empty');
      return;
    }
    
    try {
      await api.createOrder();
      setMessage('Order placed successfully!');
      loadCart();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error placing order');
    }
  };

  const getTotal = () => {
    if (!cart?.items) return 0;
    return cart.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  };

  if (loading) return <div className="loading">Loading cart...</div>;

  return (
    <div className="cart">
      <h1>Shopping Cart</h1>
      {message && <div className="message">{message}</div>}
      
      {!cart?.items?.length ? (
        <div className="empty-cart">Your cart is empty</div>
      ) : (
        <>
          <div className="cart-items">
            {cart.items.map(item => (
              <div key={item.product_id} className="cart-item">
                <div className="item-info">
                  <h3>Product: {item.product_id}</h3>
                  <p>Quantity: {item.quantity}</p>
                  <p className="price">${item.price} each</p>
                </div>
                <div className="item-actions">
                  <p className="subtotal">${(item.price * item.quantity).toFixed(2)}</p>
                  <button onClick={() => handleRemove(item.product_id)}>Remove</button>
                </div>
              </div>
            ))}
          </div>
          
          <div className="cart-summary">
            <h2>Total: ${getTotal().toFixed(2)}</h2>
            <button className="checkout-btn" onClick={handleCheckout}>
              Place Order
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default Cart;
