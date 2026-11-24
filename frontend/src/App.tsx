import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/Layout'
import { HomePage } from './pages/HomePage'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { DashboardPage } from './pages/DashboardPage'
import { ProfilePage } from './pages/ProfilePage'
import { NutritionTargetsPage } from './pages/NutritionTargetsPage'
import { RecipesPage } from './pages/RecipesPage'
import { RecipeDetailPage } from './pages/RecipeDetailPage'
import { RecommendationsPage } from './pages/RecommendationsPage'
import { MealPlannerPage } from './pages/MealPlannerPage'
import { MealPlanDetailPage } from './pages/MealPlanDetailPage'
import { NutritionBreakdownPage } from './pages/NutritionBreakdownPage'
import { PreferencesPage } from './pages/PreferencesPage'
import { SavedRecipesPage } from './pages/SavedRecipesPage'
import { HistoryPage } from './pages/HistoryPage'
import { useAuth } from './contexts/AuthContext'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-primary-600 border-t-transparent" />
      </div>
    )
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/nutrition-targets" element={<NutritionTargetsPage />} />
        <Route path="/recipes" element={<RecipesPage />} />
        <Route path="/recipes/:id" element={<RecipeDetailPage />} />
        <Route path="/recommendations" element={<RecommendationsPage />} />
        <Route path="/meal-planner" element={<MealPlannerPage />} />
        <Route path="/meal-plan/:id" element={<MealPlanDetailPage />} />
        <Route path="/nutrition-breakdown" element={<NutritionBreakdownPage />} />
        <Route path="/saved-recipes" element={<SavedRecipesPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/preferences" element={<PreferencesPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
