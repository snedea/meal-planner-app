// Auth store unit tests

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useAuthStore } from '../authStore';
import api from '../../services/api';

// Mock the API
vi.mock('../../services/api');

describe('authStore', () => {
  beforeEach(() => {
    // Reset store before each test
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });

    // Clear localStorage
    localStorage.clear();
  });

  it('should initialize with default values', () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(state.isLoading).toBe(false);
  });

  it('should set token and mark as authenticated', () => {
    const { setToken } = useAuthStore.getState();
    const testToken = 'test-token-123';

    setToken(testToken);

    const state = useAuthStore.getState();
    expect(state.token).toBe(testToken);
    expect(state.isAuthenticated).toBe(true);
    expect(localStorage.getItem('auth-token')).toBe(testToken);
  });

  it('should logout and clear state', () => {
    // First set some state
    useAuthStore.setState({
      user: { id: '1', email: 'test@example.com' } as any,
      token: 'test-token',
      isAuthenticated: true,
    });

    const { logout } = useAuthStore.getState();
    logout();

    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(localStorage.getItem('auth-token')).toBeNull();
  });

  it('should clear error', () => {
    useAuthStore.setState({ error: 'Test error' });

    const { clearError } = useAuthStore.getState();
    clearError();

    expect(useAuthStore.getState().error).toBeNull();
  });
});
