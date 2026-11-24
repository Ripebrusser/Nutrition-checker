import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import {
  Recipe,
  SearchFilters,
  SearchResponse,
  UserProfile,
  NutritionTargets,
  RecommendationsResponse,
  RecommendationRequest,
  MealPlan,
  MealPlanItem,
  SavedRecipe,
  MealHistory,
  NutritionBreakdown,
  ApiError,
} from '../types';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  register: async (email: string, password: string, full_name: string) => {
    const response = await api.post('/auth/register', { email, password, full_name });
    return response.data;
  },

  logout: async () => {
    await api.post('/auth/logout');
  },

  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

export const profileService = {
  getProfile: async (): Promise<UserProfile> => {
    const response = await api.get('/profile');
    return response.data;
  },

  updateProfile: async (data: Partial<UserProfile>): Promise<UserProfile> => {
    const response = await api.patch('/profile', data);
    return response.data;
  },
};

export const nutritionService = {
  getTargets: async (): Promise<NutritionTargets> => {
    const response = await api.get('/nutrition/targets');
    return response.data;
  },

  calculateTargets: async (profileData: Partial<UserProfile>): Promise<NutritionTargets> => {
    const response = await api.post('/nutrition/calculate', profileData);
    return response.data;
  },

  getBreakdown: async (recipeId: number): Promise<NutritionBreakdown> => {
    const response = await api.get(`/nutrition/breakdown/${recipeId}`);
    return response.data;
  },

  getMealPlanNutrition: async (mealPlanId: number) => {
    const response = await api.get(`/nutrition/meal-plan/${mealPlanId}`);
    return response.data;
  },
};

export const recipeService = {
  search: async (filters: SearchFilters): Promise<SearchResponse> => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach(v => params.append(key, v));
        } else {
          params.set(key, String(value));
        }
      }
    });
    const response = await api.get(`/recipes?${params.toString()}`);
    return response.data;
  },

  getById: async (id: number): Promise<Recipe> => {
    const response = await api.get(`/recipes/${id}`);
    return response.data;
  },

  getCuisines: async (): Promise<string[]> => {
    const response = await api.get('/recipes/meta/cuisines');
    return response.data;
  },

  getCourses: async (): Promise<string[]> => {
    const response = await api.get('/recipes/meta/courses');
    return response.data;
  },

  getDietLabels: async (): Promise<string[]> => {
    const response = await api.get('/recipes/meta/diet-labels');
    return response.data;
  },
};

export const recommendationService = {
  getRecommendations: async (request: RecommendationRequest): Promise<RecommendationsResponse> => {
    const response = await api.post('/recommendations', request);
    return response.data;
  },

  getSimilarRecipes: async (recipeId: number, k: number = 10): Promise<RecommendationsResponse> => {
    const response = await api.get(`/recommendations/similar/${recipeId}?k=${k}`);
    return response.data;
  },
};

export const mealPlanService = {
  getAll: async (): Promise<MealPlan[]> => {
    const response = await api.get('/meal-plans');
    return response.data;
  },

  getActive: async (): Promise<MealPlan | null> => {
    const response = await api.get('/meal-plans/active');
    return response.data;
  },

  getById: async (id: number): Promise<MealPlan> => {
    const response = await api.get(`/meal-plans/${id}`);
    return response.data;
  },

  create: async (data: { name?: string; start_date: string; end_date: string }): Promise<MealPlan> => {
    const response = await api.post('/meal-plans', data);
    return response.data;
  },

  update: async (id: number, data: Partial<MealPlan>): Promise<MealPlan> => {
    const response = await api.patch(`/meal-plans/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/meal-plans/${id}`);
  },

  addMeal: async (mealPlanId: number, data: Omit<MealPlanItem, 'id' | 'meal_plan_id'>): Promise<MealPlanItem> => {
    const response = await api.post(`/meal-plans/${mealPlanId}/meals`, data);
    return response.data;
  },

  updateMeal: async (mealPlanId: number, mealId: number, data: Partial<MealPlanItem>): Promise<MealPlanItem> => {
    const response = await api.patch(`/meal-plans/${mealPlanId}/meals/${mealId}`, data);
    return response.data;
  },

  removeMeal: async (mealPlanId: number, mealId: number): Promise<void> => {
    await api.delete(`/meal-plans/${mealPlanId}/meals/${mealId}`);
  },

  completeMeal: async (mealPlanId: number, mealId: number): Promise<MealPlanItem> => {
    const response = await api.post(`/meal-plans/${mealPlanId}/meals/${mealId}/complete`);
    return response.data;
  },

  optimize: async (mealPlanId: number): Promise<MealPlan> => {
    const response = await api.post(`/meal-plans/${mealPlanId}/optimize`);
    return response.data;
  },
};

export const savedRecipeService = {
  getAll: async (): Promise<SavedRecipe[]> => {
    const response = await api.get('/saved-recipes');
    return response.data;
  },

  save: async (recipeId: number): Promise<SavedRecipe> => {
    const response = await api.post('/saved-recipes', { recipe_id: recipeId });
    return response.data;
  },

  unsave: async (recipeId: number): Promise<void> => {
    await api.delete(`/saved-recipes/${recipeId}`);
  },

  isSaved: async (recipeId: number): Promise<boolean> => {
    const response = await api.get(`/saved-recipes/${recipeId}/check`);
    return response.data.saved;
  },
};

export const historyService = {
  getAll: async (limit: number = 50): Promise<MealHistory[]> => {
    const response = await api.get(`/history?limit=${limit}`);
    return response.data;
  },

  getByDateRange: async (startDate: string, endDate: string): Promise<MealHistory[]> => {
    const response = await api.get(`/history/range?start=${startDate}&end=${endDate}`);
    return response.data;
  },
};

export const cuisineService = {
  getAll: async (): Promise<string[]> => {
    const response = await api.get('/meta/cuisines');
    return response.data;
  },
};

export { api };