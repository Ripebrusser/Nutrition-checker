import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { MealPlan, MealPlanItem, Recipe } from '../types';
import { mealPlanService, recipeService } from '../services/api';
import { toast } from 'react-hot-toast';
import { Loader2, Plus, Trash2, Calendar, Utensils, ArrowUpDown, CheckCircle2, XCircle, Sparkles, Download, Copy } from 'lucide-react';

const MEAL_SLOTS = [
  { id: 'BREAKFAST', label: 'Breakfast', icon: '🌅', time: '7:00 AM' },
  { id: 'MORNING_SNACK', label: 'Morning Snack', icon: '🍎', time: '10:00 AM' },
  { id: 'LUNCH', label: 'Lunch', icon: '🍱', time: '1:00 PM' },
  { id: 'EVENING_SNACK', label: 'Evening Snack', icon: '☕', time: '4:00 PM' },
  { id: 'DINNER', label: 'Dinner', icon: '🍽️', time: '7:30 PM' },
];

const DAYS = [
  { index: 0, name: 'Monday', short: 'Mon' },
  { index: 1, name: 'Tuesday', short: 'Tue' },
  { index: 2, name: 'Wednesday', short: 'Wed' },
  { index: 3, name: 'Thursday', short: 'Thu' },
  { index: 4, name: 'Friday', short: 'Fri' },
  { index: 5, name: 'Saturday', short: 'Sat' },
  { index: 6, name: 'Sunday', short: 'Sun' },
];

export function MealPlannerPage() {
  const [mealPlans, setMealPlans] = useState<MealPlan[]>([]);
  const [activePlan, setActivePlan] = useState<MealPlan | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newPlanName, setNewPlanName] = useState('');
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState(
    new Date(Date.now() + 6 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  );
  const [editingMeal, setEditingMeal] = useState<{ mealSlot: string; dayIndex: number } | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Recipe[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    loadMealPlans();
  }, []);

  const loadMealPlans = async () => {
    try {
      setIsLoading(true);
      const [plansData, activeData] = await Promise.all([
        mealPlanService.getAll(),
        mealPlanService.getActive().catch(() => null),
      ]);
      setMealPlans(plansData);
      setActivePlan(activeData);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to load meal plans');
    } finally {
      setIsLoading(false);
    }
  };

  const createPlan = async () => {
    if (!newPlanName.trim()) {
      toast.error('Please enter a plan name');
      return;
    }
    setIsCreating(true);
    try {
      const plan = await mealPlanService.create({
        name: newPlanName,
        start_date: startDate,
        end_date: endDate,
      });
      setMealPlans(prev => [plan, ...prev]);
      setActivePlan(plan);
      setShowCreateModal(false);
      setNewPlanName('');
      toast.success('Meal plan created!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create meal plan');
    } finally {
      setIsCreating(false);
    }
  };

  const deletePlan = async (planId: number) => {
    if (!confirm('Are you sure you want to delete this meal plan?')) return;
    try {
      await mealPlanService.delete(planId);
      setMealPlans(prev => prev.filter(p => p.id !== planId));
      if (activePlan?.id === planId) setActivePlan(null);
      toast.success('Meal plan deleted');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to delete meal plan');
    }
  };

  const setActive = async (plan: MealPlan) => {
    try {
      const updated = await mealPlanService.update(plan.id, { status: 'ACTIVE' });
      setMealPlans(prev => prev.map(p =>
        p.id === plan.id ? updated : p.id === activePlan?.id ? { ...p, status: 'DRAFT' } : p
      ));
      setActivePlan(updated);
      toast.success('Meal plan activated');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to activate meal plan');
    }
  };

  const addMeal = async (dayIndex: number, mealSlot: string, recipeId: number) => {
    if (!activePlan) return;
    try {
      await mealPlanService.addMeal(activePlan.id, {
        meal_slot: mealSlot as any,
        day_index: dayIndex,
        recipe_id: recipeId,
        servings: 1,
        is_completed: false,
      });
      // Refresh active plan
      const updated = await mealPlanService.getActive();
      setActivePlan(updated);
      toast.success('Meal added!');
      setEditingMeal(null);
      setSearchQuery('');
      setSearchResults([]);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to add meal');
    }
  };

  const removeMeal = async (mealId: number) => {
    if (!activePlan) return;
    try {
      await mealPlanService.removeMeal(activePlan.id, mealId);
      const updated = await mealPlanService.getActive();
      setActivePlan(updated);
      toast.success('Meal removed');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to remove meal');
    }
  };

  const toggleComplete = async (meal: MealPlanItem) => {
    if (!activePlan) return;
    try {
      await mealPlanService.completeMeal(activePlan.id, meal.id);
      const updated = await mealPlanService.getActive();
      setActivePlan(updated);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update meal');
    }
  };

  const updateServings = async (mealId: number, servings: number) => {
    if (!activePlan) return;
    try {
      await mealPlanService.updateMeal(activePlan.id, mealId, { servings });
      const updated = await mealPlanService.getActive();
      setActivePlan(updated);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update servings');
    }
  };

  const searchRecipes = async (query: string) => {
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
    (window as any).searchTimeout = setTimeout(() => searchRecipes(value), 300);
  };

  const openEditMeal = (meal: MealPlanItem, dayIndex: number) => {
    setEditingMeal({ mealSlot: meal.meal_slot, dayIndex });
    setSearchQuery(meal.recipe?.recipe_name || '');
    if (meal.recipe) setSearchResults([meal.recipe]);
  };

  const getMealForSlot = (dayIndex: number, mealSlot: string) => {
    return activePlan?.items?.find(item => item.day_index === dayIndex && item.meal_slot === mealSlot);
  };

  const getDayMeals = (dayIndex: number) => {
    return activePlan?.items?.filter(item => item.day_index === dayIndex) || [];
  };

  const getCompletedCount = (dayIndex: number) => {
    return getDayMeals(dayIndex).filter(m => m.is_completed).length;
  };

  const getTotalCount = (dayIndex: number) => {
    return getDayMeals(dayIndex).filter(m => m.recipe_id).length;
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
            <Calendar className="w-8 h-8 text-primary-600" />
            Meal Planner
          </h1>
          <p className="text-neutral-600 mt-1">
            Plan your weekly meals with nutrition tracking
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={activePlan?.id || ''}
            onChange={e => e.target.value ? setActive(mealPlans.find(p => p.id === parseInt(e.target.value))!) : {}}
            className="input-field w-auto"
          >
            <option value="">Select Meal Plan</option>
            {mealPlans.map(plan => (
              <option key={plan.id} value={plan.id}>
                {plan.name || `Plan ${plan.id}`} ({plan.status})
              </option>
            ))}
          </select>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Plan
          </button>
        </div>
      </div>

      {/* Active Plan Info */}
      {activePlan && (
        <div className="card p-4 mb-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <h2 className="font-semibold text-neutral-900">{activePlan.name || 'Untitled Plan'}</h2>
              <span className={`badge ${activePlan.status === 'ACTIVE' ? 'badge-success' : 'badge-gray'}`}>
                {activePlan.status}
              </span>
              <span className="text-sm text-neutral-500">
                {new Date(activePlan.start_date).toLocaleDateString()} - {new Date(activePlan.end_date).toLocaleDateString()}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => mealPlanService.optimize(activePlan.id).then(updated => {
                  setActivePlan(updated);
                  toast.success('Meal plan optimized!');
                })}
                className="btn-secondary text-sm"
              >
                <Sparkles className="w-4 h-4 mr-1" />
                Optimize
              </button>
              <button className="btn-secondary text-sm">
                <Download className="w-4 h-4 mr-1" />
                Export
              </button>
              <button className="btn-secondary text-sm">
                <Copy className="w-4 h-4 mr-1" />
                Duplicate
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Meal Grid */}
      {activePlan ? (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1000px]">
            <thead className="bg-neutral-50 sticky top-0 z-10">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-neutral-500 uppercase tracking-wider w-24">
                  Meal / Day
                </th>
                {DAYS.map(day => (
                  <th key={day.index} className="px-3 py-3 text-center text-xs font-semibold text-neutral-500 uppercase tracking-wider">
                    <div className="flex flex-col items-center">
                      <span>{day.short}</span>
                      <span className="text-xs text-neutral-400">{getCompletedCount(day.index)}/{getTotalCount(day.index)}</span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {MEAL_SLOTS.map(slot => (
                <tr key={slot.id} className="border-t border-neutral-100">
                  <td className="px-4 py-2 sticky left-0 bg-white z-10 w-24">
                    <div className="flex items-center gap-2">
                      <span className="text-xl">{slot.icon}</span>
                      <div>
                        <p className="font-medium text-neutral-900">{slot.label}</p>
                        <p className="text-xs text-neutral-500">{slot.time}</p>
                      </div>
                    </div>
                  </td>
                  {DAYS.map(day => {
                    const meal = getMealForSlot(day.index, slot.id);
                    return (
                      <td key={`${day.index}-${slot.id}`} className="px-2 py-2 align-top">
                        <MealCell
                          meal={meal}
                          dayIndex={day.index}
                          mealSlot={slot.id}
                          onEdit={openEditMeal}
                          onRemove={removeMeal}
                          onToggleComplete={toggleComplete}
                          onUpdateServings={updateServings}
                        />
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center py-16">
          <Calendar className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-neutral-900 mb-2">No Active Meal Plan</h3>
          <p className="text-neutral-500 mb-4">Create a new meal plan or select an existing one to get started.</p>
          <button onClick={() => setShowCreateModal(true)} className="btn-primary">
            <Plus className="w-4 h-4 mr-2" />
            Create Meal Plan
          </button>
        </div>
      )}

      {/* Edit Meal Modal */}
      {editingMeal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="bg-white rounded-xl max-w-md w-full max-h-[80vh] overflow-y-auto">
            <div className="p-4 border-b border-neutral-200 flex items-center justify-between">
              <h3 className="font-semibold text-neutral-900">Add Meal to {DAYS.find(d => d.index === editingMeal.dayIndex)?.name} - {MEAL_SLOTS.find(s => s.id === editingMeal.mealSlot)?.label}</h3>
              <button onClick={() => setEditingMeal(null)} className="p-2 hover:bg-neutral-100 rounded-lg">
                <XCircle className="w-5 h-5" />
              </button>
            </div>
            <div className="p-4">
              <div className="mb-4">
                <label className="label">Search Recipe</label>
                <div className="relative">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={handleSearchChange}
                    placeholder="Search recipes..."
                    className="input-field pr-10"
                  />
                  {isSearching && <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 animate-spin text-primary-600" />}
                </div>
              </div>
              {searchResults.length > 0 && (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {searchResults.map(recipe => (
                    <button
                      key={recipe.id}
                      onClick={() => addMeal(editingMeal.dayIndex, editingMeal.mealSlot, recipe.id)}
                      className="w-full text-left p-3 border border-neutral-200 rounded-lg hover:bg-neutral-50 transition-colors flex items-center gap-3"
                    >
                      <div className="w-12 h-12 rounded-lg bg-neutral-100 flex items-center justify-center flex-shrink-0">
                        <Utensils className="w-5 h-5 text-neutral-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-neutral-900 truncate">{recipe.recipe_name}</p>
                        <p className="text-sm text-neutral-500">{recipe.total_time_min} min · {recipe.servings} servings</p>
                      </div>
                    </button>
                  ))}
                </div>
              )}
              {searchQuery && searchResults.length === 0 && !isSearching && (
                <p className="text-center text-neutral-500 py-4">No recipes found matching "{searchQuery}"</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Create Plan Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="bg-white rounded-xl max-w-md w-full">
            <div className="p-4 border-b border-neutral-200 flex items-center justify-between">
              <h3 className="font-semibold text-neutral-900">Create New Meal Plan</h3>
              <button onClick={() => setShowCreateModal(false)} className="p-2 hover:bg-neutral-100 rounded-lg">
                <XCircle className="w-5 h-5" />
              </button>
            </div>
            <div className="p-4 space-y-4">
              <div>
                <label htmlFor="planName" className="label">Plan Name</label>
                <input
                  id="planName"
                  type="text"
                  value={newPlanName}
                  onChange={e => setNewPlanName(e.target.value)}
                  placeholder="e.g., Week of Jan 15"
                  className="input-field"
                  autoFocus
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="startDate" className="label">Start Date</label>
                  <input
                    id="startDate"
                    type="date"
                    value={startDate}
                    onChange={e => setStartDate(e.target.value)}
                    className="input-field"
                  />
                </div>
                <div>
                  <label htmlFor="endDate" className="label">End Date</label>
                  <input
                    id="endDate"
                    type="date"
                    value={endDate}
                    onChange={e => setEndDate(e.target.value)}
                    className="input-field"
                  />
                </div>
              </div>
              <div className="flex gap-2 pt-2">
                <button onClick={() => setShowCreateModal(false)} className="btn-secondary flex-1">Cancel</button>
                <button onClick={createPlan} disabled={isCreating} className="btn-primary flex-1">
                  {isCreating ? <Loader2 className="animate-spin w-4 h-4" /> : 'Create Plan'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Saved Plans List */}
      {mealPlans.length > 0 && (
        <div className="mt-8">
          <h2 className="text-xl font-bold text-neutral-900 mb-4">All Meal Plans</h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {mealPlans.map(plan => (
              <div key={plan.id} className={`card p-4 ${activePlan?.id === plan.id ? 'ring-2 ring-primary-500' : ''}`}>
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-neutral-900">{plan.name || 'Untitled Plan'}</h3>
                    <p className="text-sm text-neutral-500">
                      {new Date(plan.start_date).toLocaleDateString()} - {new Date(plan.end_date).toLocaleDateString()}
                    </p>
                  </div>
                  <span className={`badge ${plan.status === 'ACTIVE' ? 'badge-success' : plan.status === 'COMPLETED' ? 'badge-info' : 'badge-gray'}`}>
                    {plan.status}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-sm text-neutral-600 mb-3">
                  <span>{plan.items?.length || 0} meals</span>
                  <span>{plan.items?.filter(m => m.is_completed).length || 0} completed</span>
                </div>
                <div className="flex gap-2">
                  {activePlan?.id !== plan.id && (
                    <button
                      onClick={() => setActive(plan)}
                      className="btn-secondary flex-1 text-sm"
                    >
                      Activate
                    </button>
                  )}
                  <Link to={`/meal-plan/${plan.id}`} className="btn-ghost flex-1 text-sm">
                    View
                  </Link>
                  <button
                    onClick={() => deletePlan(plan.id)}
                    className="btn-ghost text-red-600 hover:text-red-700 p-2"
                    aria-label="Delete plan"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function MealCell({
  meal,
  dayIndex,
  mealSlot,
  onEdit,
  onRemove,
  onToggleComplete,
  onUpdateServings,
}: {
  meal: MealPlanItem | undefined;
  dayIndex: number;
  mealSlot: string;
  onEdit: (meal: MealPlanItem, dayIndex: number) => void;
  onRemove: (mealId: number) => void;
  onToggleComplete: (meal: MealPlanItem) => void;
  onUpdateServings: (mealId: number, servings: number) => void;
}) {
  if (!meal) {
    return (
      <button
        onClick={() => onEdit({ id: 0, meal_plan_id: 0, meal_slot: mealSlot as any, day_index: dayIndex, recipe_id: null, servings: 1, is_completed: false }, dayIndex)}
        className="w-full h-24 border-2 border-dashed border-neutral-200 rounded-lg flex flex-col items-center justify-center gap-2 text-neutral-400 hover:border-primary-300 hover:bg-primary-50 transition-colors"
      >
        <Plus className="w-6 h-6" />
        <span className="text-xs">Add meal</span>
      </button>
    );
  }

  if (!meal.recipe_id) {
    return (
      <button
        onClick={() => onEdit(meal, dayIndex)}
        className="w-full h-24 border-2 border-dashed border-neutral-200 rounded-lg flex flex-col items-center justify-center gap-2 text-neutral-400 hover:border-primary-300 hover:bg-primary-50 transition-colors"
      >
        <Plus className="w-6 h-6" />
        <span className="text-xs">Add recipe</span>
      </button>
    );
  }

  const recipe = meal.recipe!;

  return (
    <div className={`relative h-24 p-2 ${meal.is_completed ? 'bg-green-50 border-l-4 border-green-500' : 'bg-white'}`}>
      <Link to={`/recipes/${recipe.id}`} className="block h-full">
        <div className="flex items-start gap-2 h-full">
          <div className="w-16 h-16 rounded-lg bg-neutral-100 flex items-center justify-center flex-shrink-0 overflow-hidden">
            {recipe.image_url ? (
              <img src={recipe.image_url} alt={recipe.recipe_name} className="w-full h-full object-cover" />
            ) : (
              <Utensils className="w-5 h-5 text-neutral-400" />
            )}
          </div>
          <div className="flex-1 min-w-0 overflow-hidden">
            <p className="font-medium text-neutral-900 truncate">{recipe.recipe_name}</p>
            <p className="text-xs text-neutral-500 mt-1">{recipe.total_time_min} min · {recipe.servings} servings</p>
            <div className="flex items-center gap-2 mt-2">
              <input
                type="number"
                min="1"
                max="10"
                value={meal.servings}
                onChange={e => onUpdateServings(meal.id, parseInt(e.target.value) || 1)}
                className="w-16 px-1 py-0.5 text-xs border border-neutral-300 rounded text-center"
              />
              <span className="text-xs text-neutral-500">servings</span>
            </div>
          </div>
        </div>
      </Link>
      <div className="absolute top-1 right-1 flex gap-1 opacity-0 hover:opacity-100 transition-opacity">
        <button
          onClick={(e) => { e.preventDefault(); e.stopPropagation(); onToggleComplete(meal); }}
          className={`p-1.5 rounded ${meal.is_completed ? 'bg-green-100 text-green-600' : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'}`}
          aria-label={meal.is_completed ? 'Mark incomplete' : 'Mark complete'}
        >
          {meal.is_completed ? (
            <CheckCircle2 className="w-4 h-4 fill-current" />
          ) : (
            <CheckCircle2 className="w-4 h-4" />
          )}
        </button>
        <button
          onClick={(e) => { e.preventDefault(); e.stopPropagation(); onEdit(meal, dayIndex); }}
          className="p-1.5 rounded bg-neutral-100 text-neutral-600 hover:bg-neutral-200"
          aria-label="Replace meal"
        >
          <ArrowUpDown className="w-4 h-4" />
        </button>
        <button
          onClick={(e) => { e.preventDefault(); e.stopPropagation(); onRemove(meal.id); }}
          className="p-1.5 rounded bg-neutral-100 text-red-600 hover:bg-red-50"
          aria-label="Remove meal"
        >
          <XCircle className="w-4 h-4" />
        </button>
      </div>
      {meal.is_completed && (
        <div className="absolute inset-0 bg-green-500/10 flex items-center justify-center pointer-events-none">
          <CheckCircle2 className="w-8 h-8 text-green-500" />
        </div>
      )}
    </div>
  );
}

export default MealPlannerPage;