// Food-related types

export interface NutritionInfo {
  serving_size: number;
  serving_unit: string;
  servings_per_container?: number;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fats_g: number;
  fiber_g?: number;
  sugar_g?: number;
  saturated_fat_g?: number;
  trans_fat_g?: number;
  cholesterol_mg?: number;
  sodium_mg?: number;
  micronutrients?: Record<string, number>;
}

export interface Food {
  id: string;
  name: string;
  brand?: string;
  barcode?: string;
  source: 'openfoodfacts' | 'usda' | 'custom';
  source_id?: string;
  description?: string;
  is_verified: boolean;
  created_by_user_id?: string;
  nutrition: NutritionInfo;
  created_at?: string;
}

export interface FoodSearchResult {
  results: Food[];
  total: number;
  page: number;
  limit: number;
}

export interface CreateCustomFood {
  name: string;
  brand?: string;
  description?: string;
  nutrition: Omit<NutritionInfo, 'id'>;
}
