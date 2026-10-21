import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchProducts, type Product } from '../api'
import ProductCard from '../components/ProductCard'
import SidePhoto from '../components/SidePhoto'
import type { HeroStyle } from '../heroStyle'

/** Small inline glyphs for the "Shop by style" tiles — kept as simple line icons so they read
 * clearly at this size and recolor on hover with the rest of the tile (see .tile__icon in CSS). */
const ICONS = {
  hoodie: (
    <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 44V22L6 18l6-8h5l3 4h8l3-4h5l6 8-6 4v22" />
      <path d="M17 14a7 7 0 0 0 14 0" />
    </svg>
  ),
  crewneck: (
    <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
      <path d="M8 44V16l7-6h4a5 5 0 0 0 10 0h4l7 6v28" />
    </svg>
  ),
  tee: (
    <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 7 6 13l3 7 5-2v26h20V18l5 2 3-7-11-6a5 5 0 0 1-10 0Z" />
    </svg>
  ),
  zip: (
    <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 44V22L6 18l6-8h5l3 4h8l3-4h5l6 8-6 4v22" />
      <path d="M24 16v28" strokeDasharray="2.5 3" />
    </svg>
  ),
}

const shelves: { label: string; q: string; icon: keyof typeof ICONS }[] = [
  { label: 'Hoodies', q: 'hoodie', icon: 'hoodie' },
  { label: 'Crewnecks', q: 'crewneck', icon: 'crewneck' },
  { label: 'T-Shirts', q: 't-shirt', icon: 'tee' },
  { label: 'Quarter-Zips', q: 'quarter-zip', icon: 'zip' },
]

export default function Home() {
  const [featured, setFeatured] = useState<Product[]>([])

  useEffect(() => {
    fetchProducts()
      .then((all) => setFeatured(all.filter((p) => p.in_stock).slice(0, 4)))
      .catch(() => setFeatured([]))
  }, [])

  return (
    <>
      <section className="hero" style={{ '--hero-photo': "url('/campus/harkness-tower.jpg')" } as HeroStyle}>
        <div className="hero__watermark">Campus Customs</div>
        <div className="hero__inner">
          <p className="hero__eyebrow">Fresh from New Haven</p>
          <h1>Wear the Blue.</h1>
          <p className="hero__lede">
            Sweatshirts, tees, and layers for every college, team, and Saturday in the stands.
            Find something that feels like your corner of campus.
          </p>
          <Link to="/products" className="btn">
            Shop all merch
          </Link>
        </div>
      </section>

      <section className="section reveal">
        <h2 style={{ textAlign: 'center' }}>Shop by style</h2>
        <div className="divider">
          <span className="divider__mark" />
        </div>
        <div className="tiles">
          {shelves.map((s) => (
            <Link key={s.q} to={`/products?q=${encodeURIComponent(s.q)}`} className="tile">
              <span className="tile__icon">{ICONS[s.icon]}</span>
              <span className="tile__label">{s.label}</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="section">
        <SidePhoto src="/campus/old-campus.jpg" alt="Old Campus, Yale University">
          <h2>Designed for actual New Haven weather</h2>
          <p>
            Cold stone, green lawns, a walk across the yard that's never quite short enough. Our
            layers are picked for the campus you actually live on — warm enough for a Harkness
            Tower chime at 8am, light enough for the walk back at midnight.
          </p>
        </SidePhoto>
      </section>

      {featured.length > 0 && (
        <section className="section reveal">
          <h2 style={{ textAlign: 'center' }}>Fan favorites</h2>
          <div className="divider">
            <span className="divider__mark" />
          </div>
          <div className="grid">
            {featured.map((p) => (
              <ProductCard key={p.product_id} product={p} />
            ))}
          </div>
        </section>
      )}

      <section className="section section--band reveal">
        <h2>Not sure what to get?</h2>
        <p>
          Open the chat in the corner and tell us what you're after. Ask about colors, sizes, or
          what's still on the shelf.
        </p>
      </section>
    </>
  )
}
