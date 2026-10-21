import { Link } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import { useFavorites } from '../FavoritesContext'
import ProductCard from '../components/ProductCard'

export default function Favorites() {
  const { user } = useAuth()
  const { favorites } = useFavorites()

  if (!user) {
    return (
      <section className="section">
        <h1>Favorites</h1>
        <p className="notice">
          <Link to="/login">Log in</Link> to save items here and find them again later.
        </p>
      </section>
    )
  }

  return (
    <section className="section">
      <h1>Favorites</h1>
      {favorites.length === 0 ? (
        <p className="notice">
          Nothing saved yet. Tap the heart on any product to keep it here for later —{' '}
          <Link to="/products">browse products</Link>.
        </p>
      ) : (
        <div className="grid">
          {favorites.map((p) => (
            <ProductCard key={p.product_id} product={p} />
          ))}
        </div>
      )}
    </section>
  )
}
