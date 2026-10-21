import type { CSSProperties } from 'react'

/** React's CSSProperties doesn't know about custom properties — this just widens it enough to
 * set --hero-photo (see .hero in index.css) from a page component. */
export type HeroStyle = CSSProperties & { '--hero-photo'?: string }
