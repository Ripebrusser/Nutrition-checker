import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Recipe } from '../types'
import { Calendar, Clock, Utensils, Sparkles } from 'lucide-react'

interface PlanItem {
  id: number
  meal_slot: string
  day_index: number
  recipe_id: number | null
  servings: number
  recipe?: Recipe | null
  is_completed: boolean
}

interface MealPlanWithItems {
  id: number
  name: string | null
  start_date: string
  end_date: string
  status: string
  items: PlanItem[]
  total_nutrients?: {
    energy_kcal?: number | null
    protein_g?: number | null
    carbohydrate_g?: number | null
    fat_g?: number | null
  }
}

export function DashboardPage() {
  const { user, profile } = useAuth()
  const [activePlan, setActivePlan] = useState<MealPlanWithItems | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchActivePlan = async () => {
    try {
      const response = await fetch('/api/meal-plans/active', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setActivePlan(data)
      } else if (response.status !== 404) {
        setError('Failed to load meal plan')
      }
    } catch {
      setError('Failed to load meal plan. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchActivePlan()
  }, [])

  if (loading) {
    return (
      <div className="page-container">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-4 border-primary-600 border-t-transparent" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="bg-red-50 border border-red-200 rounded-xl p-6">
          <p className="text-red-700">{error}</p>
          <button onClick={() => window.location.reload()} className="btn-primary mt-4">
            Retry
          </button>
        </div>
      </div>
    )
  }

  // day_index is 0=Monday in the backend
  const todayIndex = new Date().getDay()
  const dayIndex = todayIndex === 0 ? 6 : todayIndex - 1
  const todayMeals = activePlan?.items?.filter(item => item.day_index === dayIndex) || []
  const completedMeals = activePlan?.items?.filter(item => item.is_completed).length || 0
  const totalMeals = activePlan?.items?.filter(item => item.recipe_id).length || 0

  return (
    <div className="page-container">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-neutral-900">Dashboard</h1>
        <p className="text-neutral-600 mt-1">
          Welcome back, {user?.full_name?.split(' ')[0] || 'there'}! Here's your nutrition overview.
        </p>
      </div>

      {!profile?.height_cm && (
        <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4">
          <p className="text-sm text-amber-800">
            Your profile is incomplete. Add height, weight, age and activity level to calculate nutrition targets.
          </p>
          <Link to="/profile" className="btn-primary text-sm whitespace-nowrap">
            Complete profile
          </Link>
        </div>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          icon="🎯"
          label="Daily Calories"
          value={`${activePlan?.total_nutrients?.energy_kcal?.toFixed(0) || '—'} kcal`}
          subtitle="Plan total"
        />
        <StatCard
          icon="🥩"
          label="Protein"
          value={activePlan?.total_nutrients?.protein_g != null ? `${Math.round(activePlan.total_nutrients.protein_g)}g` : '—'}
          subtitle="Plan total"
        />
        <StatCard
          icon="🍞"
          label="Carbs"
          value={activePlan?.total_nutrients?.carbohydrate_g != null ? `${Math.round(activePlan.total_nutrients.carbohydrate_g)}g` : '—'}
          subtitle="Plan total"
        />
        <StatCard
          icon="🥑"
          label="Fat"
          value={activePlan?.total_nutrients?.fat_g != null ? `${Math.round(activePlan.total_nutrients.fat_g)}g` : '—'}
          subtitle="Plan total"
        />
      </div>

      {/* Today's Meals */}
      <section className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-neutral-900">Today's Meals</h2>
            <p className="text-neutral-600 mt-1">
              {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
            </p>
          </div>
          <Link to="/meal-planner" className="btn-ghost text-sm">
            View Full Plan
          </Link>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[
            { slot: 'BREAKFAST', label: 'Breakfast', icon: '🌅' },
            { slot: 'LUNCH', label: 'Lunch', icon: '🍱' },
            { slot: 'DINNER', label: 'Dinner', icon: '🍽️' },
            { slot: 'EVENING_SNACK', label: 'Snack', icon: '🍎' },
          ].map(({ slot, label, icon }) => {
            const meal = todayMeals.find(item => item.meal_slot === slot)
            const recipe = meal?.recipe

            return (
              <div key={slot} className="meal-slot">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{icon}</span>
                    <span className="font-semibold text-neutral-900">{label}</span>
                  </div>
                  {meal?.is_completed && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      ✓ Completed
                    </span>
                  )}
                </div>
                {recipe ? (
                  <Link
                    to={`/recipes/${recipe.id}`}
                    className="block mt-2 p-3 bg-neutral-50 rounded-lg hover:bg-neutral-100 transition-colors"
                  >
                    <p className="font-medium text-neutral-900 truncate">{recipe.recipe_name}</p>
                    <p className="text-sm text-neutral-500 mt-1">
                      {recipe.total_time_min} min · {recipe.servings} servings
                    </p>
                  </Link>
                ) : (
                  <Link to="/meal-planner" className="block w-full mt-2 btn-secondary text-sm py-2 text-center">
                    Add Meal
                  </Link>
                )}
              </div>
            )
          })}
        </div>
      </section>

      {/* Weekly Overview */}
      <section className="mb-8">
        <h2 className="text-xl font-bold text-neutral-900 mb-4">Weekly Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatCard
            label="Meals Completed"
            value={`${completedMeals}/${totalMeals}`}
            icon="✅"
            trend={`${totalMeals > 0 ? Math.round((completedMeals / totalMeals) * 100) : 0}%`}
          />
          <StatCard
            label="Cuisines This Week"
            value={`${new Set(activePlan?.items?.map(i => i.recipe?.cuisine).filter(Boolean)).size}`}
            icon="🌍"
          />
          <StatCard
            label="Unique Recipes"
            value={`${new Set(activePlan?.items?.map(i => i.recipe_id).filter(Boolean)).size}`}
            icon="🍽️"
          />
        </div>
      </section>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link to="/meal-planner" className="card-hover card p-6 text-center">
          <div className="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center mx-auto mb-3">
            <Calendar className="w-8 h-8 text-primary-600" />
          </div>
          <h3 className="font-semibold text-neutral-900 mb-1">Create Meal Plan</h3>
          <p className="text-neutral-600 text-sm">Build your weekly plan</p>
        </Link>
        <Link to="/recipes" className="card-hover card p-6 text-center">
          <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center mx-auto mb-3">
            <Utensils className="w-8 h-8 text-green-600" />
          </div>
          <h3 className="font-semibold text-neutral-900 mb-1">Browse Recipes</h3>
          <p className="text-neutral-600 text-sm">6,865+ recipes</p>
        </Link>
        <Link to="/recommendations" className="card-hover card p-6 text-center">
          <div className="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center mx-auto mb-3">
            <Sparkles className="w-8 h-8 text-purple-600" />
          </div>
          <h3 className="font-semibold text-neutral-900 mb-1">Recommendations</h3>
          <p className="text-neutral-600 text-sm">Content-based suggestions</p>
        </Link>
        <Link to="/history" className="card-hover card p-6 text-center">
          <div className="w-12 h-12 rounded-xl bg-orange-100 flex items-center justify-center mx-auto mb-3">
            <Clock className="w-8 h-8 text-orange-600" />
          </div>
          <h3 className="font-semibold text-neutral-900 mb-1">Meal History</h3>
          <p className="text-neutral-600 text-sm">Track your progress</p>
        </Link>
      </div>
    </div>
  )
}

function StatCard({ label, value, icon, trend, subtitle }: { label: string; value: string; icon: string; trend?: string; subtitle?: string }) {
  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl">{icon}</span>
        {trend && <span className="text-xs font-medium text-green-600 bg-green-50 px-2 py-0.5 rounded">{trend}</span>}
      </div>
      <p className="text-2xl font-bold text-neutral-900">{value}</p>
      <p className="text-sm text-neutral-500 mt-1">{label}</p>
      {subtitle && <p className="text-xs text-neutral-400 mt-0.5">{subtitle}</p>}
    </div>
  )
}

export default DashboardPage
