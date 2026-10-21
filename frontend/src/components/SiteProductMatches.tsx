import { Link, useLocation } from 'react-router-dom'
import { useSearchResults } from '../SearchResultsContext'
import { formatPrice } from '../api'

/**
 * Problem 7: when the chat agent's reply includes product matches (ChatResponse.products),
 * ChatWidget hands them to SearchResultsContext and this component — mounted once in App.tsx,
 * so it's visible no matter which page you're on — renders them as real product cards right on
 * the site. Each card links to /products/:id, the exact same single-item page from Problem 3.
 */
export default function SiteProductMatches() {
  const { results, query, clear } = useSearchResults()
  const { pathname } = useLocation()

  // Hidden on a single product's own page — showing a wall of other matches above it would
  // bury the detail view it opens to.
  if (results.length === 0 || /^\/products\/[^/]+$/.test(pathname)) return null

  return (
    <section className="matches" aria-label="Chat search results">
      <div className="matches__head">
        <p className="matches__title">
          Handsome Dan fetched these{query ? ` for "${query}"` : ''}:
        </p>
        <button className="matches__clear" onClick={clear}>
          Clear
        </button>
      </div>
      <div className="grid">
        {results.map((p) => (
          <Link key={p.product_id} to={`/products/${p.product_id}`} className="card">
            <div className="card__image">
              <img src={p.image_url} alt={p.name} loading="lazy" />
              {!p.in_stock && <span className="card__badge">Sold out</span>}
            </div>
            <div className="card__body">
              <h3 className="card__name">{p.name}</h3>
              <p className="card__desc">{p.short_description}</p>
              <p className="card__price">{formatPrice(p.price)}</p>
            </div>
          </Link>
        ))}
      </div>
    </section>
  )
}
