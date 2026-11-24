import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { MealPlan, MealPlanItem } from '../types';
import { mealPlanService, nutritionService } from '../services/api';
import { toast } from 'react-hot-toast';
import { Loader2, ArrowLeft, Calendar, Utensils, Download, Trash2, CheckCircle2, Sparkles, Printer } from 'lucide-react';
import { Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';

const MEAL_SLOTS = [
  { id: 'BREAKFAST', label: 'Breakfast', icon: '🌅' },
  { id: 'MORNING_SNACK', label: 'Morning Snack', icon: '🍎' },
  { id: 'LUNCH', label: 'Lunch', icon: '🍱' },
  { id: 'EVENING_SNACK', label: 'Evening Snack', icon: '☕' },
  { id: 'DINNER', label: 'Dinner', icon: '🍽️' },
];

const DAYS = [
  { index: 0, name: 'Monday' },
  { index: 1, name: 'Tuesday' },
  { index: 2, name: 'Wednesday' },
  { index: 3, name: 'Thursday' },
  { index: 4, name: 'Friday' },
  { index: 5, name: 'Saturday' },
  { index: 6, name: 'Sunday' },
];

export function MealPlanDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [mealPlan, setMealPlan] = useState<MealPlan | null>(null);
  const [nutrition, setNutrition] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isOptimizing, setIsOptimizing] = useState(false);

  useEffect(() => {
    if (id) {
      loadMealPlan();
    }
  }, [id]);

  const loadMealPlan = async () => {
    try {
      setIsLoading(true);
      const [planData, nutritionData] = await Promise.all([
        mealPlanService.getById(parseInt(id!)),
        nutritionService.getMealPlanNutrition(parseInt(id!)).catch(() => null),
      ]);
      setMealPlan(planData);
      setNutrition(nutritionData);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to load meal plan');
    } finally {
      setIsLoading(false);
    }
  };

  const optimizePlan = async () => {
    if (!mealPlan) return;
    setIsOptimizing(true);
    try {
      const optimized = await mealPlanService.optimize(mealPlan.id);
      setMealPlan(optimized);
      const nutritionData = await nutritionService.getMealPlanNutrition(mealPlan.id);
      setNutrition(nutritionData);
      toast.success('Meal plan optimized!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to optimize meal plan');
    } finally {
      setIsOptimizing(false);
    }
  };

  const deletePlan = async () => {
    if (!mealPlan || !confirm('Are you sure you want to delete this meal plan?')) return;
    try {
      await mealPlanService.delete(mealPlan.id);
      toast.success('Meal plan deleted');
      window.history.back();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to delete meal plan');
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

  if (!mealPlan) {
    return (
      <div className="page-container">
        <div className="max-w-2xl mx-auto text-center py-16">
          <h2 className="text-xl font-semibold text-neutral-900 mb-2">Meal Plan Not Found</h2>
          <p className="text-neutral-600 mb-6">The meal plan you're looking for doesn't exist.</p>
          <Link to="/meal-planner" className="btn-primary">Back to Meal Planner</Link>
        </div>
      </div>
    );
  }

  const getDayMeals = (dayIndex: number) => {
    return mealPlan.items?.filter(item => item.day_index === dayIndex) || [];
  };

  const getMealForSlot = (dayIndex: number, mealSlot: string) => {
    return mealPlan.items?.find(item => item.day_index === dayIndex && item.meal_slot === mealSlot);
  };

  const totalMeals = mealPlan.items?.filter(m => m.recipe_id).length || 0;
  const completedMeals = mealPlan.items?.filter(m => m.is_completed).length || 0;
  const completionRate = totalMeals > 0 ? Math.round((completedMeals / totalMeals) * 100) : 0;

  const macroData = nutrition?.total_nutrients ? [
    { name: 'Protein', value: nutrition.total_nutrients.protein_g || 0, color: '#ef4444', target: nutrition.targets?.protein_g },
    { name: 'Fat', value: nutrition.total_nutrients.fat_g || 0, color: '#f59e0b', target: nutrition.targets?.fat_g },
    { name: 'Carbs', value: nutrition.total_nutrients.carbohydrate_g || 0, color: '#3b82f6', target: nutrition.targets?.carbohydrate_g },
  ] : [];

  return (
    <div className="page-container">
      <Link to="/meal-planner" className="btn-ghost mb-6 inline-flex items-center gap-2">
        <ArrowLeft className="w-4 h-4" />
        Back to Planner
      </Link>

      {/* Header */}
      <div className="card p-6 mb-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold text-neutral-900">{mealPlan.name || 'Untitled Plan'}</h1>
              <span className={`badge ${mealPlan.status === 'ACTIVE' ? 'badge-success' : mealPlan.status === 'COMPLETED' ? 'badge-info' : 'badge-gray'}`}>
                {mealPlan.status}
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-4 text-sm text-neutral-600">
              <span className="flex items-center gap-1"><Calendar className="w-4 h-4" /> {new Date(mealPlan.start_date).toLocaleDateString()} - {new Date(mealPlan.end_date).toLocaleDateString()}</span>
              <span className="flex items-center gap-1"><Utensils className="w-4 h-4" /> {totalMeals} meals</span>
              <span className="flex items-center gap-1"><CheckCircle2 className="w-4 h-4" /> {completedMeals} completed ({completionRate}%)</span>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button onClick={optimizePlan} disabled={isOptimizing} className="btn-secondary">
              <Sparkles className="w-4 h-4 mr-2" />
              {isOptimizing ? 'Optimizing...' : 'Optimize'}
            </button>
            <button className="btn-secondary">
              <Download className="w-4 h-4 mr-2" />
              Export
            </button>
            <button className="btn-secondary">
              <Printer className="w-4 h-4 mr-2" />
              Print
            </button>
            <button onClick={deletePlan} className="btn-ghost text-red-600 hover:text-red-700">
              <Trash2 className="w-4 h-4 mr-2" />
              Delete
            </button>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Weekly View */}
        <div className="lg:col-span-2 space-y-6">
          {DAYS.map(day => (
            <DayColumn
              key={day.index}
              day={day}
              meals={getDayMeals(day.index)}
              getMealForSlot={getMealForSlot}
            />
          ))}
        </div>

        {/* Sidebar - Nutrition Summary */}
        <div className="space-y-6">
          {/* Completion */}
          <div className="card p-6">
            <h3 className="font-semibold text-neutral-900 mb-4">Weekly Progress</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-neutral-600">Meals Completed</span>
                  <span className="font-medium">{completedMeals}/{totalMeals}</span>
                </div>
                <div className="h-2 bg-neutral-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary-600 rounded-full transition-all duration-300"
                    style={{ width: `${completionRate}%` }}
                  />
                </div>
                <p className="text-xs text-neutral-500 mt-1">{completionRate}% complete</p>
              </div>
              <div className="grid grid-cols-3 gap-4 pt-4 border-t border-neutral-200">
                <div className="text-center">
                  <p className="text-2xl font-bold text-primary-600">{completedMeals}</p>
                  <p className="text-xs text-neutral-500">Completed</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-neutral-900">{totalMeals - completedMeals}</p>
                  <p className="text-xs text-neutral-500">Remaining</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">{completionRate}%</p>
                  <p className="text-xs text-neutral-500">Rate</p>
                </div>
              </div>
            </div>
          </div>

          {/* Nutrition Summary */}
          {nutrition && (
            <div className="card p-6">
              <h3 className="font-semibold text-neutral-900 mb-4">Weekly Nutrition Summary</h3>
              <div className="space-y-4">
                <NutritionStat
                  label="Total Calories"
                  value={nutrition.total_nutrients?.energy_kcal?.toFixed(0) || '—'}
                  unit="kcal"
                  target={nutrition.targets?.target_energy_kcal}
                />
                <NutritionStat
                  label="Protein"
                  value={nutrition.total_nutrients?.protein_g?.toFixed(1) || '—'}
                  unit="g"
                  target={nutrition.targets?.protein_g}
                />
                <NutritionStat
                  label="Fat"
                  value={nutrition.total_nutrients?.fat_g?.toFixed(1) || '—'}
                  unit="g"
                  target={nutrition.targets?.fat_g}
                />
                <NutritionStat
                  label="Carbohydrates"
                  value={nutrition.total_nutrients?.carbohydrate_g?.toFixed(1) || '—'}
                  unit="g"
                  target={nutrition.targets?.carbohydrate_g}
                />
                <NutritionStat
                  label="Fibre"
                  value={nutrition.total_nutrients?.fibre_g?.toFixed(1) || '—'}
                  unit="g"
                  target={nutrition.targets?.fibre_g}
                />
              </div>

              {macroData.length > 0 && (
                <div className="mt-6">
                  <h4 className="font-medium text-neutral-900 mb-3">Macro Distribution</h4>
                  <div className="h-48">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={macroData}
                          cx="50%"
                          cy="50%"
                          innerRadius={50}
                          outerRadius={80}
                          paddingAngle={2}
                          dataKey="value"
                          nameKey="name"
                          label={({ name, value }) => `${name}: ${value.toFixed(1)}g`}
                          labelLine={false}
                        >
                          {macroData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value: number) => [`${value.toFixed(1)}g`, 'Grams']} />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Daily Average */}
          {nutrition && (
            <div className="card p-6">
              <h3 className="font-semibold text-neutral-900 mb-4">Daily Average (Per Day)</h3>
              <div className="grid grid-cols-2 gap-4">
                <NutritionStat
                  label="Calories"
                  value={(nutrition.total_nutrients?.energy_kcal / 7).toFixed(0)}
                  unit="kcal"
                  target={nutrition.targets?.target_energy_kcal}
                />
                <NutritionStat
                  label="Protein"
                  value={(nutrition.total_nutrients?.protein_g / 7).toFixed(1)}
                  unit="g"
                  target={nutrition.targets?.protein_g}
                />
                <NutritionStat
                  label="Fat"
                  value={(nutrition.total_nutrients?.fat_g / 7).toFixed(1)}
                  unit="g"
                  target={nutrition.targets?.fat_g}
                />
                <NutritionStat
                  label="Carbs"
                  value={(nutrition.total_nutrients?.carbohydrate_g / 7).toFixed(1)}
                  unit="g"
                  target={nutrition.targets?.carbohydrate_g}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function DayColumn({ day, meals, getMealForSlot }: { day: { index: number; name: string }; meals: MealPlanItem[]; getMealForSlot: (dayIndex: number, mealSlot: string) => MealPlanItem | undefined }) {
  const dayMeals = meals;
  const completedCount = dayMeals.filter(m => m.is_completed).length;
  const totalCount = dayMeals.filter(m => m.recipe_id).length;

  return (
    <div className="card">
      <div className="p-4 border-b border-neutral-200 bg-neutral-50">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-neutral-900">{day.name}</h3>
          <span className="text-sm text-neutral-500">{completedCount}/{totalCount}</span>
        </div>
      </div>
      <div className="p-4 space-y-3">
        {MEAL_SLOTS.map(slot => {
          const meal = getMealForSlot(day.index, slot.id);
          return (
            <MealSlotCard key={slot.id} meal={meal} slot={slot} />
          );
        })}
      </div>
    </div>
  );
}

function MealSlotCard({ meal, slot }: { meal: MealPlanItem | undefined; slot: { id: string; label: string; icon: string } }) {
  if (!meal) {
    return (
      <div className="p-3 bg-neutral-50 rounded-lg border border-dashed border-neutral-200">
        <div className="flex items-center gap-2 text-neutral-400">
          <span>{slot.icon}</span>
          <span className="font-medium">{slot.label}</span>
          <span className="text-xs">No meal planned</span>
        </div>
      </div>
    );
  }

  if (!meal.recipe_id) {
    return (
      <div className="p-3 bg-neutral-50 rounded-lg border border-dashed border-neutral-200">
        <div className="flex items-center gap-2 text-neutral-400">
          <span>{slot.icon}</span>
          <span className="font-medium">{slot.label}</span>
          <span className="text-xs">Empty slot</span>
        </div>
      </div>
    );
  }

  const recipe = meal.recipe!;

  return (
    <Link to={`/recipes/${recipe.id}`} className="block">
      <div className={`p-3 rounded-lg transition-colors ${meal.is_completed ? 'bg-green-50 border border-green-200' : 'bg-white border border-neutral-200 hover:bg-neutral-50'}`}>
        <div className="flex items-start gap-3">
          <span className="text-xl">{slot.icon}</span>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <p className="font-medium text-neutral-900 truncate">{recipe.recipe_name}</p>
              {meal.is_completed && (
                <CheckCircle2 className="w-5 h-5 text-green-500 fill-current flex-shrink-0" />
              )}
            </div>
            <p className="text-xs text-neutral-500 mt-1">{recipe.total_time_min} min · {meal.servings} servings</p>
          </div>
        </div>
      </div>
    </Link>
  );
}

function NutritionStat({ label, value, unit, target }: { label: string; value: string; unit: string; target?: number }) {
  const percentage = target ? ((parseFloat(value) / target) * 100).toFixed(0) : null;
  return (
    <div className="p-3 bg-neutral-50 rounded-lg">
      <p className="text-xs text-neutral-500">{label}</p>
      <div className="flex items-baseline gap-1 mt-1">
        <p className="text-xl font-bold text-neutral-900">{value}</p>
        <p className="text-sm text-neutral-500">{unit}</p>
      </div>
      {percentage && (
        <p className="text-xs text-primary-600 mt-1">{percentage}% of target</p>
      )}
    </div>
  );
}

export default MealPlanDetailPage;