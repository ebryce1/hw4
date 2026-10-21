import { useEffect, useRef, useState, type FormEvent } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import { useSearchResults } from '../SearchResultsContext'
import {
  fetchChatHistory,
  formatPrice,
  sendChatMessage,
  type ChatProductCard,
  type ChatTurn,
  type PageContext,
} from '../api'

interface Message {
  role: 'user' | 'assistant'
  text: string
  products?: ChatProductCard[]
}

const GREETING: Message = {
  role: 'assistant',
  text:
    "Ruff. Handsome Dan here — best jawline in the Ivy League, and not bad at finding merch either. " +
    'Ask me about hoodies, tees, sizes, or prices.',
}

/** Pulls a product_id out of the URL when the shopper is on that product's own page. */
function productIdFromPath(pathname: string): string | null {
  const match = pathname.match(/^\/products\/([^/]+)$/)
  return match ? match[1] : null
}

export default function ChatWidget() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([GREETING])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const { user } = useAuth()
  const { setResults } = useSearchResults()
  const { pathname } = useLocation()
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, busy, open])

  // Problem 8: reload a signed-in shopper's saved history whenever they sign in (including
  // already being signed in on page load, since AuthContext restores from localStorage). Clear
  // back to the greeting on sign-out or when a different account signs in on this device, so one
  // shopper's chat never bleeds into another's screen.
  useEffect(() => {
    let cancelled = false
    if (!user) {
      setMessages([GREETING])
      return
    }
    fetchChatHistory(user.id)
      .then((entries) => {
        if (cancelled) return
        if (entries.length === 0) {
          setMessages([GREETING])
        } else {
          setMessages(entries.map((e) => ({ role: e.role, text: e.content, products: e.products })))
        }
      })
      .catch(() => {
        if (!cancelled) setMessages([GREETING])
      })
    return () => {
      cancelled = true
    }
  }, [user?.id])

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    const text = input.trim()
    if (!text || busy) return
    setInput('')
    const history: ChatTurn[] = messages.map((m) => ({ role: m.role, content: m.text }))
    const pageContext: PageContext = { path: pathname, product_id: productIdFromPath(pathname) }
    setMessages((m) => [...m, { role: 'user', text }])
    setBusy(true)
    try {
      const { reply, products } = await sendChatMessage(text, history, user?.id ?? null, pageContext)
      setMessages((m) => [...m, { role: 'assistant', text: reply, products }])
      // Push matches onto the page itself (Problem 7). A reply with no matches (e.g. "thanks!")
      // leaves whatever was last shown on the page alone, rather than clearing it.
      if (products.length > 0) setResults(products, text)
    } catch {
      setMessages((m) => [
        ...m,
        { role: 'assistant', text: "Even a dog this good-looking hits a snag sometimes. Try again?" },
      ])
    } finally {
      setBusy(false)
    }
  }

  if (!open) {
    return (
      <button className="chat-fab" onClick={() => setOpen(true)} aria-label="Open chat">
        Chat
      </button>
    )
  }

  return (
    <section className="chat" aria-label="Chat with Handsome Dan">
      <header className="chat__header">
        <span>Handsome Dan, Campus Customs</span>
        <button onClick={() => setOpen(false)} aria-label="Close chat">
          ×
        </button>
      </header>
      <div className="chat__messages">
        {messages.map((m, i) => (
          <div key={i} className={`chat__msg chat__msg--${m.role}`}>
            {m.text}
            {m.products && m.products.length > 0 && (
              <div className="chat__products">
                {m.products.map((p) => (
                  <Link key={p.product_id} to={`/products/${p.product_id}`} className="chat__product">
                    <img src={p.image_url} alt={p.name} loading="lazy" />
                    <div>
                      <p className="chat__product-name">{p.name}</p>
                      <p className="chat__product-price">
                        {formatPrice(p.price)}
                        {!p.in_stock && ' · Sold out'}
                      </p>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        ))}
        {busy && <div className="chat__msg chat__msg--assistant chat__typing">Typing...</div>}
        <div ref={endRef} />
      </div>
      <form className="chat__form" onSubmit={onSubmit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about merch..."
          aria-label="Message"
          autoFocus
        />
        <button type="submit" disabled={busy || !input.trim()}>
          Send
        </button>
      </form>
    </section>
  )
}
