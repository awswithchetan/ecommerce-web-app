const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080/api';

// Get current authenticated user ID
const getUserId = async () => {
  try {
    const { fetchAuthSession } = await import('aws-amplify/auth');
    const session = await fetchAuthSession();
    return session.tokens?.idToken?.payload?.sub;
  } catch (error) {
    return null;
  }
};

export const api = {
  // Products (public)
  getProducts: () => 
    fetch(`${API_BASE_URL}/products`).then(res => res.json()),
  
  getProduct: (id) => 
    fetch(`${API_BASE_URL}/products/${id}`).then(res => res.json()),
  
  // Cart (authenticated)
  getCart: async () => {
    const userId = await getUserId();
    return fetch(`${API_BASE_URL}/cart`, {
      headers: { 'X-User-Id': userId }
    }).then(res => res.json());
  },
  
  addToCart: async (productId, quantity, price) => {
    const userId = await getUserId();
    return fetch(`${API_BASE_URL}/cart/items`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': userId
      },
      body: JSON.stringify({ product_id: productId, quantity, price })
    }).then(res => res.json());
  },
  
  removeFromCart: async (productId) => {
    const userId = await getUserId();
    return fetch(`${API_BASE_URL}/cart/items/${productId}`, {
      method: 'DELETE',
      headers: { 'X-User-Id': userId }
    }).then(res => res.json());
  },
  
  // Orders (authenticated)
  createOrder: async () => {
    const userId = await getUserId();
    return fetch(`${API_BASE_URL}/orders`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': userId
      },
      body: JSON.stringify({})
    }).then(res => res.json());
  },
  
  getOrders: async () => {
    const userId = await getUserId();
    return fetch(`${API_BASE_URL}/orders`, {
      headers: { 'X-User-Id': userId }
    }).then(res => res.json());
  },
  
  // User (authenticated)
  getProfile: async () => {
    const userId = await getUserId();
    return fetch(`${API_BASE_URL}/users/profile`, {
      headers: { 'X-User-Id': userId }
    }).then(res => res.json());
  },

  // Create user profile after Cognito signup
  createProfile: async (email, name) => {
    const userId = await getUserId();
    return fetch(`${API_BASE_URL}/users/profile`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        cognito_sub: userId,
        email: email,
        name: name
      })
    }).then(res => res.json());
  },
};

