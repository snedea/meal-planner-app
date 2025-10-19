// Recipe store with Zustand

import { create } from 'zustand';
import api from '../services/api';
import { Recipe, CreateRecipe } from '../types/recipe.types';

interface RecipeState {
  recipes: Recipe[];
  selectedRecipe: Recipe | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchRecipes: () => Promise<void>;
  getRecipeById: (id: string) => Promise<void>;
  createRecipe: (data: CreateRecipe) => Promise<void>;
  deleteRecipe: (id: string) => Promise<void>;
  setSelectedRecipe: (recipe: Recipe | null) => void;
  clearError: () => void;
}

export const useRecipeStore = create<RecipeState>((set, get) => ({
  recipes: [],
  selectedRecipe: null,
  isLoading: false,
  error: null,

  fetchRecipes: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.get<{ results: Recipe[] }>('/recipes');
      set({ recipes: response.data.results, isLoading: false });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to fetch recipes';
      set({ error: errorMessage, isLoading: false });
    }
  },

  getRecipeById: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.get<Recipe>(`/recipes/${id}`);
      set({ selectedRecipe: response.data, isLoading: false });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to fetch recipe';
      set({ error: errorMessage, isLoading: false });
    }
  },

  createRecipe: async (data: CreateRecipe) => {
    set({ isLoading: true, error: null });
    try {
      await api.post<Recipe>('/recipes', data);

      // Refresh recipe list
      await get().fetchRecipes();

      set({ isLoading: false });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to create recipe';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  deleteRecipe: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await api.delete(`/recipes/${id}`);

      // Refresh recipe list
      await get().fetchRecipes();

      set({ isLoading: false });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to delete recipe';
      set({ error: errorMessage, isLoading: false });
    }
  },

  setSelectedRecipe: (recipe: Recipe | null) => {
    set({ selectedRecipe: recipe });
  },

  clearError: () => {
    set({ error: null });
  },
}));
