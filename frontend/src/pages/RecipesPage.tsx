import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Recipe, SearchFilters, SearchResponse } from '../types';
import { recipeService } from '../services/api';
import { toast } from 'react-hot-toast';
import { Search, Filter, X, ChevronLeft, ChevronRight, Utensils, Clock, Users } from 'lucide-react';

const CUISINE_OPTIONS = [
  'North Indian', 'South Indian', 'Gujarati', 'Maharashtrian', 'Bengali', 'Punjabi',
  'Rajasthani', 'Kerala', 'Andhra', 'Tamil', 'Kashmiri', 'Goan', 'Hyderabadi',
  'Awadhi', 'Chettinad', 'Malvani', 'Konkani', 'Assamese', 'Odia', 'Other'
];

const COURSE_OPTIONS = [
  'Breakfast', 'Lunch', 'Dinner', 'Snack', 'Appetizer', 'Soup', 'Salad',
  'Side Dish', 'Main Course', 'Dessert', 'Beverage', 'Condiment'
];

const DIET_LABEL_OPTIONS = [
  'vegetarian', 'vegan', 'eggetarian', 'gluten-free', 'dairy-free', 'nut-free',
  'low-carb', 'high-protein', 'low-fat', 'diabetic-friendly', 'heart-healthy',
  'jain', 'keto', 'paleo', 'mediterranean'
];

export function RecipesPage() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [perPage] = useState(12);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    cuisine: '',
    course: '',
    diet_labels: [],
    max_prep_time: undefined,
    max_cook_time: undefined,
    max_total_time: undefined,
    page: 1,
    per_page: 12,
  });
  const [showFilters, setShowFilters] = useState(false);
  const [cuisines, setCuisines] = useState<string[]>([]);
  const [courses, setCourses] = useState<string[]>([]);
  const [dietLabels, setDietLabels] = useState<string[]>([]);

  useEffect(() => {
    loadMetadata();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      loadRecipes();
    }, 300);
    return () => clearTimeout(timer);
  }, [filters]);

  const loadMetadata = async () => {
    try {
      const [cuisinesData, coursesData, dietLabelsData] = await Promise.all([
        recipeService.getCuisines(),
        recipeService.getCourses(),
        recipeService.getDietLabels(),
      ]);
      setCuisines(cuisinesData);
      setCourses(coursesData);
      setDietLabels(dietLabelsData);
    } catch {
      // Fallback to defaults
    }
  };

  const loadRecipes = async () => {
    setIsLoading(true);
    try {
      const response: SearchResponse = await recipeService.search({
        ...filters,
        page,
        per_page: perPage,
      });
      setRecipes(response.recipes);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to load recipes');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilterChange = (key: keyof SearchFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value, page: 1 }));
    setPage(1);
  };

  const handleDietLabelToggle = (label: string) => {
    setFilters(prev => ({
      ...prev,
      diet_labels: prev.diet_labels?.includes(label)
        ? prev.diet_labels.filter(l => l !== label)
        : [...(prev.diet_labels || []), label],
      page: 1,
    }));
    setPage(1);
  };

  const clearFilters = () => {
    setFilters({
      query: '',
      cuisine: '',
      course: '',
      diet_labels: [],
      max_prep_time: undefined,
      max_cook_time: undefined,
      max_total_time: undefined,
      page: 1,
      per_page: 12,
    });
    setPage(1);
  };

  const hasActiveFilters = filters.query || filters.cuisine || filters.course ||
    (filters.diet_labels && filters.diet_labels.length > 0) ||
    filters.max_prep_time || filters.max_cook_time || filters.max_total_time;

  return (
    <div className="page-container">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Discover Recipes</h1>
          <p className="text-neutral-600 mt-1">
            {total} recipes available · Showing {recipes.length} of {total}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`btn-secondary flex items-center gap-2 ${hasActiveFilters ? 'bg-primary-50 border-primary-200 text-primary-700' : ''}`}
          >
            <Filter className="w-4 h-4" />
            Filters {hasActiveFilters && <span className="badge badge-info">{filters.diet_labels?.length || 0 + (filters.cuisine ? 1 : 0) + (filters.course ? 1 : 0)}</span>}
          </button>
          {hasActiveFilters && (
            <button onClick={clearFilters} className="btn-ghost text-sm text-red-600 hover:text-red-700">
              <X className="w-4 h-4 mr-1" />
              Clear All
            </button>
          )}
        </div>
      </div>

      {/* Filter Sidebar */}
      <div className="lg:hidden">
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`w-full btn-secondary justify-center ${hasActiveFilters ? 'bg-primary-50 border-primary-200 text-primary-700' : ''}`}
        >
          <Filter className="w-4 h-4 mr-2" />
          {showFilters ? 'Hide Filters' : 'Show Filters'}
          {hasActiveFilters && <span className="badge badge-info ml-2">{filters.diet_labels?.length || 0 + (filters.cuisine ? 1 : 0) + (filters.course ? 1 : 0)}</span>}
        </button>
      </div>

      <div className="flex gap-6">
        {/* Filters Panel */}
        <aside className={`w-72 flex-shrink-0 ${showFilters || true ? '' : 'hidden lg:block'}`}>
          <div className="card p-4 sticky top-24">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold text-neutral-900">Filters</h2>
              {hasActiveFilters && (
                <button onClick={clearFilters} className="text-sm text-primary-600 hover:underline">
                  Clear all
                </button>
              )}
            </div>

            <div className="space-y-6">
              {/* Search */}
              <div>
                <label className="label">Search</label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                  <input
                    type="text"
                    value={filters.query || ''}
                    onChange={e => handleFilterChange('query', e.target.value)}
                    placeholder="Search recipes..."
                    className="input-field pl-10"
                  />
                </div>
              </div>

              {/* Cuisine */}
              <div>
                <label className="label">Cuisine</label>
                <select
                  value={filters.cuisine || ''}
                  onChange={e => handleFilterChange('cuisine', e.target.value || undefined)}
                  className="input-field"
                >
                  <option value="">All Cuisines</option>
                  {cuisines.length > 0 ? cuisines.map(c => <option key={c} value={c}>{c}</option>) : CUISINE_OPTIONS.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>

              {/* Course */}
              <div>
                <label className="label">Course</label>
                <select
                  value={filters.course || ''}
                  onChange={e => handleFilterChange('course', e.target.value || undefined)}
                  className="input-field"
                >
                  <option value="">All Courses</option>
                  {courses.length > 0 ? courses.map(c => <option key={c} value={c}>{c}</option>) : COURSE_OPTIONS.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>

              {/* Diet Labels */}
              <div>
                <label className="label">Dietary Preferences</label>
                <div className="flex flex-wrap gap-2">
                  {(dietLabels.length > 0 ? dietLabels : DIET_LABEL_OPTIONS).map(label => (
                    <button
                      key={label}
                      type="button"
                      onClick={() => handleDietLabelToggle(label)}
                      className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                        filters.diet_labels?.includes(label)
                          ? 'bg-primary-100 text-primary-700'
                          : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Time Filters */}
              <div>
                <label className="label">Max Prep Time (min)</label>
                <input
                  type="number"
                  min="0"
                  max="300"
                  value={filters.max_prep_time || ''}
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
                  max="300"
                  value={filters.max_cook_time || ''}
                  onChange={e => handleFilterChange('max_cook_time', e.target.value ? parseInt(e.target.value) : undefined)}
                  className="input-field"
                  placeholder="Any"
                />
              </div>

              <div>
                <label className="label">Max Total Time (min)</label>
                <input
                  type="number"
                  min="0"
                  max="300"
                  value={filters.max_total_time || ''}
                  onChange={e => handleFilterChange('max_total_time', e.target.value ? parseInt(e.target.value) : undefined)}
                  className="input-field"
                  placeholder="Any"
                />
              </div>
            </div>
          </div>
        </aside>

        {/* Recipes Grid */}
        <main className="flex-1 min-w-0">
          {isLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {[...Array(8)].map((_, i) => (
                <RecipeCardSkeleton key={i} />
              ))}
            </div>
          ) : recipes.length === 0 ? (
            <div className="text-center py-16">
              <Utensils className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-neutral-900 mb-2">No recipes found</h3>
              <p className="text-neutral-500 mb-4">Try adjusting your filters or search terms</p>
              <button onClick={clearFilters} className="btn-primary">Clear Filters</button>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {recipes.map(recipe => (
                  <RecipeCard key={recipe.id} recipe={recipe} />
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-center gap-2 mt-8">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="btn-secondary p-2"
                    aria-label="Previous page"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                  <div className="flex items-center gap-1">
                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                      let pageNum;
                      if (totalPages <= 5) {
                        pageNum = i + 1;
                      } else if (page <= 3) {
                        pageNum = i + 1;
                      } else if (page >= totalPages - 2) {
                        pageNum = totalPages - 4 + i;
                      } else {
                        pageNum = page - 2 + i;
                      }
                      return (
                        <button
                          key={pageNum}
                          onClick={() => setPage(pageNum)}
                          className={`w-10 h-10 rounded-lg font-medium transition-colors ${
                            page === pageNum
                              ? 'bg-primary-600 text-white'
                              : 'text-neutral-600 hover:bg-neutral-100'
                          }`}
                        >
                          {pageNum}
                        </button>
                      );
                    })}
                  </div>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="btn-secondary p-2"
                    aria-label="Next page"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}

function RecipeCard({ recipe }: { recipe: Recipe }) {
  const dietLabels = recipe.diet_labels?.split('|').filter(Boolean) || [];
  const recipeType = recipe.recipe_type || 'Unknown';

  return (
    <Link to={`/recipes/${recipe.id}`} className="card-hover card overflow-hidden h-full flex flex-col">
      <div className="aspect-[4/3] bg-neutral-100 relative overflow-hidden">
        {recipe.image_url ? (
          <img
            src={recipe.image_url}
            alt={recipe.recipe_name}
            className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-neutral-400">
            <Utensils className="w-12 h-12" />
          </div>
        )}
        <div className="absolute top-2 right-2 flex gap-1">
          <span className={`badge ${recipeType === 'veg' ? 'badge-success' : recipeType === 'non-veg' ? 'badge-error' : 'badge-warning'}`}>
            {recipeType}
          </span>
        </div>
      </div>
      <div className="p-4 flex-1 flex flex-col">
        <h3 className="font-semibold text-neutral-900 truncate mb-2">{recipe.recipe_name}</h3>
        <div className="flex items-center gap-3 text-sm text-neutral-500 mb-2">
          <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {recipe.total_time_min} min</span>
          <span className="flex items-center gap-1"><Users className="w-3.5 h-3.5" /> {recipe.servings} servings</span>
        </div>
        <p className="text-sm text-neutral-600 mb-3 line-clamp-2">{recipe.cuisine} · {recipe.course}</p>
        <div className="flex flex-wrap gap-1 mt-auto">
          {dietLabels.slice(0, 3).map(label => (
            <span key={label} className="badge badge-gray">{label}</span>
          ))}
          {dietLabels.length > 3 && (
            <span className="badge badge-gray">+{dietLabels.length - 3} more</span>
          )}
        </div>
      </div>
    </Link>
  );
}

function RecipeCardSkeleton() {
  return (
    <div className="card overflow-hidden animate-pulse">
      <div className="aspect-[4/3] bg-neutral-200" />
      <div className="p-4 space-y-3">
        <div className="h-4 bg-neutral-200 rounded w-3/4" />
        <div className="h-3 bg-neutral-200 rounded w-1/2" />
        <div className="h-3 bg-neutral-200 rounded w-1/3" />
        <div className="flex gap-2">
          <div className="h-5 bg-neutral-200 rounded-full w-20" />
          <div className="h-5 bg-neutral-200 rounded-full w-20" />
        </div>
      </div>
    </div>
  );
}

export default RecipesPage;