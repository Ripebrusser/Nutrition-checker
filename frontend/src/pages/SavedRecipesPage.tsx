import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { SavedRecipe } from '../types';
import { savedRecipeService } from '../services/api';
import { toast } from 'react-hot-toast';
import { Loader2, Heart, HeartOff, BookOpen, Utensils, Clock, Users, Tag, Grid, List, Download } from 'lucide-react';

export function SavedRecipesPage() {
  const [savedRecipes, setSavedRecipes] = useState<SavedRecipe[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState<'recent' | 'name' | 'cuisine' | 'time'>('recent');

  useEffect(() => {
    loadSavedRecipes();
  }, []);

  const loadSavedRecipes = async () => {
    try {
      setIsLoading(true);
      const data = await savedRecipeService.getAll();
      setSavedRecipes(data);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to load saved recipes');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUnsave = async (recipeId: number) => {
    try {
      await savedRecipeService.unsave(recipeId);
      setSavedRecipes(prev => prev.filter(r => r.recipe_id !== recipeId));
      toast.success('Recipe removed from saved');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to remove recipe');
    }
  };

  const sortedRecipes = [...savedRecipes].sort((a, b) => {
    switch (sortBy) {
      case 'name':
        return (a.recipe?.recipe_name || '').localeCompare(b.recipe?.recipe_name || '');
      case 'cuisine':
        return (a.recipe?.cuisine || '').localeCompare(b.recipe?.cuisine || '');
      case 'time':
        return (a.recipe?.total_time_min || 0) - (b.recipe?.total_time_min || 0);
      default:
        return new Date(b.saved_at).getTime() - new Date(a.saved_at).getTime();
    }
  });

  const getCuisines = () => {
    const cuisines = new Set(savedRecipes.map(r => r.recipe?.cuisine).filter(Boolean));
    return Array.from(cuisines).sort();
  };

  const getDietLabels = () => {
    const labels = new Set<string>();
    savedRecipes.forEach(r => {
      r.recipe?.diet_labels?.split('|').filter(Boolean).forEach(l => labels.add(l));
    });
    return Array.from(labels).sort();
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

  return (
    <div className="page-container">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900 flex items-center gap-3">
            <BookOpen className="w-8 h-8 text-primary-600" />
            Saved Recipes
          </h1>
          <p className="text-neutral-600 mt-1">{savedRecipes.length} recipe{savedRecipes.length !== 1 ? 's' : ''} saved</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-1 bg-neutral-50 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded transition-colors ${viewMode === 'grid' ? 'bg-white text-primary-700 shadow-sm' : 'text-neutral-600'}`}
              aria-label="Grid view"
            >
              <Grid className="w-5 h-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded transition-colors ${viewMode === 'list' ? 'bg-white text-primary-700 shadow-sm' : 'text-neutral-600'}`}
              aria-label="List view"
            >
              <List className="w-5 h-5" />
            </button>
          </div>
          <select
            value={sortBy}
            onChange={e => setSortBy(e.target.value as any)}
            className="input-field w-auto"
          >
            <option value="recent">Recently Saved</option>
            <option value="name">Name (A-Z)</option>
            <option value="cuisine">Cuisine</option>
            <option value="time">Cook Time</option>
          </select>
          <button className="btn-secondary">
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <label className="flex items-center gap-2 text-sm font-medium text-neutral-700">Filter by:</label>
          <div className="flex flex-wrap gap-2">
            {getCuisines().map(cuisine => (
              <button
                key={cuisine}
                type="button"
                className="px-3 py-1 rounded-full text-xs font-medium bg-neutral-100 text-neutral-600 hover:bg-neutral-200 transition-colors"
              >
                {cuisine}
              </button>
            ))}
          </div>
          <div className="flex flex-wrap gap-2 ml-auto">
            {getDietLabels().map(label => (
              <span key={label} className="badge badge-info">{label}</span>
            ))}
          </div>
        </div>
      </div>

      {savedRecipes.length === 0 ? (
        <div className="text-center py-16">
          <HeartOff className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-neutral-900 mb-2">No Saved Recipes</h3>
          <p className="text-neutral-500 mb-6 max-w-md mx-auto">
            Start exploring recipes and save your favorites to build your personal cookbook.
          </p>
          <Link to="/recipes" className="btn-primary">
            <Utensils className="w-4 h-4 mr-2" />
            Browse Recipes
          </Link>
        </div>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {sortedRecipes.map(saved => (
            <SavedRecipeCard
              key={saved.id}
              saved={saved}
              onUnsave={handleUnsave}
            />
          ))}
        </div>
      ) : (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-neutral-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-neutral-500 uppercase tracking-wider">Recipe</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-neutral-500 uppercase tracking-wider hidden md:table-cell">Cuisine</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-neutral-500 uppercase tracking-wider hidden lg:table-cell">Course</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-neutral-500 uppercase tracking-wider hidden lg:table-cell">Time</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-neutral-500 uppercase tracking-wider hidden md:table-cell">Diet</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-neutral-500 uppercase tracking-wider">Saved</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-neutral-500 uppercase tracking-wider w-24">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-200">
                {sortedRecipes.map(saved => (
                  <tr key={saved.id} className="hover:bg-neutral-50">
                    <td className="px-4 py-3">
                      <Link
                        to={saved.recipe_id ? `/recipes/${saved.recipe_id}` : '#'}
                        className="flex items-center gap-3"
                      >
                        <div className="w-12 h-12 rounded-lg bg-neutral-100 flex items-center justify-center flex-shrink-0 overflow-hidden">
                          {saved.recipe?.image_url ? (
                            <img src={saved.recipe.image_url} alt={saved.recipe.recipe_name} className="w-full h-full object-cover" />
                          ) : (
                            <Utensils className="w-5 h-5 text-neutral-400" />
                          )}
                        </div>
                        <div>
                          <p className="font-medium text-neutral-900">{saved.recipe?.recipe_name || 'Unknown Recipe'}</p>
                          <p className="text-sm text-neutral-500">{saved.recipe?.servings} servings</p>
                        </div>
                      </Link>
                    </td>
                    <td className="px-4 py-3 hidden md:table-cell text-sm text-neutral-600">{saved.recipe?.cuisine}</td>
                    <td className="px-4 py-3 hidden lg:table-cell text-sm text-neutral-600">{saved.recipe?.course}</td>
                    <td className="px-4 py-3 hidden lg:table-cell text-sm text-neutral-600 flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" /> {saved.recipe?.total_time_min} min
                    </td>
                    <td className="px-4 py-3 hidden md:table-cell">
                      <div className="flex flex-wrap gap-1">
                        {saved.recipe?.diet_labels?.split('|').filter(Boolean).slice(0, 3).map(label => (
                          <span key={label} className="badge badge-gray text-xs">{label}</span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-neutral-500">{new Date(saved.saved_at).toLocaleDateString()}</td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          to={saved.recipe_id ? `/recipes/${saved.recipe_id}` : '#'}
                          className="btn-ghost p-2 text-primary-600 hover:text-primary-700"
                          aria-label="View recipe"
                        >
                          <BookOpen className="w-4 h-4" />
                        </Link>
                        <button
                          onClick={() => handleUnsave(saved.recipe_id!)}
                          className="btn-ghost p-2 text-red-600 hover:text-red-700"
                          aria-label="Remove from saved"
                        >
                          <HeartOff className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Stats */}
      {savedRecipes.length > 0 && (
        <div className="mt-8 card p-6">
          <h3 className="font-semibold text-neutral-900 mb-4">Your Recipe Collection</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <StatCard label="Total Recipes" value={savedRecipes.length} icon={<BookOpen className="w-6 h-6 text-primary-600" />} />
            <StatCard label="Cuisines" value={getCuisines().length} icon={<Tag className="w-6 h-6 text-green-600" />} />
            <StatCard label="Diet Types" value={getDietLabels().length} icon={<Utensils className="w-6 h-6 text-orange-600" />} />
            <StatCard label="Avg Cook Time" value={Math.round(savedRecipes.reduce((sum, r) => sum + (r.recipe?.total_time_min || 0), 0) / savedRecipes.length)} unit="min" icon={<Clock className="w-6 h-6 text-blue-600" />} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-neutral-900 mb-3">Cuisine Distribution</h4>
              <div className="space-y-2">
                {getCuisines().slice(0, 10).map(cuisine => {
                  const count = savedRecipes.filter(r => r.recipe?.cuisine === cuisine).length;
                  return (
                    <div key={cuisine} className="flex items-center gap-3">
                      <span className="w-24 text-sm text-neutral-600 truncate">{cuisine}</span>
                      <div className="flex-1 h-2 bg-neutral-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary-500 rounded-full"
                          style={{ width: `${(count / savedRecipes.length) * 100}%` }}
                        />
                      </div>
                      <span className="w-12 text-sm text-neutral-500 text-right">{count}</span>
                    </div>
                  );
                })}
              </div>
            </div>
            <div>
              <h4 className="font-medium text-neutral-900 mb-3">Diet Labels</h4>
              <div className="flex flex-wrap gap-2">
                {getDietLabels().map(label => {
                  const count = savedRecipes.filter(r => r.recipe?.diet_labels?.includes(label)).length;
                  return (
                    <span key={label} className="badge badge-info">{label} ({count})</span>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function SavedRecipeCard({ saved, onUnsave }: { saved: SavedRecipe; onUnsave: (recipeId: number) => void }) {
  const recipe = saved.recipe;

  return (
    <Link to={recipe?.id ? `/recipes/${recipe.id}` : '#'} className="card-hover card overflow-hidden h-full flex flex-col relative group">
      <div className="absolute top-2 right-2 z-10">
        <button
          onClick={e => { e.preventDefault(); e.stopPropagation(); onUnsave(recipe!.id!); }}
          className="p-2 rounded-full bg-white/90 backdrop-blur-sm text-red-600 hover:bg-red-50 hover:text-red-700 transition-colors opacity-0 group-hover:opacity-100"
          aria-label="Remove from saved"
        >
          <HeartOff className="w-5 h-5" />
        </button>
      </div>
      <div className="aspect-[4/3] bg-neutral-100 relative overflow-hidden">
        {recipe?.image_url ? (
          <img
            src={recipe.image_url}
            alt={recipe.recipe_name}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-neutral-400">
            <Utensils className="w-12 h-12" />
          </div>
        )}
        <div className="absolute top-2 left-2 flex gap-1">
          <span className={`badge ${recipe?.recipe_type === 'veg' ? 'badge-success' : recipe?.recipe_type === 'non-veg' ? 'badge-error' : 'badge-warning'}`}>
            {recipe?.recipe_type}
          </span>
        </div>
      </div>
      <div className="p-4 flex-1 flex flex-col">
        <h3 className="font-semibold text-neutral-900 truncate mb-2">{recipe?.recipe_name}</h3>
        <div className="flex items-center gap-3 text-sm text-neutral-500 mb-2">
          <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {recipe?.total_time_min} min</span>
          <span className="flex items-center gap-1"><Users className="w-3.5 h-3.5" /> {recipe?.servings} servings</span>
        </div>
        <p className="text-sm text-neutral-600 mb-3 line-clamp-1">{recipe?.cuisine} · {recipe?.course}</p>
        <div className="flex flex-wrap gap-1 mt-auto">
          {recipe?.diet_labels?.split('|').filter(Boolean).slice(0, 3).map(label => (
            <span key={label} className="badge badge-gray">{label}</span>
          ))}
          {(recipe?.diet_labels?.split('|').filter(Boolean).length || 0) > 3 && (
            <span className="badge badge-gray">+{(recipe?.diet_labels?.split('|').filter(Boolean).length || 0) - 3} more</span>
          )}
        </div>
        <div className="mt-3 pt-3 border-t border-neutral-100 flex items-center justify-between text-xs text-neutral-500">
          <span>Saved {new Date(saved.saved_at).toLocaleDateString()}</span>
          <Heart className="w-4 h-4 text-red-500 fill-current" />
        </div>
      </div>
    </Link>
  );
}

function StatCard({ label, value, unit = '', icon }: { label: string; value: string | number; unit?: string; icon: React.ReactNode }) {
  return (
    <div className="p-4 bg-neutral-50 rounded-lg text-center">
      <div className="mb-2">{icon}</div>
      <p className="text-2xl font-bold text-neutral-900">{value}{unit && <span className="text-lg font-normal text-neutral-500 ml-1">{unit}</span>}</p>
      <p className="text-sm text-neutral-500 mt-1">{label}</p>
    </div>
  );
}

export default SavedRecipesPage;