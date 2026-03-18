import awsConfig from './aws-config';

const API_BASE_URL = awsConfig.API.baseUrl || process.env.REACT_APP_API_URL || 'http://localhost:8080/api';

// Get authentication headers
const getAuthHeaders = async () => {
  try {
    const { fetchAuthSession } = await import('aws-amplify/auth');
    const session = await fetchAuthSession();
    const token = session.tokens?.idToken?.toString();
    
    if (token) {
      const payload = session.tokens?.idToken?.payload;
      return {
        'Authorization': `Bearer ${token}`,
        'X-User-Id': payload?.sub || '',
        'X-User-Email': payload?.email || '',
        'X-User-Name': payload?.name || payload?.username || ''
      };
    }
    return {};
  } catch (error) {
    console.error('Error getting auth token:', error);
    return {};
  }
};

export const api = {
  // Search (public)
  searchProducts: (query, category) => {
    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (category) params.append('category', category);
    return fetch(`${API_BASE_URL}/search?${params.toString()}`).then(res => res.json());
  },

  // Products (public)
  getProducts: () => 
    fetch(`${API_BASE_URL}/products`).then(res => res.json()),
  
  getProduct: (id) => 
    fetch(`${API_BASE_URL}/products/${id}`).then(res => res.json()),
  
  // Cart (authenticated)
  getCart: async () => {
    const headers = await getAuthHeaders();
    return fetch(`${API_BASE_URL}/cart`, {
      headers
    }).then(res => res.json());
  },
  
  addToCart: async (productId, quantity, price) => {
    const headers = await getAuthHeaders();
    return fetch(`${API_BASE_URL}/cart/items`, {
      method: 'POST',
      headers: {
        ...headers,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ product_id: productId, quantity, price })
    }).then(res => res.json());
  },
  
  removeFromCart: async (productId) => {
    const headers = await getAuthHeaders();
    return fetch(`${API_BASE_URL}/cart/items/${productId}`, {
      method: 'DELETE',
      headers
    }).then(res => res.json());
  },
  
  // Orders (authenticated)
  createOrder: async () => {
    const headers = await getAuthHeaders();
    return fetch(`${API_BASE_URL}/orders`, {
      method: 'POST',
      headers: {
        ...headers,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    }).then(res => res.json());
  },
  
  getOrders: async () => {
    const headers = await getAuthHeaders();
    return fetch(`${API_BASE_URL}/orders`, {
      headers
    }).then(res => res.json());
  },
  
  // User (authenticated)
  getProfile: async () => {
    const headers = await getAuthHeaders();
    return fetch(`${API_BASE_URL}/users/profile`, {
      headers
    }).then(res => res.json());
  },

  // Create user profile after Cognito signup
  createProfile: async (email, name) => {
    const headers = await getAuthHeaders();
    const { fetchAuthSession } = await import('aws-amplify/auth');
    const session = await fetchAuthSession();
    const userId = session.tokens?.idToken?.payload?.sub;
    
    return fetch(`${API_BASE_URL}/users/profile`, {
      method: 'POST',
      headers: {
        ...headers,
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

