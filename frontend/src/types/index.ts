// User types
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  is_admin: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  token: string;
  user: User;
}

// Product types
export interface Product {
  id: number;
  name: string;
  description: string;
  sku?: string;
  category_id?: number;
  category_name?: string;
  base_price?: number;
  current_price?: number;
  price: number; // Main price field (mapped from current_price)
  stock_quantity: number;
  image_url?: string; // Legacy single image field
  images?: string[]; // New multiple images field
  tags?: string[];
  is_active?: boolean;
  is_featured?: boolean;
  demand_score?: number;
  price_elasticity?: number;
  created_at?: string;
  updated_at?: string;
  category?: Category;
  average_rating?: number;
  review_count?: number;
}

export interface Category {
  id: number;
  name: string;
  description?: string;
}

// Cart types
export interface CartItem {
  id: number;
  product_id: number;
  quantity: number;
  price: number;
  product: Product;
}

export interface CartSummary {
  items: CartItem[];
  total_items: number;
  subtotal: number;
  tax: number;
  total: number;
  total_amount: number;
}

// Order types
export interface Order {
  id: number;
  user_id: number;
  status: 'pending' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  total_amount: number;
  shipping_address: string;
  billing_address: string;
  created_at: string;
  updated_at: string;
  items: OrderItem[];
}

export interface OrderItem {
  id: number;
  order_id: number;
  product_id: number;
  quantity: number;
  price: number;
  product: Product;
}

// Agent types
export interface AgentStatus {
  [agentName: string]: {
    is_active: boolean;
    execution_count: number;
    last_execution?: string;
    status?: string;
  };
}

export interface AgentPerformance {
  total_executions: number;
  success_rate: number;
  average_execution_time: number;
  agent_breakdown: {
    [agentName: string]: {
      executions: number;
      success_rate: number;
      avg_time: number;
    };
  };
}

// Analytics types
export interface DashboardAnalytics {
  revenue: {
    total_revenue: number;
    total_orders: number;
    average_order_value: number;
    growth_rate: number;
  };
  users: {
    total_users: number;
    active_users: number;
    new_users: number;
    growth_rate: number;
  };
  products: {
    total_products: number;
    low_stock_products: number;
    stock_alert_rate: number;
    out_of_stock: number;
  };
  top_selling_products: Array<{
    id: number;
    name: string;
    sales_count: number;
    revenue: number;
  }>;
  ai_agents: {
    performance: Array<{
      agent_name: string;
      execution_count: number;
      success_rate: number;
      avg_execution_time: number;
    }>;
  };
}

// API Response types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// Review types
export interface Review {
  id: number;
  user_id: number;
  product_id: number;
  rating: number;
  comment?: string;
  created_at: string;
  user?: User;
  product?: Product;
}

// Error types
export interface ApiError {
  detail: string;
  message?: string;
  code?: string;
}
