import axios from 'axios';
import type {
  User,
  Product,
  DiscountRule,
  Order,
} from '@/types';

const API_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_URL,
});

let getTokenFunction: (() => Promise<string | null>) | null = null;

// Set token getter function (called from App.tsx with Clerk's getToken)
export const setTokenGetter = (fn: () => Promise<string | null>) => {
  getTokenFunction = fn;
};

// Request interceptor to add Clerk auth token
api.interceptors.request.use(async (config) => {
  if (config.data instanceof FormData) {
    // Let the browser set multipart/form-data with the required boundary.
    delete config.headers['Content-Type'];
  } else {
    config.headers['Content-Type'] = 'application/json';
  }

  if (getTokenFunction) {
    try {
      const token = await getTokenFunction();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('Error getting auth token:', error);
    }
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clerk handles authentication, just show error
      console.error('Authentication error:', error);
    }
    return Promise.reject(error);
  }
);

// Auth
export const auth = {
  getCurrentUser: async (): Promise<User> => {
    const { data } = await api.get<User>('/auth/me');
    return data;
  },
  
  updateUser: async (userData: Partial<User>): Promise<User> => {
    const { data } = await api.patch<User>('/auth/me', userData);
    return data;
  },
};

// Products
export const products = {
  getAll: async (): Promise<Product[]> => {
    const { data } = await api.get<Product[]>('/products');
    return data;
  },
  
  getById: async (id: number): Promise<Product> => {
    const { data } = await api.get<Product>(`/products/${id}`);
    return data;
  },
  
  create: async (productData: Omit<Product, 'id' | 'user_id' | 'created_at' | 'updated_at'>): Promise<Product> => {
    const { data } = await api.post<Product>('/products', productData);
    return data;
  },
  
  update: async (id: number, productData: Partial<Product>): Promise<Product> => {
    const { data } = await api.put<Product>(`/products/${id}`, productData);
    return data;
  },
  
  delete: async (id: number): Promise<void> => {
    await api.delete(`/products/${id}`);
  },
};

// Discounts
export const discounts = {
  getByProduct: async (productId: number): Promise<DiscountRule[]> => {
    const { data } = await api.get<DiscountRule[]>(`/discounts/product/${productId}`);
    return data;
  },
  
  create: async (ruleData: Omit<DiscountRule, 'id' | 'created_at' | 'updated_at'>): Promise<DiscountRule> => {
    const { data } = await api.post<DiscountRule>('/discounts', ruleData);
    return data;
  },
  
  update: async (id: number, ruleData: Partial<DiscountRule>): Promise<DiscountRule> => {
    const { data } = await api.put<DiscountRule>(`/discounts/${id}`, ruleData);
    return data;
  },
  
  delete: async (id: number): Promise<void> => {
    await api.delete(`/discounts/${id}`);
  },
};

// Orders
export const orders = {
  getAll: async (status?: string): Promise<Order[]> => {
    const { data } = await api.get<Order[]>('/orders', {
      params: { status },
    });
    return data;
  },
  
  getById: async (id: number): Promise<Order> => {
    const { data } = await api.get<Order>(`/orders/${id}`);
    return data;
  },
  
  updateStatus: async (id: number, newStatus: string): Promise<void> => {
    await api.patch(`/orders/${id}/status`, null, {
      params: { new_status: newStatus },
    });
  },
};

// Telegram
export const telegram = {
  updateBotToken: async (botToken: string, botUsername?: string): Promise<void> => {
    await api.post('/telegram/update-bot-token', null, {
      params: { bot_token: botToken, bot_username: botUsername },
    });
  },
  
  setWebhook: async (webhookUrl: string): Promise<void> => {
    await api.post('/telegram/set-webhook', null, {
      params: { webhook_url: webhookUrl },
    });
  },
};

// Uploads
export const uploads = {
  getPresignedUrl: async (filename: string, contentType: string): Promise<{
    presigned_url: string;
    public_url: string;
    s3_key: string;
  }> => {
    const { data } = await api.post('/uploads/presigned-url', null, {
      params: { filename, content_type: contentType },
    });
    return data;
  },
  
  uploadFile: async (file: File): Promise<string> => {
    const formData = new FormData();
    formData.append('file', file);

    const { data } = await api.post<{ public_url: string }>('/uploads/local', formData);

    return data.public_url;
  },
};

export default api;
