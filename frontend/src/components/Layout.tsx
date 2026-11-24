import { useState } from 'react'
import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import {
  LayoutDashboard,
  User,
  Target,
  Utensils,
  Sparkles,
  Calendar,
  FlaskConical,
  BookOpen,
  Clock,
  Settings,
  LogOut,
  Menu,
  X,
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Profile', href: '/profile', icon: User },
  { name: 'Nutrition Targets', href: '/nutrition-targets', icon: Target },
  { name: 'Discover Recipes', href: '/recipes', icon: Utensils },
  { name: 'Recommendations', href: '/recommendations', icon: Sparkles },
  { name: 'Meal Planner', href: '/meal-planner', icon: Calendar },
  { name: 'Nutrition Analysis', href: '/nutrition-breakdown', icon: FlaskConical },
  { name: 'Saved Recipes', href: '/saved-recipes', icon: BookOpen },
  { name: 'Meal History', href: '/history', icon: Clock },
  { name: 'Preferences', href: '/preferences', icon: Settings },
]

export function Layout() {
  const { user, profile, logout } = useAuth()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
      isActive
        ? 'bg-primary-50 text-primary-700'
        : 'text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900'
    }`

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Mobile menu button */}
      <button
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-white shadow-lg"
        onClick={() => setSidebarOpen(true)}
        aria-label="Open menu"
      >
        <Menu className="w-6 h-6" />
      </button>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-neutral-200 transform transition-transform duration-200 ease-in-out ${
          sidebarOpen ? 'translate-x-0' : 'max-lg:-translate-x-full'
        }`}
        aria-label="Sidebar"
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-4 border-b border-neutral-200">
            <NavLink to="/dashboard" className="text-lg font-bold text-primary-600">
              🥗 Nutrition Planner
            </NavLink>
            <button
              className="lg:hidden p-2 rounded-lg hover:bg-neutral-100"
              onClick={() => setSidebarOpen(false)}
              aria-label="Close sidebar"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-4 space-y-1" aria-label="Main navigation">
            {navigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                className={navLinkClass}
                aria-current={location.pathname === item.href ? 'page' : undefined}
                onClick={() => setSidebarOpen(false)}
              >
                <item.icon className="w-5 h-5" aria-hidden="true" />
                <span>{item.name}</span>
              </NavLink>
            ))}
          </nav>

          {/* User card */}
          <div className="p-4 border-t border-neutral-200">
            <div className="flex items-center gap-3 px-1 mb-3">
              <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                <span className="text-primary-700 font-medium">
                  {user?.full_name?.charAt(0) || user?.email?.charAt(0)?.toUpperCase() || 'U'}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-neutral-900 truncate">
                  {user?.full_name || 'User'}
                </p>
                <p className="text-xs text-neutral-500 truncate">{user?.email}</p>
              </div>
            </div>
            {!profile?.height_cm && (
              <NavLink
                to="/profile"
                className="block text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-2 py-1.5 mb-2"
              >
                Profile incomplete — add your metrics
              </NavLink>
            )}
            <button
              onClick={logout}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
            >
              <LogOut className="w-4 h-4" aria-hidden="true" />
              Log out
            </button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="lg:pl-64 flex-1 min-h-screen">
        <div className="pt-16 lg:pt-6 pb-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
