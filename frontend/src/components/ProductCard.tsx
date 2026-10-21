import { Link } from 'react-router-dom'
import { formatPrice, shortDescription, type Product } from '../api'
import FavoriteButton from './FavoriteButton'

export default function ProductCard({ product }: { product: Product }) {
  return (
    <Link to={`/products/${product.product_id}`} className="card">
      <div className="card__image">
        <img src={product.image_url} alt={product.name} loading="lazy" />
        {!product.in_stock && <span className="card__badge">Sold out</span>}
        <FavoriteButton product={product} />
      </div>
      <div className="card__body">
        <h3 className="card__name">{product.name}</h3>
        <p className="card__desc">{shortDescription(product.description)}</p>
        <p className="card__price">{formatPrice(product.price)}</p>
      </div>
    </Link>
  )
}
