import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'

const links = [
  { to: '/', label: 'Home', end: true },
  { to: '/products', label: 'Products' },
  { to: '/about', label: 'About Us' },
]

export default function NavBar() {
  const { user, setUser } = useAuth()
  const navigate = useNavigate()

  function logOut() {
    setUser(null)
    navigate('/')
  }

  return (
    <header className="nav">
      <div className="nav__inner">
        <NavLink to="/" className="nav__brand">
          <svg viewBox="0 0 32 32" className="nav__crest" aria-hidden="true">
            <circle cx="16" cy="16" r="15" fill="none" stroke="#c9a227" strokeWidth="2" />
            <text x="16" y="22" textAnchor="middle" fontFamily="Playfair Display, serif" fontWeight="700" fontSize="17" fill="#fff">
              Y
            </text>
          </svg>
          Campus Customs
        </NavLink>
        <nav className="nav__links" aria-label="Main">
          {links.map((l) => (
            <NavLink key={l.to} to={l.to} end={l.end} className="nav__link">
              {l.label}
            </NavLink>
          ))}
        </nav>
        <div className="nav__account">
          {user ? (
            <>
              <NavLink to="/favorites" className="nav__link">
                Favorites
              </NavLink>
              <span className="nav__hello">Hi, {user.first_name ?? user.name}</span>
              <button className="nav__link nav__linkbtn" onClick={logOut}>
                Log Out
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className="nav__link">
                Log In
              </NavLink>
              <NavLink to="/register" className="btn btn--small">
                Create Account
              </NavLink>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
