import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { useAuthStore } from '../stores/authStore';
import {
  User,
  LoginResponse,
  RegisterData,
  Product,
  CartItem,
  CartSummary,
  AgentStatus,
  AgentPerformance,
  DashboardAnalytics,
  PaginatedResponse
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = useAuthStore.getState().token;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid, logout user
          useAuthStore.getState().logout();
        }
        
        // Format error message
        const message = error.response?.data?.detail || 
                       error.response?.data?.message || 
                       error.message || 
                       'An error occurred';
        
        return Promise.reject(new Error(message));
      }
    );
  }

  // Generic methods
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.get(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.post(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.put(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.delete(url, config);
    return response.data;
  }

  // Auth endpoints
  async login(email: string, password: string): Promise<LoginResponse> {
    return this.post<LoginResponse>('/api/auth/login', { email, password });
  }

  async register(userData: RegisterData): Promise<User> {
    return this.post<User>('/api/auth/register', userData);
  }

  async getCurrentUser(): Promise<User> {
    return this.get<User>('/api/auth/me');
  }

  // Product endpoints
  async getProducts(params?: any): Promise<PaginatedResponse<Product>> {
    const response = await this.get<PaginatedResponse<any>>('/api/products', { params });
    
    // Transform backend response to match frontend expectations
    const transformedItems = response.items.map((item: any) => ({
      ...item,
      price: item.current_price || item.price || 0,
      description: item.description || '',
      images: item.images || [],
      image_url: item.images && item.images.length > 0 ? item.images[0] : undefined,
      tags: item.tags || []
    }));
    
    return {
      ...response,
      items: transformedItems
    };
  }

  async getProduct(id: number): Promise<Product> {
    const product = await this.get<any>(`/api/products/${id}`);
    return {
      ...product,
      price: product.current_price || product.price || 0,
      description: product.description || '',
      images: product.images || [],
      image_url: product.images && product.images.length > 0 ? product.images[0] : undefined,
      tags: product.tags || []
    };
  }

  async getFeaturedProducts(): Promise<Product[]> {
    const products = await this.get<any[]>('/api/products/featured');
    return products.map((product: any) => ({
      ...product,
      price: product.current_price || product.price || 0,
      description: product.description || '',
      images: product.images || [],
      image_url: product.images && product.images.length > 0 ? product.images[0] : undefined,
      tags: product.tags || []
    }));
  }

  async getProductRecommendations(productId: number, limit?: number): Promise<Product[]> {
    return this.get<Product[]>(`/api/products/${productId}/recommendations`, { 
      params: { limit } 
    });
  }

  // Cart endpoints
  async getCart(): Promise<CartItem[]> {
    return this.get<CartItem[]>('/api/users/cart');
  }

  async addToCart(productId: number, quantity: number): Promise<CartItem> {
    return this.post<CartItem>('/api/users/cart', { product_id: productId, quantity });
  }

  async updateCartItem(itemId: number, quantity: number): Promise<CartItem> {
    return this.put<CartItem>(`/api/users/cart/${itemId}`, { quantity });
  }

  async removeFromCart(itemId: number): Promise<void> {
    return this.delete<void>(`/api/users/cart/${itemId}`);
  }

  async clearCart(): Promise<void> {
    return this.delete<void>('/api/users/cart');
  }

  async getCartSummary(): Promise<CartSummary> {
    return this.get<CartSummary>('/api/users/cart/summary');
  }

  // Order endpoints
  async createOrder(orderData: any) {
    return this.post('/api/orders', orderData);
  }

  async getUserOrders(params?: any) {
    return this.get('/api/orders', { params });
  }

  async getOrder(id: number) {
    return this.get(`/api/orders/${id}`);
  }

  async updateOrder(id: number, data: any) {
    return this.put(`/api/orders/${id}`, data);
  }

  // User endpoints
  async getUserRecommendations(limit?: number) {
    return this.get('/api/users/recommendations', { params: { limit } });
  }

  async createReview(reviewData: any) {
    return this.post('/api/users/reviews', reviewData);
  }

  async getUserReviews(params?: any) {
    return this.get('/api/users/reviews', { params });
  }

  // Admin endpoints
  async getAllOrders(params?: any) {
    return this.get('/api/orders/admin/all', { params });
  }

  async createProduct(productData: any) {
    return this.post('/api/products', productData);
  }

  async updateProduct(id: number, productData: any) {
    return this.put(`/api/products/${id}`, productData);
  }

  // Analytics endpoints
  async getDashboardAnalytics(days?: number): Promise<DashboardAnalytics> {
    return this.get<DashboardAnalytics>('/api/analytics/dashboard', { params: { days } });
  }

  async getSalesAnalytics(days?: number, groupBy?: string) {
    return this.get('/api/analytics/sales', { params: { days, group_by: groupBy } });
  }

  async getInventoryAnalytics() {
    return this.get('/api/analytics/inventory');
  }

  async getPricingAnalytics(days?: number) {
    return this.get('/api/analytics/pricing', { params: { days } });
  }

  async getCustomerServiceAnalytics(days?: number) {
    return this.get('/api/analytics/customer-service', { params: { days } });
  }

  async getAiAgentAnalytics(days?: number) {
    return this.get('/api/analytics/ai-agents', { params: { days } });
  }

  // AI Agent endpoints
  async getAgentStatus(): Promise<AgentStatus> {
    return this.get<AgentStatus>('/api/agents/status');
  }

  async executeAgent(agentName: string, context?: any) {
    return this.post(`/api/agents/execute/${agentName}`, { 
      agent_name: agentName, 
      context: context || {} 
    });
  }

  async executeAllAgents(context?: any) {
    return this.post('/api/agents/execute-all', context || {});
  }

  async activateAgent(agentName: string) {
    return this.post(`/api/agents/activate/${agentName}`);
  }

  async deactivateAgent(agentName: string) {
    return this.post(`/api/agents/deactivate/${agentName}`);
  }

  async generateRecommendations(userId: number, limit?: number) {
    return this.post('/api/agents/recommendations/generate', { 
      user_id: userId, 
      limit: limit || 10 
    });
  }

  async handleCustomerInquiry(userId: number, message: string, type?: string) {
    return this.post('/api/agents/customer-service/handle-inquiry', {
      user_id: userId,
      message,
      interaction_type: type || 'chat'
    });
  }

  async checkInventoryStatus() {
    return this.post('/api/agents/inventory/check-stock');
  }

  async optimizePricing() {
    return this.post('/api/agents/pricing/optimize');
  }

  async getAgentPerformance(): Promise<AgentPerformance> {
    return this.get<AgentPerformance>('/api/agents/analytics/agent-performance');
  }

  async getAgentLogs(agentName: string, limit?: number) {
    return this.get(`/api/agents/logs/${agentName}`, { params: { limit } });
  }
}

export const apiService = new ApiService();
export default apiService;
