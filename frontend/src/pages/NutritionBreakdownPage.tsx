import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { NutritionBreakdown, Recipe } from '../types';
import { nutritionService, recipeService } from '../services/api';
import { toast } from 'react-hot-toast';
import { Loader2, Search, AlertTriangle, Info, CheckCircle2, XCircle, Leaf, FlaskConical, ChevronRight } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';

export function NutritionBreakdownPage() {
  const [searchParams] = useSearchParams();
  const recipeIdParam = searchParams.get('recipe');
  const [recipeId, setRecipeId] = useState<string>(recipeIdParam || '');
  const [breakdown, setBreakdown] = useState<NutritionBreakdown | null>(null);
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Recipe[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [, setShowSearch] = useState(!recipeIdParam);

  useEffect(() => {
    if (recipeId) {
      loadBreakdown();
    }
  }, [recipeId]);

  const loadBreakdown = async () => {
    setIsLoading(true);
    try {
      const [breakdownData, recipeData] = await Promise.all([
        nutritionService.getBreakdown(parseInt(recipeId)),
        recipeService.getById(parseInt(recipeId)),
      ]);
      setBreakdown(breakdownData);
      setRecipe(recipeData);
      setShowSearch(false);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to load nutrition breakdown');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }
    setIsSearching(true);
    try {
      const response = await recipeService.search({ query, per_page: 10 });
      setSearchResults(response.recipes);
    } catch {
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchQuery(value);
    clearTimeout((window as any).searchTimeout);
    (window as any).searchTimeout = setTimeout(() => handleSearch(value), 300);
  };

  const selectRecipe = (selectedRecipe: Recipe) => {
    setRecipeId(String(selectedRecipe.id));
    setSearchQuery('');
    setSearchResults([]);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETE': return 'text-green-600 bg-green-100';
      case 'PARTIAL': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-red-600 bg-red-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLETE': return <CheckCircle2 className="w-4 h-4" />;
      case 'PARTIAL': return <AlertTriangle className="w-4 h-4" />;
      default: return <XCircle className="w-4 h-4" />;
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

  if (!breakdown) {
    return (
      <div className="page-container">
        <div className="max-w-3xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-neutral-900 flex items-center gap-3">
              <FlaskConical className="w-8 h-8 text-primary-600" />
              Nutrition Analysis
            </h1>
            <p className="text-neutral-600 mt-1">Analyze the nutritional content of any recipe</p>
          </div>

          {/* Search */}
          <div className="card p-6 mb-8">
            <h2 className="text-lg font-semibold text-neutral-900 mb-4">Search for a Recipe</h2>
            <div className="relative max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={handleSearchChange}
                placeholder="Search recipes by name, ingredient, or cuisine..."
                className="input-field pl-10 pr-10"
              />
              {isSearching && <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 animate-spin text-primary-600" />}
            </div>
            {searchResults.length > 0 && (
              <div className="mt-4 space-y-2 max-h-64 overflow-y-auto">
                {searchResults.map(r => (
                  <button
                    key={r.id}
                    onClick={() => selectRecipe(r)}
                    className="w-full text-left p-3 border border-neutral-200 rounded-lg hover:bg-neutral-50 transition-colors flex items-center gap-3"
                  >
                    <div className="w-12 h-12 rounded-lg bg-neutral-100 flex items-center justify-center flex-shrink-0">
                      <Leaf className="w-5 h-5 text-neutral-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-neutral-900 truncate">{r.recipe_name}</p>
                      <p className="text-sm text-neutral-500">{r.cuisine} · {r.total_time_min} min · {r.servings} servings</p>
                    </div>
                    <ChevronRight className="w-5 h-5 text-neutral-400" />
                  </button>
                ))}
              </div>
            )}
            {searchQuery && searchResults.length === 0 && !isSearching && (
              <p className="mt-4 text-center text-neutral-500">No recipes found matching "{searchQuery}"</p>
            )}
          </div>

          {/* Manual ID Entry */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-neutral-900 mb-4">Or Enter Recipe ID</h2>
            <div className="flex gap-2 max-w-md">
              <input
                type="number"
                min="1"
                placeholder="Recipe ID"
                className="input-field flex-1"
                onKeyDown={e => e.key === 'Enter' && e.currentTarget.value && setRecipeId(e.currentTarget.value)}
              />
              <button
                onClick={() => {
                  const input = document.querySelector('input[type="number"]') as HTMLInputElement;
                  if (input?.value) setRecipeId(input.value);
                }}
                className="btn-primary"
              >
                Analyze
              </button>
            </div>
          </div>

          {/* Limitations Info */}
          <div className="mt-8 card p-6 border-yellow-200 bg-yellow-50">
            <h3 className="font-semibold text-yellow-800 mb-3 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              Important Limitations
            </h3>
            <ul className="list-disc list-inside space-y-2 text-yellow-700 text-sm">
              <li><strong>Zero approved IFCT mappings:</strong> No ingredient-to-nutrient mappings have been approved</li>
              <li><strong>1.4% gram weight coverage:</strong> Most ingredients lack resolved weight data</li>
              <li><strong>42% nutrient gaps:</strong> Fibre/carbohydrate missing for 222/528 IFCT foods</li>
              <li><strong>34% edible portion coverage:</strong> Only ~180/528 IFCT codes have factors</li>
              <li><strong>Gate C pending:</strong> Human review required before mappings are approved</li>
            </ul>
            <p className="mt-3 text-sm text-yellow-600">
              Nutrition information will show as <strong>UNAVAILABLE</strong> for all recipes until approved mappings exist.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const status = breakdown.completeness;
  const perServing = breakdown.per_serving;
  const ingredients = breakdown.ingredients || [];

  return (
    <div className="page-container">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Link to="/nutrition-breakdown" className="btn-ghost mb-2 inline-flex items-center gap-2">
            <ChevronRight className="w-4 h-4 rotate-180" />
            New Analysis
          </Link>
          <h1 className="text-3xl font-bold text-neutral-900">{recipe?.recipe_name || 'Recipe'}</h1>
          <p className="text-neutral-600 mt-1">{recipe?.cuisine} · {recipe?.course} · {recipe?.total_time_min} min · {recipe?.servings} servings</p>
        </div>
        <div className="flex items-center gap-3">
          <span className={`badge px-3 py-1 ${getStatusColor(status)} flex items-center gap-1`}>
            {getStatusIcon(status)}
            {status}
          </span>
        </div>
      </div>

      {status === 'UNAVAILABLE' && (
        <div className="card p-8 text-center mb-6">
          <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-neutral-900 mb-2">Nutrition Analysis Unavailable</h2>
          <p className="text-neutral-600 mb-4 max-w-2xl mx-auto">
            This recipe cannot be analyzed for nutrition content due to insufficient data in the system.
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
          {breakdown.notes.length > 0 && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-left">
              <h4 className="font-semibold text-red-800 mb-2">Details</h4>
              <ul className="list-disc list-inside space-y-1 text-sm text-red-700">
                {breakdown.notes.map((note, i) => <li key={i}>{note}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}

      {status !== 'UNAVAILABLE' && (
        <>
          {/* Per Serving Summary */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
            <NutritionCard
              label="Energy"
              value={perServing.energy_kcal?.toFixed(0) || '—'}
              unit="kcal"
              color="#ef4444"
              icon={<span className="text-2xl">🔥</span>}
            />
            <NutritionCard
              label="Protein"
              value={perServing.protein_g?.toFixed(1) || '—'}
              unit="g"
              color="#dc2626"
              icon={<span className="text-2xl">🥩</span>}
            />
            <NutritionCard
              label="Fat"
              value={perServing.fat_g?.toFixed(1) || '—'}
              unit="g"
              color="#f59e0b"
              icon={<span className="text-2xl">🥑</span>}
            />
            <NutritionCard
              label="Carbs"
              value={perServing.carbohydrate_g?.toFixed(1) || '—'}
              unit="g"
              color="#3b82f6"
              icon={<span className="text-2xl">🍞</span>}
            />
            <NutritionCard
              label="Fibre"
              value={perServing.fibre_g?.toFixed(1) || '—'}
              unit="g"
              color="#22c55e"
              icon={<span className="text-2xl">🌿</span>}
            />
            <NutritionCard
              label="Sodium"
              value={perServing.sodium_mg?.toFixed(0) || '—'}
              unit="mg"
              color="#8b5cf6"
              icon={<span className="text-2xl">🧂</span>}
            />
          </div>

          {status === 'PARTIAL' && (
            <div className="card p-4 mb-6 border-yellow-200 bg-yellow-50">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-yellow-800">Partial Nutrition Data</h3>
                  <p className="text-yellow-700 text-sm mt-1">
                    Some nutrients could not be calculated due to missing ingredient mappings or weight data.
                    {breakdown.per_serving.missing_nutrients.length > 0 && (
                      <> Missing: {breakdown.per_serving.missing_nutrients.join(', ')}</>
                    )}
                  </p>
                </div>
              </div>
            </div>
          )}

          <div className="grid lg:grid-cols-2 gap-6">
            {/* Macro Chart */}
            <div className="card p-6">
              <h3 className="font-semibold text-neutral-900 mb-4">Macronutrient Distribution (Per Serving)</h3>
              <div className="h-64 mb-4">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={[
                        { name: 'Protein', value: perServing.protein_g || 0, calories: (perServing.protein_g || 0) * 4, color: '#dc2626' },
                        { name: 'Fat', value: perServing.fat_g || 0, calories: (perServing.fat_g || 0) * 9, color: '#f59e0b' },
                        { name: 'Carbs', value: perServing.carbohydrate_g || 0, calories: (perServing.carbohydrate_g || 0) * 4, color: '#3b82f6' },
                      ].filter(d => d.value > 0)}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={2}
                      dataKey="calories"
                      nameKey="name"
                      label={({ name, value }) => `${name}: ${value}g`}
                      labelLine={false}
                    >
                      {[
                        { name: 'Protein', value: perServing.protein_g || 0, calories: (perServing.protein_g || 0) * 4, color: '#dc2626' },
                        { name: 'Fat', value: perServing.fat_g || 0, calories: (perServing.fat_g || 0) * 9, color: '#f59e0b' },
                        { name: 'Carbs', value: perServing.carbohydrate_g || 0, calories: (perServing.carbohydrate_g || 0) * 4, color: '#3b82f6' },
                      ].filter(d => d.value > 0).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => [`${value}kcal`, 'Calories']} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="grid grid-cols-3 gap-4">
                {[
                  { name: 'Protein', value: perServing.protein_g, color: '#dc2626', kcal: (perServing.protein_g || 0) * 4 },
                  { name: 'Fat', value: perServing.fat_g, color: '#f59e0b', kcal: (perServing.fat_g || 0) * 9 },
                  { name: 'Carbs', value: perServing.carbohydrate_g, color: '#3b82f6', kcal: (perServing.carbohydrate_g || 0) * 4 },
                ].filter(d => d.value != null).map(item => (
                  <div key={item.name} className="text-center p-3 bg-neutral-50 rounded-lg">
                    <div className="w-3 h-3 rounded-full mx-auto mb-1" style={{ backgroundColor: item.color }} />
                    <p className="text-sm font-medium text-neutral-900">{item.name}</p>
                    <p className="text-lg font-bold text-neutral-900">{item.value?.toFixed(1)}g</p>
                    <p className="text-xs text-neutral-500">{item.kcal.toFixed(0)} kcal</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Ingredient Breakdown */}
            <div className="card p-6">
              <h3 className="font-semibold text-neutral-900 mb-4">Ingredient Contribution</h3>
              {ingredients.length === 0 ? (
                <p className="text-neutral-500 text-center py-8">No ingredient breakdown available</p>
              ) : (
                <>
                <div className="h-80 mb-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={ingredients.slice(0, 10).map((ing) => ({
                      name: ing.ingredient.length > 15 ? ing.ingredient.substring(0, 15) + '...' : ing.ingredient,
                      energy: ing.nutrition.energy_kcal || 0,
                      protein: ing.nutrition.protein_g || 0,
                      fat: ing.nutrition.fat_g || 0,
                      carbs: ing.nutrition.carbohydrate_g || 0,
                      fullName: ing.ingredient,
                    }))}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis dataKey="name" stroke="#9ca3af" fontSize={10} tick={{ fill: '#6b7280' }} />
                      <YAxis stroke="#9ca3af" fontSize={10} tick={{ fill: '#6b7280' }} />
                      <Tooltip
                        formatter={(value: number, name: string) => [`${value.toFixed(1)}`, name]}
                        labelFormatter={(label: string) => label}
                      />
                      <Legend />
                      <Bar dataKey="energy" name="Energy (kcal)" fill="#ef4444" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="protein" name="Protein (g)" fill="#dc2626" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="fat" name="Fat (g)" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="carbs" name="Carbs (g)" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {ingredients.slice(0, 15).map((ing, i) => (
                    <div key={i} className="flex items-center justify-between p-2 bg-neutral-50 rounded">
                      <span className="text-sm text-neutral-900 truncate pr-2">{ing.ingredient}</span>
                      <span className="text-xs text-neutral-500">{ing.amount_g.toFixed(0)}g</span>
                      <span className="text-xs text-neutral-500">{ing.nutrition.energy_kcal?.toFixed(0) || 0} kcal</span>
                    </div>
                  ))}
                  {ingredients.length > 15 && (
                    <p className="text-xs text-neutral-500 text-center">+{ingredients.length - 15} more ingredients</p>
                  )}
                </div>
                </>
              )}
            </div>
          </div>

          {/* Micronutrients */}
          {perServing && Object.keys(perServing).some(k => !['energy_kcal', 'protein_g', 'fat_g', 'carbohydrate_g', 'fibre_g', 'sodium_mg', 'calculation_status', 'missing_nutrients', 'provenance'].includes(k)) && (
            <div className="card p-6 mt-6">
              <h3 className="font-semibold text-neutral-900 mb-4">Micronutrients (Per Serving)</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {Object.entries(perServing).filter(([key]) => !['energy_kcal', 'protein_g', 'fat_g', 'carbohydrate_g', 'fibre_g', 'sodium_mg', 'calculation_status', 'missing_nutrients', 'provenance'].includes(key)).map(([key, value]) => (
                  <div key={key} className="p-3 bg-neutral-50 rounded-lg">
                    <p className="text-xs text-neutral-500 capitalize">{key.replace(/_/g, ' ')}</p>
                    <p className="text-lg font-bold text-neutral-900">{typeof value === 'number' ? value.toFixed(1) : value}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Provenance */}
          <div className="card p-6 mt-6">
            <h3 className="font-semibold text-neutral-900 mb-3 flex items-center gap-2">
              <Info className="w-5 h-5 text-blue-600" />
              Data Provenance
            </h3>
            <p className="text-sm text-neutral-600">{breakdown.per_serving.provenance || 'Calculated using IFCT 2017 food composition data with approved mappings only.'}</p>
            {breakdown.notes.length > 0 && (
              <div className="mt-3 space-y-1">
                {breakdown.notes.map((note, i) => (
                  <p key={i} className="text-sm text-neutral-600 flex items-center gap-1">
                    <Info className="w-3.5 h-3.5 text-blue-500" /> {note}
                  </p>
                ))}
              </div>
            )}
          </div>
        </>
      )}

      {/* Recipe Link */}
      {recipe && (
        <div className="mt-6 card p-4">
          <Link to={`/recipes/${recipe.id}`} className="flex items-center gap-3 p-2 hover:bg-neutral-50 rounded-lg transition-colors">
            <div className="w-12 h-12 rounded-lg bg-neutral-100 flex items-center justify-center">
              <Leaf className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <p className="font-medium text-neutral-900">{recipe.recipe_name}</p>
              <p className="text-sm text-neutral-500">View full recipe details</p>
            </div>
            <ChevronRight className="w-5 h-5 text-neutral-400 ml-auto" />
          </Link>
        </div>
      )}
    </div>
  );
}

function NutritionCard({ label, value, unit, color, icon }: { label: string; value: string; unit: string; color: string; icon: React.ReactNode }) {
  return (
    <div className="card p-4 text-center">
      <div className="mb-2">{icon}</div>
      <p className="text-2xl font-bold text-neutral-900">{value}</p>
      <p className="text-sm text-neutral-500">{label} ({unit})</p>
      <div className="mt-2 h-1.5 bg-neutral-200 rounded-full overflow-hidden">
        <div className="h-full rounded-full" style={{ backgroundColor: color, width: '100%' }} />
      </div>
    </div>
  );
}

export default NutritionBreakdownPage;