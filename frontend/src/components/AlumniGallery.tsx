/**
 * Stylized "engraved cameo" portraits of three Yale alumni, in the flat woodcut-print style of an
 * old yearbook plate — not photographs, not product placements, nobody shown wearing any
 * merchandise. Purely decorative school-spirit flavor for the About page, each one captioned with
 * the real person's name and Yale class year.
 */
const ALUMNI = [
  { name: 'Eli Whitney', note: 'B.A. 1792 — inventor', variant: 'whitney' as const },
  { name: 'Nathan Hale', note: 'B.A. 1773 — patriot', variant: 'hale' as const },
  { name: 'William H. Taft', note: 'B.A. 1878 — 27th President', variant: 'taft' as const },
]

function Cameo({ variant }: { variant: 'whitney' | 'hale' | 'taft' }) {
  return (
    <svg viewBox="0 0 160 160" className="cameo__art" aria-hidden="true">
      <circle cx="80" cy="80" r="76" fill="#f3ead2" stroke="#c9a227" strokeWidth="3" />
      <circle cx="80" cy="80" r="68" fill="none" stroke="#00356b" strokeOpacity="0.25" strokeWidth="1.5" />
      <g fill="#00356b" fillOpacity="0.82">
        {/* shoulders / coat */}
        <path d="M30 150 Q80 110 130 150 L130 165 L30 165 Z" />
        {/* neck */}
        <rect x="68" y="92" width="24" height="22" />
        {/* head */}
        <ellipse cx="80" cy="76" rx="30" ry="34" />
        {variant === 'whitney' && (
          <>
            {/* queued hair + collar, 18th-century inventor */}
            <path d="M52 60 Q80 32 108 60 Q108 40 80 36 Q52 40 52 60 Z" />
            <rect x="60" y="100" width="40" height="10" fill="#f3ead2" fillOpacity="0.9" />
          </>
        )}
        {variant === 'hale' && (
          <>
            {/* tricorn-ish hairline + jabot */}
            <path d="M50 58 Q80 30 110 58 L104 66 Q80 44 56 66 Z" />
            <path d="M70 100 L90 100 L84 118 L76 118 Z" fill="#f3ead2" fillOpacity="0.9" />
          </>
        )}
        {variant === 'taft' && (
          <>
            {/* mustache + rounder build, early-1900s */}
            <path d="M54 62 Q80 34 106 62 Q90 44 80 44 Q70 44 54 62 Z" />
            <rect x="58" y="88" width="10" height="16" rx="5" fill="#00356b" fillOpacity="0.82" />
            <rect x="92" y="88" width="10" height="16" rx="5" fill="#00356b" fillOpacity="0.82" />
            <ellipse cx="80" cy="96" rx="18" ry="6" />
          </>
        )}
      </g>
    </svg>
  )
}

export default function AlumniGallery() {
  return (
    <div className="alumni">
      {ALUMNI.map((a) => (
        <figure key={a.name} className="cameo reveal">
          <Cameo variant={a.variant} />
          <figcaption>
            <span className="cameo__name">{a.name}</span>
            <span className="cameo__note">{a.note}</span>
          </figcaption>
        </figure>
      ))}
    </div>
  )
}
