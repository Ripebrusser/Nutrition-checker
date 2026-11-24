import React, { createContext, useContext, useState, useEffect } from 'react'
import type { UserProfile } from '../types'

export interface AuthUser {
  id: number
  email: string
  full_name: string
  role: string
}

interface AuthContextType {
  user: AuthUser | null
  profile: UserProfile | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: { email: string; password: string; full_name: string }) => Promise<void>
  logout: () => Promise<void>
  updateProfile: (data: Partial<UserProfile>) => Promise<void>
  refreshProfile: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const TOKEN_KEY = 'access_token'

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem(TOKEN_KEY)
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function readError(response: Response, fallback: string): Promise<string> {
  try {
    const body = await response.json()
    if (typeof body?.detail === 'string') return body.detail
    if (Array.isArray(body?.detail) && body.detail[0]?.msg) return body.detail[0].msg
  } catch {
    /* non-JSON error body */
  }
  return fallback
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const isAuthenticated = user !== null

  const loadProfile = async () => {
    const response = await fetch('/api/profile', { headers: authHeaders() })
    if (response.ok) {
      setProfile(await response.json())
    }
    return response.ok
  }

  // Restore the session from the stored token on first load.
  useEffect(() => {
    let cancelled = false

    const initAuth = async () => {
      const token = localStorage.getItem(TOKEN_KEY)
      if (!token) {
        if (!cancelled) setIsLoading(false)
        return
      }
      try {
        const response = await fetch('/api/auth/me', { headers: authHeaders() })
        if (!response.ok) {
          localStorage.removeItem(TOKEN_KEY)
          return
        }
        const data = await response.json()
        if (cancelled) return
        setUser({
          id: data.id,
          email: data.email,
          full_name: data.full_name,
          role: data.role,
        })
        await loadProfile()
      } catch {
        localStorage.removeItem(TOKEN_KEY)
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }

    initAuth()
    return () => {
      cancelled = true
    }
  }, [])

  const login = async (email: string, password: string) => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    if (!response.ok) {
      throw new Error(await readError(response, 'Login failed'))
    }
    const data = await response.json()
    localStorage.setItem(TOKEN_KEY, data.access_token)
    setUser({
      id: data.user.id,
      email: data.user.email,
      full_name: data.user.full_name,
      role: data.user.role,
    })
    await loadProfile()
  }

  const register = async (data: { email: string; password: string; full_name: string }) => {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!response.ok) {
      throw new Error(await readError(response, 'Registration failed'))
    }
    const result = await response.json()
    localStorage.setItem(TOKEN_KEY, result.access_token)
    setUser({
      id: result.user.id,
      email: result.user.email,
      full_name: result.user.full_name,
      role: result.user.role,
    })
    await loadProfile()
  }

  const logout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST', headers: authHeaders() })
    } catch {
      /* the token is cleared locally even if the call fails */
    }
    localStorage.removeItem(TOKEN_KEY)
    setUser(null)
    setProfile(null)
  }

  const updateProfile = async (data: Partial<UserProfile>) => {
    const response = await fetch('/api/profile', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(data),
    })
    if (!response.ok) {
      throw new Error(await readError(response, 'Failed to update profile'))
    }
    setProfile(await response.json())
  }

  const refreshProfile = async () => {
    await loadProfile()
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        isAuthenticated,
        isLoading,
        login,
        register,
        logout,
        updateProfile,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
