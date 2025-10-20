// Auth store with Zustand

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../services/api';
import { User, LoginCredentials, RegisterData } from '../types/user.types';
import { AuthResponse } from '../types/api.types';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  fetchCurrentUser: () => Promise<void>;
  clearError: () => void;
  setToken: (token: string) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      setToken: (token: string) => {
        localStorage.setItem('auth-token', token);
        set({ token, isAuthenticated: true });
      },

      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.post<AuthResponse>('/auth/login', credentials);
          const { access_token } = response.data;

          get().setToken(access_token);

          // Fetch user profile
          await get().fetchCurrentUser();

          set({ isLoading: false });
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Login failed';
          set({ error: errorMessage, isLoading: false, isAuthenticated: false });
          throw error;
        }
      },

      register: async (data: RegisterData) => {
        set({ isLoading: true, error: null });
        try {
          await api.post('/auth/register', data);

          // Auto-login after registration
          await get().login({
            email: data.email,
            password: data.password,
          });

          set({ isLoading: false });
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Registration failed';
          set({ error: errorMessage, isLoading: false });
          throw error;
        }
      },

      logout: () => {
        localStorage.removeItem('auth-token');
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null
        });
      },

      fetchCurrentUser: async () => {
        try {
          const response = await api.get<User>('/users/me');
          set({ user: response.data });
        } catch (error: any) {
          console.error('Failed to fetch user:', error);
          // If authentication fails (401), logout to clear stale tokens
          if (error.response?.status === 401) {
            get().logout();
          } else {
            set({ error: 'Failed to fetch user profile' });
          }
        }
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token, isAuthenticated: state.isAuthenticated }),
    }
  )
);
