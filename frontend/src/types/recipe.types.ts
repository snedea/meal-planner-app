// Recipe-related types

import { Food, NutritionInfo } from './food.types';

export interface RecipeIngredient {
  id?: string;
  food_id: string;
  food?: Food;
  quantity: number;
  unit: string;
  display_order?: number;
}

export interface Recipe {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  instructions?: string;
  prep_time_minutes?: number;
  cook_time_minutes?: number;
  servings: number;
  is_public: boolean;
  ingredients?: RecipeIngredient[];
  nutrition_total?: NutritionInfo;
  nutrition_per_serving?: NutritionInfo;
  created_at?: string;
  updated_at?: string;
}

export interface CreateRecipe {
  name: string;
  description?: string;
  instructions?: string;
  prep_time_minutes?: number;
  cook_time_minutes?: number;
  servings: number;
  is_public?: boolean;
  ingredients: Array<{
    food_id: string;
    quantity: number;
    unit: string;
  }>;
}

export interface UpdateRecipe extends Partial<CreateRecipe> {
  id: string;
}
