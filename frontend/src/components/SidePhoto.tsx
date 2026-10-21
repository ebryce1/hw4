import type { ReactNode } from 'react'

/**
 * A real campus photo running alongside a block of copy, alternating sides down the page — the
 * layout yalebulldogblue.com uses throughout its own pages. Problem 11: swaps the Problem 10
 * illustrated skyline for actual (properly licensed) photography in the body of the page, not
 * just the hero banner. See Footer's "Photo credits" for where each photo comes from.
 */
export default function SidePhoto({
  src,
  alt,
  align = 'left',
  children,
}: {
  src: string
  alt: string
  align?: 'left' | 'right'
  children: ReactNode
}) {
  return (
    <div className={`side-photo side-photo--${align} reveal`}>
      <img src={src} alt={alt} className="side-photo__img" loading="lazy" />
      <div className="side-photo__text">{children}</div>
    </div>
  )
}
