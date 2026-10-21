import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import FavoriteButton from '../components/FavoriteButton'
import ProductCard from '../components/ProductCard'
import { fetchProduct, fetchSimilarProducts, formatPrice, type Product, type ProductDetail } from '../api'

const stockLabel = (qty: number) => {
  if (qty === 0) return 'Sold out'
  if (qty <= 5) return `Only ${qty} left`
  return 'In stock'
}

export default function ProductDetailPage() {
  const { productId = '' } = useParams()
  const [product, setProduct] = useState<ProductDetail | null>(null)
  const [status, setStatus] = useState<'loading' | 'ready' | 'missing'>('loading')
  const [similar, setSimilar] = useState<Product[]>([])

  useEffect(() => {
    setStatus('loading')
    setSimilar([])
    fetchProduct(productId)
      .then((p) => {
        setProduct(p)
        setStatus('ready')
      })
      .catch(() => setStatus('missing'))
    fetchSimilarProducts(productId)
      .then(setSimilar)
      .catch(() => setSimilar([]))
  }, [productId])

  if (status === 'loading') return <p className="notice">Loading...</p>
  if (status === 'missing' || !product) {
    return (
      <p className="notice">
        We couldn't find that item. <Link to="/products">Back to products</Link>
      </p>
    )
  }

  return (
    <section className="section">
      <Link to="/products" className="back">
        &larr; All products
      </Link>
      <div className="detail">
        <div className="detail__image">
          <img src={product.image_url} alt={product.name} />
        </div>
        <div className="detail__info">
          <p className="detail__type">{product.garment_type}</p>
          <h1>
            {product.name}
            <FavoriteButton product={product} className="detail__favorite" />
          </h1>
          <p className="detail__price">{formatPrice(product.price)}</p>
          <p className="detail__desc">{product.description}</p>

          <h2 className="detail__h">Colors</h2>
          <p>{product.colors.join(', ')}</p>

          <h2 className="detail__h">Sizes &amp; availability</h2>
          <ul className="sizes">
            {product.sizes.map((s) => (
              <li key={s.size} className={s.quantity === 0 ? 'size size--out' : 'size'}>
                <span className="size__name">{s.size}</span>
                <span className="size__stock">{stockLabel(s.quantity)}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {similar.length > 0 && (
        <div className="similar">
          <h2>You might also like</h2>
          <div className="grid">
            {similar.map((p) => (
              <ProductCard key={p.product_id} product={p} />
            ))}
          </div>
        </div>
      )}
    </section>
  )
}
