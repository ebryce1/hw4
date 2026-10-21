import { createContext, useContext, useMemo, useState, type ReactNode } from 'react'
import type { User } from './api'

interface AuthState {
  user: User | null
  setUser: (user: User | null) => void
}

const AuthContext = createContext<AuthState | null>(null)

const STORAGE_KEY = 'campus_customs_user'

function readStoredUser(): User | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as User) : null
  } catch {
    return null
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUserState] = useState<User | null>(readStoredUser)

  const setUser = (next: User | null) => {
    setUserState(next)
    try {
      if (next) localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
      else localStorage.removeItem(STORAGE_KEY)
    } catch {
      // Private browsing or blocked storage: the session just won't persist across reloads.
    }
  }

  const value = useMemo(() => ({ user, setUser }), [user])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
