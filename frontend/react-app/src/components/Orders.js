import React, { useState, useEffect } from 'react';
import { api } from '../api';
import './Orders.css';

function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      const data = await api.getOrders();
      setOrders(data);
    } catch (error) {
      console.error('Error loading orders:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading orders...</div>;

  return (
    <div className="orders">
      <h1>My Orders</h1>
      
      {!orders.length ? (
        <div className="no-orders">No orders yet</div>
      ) : (
        <div className="orders-list">
          {orders.map(order => (
            <div key={order.id} className="order-card">
              <div className="order-header">
                <h3>Order #{order.id}</h3>
                <span className="status">{order.status}</span>
              </div>
              <p className="order-date">
                {new Date(order.created_at).toLocaleDateString()}
              </p>
              <div className="order-items">
                {order.items.map((item, idx) => (
                  <div key={idx} className="order-item">
                    <span>{item.product_id}</span>
                    <span>Qty: {item.quantity}</span>
                    <span>${item.price}</span>
                  </div>
                ))}
              </div>
              <div className="order-total">
                <strong>Total: ${order.total_amount}</strong>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Orders;
