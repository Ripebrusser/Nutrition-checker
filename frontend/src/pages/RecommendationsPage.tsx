import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { RecommendationRequest, RecommendationsResponse } from '../types';
import { recommendationService, recipeService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'react-hot-toast';
import { Loader2, Sparkles, Filter, X, Utensils, AlertTriangle, Info, Brain, Shield, Target } from 'lucide-react';

const MEAL_SLOTS = [
  { value: '', label: 'Any Meal' },
  { value: 'BREAKFAST', label: 'Breakfast' },
  { value: 'MORNING_SNACK', label: 'Morning Snack' },
  { value: 'LUNCH', label: 'Lunch' },
  { value: 'EVENING_SNACK', label: 'Evening Snack' },
  { value: 'DINNER', label: 'Dinner' },
];

export function RecommendationsPage() {
  const { profile } = useAuth();
  const [recommendations, setRecommendations] = useState<RecommendationsResponse['recommendations']>([]);
  const [queryInfo, setQueryInfo] = useState<RecommendationsResponse['query_info'] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [request, setRequest] = useState<RecommendationRequest>({
    meal_slot: '',
    cuisine: '',
    diet_labels: [],
    exclude_allergens: [],
    exclude_ingredients: [],
    max_prep_time: undefined,
    max_cook_time: undefined,
    k: 10,
  });
  const [cuisines, setCuisines] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [hasGenerated, setHasGenerated] = useState(false);

  useEffect(() => {
    loadCuisines();
  }, []);

  const loadCuisines = async () => {
    try {
      const data = await recipeService.getCuisines();
      setCuisines(data);
    } catch {
      // Ignore
    }
  };

  const generateRecommendations = async () => {
    if (!profile?.age_years || !profile?.sex || !profile?.height_cm || !profile?.weight_kg || !profile?.activity_level) {
      toast.error('Please complete your profile (age, sex, height, weight, activity level) to get personalized recommendations.');
      return;
    }

    setIsLoading(true);
    try {
      const response = await recommendationService.getRecommendations(request);
      setRecommendations(response.recommendations);
      setQueryInfo(response.query_info);
      setHasGenerated(true);
      toast.success(`Found ${response.recommendations.length} recommendations`);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to generate recommendations');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilterChange = (key: keyof RecommendationRequest, value: any) => {
    setRequest(prev => ({ ...prev, [key]: value }));
  };

  const handleDietLabelToggle = (label: string) => {
    setRequest(prev => ({
      ...prev,
      diet_labels: prev.diet_labels?.includes(label)
        ? prev.diet_labels.filter(l => l !== label)
        : [...(prev.diet_labels || []), label],
    }));
  };

  const handleExcludeToggle = (key: 'exclude_allergens' | 'exclude_ingredients', label: string) => {
    setRequest(prev => ({
      ...prev,
      [key]: prev[key]?.includes(label)
        ? prev[key]!.filter(l => l !== label)
        : [...(prev[key] || []), label],
    }));
  };

  const clearFilters = () => {
    setRequest({
      meal_slot: '',
      cuisine: '',
      diet_labels: [],
      exclude_allergens: [],
      exclude_ingredients: [],
      max_prep_time: undefined,
      max_cook_time: undefined,
      k: 10,
    });
  };

  const hasActiveFilters = request.meal_slot || request.cuisine ||
    (request.diet_labels && request.diet_labels.length > 0) ||
    (request.exclude_allergens && request.exclude_allergens.length > 0) ||
    (request.exclude_ingredients && request.exclude_ingredients.length > 0) ||
    request.max_prep_time || request.max_cook_time;

  return (
    <div className="page-container">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900 flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-primary-600" />
            Personalized Recommendations
          </h1>
          <p className="text-neutral-600 mt-1">
            Content-based recipe suggestions (TF-IDF text similarity) ranked with your dietary constraints and nutrition targets
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`btn-secondary flex items-center gap-2 ${hasActiveFilters ? 'bg-primary-50 border-primary-200 text-primary-700' : ''}`}
          >
            <Filter className="w-4 h-4" />
            Filters {hasActiveFilters && <span className="badge badge-info">{[request.diet_labels?.length || 0, request.exclude_allergens?.length || 0, request.exclude_ingredients?.length || 0].reduce((a, b) => a + b, 0) + (request.meal_slot ? 1 : 0) + (request.cuisine ? 1 : 0)}</span>}
          </button>
          {hasActiveFilters && (
            <button onClick={clearFilters} className="btn-ghost text-sm text-red-600 hover:text-red-700">
              <X className="w-4 h-4 mr-1" />
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Profile Completeness Check */}
      {!profile?.age_years || !profile?.sex || !profile?.height_cm || !profile?.weight_kg || !profile?.activity_level ? (
        <div className="card p-6 mb-6 border-yellow-200 bg-yellow-50">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
            <div>
              <h3 className="font-semibold text-yellow-800 mb-1">Complete Your Profile for Better Recommendations</h3>
              <p className="text-yellow-700 mb-3">
                Personalized recommendations require your basic profile information.
                Please update your profile with age, sex, height, weight, and activity level.
              </p>
              <Link to="/profile" className="btn-primary">
                Complete Profile
              </Link>
            </div>
          </div>
        </div>
      ) : null}

      <div className="flex gap-6">
        {/* Filters Panel */}
        <aside className={`w-80 flex-shrink-0 ${showFilters ? '' : 'hidden lg:block'}`}>
          <div className="card p-4 sticky top-24">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold text-neutral-900">Recommendation Filters</h2>
              {hasActiveFilters && (
                <button onClick={clearFilters} className="text-sm text-primary-600 hover:underline">
                  Clear all
                </button>
              )}
            </div>

            <div className="space-y-6">
              {/* Meal Slot */}
              <div>
                <label className="label">Meal Slot</label>
                <select
                  value={request.meal_slot}
                  onChange={e => handleFilterChange('meal_slot', e.target.value)}
                  className="input-field"
                >
                  {MEAL_SLOTS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
                </select>
              </div>

              {/* Cuisine */}
              <div>
                <label className="label">Cuisine</label>
                <select
                  value={request.cuisine}
                  onChange={e => handleFilterChange('cuisine', e.target.value)}
                  className="input-field"
                >
                  <option value="">Any Cuisine</option>
                  {cuisines.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>

              {/* Dietary Preferences */}
              <div>
                <label className="label">Dietary Preferences</label>
                <div className="flex flex-wrap gap-2">
                  {['vegetarian', 'vegan', 'eggetarian', 'gluten-free', 'dairy-free', 'nut-free', 'low-carb', 'high-protein', 'diabetic-friendly', 'heart-healthy', 'jain'].map(label => (
                    <button
                      key={label}
                      type="button"
                      onClick={() => handleDietLabelToggle(label)}
                      className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                        request.diet_labels?.includes(label)
                          ? 'bg-primary-100 text-primary-700'
                          : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Allergen Exclusions */}
              <div>
                <label className="label">Exclude Allergens</label>
                <div className="flex flex-wrap gap-2">
                  {['peanuts', 'tree nuts', 'shellfish', 'fish', 'dairy', 'eggs', 'soy', 'wheat', 'sesame'].map(label => (
                    <button
                      key={label}
                      type="button"
                      onClick={() => handleExcludeToggle('exclude_allergens', label)}
                      className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                        request.exclude_allergens?.includes(label)
                          ? 'bg-red-50 text-red-700'
                          : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Ingredient Exclusions */}
              <div>
                <label className="label">Exclude Ingredients</label>
                <div className="flex flex-wrap gap-2">
                  {['onion', 'garlic', 'ginger', 'tomato', 'potato', 'eggplant', 'mushroom', 'bitter gourd', 'okra'].map(label => (
                    <button
                      key={label}
                      type="button"
                      onClick={() => handleExcludeToggle('exclude_ingredients', label)}
                      className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                        request.exclude_ingredients?.includes(label)
                          ? 'bg-orange-50 text-orange-700'
                          : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Time Constraints */}
              <div>
                <label className="label">Max Prep Time (min)</label>
                <input
                  type="number"
                  min="0"
                  max="120"
                  value={request.max_prep_time || ''}
                  onChange={e => handleFilterChange('max_prep_time', e.target.value ? parseInt(e.target.value) : undefined)}
                  className="input-field"
                  placeholder="Any"
                />
              </div>

              <div>
                <label className="label">Max Cook Time (min)</label>
                <input
                  type="number"
                  min="0"
                  max="180"
                  value={request.max_cook_time || ''}
                  onChange={e => handleFilterChange('max_cook_time', e.target.value ? parseInt(e.target.value) : undefined)}
                  className="input-field"
                  placeholder="Any"
                />
              </div>

              {/* Number of Results */}
              <div>
                <label className="label">Number of Recommendations</label>
                <select
                  value={request.k}
                  onChange={e => handleFilterChange('k', parseInt(e.target.value))}
                  className="input-field"
                >
                  {[5, 10, 15, 20].map(n => <option key={n} value={n}>{n}</option>)}
                </select>
              </div>

              {/* Generate Button */}
              <button
                onClick={generateRecommendations}
                disabled={isLoading}
                className="btn-primary w-full py-3"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="animate-spin mr-2 w-5 h-5" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5 mr-2" />
                    Get Recommendations
                  </>
                )}
              </button>
            </div>
          </div>
        </aside>

        {/* Results */}
        <main className="flex-1 min-w-0">
          {!hasGenerated ? (
            <div className="text-center py-16">
              <Sparkles className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-neutral-900 mb-2">Get Personalized Recommendations</h3>
              <p className="text-neutral-500 mb-6 max-w-md mx-auto">
                Configure your preferences on the left and click "Get Recommendations" to receive
                content-based suggestions scored from recipe text similarity, your dietary constraints and nutrition targets. Scores are a proxy for relevance, not measured user preference.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto">
                <FeatureCard icon={<Brain className="w-6 h-6 text-primary-600" />} title="Content-Based" desc="TF-IDF similarity matching" />
                <FeatureCard icon={<Shield className="w-6 h-6 text-green-600" />} title="Dietary Safe" desc="Hard constraints never overridden" />
                <FeatureCard icon={<Target className="w-6 h-6 text-orange-600" />} title="Nutrition Aware" desc="Respects your calorie & macro targets" />
              </div>
            </div>
          ) : isLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {[...Array(6)].map((_, i) => <RecommendationCardSkeleton key={i} />)}
            </div>
          ) : recommendations.length === 0 ? (
            <div className="text-center py-16">
              <Sparkles className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-neutral-900 mb-2">No Recommendations Found</h3>
              <p className="text-neutral-500 mb-4">Try adjusting your filters or expanding your preferences.</p>
              <button onClick={clearFilters} className="btn-primary">Clear All Filters</button>
            </div>
          ) : (
            <>
              {queryInfo && (
                <div className="mb-6 p-4 bg-neutral-50 rounded-lg">
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-2xl font-bold text-primary-600">{recommendations.length}</p>
                      <p className="text-sm text-neutral-500">Recommendations</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-green-600">
                        {queryInfo.dietary_constraints_applied.length}
                      </p>
                      <p className="text-sm text-neutral-500">Constraints Applied</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-blue-600">
                        {queryInfo.nutrition_data_available ? 'Yes' : 'No'}
                      </p>
                      <p className="text-sm text-neutral-500">Nutrition Data</p>
                    </div>
                  </div>
                  {queryInfo.dietary_constraints_applied.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {queryInfo.dietary_constraints_applied.map(c => (
                        <span key={c} className="badge badge-info">{c}</span>
                      ))}
                    </div>
                  )}
                  {!queryInfo.nutrition_data_available && (
                    <p className="text-sm text-yellow-600 mt-2 flex items-center gap-1">
                      <Info className="w-4 h-4" />
                      Nutrition data unavailable — recommendations based on content similarity only
                    </p>
                  )}
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {recommendations.map((rec, index) => (
                  <RecommendationCard key={rec.recipe_id} recommendation={rec} rank={index + 1} />
                ))}
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, desc }: { icon: React.ReactNode; title: string; desc: string }) {
  return (
    <div className="card p-4 text-center">
      <div className="mb-2">{icon}</div>
      <h4 className="font-semibold text-neutral-900 mb-1">{title}</h4>
      <p className="text-sm text-neutral-600">{desc}</p>
    </div>
  );
}

function RecommendationCard({ recommendation, rank }: { recommendation: RecommendationsResponse['recommendations'][0]; rank: number }) {
  return (
    <div className="card-hover card p-4">
      <div className="flex items-start gap-3 mb-3">
        <span className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-100 text-primary-700 text-sm font-bold flex items-center justify-center">
          {rank}
        </span>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-neutral-900 truncate">{recommendation.recipe_id}</h3>
          <p className="text-sm text-neutral-500">Score: {(recommendation.score * 100).toFixed(1)}%</p>
        </div>
      </div>

      <div className="mb-3 p-3 bg-neutral-50 rounded-lg">
        <p className="text-sm text-neutral-700">{recommendation.explanation}</p>
      </div>

      <div className="flex flex-wrap gap-1 mb-3">
        {Object.entries(recommendation.component_scores).map(([key, value]) => (
          <span key={key} className="badge badge-gray text-xs">
            {key}: {(value * 100).toFixed(0)}%
          </span>
        ))}
      </div>

      {recommendation.shared_ingredients.length > 0 && (
        <div className="mb-3">
          <p className="text-xs text-neutral-500 mb-1">Shared ingredients:</p>
          <div className="flex flex-wrap gap-1">
            {recommendation.shared_ingredients.slice(0, 5).map(ing => (
              <span key={ing} className="badge badge-gray text-xs">{ing}</span>
            ))}
          </div>
        </div>
      )}

      <Link to={`/recipes/${recommendation.recipe_id}`} className="btn-secondary w-full justify-center text-sm">
        <Utensils className="w-4 h-4 mr-1" />
        View Recipe
      </Link>
    </div>
  );
}

function RecommendationCardSkeleton() {
  return (
    <div className="card p-4 animate-pulse">
      <div className="flex items-start gap-3 mb-3">
        <div className="w-8 h-8 rounded-full bg-neutral-200" />
        <div className="flex-1">
          <div className="h-4 bg-neutral-200 rounded w-3/4" />
          <div className="h-3 bg-neutral-200 rounded w-1/2 mt-1" />
        </div>
      </div>
      <div className="h-20 bg-neutral-200 rounded mb-3" />
      <div className="flex gap-1 mb-3">
        <div className="h-5 bg-neutral-200 rounded-full w-20" />
        <div className="h-5 bg-neutral-200 rounded-full w-20" />
      </div>
      <div className="h-10 bg-neutral-200 rounded" />
    </div>
  );
}

export default RecommendationsPage;