import { useEffect } from 'react'

/**
 * Fades/slides any element with class="reveal" into place the first time it scrolls into view.
 * One shared IntersectionObserver for the whole app's lifetime — call this once, high in the
 * tree (App.tsx).
 *
 * Content behind a data fetch (the product grid, chat-found matches, favorites...) mounts its
 * .reveal elements well after this hook's own effect runs once on app start, so a one-time DOM
 * scan isn't enough — a MutationObserver watches for any new .reveal element appearing anywhere
 * in the page, for as long as the app is open, and hands it to the IntersectionObserver too.
 */
export function useScrollReveal() {
  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      const markAll = () =>
        document.querySelectorAll('.reveal:not(.reveal--visible)').forEach((el) => el.classList.add('reveal--visible'))
      markAll()
      const mo = new MutationObserver(markAll)
      mo.observe(document.body, { childList: true, subtree: true })
      return () => mo.disconnect()
    }

    const io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add('reveal--visible')
            io.unobserve(entry.target)
          }
        }
      },
      { threshold: 0.15, rootMargin: '0px 0px -40px 0px' },
    )

    const observeNew = () => {
      document.querySelectorAll('.reveal:not(.reveal--visible)').forEach((el) => io.observe(el))
    }
    observeNew()

    const mo = new MutationObserver(observeNew)
    mo.observe(document.body, { childList: true, subtree: true })

    return () => {
      io.disconnect()
      mo.disconnect()
    }
  }, [])
}
