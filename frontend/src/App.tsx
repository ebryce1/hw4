import { Route, Routes } from 'react-router-dom'
import BulldogMascot from './components/BulldogMascot'
import ChatWidget from './components/ChatWidget'
import Footer from './components/Footer'
import NavBar from './components/NavBar'
import SiteProductMatches from './components/SiteProductMatches'
import About from './pages/About'
import Favorites from './pages/Favorites'
import Home from './pages/Home'
import Login from './pages/Login'
import ProductDetailPage from './pages/ProductDetailPage'
import Products from './pages/Products'
import Register from './pages/Register'
import { useScrollReveal } from './useScrollReveal'

export default function App() {
  useScrollReveal()
  return (
    <div className="app">
      <NavBar />
      <SiteProductMatches />
      <main className="main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/products/:productId" element={<ProductDetailPage />} />
          <Route path="/about" element={<About />} />
          <Route path="/favorites" element={<Favorites />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<p className="notice">Page not found.</p>} />
        </Routes>
      </main>
      <Footer />
      <ChatWidget />
      <BulldogMascot />
    </div>
  )
}
