export interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

export interface UserProfile {
  user_id: number;
  height_cm?: number;
  weight_kg?: number;
  age_years?: number;
  sex?: 'MALE' | 'FEMALE';
  dietary_preference: string;
  allergies: string[];
  ingredient_exclusions: string[];
  cuisine_preferences: string[];
  cuisine_exclusions: string[];
  disliked_ingredients: string[];
  religious_restrictions: string[];
  medical_conditions: string[];
  target_energy_kcal?: number;
  target_protein_g?: number;
  target_carbohydrate_g?: number;
  target_fat_g?: number;
  target_fibre_g?: number;
  target_sodium_mg?: number;
  weight_goal: string;
  weight_change_rate_kg_per_week: number;
  activity_level: string;
  meal_frequency: number;
  preferred_meal_times: Record<string, string>;
  cooking_skill: string;
  budget_constraint: string | null;
  time_constraint_minutes: number | null;
}

export interface Recipe {
  id: number;
  recipe_id: number;
  recipe_name: string;
  cuisine: string;
  course: string;
  diet_labels: string;
  recipe_type: string;
  prep_time_min: number;
  cook_time_min: number;
  total_time_min: number;
  servings: number;
  ingredients: string;
  instructions: string;
  image_url?: string;
  nutrition_per_serving?: RecipeNutrition;
  created_at: string;
  updated_at: string;
}

export interface RecipeDetail extends Recipe {
  nutrition_per_serving?: RecipeNutrition;
  ingredients_detail?: IngredientDetail[];
}

export interface RecipeNutrition {
  energy_kcal?: number;
  protein_g?: number;
  fat_g?: number;
  carbohydrate_g?: number;
  fibre_g?: number;
  sodium_mg?: number;
  calculation_status: 'COMPLETE' | 'PARTIAL' | 'MISSING_WEIGHTS' | 'MISSING_NUTRIENTS' | 'MISSING_MAPPINGS';
  missing_nutrients: string[];
  provenance: string;
}

export interface IngredientDetail {
  name: string;
  amount: number;
  unit: string;
  nutrition?: RecipeNutrition;
}

export interface MealPlan {
  id: number;
  user_id: number;
  name: string | null;
  start_date: string;
  end_date: string;
  status: 'DRAFT' | 'ACTIVE' | 'COMPLETED' | 'ARCHIVED';
  created_at: string;
  updated_at: string;
  items?: MealPlanItem[];
  total_nutrients?: RecipeNutrition;
}

export interface MealPlanItem {
  id: number;
  meal_plan_id: number;
  meal_slot: 'BREAKFAST' | 'MORNING_SNACK' | 'LUNCH' | 'EVENING_SNACK' | 'DINNER';
  day_index: number;
  recipe_id: number | null;
  servings: number;
  recipe?: Recipe | null;
  is_completed: boolean;
}

export interface NutritionTargets {
  bmr_kcal: number;
  tdee_kcal: number;
  target_energy_kcal: number;
  protein_g: number;
  fat_g: number;
  carbohydrate_g: number;
  fibre_g: number;
  sodium_mg: number;
  micronutrients: Record<string, { target: number; unit: string }>;
  calculation_method: string;
  limitations: string[];
}

export interface RecommendationRequest {
  meal_slot?: string;
  cuisine?: string;
  diet_labels?: string[];
  exclude_allergens?: string[];
  exclude_ingredients?: string[];
  max_prep_time?: number;
  max_cook_time?: number;
  k: number;
}

export interface RecommendationResult {
  recipe_id: number;
  score: number;
  explanation: string;
  component_scores: Record<string, number>;
  shared_ingredients: string[];
}

export interface RecommendationsResponse {
  recommendations: RecommendationResult[];
  query_info: {
    profile_complete: boolean;
    nutrition_data_available: boolean;
    dietary_constraints_applied: string[];
  };
}

export interface SearchFilters {
  query?: string;
  cuisine?: string;
  course?: string;
  diet_labels?: string[];
  max_prep_time?: number;
  max_cook_time?: number;
  max_total_time?: number;
  page?: number;
  per_page?: number;
}

export interface SearchResponse {
  recipes: Recipe[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface SavedRecipe {
  id: number;
  user_id: number;
  recipe_id: number;
  saved_at: string;
  recipe?: Recipe;
}

export interface MealHistory {
  id: number;
  user_id: number;
  meal_plan_id: number;
  recipe_id: number;
  meal_slot: string;
  consumed_at: string;
  servings: number;
  recipe?: Recipe;
}

export interface NutritionBreakdown {
  recipe_id: number;
  per_serving: RecipeNutrition;
  per_100g?: RecipeNutrition;
  ingredients: Array<{
    ingredient: string;
    amount_g: number;
    nutrition: RecipeNutrition;
  }>;
  completeness: 'COMPLETE' | 'PARTIAL' | 'UNAVAILABLE';
  notes: string[];
}

export interface ApiError {
  detail: string;
  status_code: number;
}