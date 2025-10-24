import { apiService } from './api';
import { User, LoginResponse, RegisterData } from '../types';

class AuthService {
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await apiService.login(email, password);
    
    // Store token for future requests
    if (response.access_token) {
      localStorage.setItem('auth_token', response.access_token);
    }
    
    return {
      user: response.user,
      token: response.access_token,
      access_token: response.access_token,
      token_type: response.token_type
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
