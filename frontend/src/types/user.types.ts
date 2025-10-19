// User-related types

export interface User {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  height_cm?: number;
  weight_kg?: number;
  activity_level?: 'sedentary' | 'lightly_active' | 'moderately_active' | 'very_active' | 'extremely_active';
  goal_type?: 'lose_weight' | 'maintain_weight' | 'gain_weight';
  daily_calorie_target?: number;
  protein_target_g?: number;
  carbs_target_g?: number;
  fats_target_g?: number;
  water_target_ml?: number;
  created_at?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface UpdateUserProfile {
  first_name?: string;
  last_name?: string;
  height_cm?: number;
  weight_kg?: number;
  activity_level?: string;
}

export interface UpdateUserGoals {
  goal_type?: string;
  daily_calorie_target?: number;
  protein_target_g?: number;
  carbs_target_g?: number;
  fats_target_g?: number;
  water_target_ml?: number;
}
