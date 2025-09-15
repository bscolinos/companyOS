import { apiService } from './api';

export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface LoginResponse {
  user: User;
  token: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
}

class AuthService {
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await apiService.login(email, password);
    
    // Store token for future requests
    if (response.access_token) {
      localStorage.setItem('auth_token', response.access_token);
    }
    
    // Get user info
    const user = await this.getCurrentUser();
    
    return {
      user,
      token: response.access_token
    };
  }

  async register(userData: RegisterData): Promise<User> {
    return await apiService.register(userData);
  }

  async getCurrentUser(): Promise<User> {
    return await apiService.getCurrentUser();
  }

  logout(): void {
    localStorage.removeItem('auth_token');
  }

  getToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }
}

export const authService = new AuthService();
