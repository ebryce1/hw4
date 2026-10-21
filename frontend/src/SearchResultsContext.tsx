import { createContext, useContext, useState, type ReactNode } from 'react'
import type { ChatProductCard } from './api'

/**
 * The chat <-> page bridge for Problem 7. ChatWidget calls setResults() whenever the agent's
 * reply includes product matches; any page can read those matches and render them live. This is
 * in-memory only (not localStorage) — it's meant to reflect "what the chat just found," not to
 * persist across a reload.
 */
interface SearchResultsState {
  results: ChatProductCard[]
  query: string | null
  setResults: (results: ChatProductCard[], query: string) => void
  clear: () => void
}

const SearchResultsContext = createContext<SearchResultsState | null>(null)

export function SearchResultsProvider({ children }: { children: ReactNode }) {
  const [results, setResultsState] = useState<ChatProductCard[]>([])
  const [query, setQuery] = useState<string | null>(null)

  const setResults = (next: ChatProductCard[], nextQuery: string) => {
    setResultsState(next)
    setQuery(nextQuery)
  }
  const clear = () => {
    setResultsState([])
    setQuery(null)
  }

  return (
    <SearchResultsContext.Provider value={{ results, query, setResults, clear }}>
      {children}
    </SearchResultsContext.Provider>
  )
}

export function useSearchResults() {
  const ctx = useContext(SearchResultsContext)
  if (!ctx) throw new Error('useSearchResults must be used within SearchResultsProvider')
  return ctx
}
