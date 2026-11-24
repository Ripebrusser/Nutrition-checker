import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { MealHistory } from '../types';
import { historyService } from '../services/api';
import { toast } from 'react-hot-toast';
import { Loader2, Clock, Utensils, ChevronLeft, ChevronRight, Download, Filter, X } from 'lucide-react';
import { format, startOfWeek, endOfWeek, addWeeks, isSameDay, parseISO } from 'date-fns';

export function HistoryPage() {
  const [history, setHistory] = useState<MealHistory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentWeek, setCurrentWeek] = useState(new Date());
  const [viewMode, setViewMode] = useState<'week' | 'month' | 'all'>('week');
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
  });
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadHistory();
  }, [currentWeek, viewMode, filters]);

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      let data: MealHistory[];
      if (viewMode === 'week') {
        const start = startOfWeek(currentWeek, { weekStartsOn: 1 });
        const end = endOfWeek(currentWeek, { weekStartsOn: 1 });
        data = await historyService.getByDateRange(
          start.toISOString().split('T')[0],
          end.toISOString().split('T')[0]
        );
      } else if (viewMode === 'month') {
        const start = new Date(currentWeek.getFullYear(), currentWeek.getMonth(), 1);
        const end = new Date(currentWeek.getFullYear(), currentWeek.getMonth() + 1, 0);
        data = await historyService.getByDateRange(
          start.toISOString().split('T')[0],
          end.toISOString().split('T')[0]
        );
      } else {
        data = await historyService.getAll(500);
      }
      setHistory(data);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to load history');
    } finally {
      setIsLoading(false);
    }
  };

  const navigateWeek = (direction: number) => {
    if (viewMode === 'week') {
      setCurrentWeek(addWeeks(currentWeek, direction));
    } else if (viewMode === 'month') {
      setCurrentWeek(new Date(currentWeek.getFullYear(), currentWeek.getMonth() + direction, 1));
    }
  };

  const getPeriodLabel = () => {
    if (viewMode === 'week') {
      const start = startOfWeek(currentWeek, { weekStartsOn: 1 });
      const end = endOfWeek(currentWeek, { weekStartsOn: 1 });
      return `${format(start, 'MMM d')} - ${format(end, 'MMM d, yyyy')}`;
    } else if (viewMode === 'month') {
      return format(currentWeek, 'MMMM yyyy');
    }
    return 'All Time';
  };

  const groupedHistory = history.reduce((acc, entry) => {
    const date = entry.consumed_at.split('T')[0];
    if (!acc[date]) acc[date] = [];
    acc[date].push(entry);
    return acc;
  }, {} as Record<string, MealHistory[]>);

  const sortedDates = Object.keys(groupedHistory).sort().reverse();

  const getMealSlotIcon = (slot: string) => {
    switch (slot) {
      case 'BREAKFAST': return '🌅';
      case 'MORNING_SNACK': return '🍎';
      case 'LUNCH': return '🍱';
      case 'EVENING_SNACK': return '☕';
      case 'DINNER': return '🍽️';
      default: return '🍽️';
    }
  };

  const calculateDayNutrition = (entries: MealHistory[]) => {
    return entries.reduce((acc, entry) => {
      if (entry.recipe?.nutrition_per_serving) {
        const n = entry.recipe.nutrition_per_serving;
        const servings = entry.servings;
        acc.energy += (n.energy_kcal || 0) * servings;
        acc.protein += (n.protein_g || 0) * servings;
        acc.fat += (n.fat_g || 0) * servings;
        acc.carbs += (n.carbohydrate_g || 0) * servings;
        acc.fibre += (n.fibre_g || 0) * servings;
      }
      return acc;
    }, { energy: 0, protein: 0, fat: 0, carbs: 0, fibre: 0 });
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

  const totalNutrition = history.reduce((acc, entry) => {
    if (entry.recipe?.nutrition_per_serving) {
      const n = entry.recipe.nutrition_per_serving;
      const s = entry.servings;
      acc.energy += (n.energy_kcal || 0) * s;
      acc.protein += (n.protein_g || 0) * s;
      acc.fat += (n.fat_g || 0) * s;
      acc.carbs += (n.carbohydrate_g || 0) * s;
      acc.fibre += (n.fibre_g || 0) * s;
    }
    return acc;
  }, { energy: 0, protein: 0, fat: 0, carbs: 0, fibre: 0 });

  const daysWithEntries = sortedDates.length;
  const hasAnyNutrition = history.some(entry => entry.recipe?.nutrition_per_serving);
  const avgPerDay = daysWithEntries > 0 ? {
    energy: totalNutrition.energy / daysWithEntries,
    protein: totalNutrition.protein / daysWithEntries,
    fat: totalNutrition.fat / daysWithEntries,
    carbs: totalNutrition.carbs / daysWithEntries,
  } : { energy: 0, protein: 0, fat: 0, carbs: 0 };

  return (
    <div className="page-container">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Meal History</h1>
          <p className="text-neutral-600 mt-1">Track your completed meals and nutrition intake</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 bg-neutral-50 rounded-lg p-1">
            {['week', 'month', 'all'].map(mode => (
              <button
                key={mode}
                onClick={() => setViewMode(mode as any)}
                className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                  viewMode === mode
                    ? 'bg-white text-primary-700 shadow-sm'
                    : 'text-neutral-600 hover:text-neutral-900'
                }`}
              >
                {mode.charAt(0).toUpperCase() + mode.slice(1)}
              </button>
            ))}
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn-secondary flex items-center gap-2"
          >
            <Filter className="w-4 h-4" />
            Filters
          </button>
          <button className="btn-secondary">
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Date Navigator */}
      <div className="card p-4 mb-6">
        <div className="flex items-center justify-between">
          <button onClick={() => navigateWeek(-1)} className="btn-ghost p-2" aria-label="Previous period">
            <ChevronLeft className="w-5 h-5" />
          </button>
          <h2 className="text-lg font-semibold text-neutral-900">{getPeriodLabel()}</h2>
          <button onClick={() => navigateWeek(1)} className="btn-ghost p-2" aria-label="Next period">
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
        {viewMode !== 'all' && (
          <div className="mt-4 flex justify-center gap-1">
            {Array.from({ length: 7 }, (_, i) => {
              const date = startOfWeek(currentWeek, { weekStartsOn: 1 });
              date.setDate(date.getDate() + i);
              const hasEntries = groupedHistory[date.toISOString().split('T')[0]];
              return (
                <div key={i} className={`w-10 h-10 rounded-lg flex flex-col items-center justify-center text-xs transition-colors ${hasEntries ? 'bg-primary-50 text-primary-700' : 'text-neutral-400'}`}>
                  <span className="font-medium">{format(date, 'EEE')}</span>
                  <span>{format(date, 'd')}</span>
                  {hasEntries && <span className="w-1.5 h-1.5 rounded-full bg-primary-500 mt-1" />}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="card p-4 mb-6">
          <div className="flex flex-wrap gap-4 items-end">
            <div>
              <label className="label">Start Date</label>
              <input
                type="date"
                value={filters.startDate}
                onChange={e => setFilters(prev => ({ ...prev, startDate: e.target.value }))}
                className="input-field"
              />
            </div>
            <div>
              <label className="label">End Date</label>
              <input
                type="date"
                value={filters.endDate}
                onChange={e => setFilters(prev => ({ ...prev, endDate: e.target.value }))}
                className="input-field"
              />
            </div>
            {(filters.startDate || filters.endDate) && (
              <button onClick={() => setFilters({ startDate: '', endDate: '' })} className="btn-ghost text-sm text-red-600">
                <X className="w-4 h-4 mr-1" />
                Clear
              </button>
            )}
          </div>
        </div>
      )}

      {/* History List */}
      {history.length === 0 ? (
        <div className="text-center py-16">
          <Utensils className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-neutral-900 mb-2">No Meal History</h3>
          <p className="text-neutral-500 mb-4">
            {viewMode === 'all' ? 'You haven\'t logged any meals yet.' : 'No meals logged for this period.'}
          </p>
          <Link to="/meal-planner" className="btn-primary">
            <Utensils className="w-4 h-4 mr-2" />
            Plan Meals
          </Link>
        </div>
      ) : (
        <div className="space-y-6">
          {sortedDates.map(dateStr => {
            const entries = groupedHistory[dateStr];
            const nutrition = calculateDayNutrition(entries);
            // Nutrition is only summarised when at least one meal actually has it;
            // otherwise we say so instead of printing 0 kcal.
            const hasNutrition = entries.some(e => e.recipe?.nutrition_per_serving);
            const date = parseISO(dateStr);
            const isToday = isSameDay(date, new Date());

            return (
              <div key={dateStr} className="card overflow-hidden">
                <div className={`p-4 ${isToday ? 'bg-primary-50 border-l-4 border-primary-500' : 'bg-white'}`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-2xl ${isToday ? 'bg-primary-100' : 'bg-neutral-100'}`}>
                        {isToday ? '📅' : format(date, 'EEE')}
                      </div>
                      <div>
                        <p className="font-semibold text-neutral-900">{isToday ? 'Today' : format(date, 'EEEE, MMMM d, yyyy')}</p>
                        <p className="text-sm text-neutral-500">{entries.length} meal{entries.length !== 1 ? 's' : ''} logged</p>
                      </div>
                    </div>
                    <div className="text-right">
                      {hasNutrition ? (
                        <>
                          <p className="text-sm text-neutral-500">{nutrition.energy.toFixed(0)} kcal total</p>
                          <p className="text-xs text-neutral-400">P: {nutrition.protein.toFixed(1)}g F: {nutrition.fat.toFixed(1)}g C: {nutrition.carbs.toFixed(1)}g</p>
                        </>
                      ) : (
                        <p className="text-xs text-neutral-400">Nutrition unavailable</p>
                      )}
                    </div>
                  </div>
                </div>
                <div className="divide-y divide-neutral-100">
                  {entries.map(entry => (
                    <div key={entry.id} className="p-4 hover:bg-neutral-50">
                      <div className="flex items-start gap-4">
                        <span className="text-2xl">{getMealSlotIcon(entry.meal_slot)}</span>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <Link
                              to={entry.recipe_id ? `/recipes/${entry.recipe_id}` : '#'}
                              className="font-medium text-neutral-900 hover:text-primary-600 truncate pr-2"
                            >
                              {entry.recipe?.recipe_name || 'Unknown Recipe'}
                            </Link>
                            <span className="text-sm text-neutral-500 flex items-center gap-1">
                              <Clock className="w-3.5 h-3.5" />
                              {format(parseISO(entry.consumed_at), 'h:mm a')}
                            </span>
                          </div>
                          {entry.recipe && (
                            <p className="text-sm text-neutral-500 mt-1">
                              {entry.recipe.cuisine} · {entry.recipe.total_time_min} min · {entry.servings} serving{entry.servings !== 1 ? 's' : ''}
                            </p>
                          )}
                          {entry.recipe?.nutrition_per_serving && (
                            <div className="mt-2 flex flex-wrap gap-3 text-xs text-neutral-500">
                              <span>🔥 {(entry.recipe.nutrition_per_serving.energy_kcal || 0) * entry.servings} kcal</span>
                              <span>🥩 {(entry.recipe.nutrition_per_serving.protein_g || 0) * entry.servings} g protein</span>
                              <span>🥑 {(entry.recipe.nutrition_per_serving.fat_g || 0) * entry.servings} g fat</span>
                              <span>🍞 {(entry.recipe.nutrition_per_serving.carbohydrate_g || 0) * entry.servings} g carbs</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Summary Stats */}
      {history.length > 0 && (
        <div className="mt-8 card p-6">
          <h3 className="font-semibold text-neutral-900 mb-4">Period Summary</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <StatCard label="Total Meals" value={history.length} icon="🍽️" />
            <StatCard label="Days Tracked" value={daysWithEntries} icon="📅" />
            <StatCard label="Avg Calories/Day" value={hasAnyNutrition ? avgPerDay.energy.toFixed(0) : '—'} unit={hasAnyNutrition ? 'kcal' : ''} icon="🔥" />
            <StatCard label="Avg Protein/Day" value={hasAnyNutrition ? avgPerDay.protein.toFixed(1) : '—'} unit={hasAnyNutrition ? 'g' : ''} icon="🥩" />
          </div>

          {hasAnyNutrition ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard label="Total Protein" value={totalNutrition.protein.toFixed(1)} unit="g" icon="🥩" />
              <StatCard label="Total Fat" value={totalNutrition.fat.toFixed(1)} unit="g" icon="🥑" />
              <StatCard label="Total Carbs" value={totalNutrition.carbs.toFixed(1)} unit="g" icon="🍞" />
              <StatCard label="Total Fibre" value={totalNutrition.fibre.toFixed(1)} unit="g" icon="🌿" />
            </div>
          ) : (
            <p className="text-sm text-neutral-500">
              Nutrient totals are unavailable: none of these recipes has an approved IFCT ingredient
              mapping, so no energy or macronutrient values can be reported without fabricating them.
            </p>
          )}
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, unit = '', icon }: { label: string; value: string | number; unit?: string; icon: string }) {
  return (
    <div className="p-4 bg-neutral-50 rounded-lg text-center">
      <div className="text-2xl mb-1">{icon}</div>
      <p className="text-2xl font-bold text-neutral-900">{value}{unit && <span className="text-lg font-normal text-neutral-500 ml-1">{unit}</span>}</p>
      <p className="text-sm text-neutral-500 mt-1">{label}</p>
    </div>
  );
}

export default HistoryPage;