import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { RecipeDetail } from '../types';
import { recipeService, savedRecipeService } from '../services/api';
import { toast } from 'react-hot-toast';
import { Loader2, Clock, Users, Utensils, Tag, BookOpen, Heart, HeartOff, Share2, ArrowLeft, AlertTriangle, Info, XCircle } from 'lucide-react';

export function RecipeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [recipe, setRecipe] = useState<RecipeDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [activeTab, setActiveTab] = useState<'ingredients' | 'instructions' | 'nutrition'>('ingredients');

  useEffect(() => {
    if (id) {
      loadRecipe();
      checkSavedStatus();
    }
  }, [id]);

  const loadRecipe = async () => {
    try {
      setIsLoading(true);
      const data = await recipeService.getById(parseInt(id!));
      setRecipe(data);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to load recipe');
    } finally {
      setIsLoading(false);
    }
  };

  const checkSavedStatus = async () => {
    try {
      const saved = await savedRecipeService.isSaved(parseInt(id!));
      setIsSaved(saved);
    } catch {
      // Ignore
    }
  };

  const toggleSave = async () => {
    setIsSaving(true);
    try {
      if (isSaved) {
        await savedRecipeService.unsave(parseInt(id!));
        setIsSaved(false);
        toast.success('Recipe removed from saved');
      } else {
        await savedRecipeService.save(parseInt(id!));
        setIsSaved(true);
        toast.success('Recipe saved!');
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to save recipe');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="page-container">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="animate-spin h-8 w-8 text-primary-600" />
        </div>
      </div>
    );
  }

  if (!recipe) {
    return (
      <div className="page-container">
        <div className="max-w-2xl mx-auto text-center py-16">
          <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-neutral-900 mb-2">Recipe Not Found</h2>
          <p className="text-neutral-600 mb-6">The recipe you're looking for doesn't exist or has been removed.</p>
          <Link to="/recipes" className="btn-primary">Browse Recipes</Link>
        </div>
      </div>
    );
  }

  const dietLabels = recipe.diet_labels?.split('|').filter(Boolean) || [];
  const ingredients = recipe.ingredients?.split('\n').filter(Boolean) || [];
  const instructions = recipe.instructions?.split('\n').filter(Boolean) || [];

  const getNutritionStatus = () => {
    if (!recipe.nutrition_per_serving) return 'unavailable';
    switch (recipe.nutrition_per_serving.calculation_status) {
      case 'COMPLETE': return 'complete';
      case 'PARTIAL': return 'partial';
      default: return 'unavailable';
    }
  };

  const status = getNutritionStatus();

  return (
    <div className="page-container">
      <Link to="/recipes" className="btn-ghost mb-6 inline-flex items-center gap-2">
        <ArrowLeft className="w-4 h-4" />
        Back to Recipes
      </Link>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Header */}
          <div>
            <div className="flex items-start justify-between gap-4 mb-4">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <span className={`badge ${recipe.recipe_type === 'veg' ? 'badge-success' : recipe.recipe_type === 'non-veg' ? 'badge-error' : 'badge-warning'}`}>
                    {recipe.recipe_type}
                  </span>
                  <span className="badge badge-gray">{recipe.cuisine}</span>
                  <span className="badge badge-gray">{recipe.course}</span>
                </div>
                <h1 className="text-3xl font-bold text-neutral-900">{recipe.recipe_name}</h1>
              </div>
              <button
                onClick={toggleSave}
                disabled={isSaving}
                className={`p-2 rounded-lg transition-colors ${isSaved ? 'bg-red-50 text-red-600 hover:bg-red-100' : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'}`}
                aria-label={isSaved ? 'Remove from saved' : 'Save recipe'}
              >
                {isSaved ? <Heart className="w-5 h-5 fill-current" /> : <HeartOff className="w-5 h-5" />}
              </button>
            </div>

            <div className="flex flex-wrap items-center gap-4 text-sm text-neutral-600">
              <span className="flex items-center gap-1"><Clock className="w-4 h-4" /> Prep: {recipe.prep_time_min} min</span>
              <span className="flex items-center gap-1"><Clock className="w-4 h-4" /> Cook: {recipe.cook_time_min} min</span>
              <span className="flex items-center gap-1"><Clock className="w-4 h-4" /> Total: {recipe.total_time_min} min</span>
              <span className="flex items-center gap-1"><Users className="w-4 h-4" /> {recipe.servings} servings</span>
            </div>
          </div>

          {/* Tabs */}
          <div className="card">
            <div className="border-b border-neutral-200">
              <nav className="flex gap-1 p-1" aria-label="Recipe tabs">
                {[
                  { id: 'ingredients', label: 'Ingredients', icon: Utensils },
                  { id: 'instructions', label: 'Instructions', icon: BookOpen },
                  { id: 'nutrition', label: 'Nutrition', icon: Info },
                ].map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      activeTab === tab.id
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-neutral-600 hover:text-neutral-900 hover:bg-neutral-50'
                    }`}
                  >
                    <tab.icon className="w-4 h-4" />
                    {tab.label}
                  </button>
                ))}
              </nav>
            </div>

            <div className="p-6">
              {activeTab === 'ingredients' && (
                <IngredientsTab ingredients={ingredients} dietLabels={dietLabels} />
              )}
              {activeTab === 'instructions' && (
                <InstructionsTab instructions={instructions} />
              )}
              {activeTab === 'nutrition' && (
                <NutritionTab recipe={recipe} status={status} />
              )}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Image */}
          <div className="card overflow-hidden">
            <div className="aspect-[4/3] bg-neutral-100 relative">
              {recipe.image_url ? (
                <img
                  src={recipe.image_url}
                  alt={recipe.recipe_name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-neutral-400">
                  <Utensils className="w-16 h-16" />
                </div>
              )}
            </div>
          </div>

          {/* Quick Info */}
          <div className="card p-6">
            <h3 className="font-semibold text-neutral-900 mb-4">Quick Info</h3>
            <dl className="space-y-4">
              <div className="flex justify-between">
                <dt className="text-neutral-600">Cuisine</dt>
                <dd className="font-medium">{recipe.cuisine}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-neutral-600">Course</dt>
                <dd className="font-medium">{recipe.course}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-neutral-600">Diet Type</dt>
                <dd className="font-medium capitalize">{recipe.recipe_type}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-neutral-600">Total Time</dt>
                <dd className="font-medium">{recipe.total_time_min} minutes</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-neutral-600">Servings</dt>
                <dd className="font-medium">{recipe.servings}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-neutral-600">Prep Time</dt>
                <dd className="font-medium">{recipe.prep_time_min} min</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-neutral-600">Cook Time</dt>
                <dd className="font-medium">{recipe.cook_time_min} min</dd>
              </div>
            </dl>
          </div>

          {/* Diet Labels */}
          {dietLabels.length > 0 && (
            <div className="card p-6">
              <h3 className="font-semibold text-neutral-900 mb-3 flex items-center gap-2">
                <Tag className="w-5 h-5 text-primary-600" />
                Dietary Labels
              </h3>
              <div className="flex flex-wrap gap-2">
                {dietLabels.map(label => (
                  <span key={label} className="badge badge-info">{label}</span>
                ))}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="card p-6">
            <h3 className="font-semibold text-neutral-900 mb-4">Actions</h3>
            <div className="space-y-2">
              <button className="btn-secondary w-full justify-center">
                <Share2 className="w-4 h-4 mr-2" />
                Share Recipe
              </button>
              <button className="btn-primary w-full justify-center" onClick={toggleSave} disabled={isSaving}>
                {isSaved ? (
                  <>
                    <Heart className="w-4 h-4 mr-2 fill-current" />
                    Remove from Saved
                  </>
                ) : (
                  <>
                    <HeartOff className="w-4 h-4 mr-2" />
                    Save Recipe
                  </>
                )}
              </button>
              <button className="btn-secondary w-full justify-center">
                <Utensils className="w-4 h-4 mr-2" />
                Add to Meal Plan
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function IngredientsTab({ ingredients, dietLabels }: { ingredients: string[]; dietLabels: string[] }) {
  const isVegetarian = dietLabels.includes('vegetarian');
  const isVegan = dietLabels.includes('vegan');
  const isJain = dietLabels.includes('jain');

  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <h3 className="font-semibold text-neutral-900">Ingredients ({ingredients.length})</h3>
        {isVegetarian && <span className="badge badge-success">Vegetarian</span>}
        {isVegan && <span className="badge badge-success">Vegan</span>}
        {isJain && <span className="badge badge-warning">Jain</span>}
      </div>
      {ingredients.length === 0 ? (
        <p className="text-neutral-500">No ingredients listed.</p>
      ) : (
        <ul className="space-y-2">
          {ingredients.map((ingredient, index) => (
            <li key={index} className="flex items-start gap-3 p-3 bg-neutral-50 rounded-lg">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 text-primary-700 text-xs font-medium flex items-center justify-center">
                {index + 1}
              </span>
              <span className="text-neutral-900">{ingredient}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function InstructionsTab({ instructions }: { instructions: string[] }) {
  return (
    <div>
      <h3 className="font-semibold text-neutral-900 mb-4">Instructions ({instructions.length} steps)</h3>
      {instructions.length === 0 ? (
        <p className="text-neutral-500">No instructions provided.</p>
      ) : (
        <ol className="space-y-4">
          {instructions.map((step, index) => (
            <li key={index} className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-100 text-primary-700 text-sm font-medium flex items-center justify-center">
                {index + 1}
              </span>
              <p className="text-neutral-900 pt-1">{step}</p>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

function NutritionTab({ recipe, status }: { recipe: RecipeDetail; status: string }) {
  const nutrition = recipe.nutrition_per_serving;

  if (!nutrition) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-neutral-900 mb-2">Nutrition Information Unavailable</h3>
        <p className="text-neutral-600 mb-4">
          This recipe cannot be analyzed for nutrition content due to insufficient data.
        </p>
        <div className="bg-neutral-50 rounded-lg p-4 text-left max-w-md mx-auto">
          <h4 className="font-semibold text-neutral-900 mb-2">Why is this unavailable?</h4>
          <ul className="list-disc list-inside space-y-1 text-sm text-neutral-600">
            <li>Zero approved IFCT (Indian Food Composition Tables) mappings</li>
            <li>1.4% gram weight coverage for ingredients</li>
            <li>42% of IFCT foods missing fibre/carbohydrate data</li>
            <li>Gate C authorization pending for ingredient mappings</li>
          </ul>
        </div>
      </div>
    );
  }

  if (status === 'unavailable') {
    return (
      <div className="text-center py-12">
        <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-neutral-900 mb-2">Nutrition Calculation Failed</h3>
        <p className="text-neutral-600 mb-4">
          Unable to calculate nutrition for this recipe. Missing ingredient mappings or weight data.
        </p>
        <p className="text-sm text-neutral-500">Status: {nutrition.calculation_status}</p>
        {nutrition.missing_nutrients.length > 0 && (
          <p className="text-sm text-neutral-500 mt-2">Missing: {nutrition.missing_nutrients.join(', ')}</p>
        )}
      </div>
    );
  }

  const isPartial = status === 'partial';

  return (
    <div>
      {isPartial && (
        <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
          <div>
            <h4 className="font-semibold text-yellow-800">Partial Nutrition Data</h4>
            <p className="text-yellow-700 text-sm mt-1">
              Some nutrients could not be calculated due to missing ingredient mappings or weight data.
              {nutrition.missing_nutrients.length > 0 && ` Missing: ${nutrition.missing_nutrients.join(', ')}`}
            </p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 mb-6">
        <NutritionStat label="Energy" value={`${nutrition.energy_kcal?.toFixed(0) || '—'}`} unit="kcal" icon={<span className="text-orange-600">🔥</span>} />
        <NutritionStat label="Protein" value={`${nutrition.protein_g?.toFixed(1) || '—'}`} unit="g" icon={<span className="text-red-600">🥩</span>} />
        <NutritionStat label="Fat" value={`${nutrition.fat_g?.toFixed(1) || '—'}`} unit="g" icon={<span className="text-yellow-600">🥑</span>} />
        <NutritionStat label="Carbs" value={`${nutrition.carbohydrate_g?.toFixed(1) || '—'}`} unit="g" icon={<span className="text-blue-600">🍞</span>} />
        <NutritionStat label="Fibre" value={`${nutrition.fibre_g?.toFixed(1) || '—'}`} unit="g" icon={<span className="text-green-600">🌿</span>} />
        <NutritionStat label="Sodium" value={`${nutrition.sodium_mg?.toFixed(0) || '—'}`} unit="mg" icon={<span className="text-purple-600">🧂</span>} />
      </div>

      <div className="border-t border-neutral-200 pt-4">
        <h4 className="font-semibold text-neutral-900 mb-3">Per 100g (Estimated)</h4>
        <p className="text-sm text-neutral-500 mb-4">
          Values estimated from per-serving nutrition. Actual values may vary based on preparation.
        </p>
        {recipe.nutrition_per_serving && recipe.servings && (
          <div className="grid grid-cols-2 gap-4">
            <NutritionStat
              label="Energy"
              value={recipe.nutrition_per_serving.energy_kcal ? (recipe.nutrition_per_serving.energy_kcal / recipe.servings / 100 * 100).toFixed(0) : '—'}
              unit="kcal"
              icon={<span className="text-orange-600">🔥</span>}
            />
            <NutritionStat
              label="Protein"
              value={recipe.nutrition_per_serving.protein_g ? (recipe.nutrition_per_serving.protein_g / recipe.servings / 100 * 100).toFixed(1) : '—'}
              unit="g"
              icon={<span className="text-red-600">🥩</span>}
            />
          </div>
        )}
      </div>

      <div className="border-t border-neutral-200 pt-4 mt-6">
        <h4 className="font-semibold text-neutral-900 mb-2">Data Provenance</h4>
        <p className="text-sm text-neutral-600">{nutrition.provenance || 'Calculated using IFCT 2017 food composition data with approved mappings only.'}</p>
      </div>
    </div>
  );
}

function NutritionStat({ label, value, unit, icon }: { label: string; value: string; unit: string; icon: React.ReactNode }) {
  return (
    <div className="card p-4 text-center">
      <div className="text-2xl mb-1">{icon}</div>
      <p className="text-2xl font-bold text-neutral-900">{value}</p>
      <p className="text-sm text-neutral-500">{label} ({unit})</p>
    </div>
  );
}

export default RecipeDetailPage;