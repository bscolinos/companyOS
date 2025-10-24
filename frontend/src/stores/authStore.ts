import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authService } from '../services/authService';
import { User } from '../types';
import toast from 'react-hot-toast';

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  register: (userData: RegisterData) => Promise<boolean>;
  logout: () => void;
  initializeAuth: () => void;
}

interface RegisterData {
  email: string;
  username: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true });
        try {
          const response = await authService.login(email, password);
          set({
            user: response.user,
            token: response.token,
            isLoading: false,
          });
          toast.success('Login successful!');
          return true;
        } catch (error: any) {
          set({ isLoading: false });
          toast.error(error.message || 'Login failed');
          return false;
        }
      },

      register: async (userData: RegisterData) => {
        set({ isLoading: true });
        try {
          const user = await authService.register(userData);
          set({ isLoading: false });
          toast.success('Registration successful! Please login.');
          return true;
        } catch (error: any) {
          set({ isLoading: false });
          toast.error(error.message || 'Registration failed');
          return false;
        }
      },

      logout: () => {
        set({ user: null, token: null });
        authService.logout();
        toast.success('Logged out successfully');
      },

      initializeAuth: async () => {
        const token = get().token;
        if (token) {
          set({ isLoading: true });
          try {
            const user = await authService.getCurrentUser();
            set({ user, isLoading: false });
          } catch (error) {
            // Token is invalid, clear it
            set({ user: null, token: null, isLoading: false });
          }
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token }),
    }
  )
);
