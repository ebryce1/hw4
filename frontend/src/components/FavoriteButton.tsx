import type { MouseEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import { useFavorites } from '../FavoritesContext'
import type { Product } from '../api'

/** A heart toggle for saving a product to favorites. Sends a guest to log in instead of
 * failing silently, so "favorite this" always does something sensible either way. */
export default function FavoriteButton({
  product,
  size = 'normal',
  className = '',
}: {
  product: Product
  size?: 'normal' | 'small'
  className?: string
}) {
  const { user } = useAuth()
  const { isFavorite, toggleFavorite } = useFavorites()
  const navigate = useNavigate()
  const active = user ? isFavorite(product.product_id) : false

  function onClick(e: MouseEvent) {
    e.preventDefault() // these sit inside a product card's own <Link>
    e.stopPropagation()
    if (!user) {
      navigate('/login')
      return
    }
    toggleFavorite(product)
  }

  return (
    <button
      type="button"
      className={`favorite-btn favorite-btn--${size}${active ? ' favorite-btn--active' : ''}${className ? ` ${className}` : ''}`}
      onClick={onClick}
      aria-pressed={active}
      aria-label={active ? 'Remove from favorites' : 'Save to favorites'}
      title={user ? (active ? 'Remove from favorites' : 'Save to favorites') : 'Log in to save favorites'}
    >
      {active ? '♥' : '♡'}
    </button>
  )
}
