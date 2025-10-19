// Food store with Zustand

import { create } from 'zustand';
import api from '../services/api';
import { Food, FoodSearchResult } from '../types/food.types';

interface FoodState {
  searchResults: Food[];
  selectedFood: Food | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  searchFoods: (query: string) => Promise<void>;
  getFoodById: (id: string) => Promise<Food>;
  setSelectedFood: (food: Food | null) => void;
  clearSearchResults: () => void;
  clearError: () => void;
}

export const useFoodStore = create<FoodState>((set) => ({
  searchResults: [],
  selectedFood: null,
  isLoading: false,
  error: null,

  searchFoods: async (query: string) => {
    if (!query.trim()) {
      set({ searchResults: [] });
      return;
    }

    set({ isLoading: true, error: null });
    try {
      const response = await api.get<FoodSearchResult>(`/foods/search`, {
        params: { q: query, limit: 20 },
      });
      set({ searchResults: response.data.results, isLoading: false });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Food search failed';
      set({ error: errorMessage, isLoading: false, searchResults: [] });
    }
  },

  getFoodById: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.get<Food>(`/foods/${id}`);
      set({ isLoading: false });
      return response.data;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to fetch food';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  setSelectedFood: (food: Food | null) => {
    set({ selectedFood: food });
  },

  clearSearchResults: () => {
    set({ searchResults: [] });
  },

  clearError: () => {
    set({ error: null });
  },
}));
