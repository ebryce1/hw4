import { useEffect, useRef, useState } from 'react'

const QUIPS = [
  "Ruff! Did I mention my jawline?",
  "Pssst — the hoodies are navy. Obviously.",
  "I peek, I wink, I sell sweatshirts. A full day.",
  "Handsome Dan sent me. He's busy being handsome.",
  "Go on, click the chat. I'll wait here looking great.",
]

/**
 * A little bulldog in a Yale sweater who peeks up from the bottom-left corner, winks every so
 * often on his own, and winks on demand (with a quip) if you click him. Pure flourish — part of
 * Problem 10's "chat feel, but for the whole page" ask.
 */
export default function BulldogMascot() {
  const [winking, setWinking] = useState(false)
  const [quip, setQuip] = useState<string | null>(null)
  const quipTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    const id = setInterval(() => {
      setWinking(true)
      setTimeout(() => setWinking(false), 260)
    }, 6500)
    return () => clearInterval(id)
  }, [])

  function onClick() {
    setWinking(true)
    setTimeout(() => setWinking(false), 260)
    setQuip(QUIPS[Math.floor(Math.random() * QUIPS.length)])
    if (quipTimer.current) clearTimeout(quipTimer.current)
    quipTimer.current = setTimeout(() => setQuip(null), 2600)
  }

  return (
    <div className="mascot" aria-hidden="true">
      {quip && <div className="mascot__quip">{quip}</div>}
      <button type="button" className="mascot__btn" onClick={onClick} aria-label="Say hi to the mascot">
        <svg viewBox="0 0 140 110" className="mascot__svg">
          <ellipse cx="70" cy="100" rx="52" ry="26" fill="#00356b" />
          <rect x="48" y="78" width="44" height="18" fill="#ffffff" opacity="0.9" />
          <text x="70" y="92" textAnchor="middle" fontFamily="Playfair Display, serif" fontWeight="700" fontSize="16" fill="#00356b">
            Y
          </text>
          <ellipse cx="30" cy="48" rx="16" ry="22" fill="#9b6a3f" transform="rotate(-18 30 48)" />
          <ellipse cx="110" cy="48" rx="16" ry="22" fill="#9b6a3f" transform="rotate(18 110 48)" />
          <ellipse cx="70" cy="58" rx="46" ry="40" fill="#c08a52" />
          <ellipse cx="70" cy="78" rx="30" ry="18" fill="#dcb285" />
          <ellipse cx="50" cy="52" rx="7" ry={winking ? 1 : 7} fill="#241508" style={{ transition: 'ry 0.12s' }} />
          <ellipse cx="90" cy="52" rx="7" ry="7" fill="#241508" />
          <ellipse cx="70" cy="70" rx="8" ry="6" fill="#241508" />
          <path d="M55 86 Q70 96 85 86" stroke="#5c3a1a" strokeWidth="3" fill="none" strokeLinecap="round" />
        </svg>
      </button>
    </div>
  )
}
