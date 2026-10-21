import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { fetchProducts, type Product } from '../api'
import ProductCard from '../components/ProductCard'

export default function Products() {
  const [params, setParams] = useSearchParams()
  const query = params.get('q') ?? ''
  const [products, setProducts] = useState<Product[]>([])
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading')

  useEffect(() => {
    fetchProducts()
      .then((p) => {
        setProducts(p)
        setStatus('ready')
      })
      .catch(() => setStatus('error'))
  }, [])

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return products
    return products.filter((p) =>
      [p.name, p.garment_type, p.description, ...p.search_tags]
        .join(' ')
        .toLowerCase()
        .includes(q),
    )
  }, [products, query])

  return (
    <section className="section">
      <div className="section__head">
        <h1>Products</h1>
        <input
          className="search"
          type="search"
          value={query}
          onChange={(e) => setParams(e.target.value ? { q: e.target.value } : {})}
          placeholder="Search by name, type, or team"
          aria-label="Search products"
        />
      </div>

      {query && (
        <div className="filter-chip reveal reveal--visible">
          Filtered by <strong>{query}</strong>
          <button type="button" onClick={() => setParams({})} aria-label="Clear filter">
            ×
          </button>
        </div>
      )}

      {status === 'loading' && <p className="notice">Loading products...</p>}
      {status === 'error' && (
        <p className="notice">Couldn't load products. Is the backend running on port 8000?</p>
      )}
      {status === 'ready' && (
        <>
          <p className="count">
            {visible.length} item{visible.length === 1 ? '' : 's'}
          </p>
          {visible.length === 0 ? (
            <p className="notice">Nothing matches that search.</p>
          ) : (
            <div className="grid">
              {visible.map((p, i) => (
                <div key={p.product_id} className="reveal" style={{ transitionDelay: `${Math.min(i, 8) * 40}ms` }}>
                  <ProductCard product={p} />
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </section>
  )
}
