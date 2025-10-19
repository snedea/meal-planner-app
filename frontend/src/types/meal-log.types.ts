// Meal log types

import { Food } from './food.types';
import { Recipe } from './recipe.types';

export type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack';

export interface MealLog {
  id: string;
  user_id: string;
  food_id?: string;
  recipe_id?: string;
  food?: Food;
  recipe?: Recipe;
  quantity: number;
  unit: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fats_g: number;
  meal_type: MealType;
  logged_date: string;
  logged_time?: string;
  notes?: string;
  created_at: string;
}

export interface CreateMealLog {
  food_id?: string;
  recipe_id?: string;
  quantity: number;
  unit: string;
  meal_type: MealType;
  logged_date: string;
  logged_time?: string;
  notes?: string;
}

export interface DailySummary {
  total_calories: number;
  total_protein_g: number;
  total_carbs_g: number;
  total_fats_g: number;
  calorie_target: number;
  protein_target_g: number;
  carbs_target_g: number;
  fats_target_g: number;
  calorie_remaining: number;
  protein_remaining_g: number;
  carbs_remaining_g: number;
  fats_remaining_g: number;
}

export interface MealLogsResponse {
  logs: MealLog[];
  summary: DailySummary;
}
