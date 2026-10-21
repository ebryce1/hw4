import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { useAuth } from './AuthContext'
import { addFavorite, fetchFavorites, removeFavorite, type Product } from './api'

/**
 * Problem 9: "favorites" (save an item to check out later without committing to it now).
 * Login-gated, same choice as chat history (Problem 8) — persisting only for a signed-in account
 * is what lets the list follow a shopper to a different device, and keeps this app's rule
 * consistent: nothing is saved server-side for a guest.
 */
interface FavoritesState {
  favorites: Product[]
  isFavorite: (productId: string) => boolean
  toggleFavorite: (product: Product) => Promise<void>
}

const FavoritesContext = createContext<FavoritesState | null>(null)

export function FavoritesProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  const [favorites, setFavorites] = useState<Product[]>([])

  useEffect(() => {
    if (!user) {
      setFavorites([])
      return
    }
    let cancelled = false
    fetchFavorites(user.id)
      .then((list) => {
        if (!cancelled) setFavorites(list)
      })
      .catch(() => {
        if (!cancelled) setFavorites([])
      })
    return () => {
      cancelled = true
    }
  }, [user?.id])

  const isFavorite = (productId: string) => favorites.some((f) => f.product_id === productId)

  async function toggleFavorite(product: Product) {
    if (!user) return // caller (FavoriteButton) sends a guest to /login instead of calling this
    const already = isFavorite(product.product_id)
    // Optimistic update so the heart responds instantly; revert if the request fails.
    setFavorites((prev) =>
      already ? prev.filter((f) => f.product_id !== product.product_id) : [product, ...prev],
    )
    try {
      if (already) await removeFavorite(user.id, product.product_id)
      else await addFavorite(user.id, product.product_id)
    } catch {
      setFavorites((prev) =>
        already
          ? [product, ...prev]
          : prev.filter((f) => f.product_id !== product.product_id),
      )
    }
  }

  return (
    <FavoritesContext.Provider value={{ favorites, isFavorite, toggleFavorite }}>
      {children}
    </FavoritesContext.Provider>
  )
}

export function useFavorites() {
  const ctx = useContext(FavoritesContext)
  if (!ctx) throw new Error('useFavorites must be used within FavoritesProvider')
  return ctx
}
