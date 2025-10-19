// Meal log store with Zustand

import { create } from 'zustand';
import api from '../services/api';
import { MealLog, CreateMealLog, DailySummary, MealLogsResponse } from '../types/meal-log.types';
import { format } from 'date-fns';

interface MealLogState {
  logs: MealLog[];
  currentDate: string;
  dailySummary: DailySummary | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchLogs: (date: string) => Promise<void>;
  addLog: (log: CreateMealLog) => Promise<void>;
  deleteLog: (id: string) => Promise<void>;
  setCurrentDate: (date: string) => void;
  clearError: () => void;
}

export const useMealLogStore = create<MealLogState>((set, get) => ({
  logs: [],
  currentDate: format(new Date(), 'yyyy-MM-dd'),
  dailySummary: null,
  isLoading: false,
  error: null,

  fetchLogs: async (date: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.get<MealLogsResponse>('/meal-logs', {
        params: { date },
      });
      set({
        logs: response.data.logs,
        dailySummary: response.data.summary,
        currentDate: date,
        isLoading: false,
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to fetch meal logs';
      set({ error: errorMessage, isLoading: false });
    }
  },

  addLog: async (log: CreateMealLog) => {
    set({ isLoading: true, error: null });
    try {
      await api.post<MealLog>('/meal-logs', log);

      // Refresh logs for current date
      await get().fetchLogs(get().currentDate);

      set({ isLoading: false });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to add meal log';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  deleteLog: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await api.delete(`/meal-logs/${id}`);

      // Refresh logs for current date
      await get().fetchLogs(get().currentDate);

      set({ isLoading: false });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to delete meal log';
      set({ error: errorMessage, isLoading: false });
    }
  },

  setCurrentDate: (date: string) => {
    set({ currentDate: date });
    get().fetchLogs(date);
  },

  clearError: () => {
    set({ error: null });
  },
}));
