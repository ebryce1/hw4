export interface Product {
  product_id: string
  name: string
  garment_type: string
  description: string
  colors: string[]
  search_tags: string[]
  price: number
  image_url: string
  in_stock: boolean
}

export interface SizeStock {
  size: string
  quantity: number
}

export interface ProductDetail extends Product {
  sizes: SizeStock[]
}

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Request failed (${res.status})`)
  return res.json() as Promise<T>
}

/** POST JSON and surface the API's `detail` message on failure (e.g. "Invalid email or password"). */
async function postJson<T>(url: string, body: unknown): Promise<T> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = await res.json().catch(() => null)
  if (!res.ok) {
    const detail = data?.detail
    const message = Array.isArray(detail) ? detail[0]?.msg : detail
    throw new Error(message || `Request failed (${res.status})`)
  }
  return data as T
}

export const fetchProducts = () => getJson<Product[]>('/api/products')
export const fetchProduct = (id: string) =>
  getJson<ProductDetail>(`/api/products/${encodeURIComponent(id)}`)

/** Problem 9: 2-3 products like this one, for the "You might also like" section. */
export const fetchSimilarProducts = (id: string) =>
  getJson<Product[]>(`/api/products/${encodeURIComponent(id)}/similar`)

export interface User {
  id: number
  first_name: string | null
  last_name: string | null
  name: string
  email: string
}

export interface SignupInput {
  first_name: string
  last_name: string
  email: string
  password: string
  confirm_password: string
}

export interface LoginInput {
  email: string
  password: string
}

export const signup = (body: SignupInput) => postJson<User>('/api/signup', body)
export const login = (body: LoginInput) => postJson<User>('/api/login', body)

export const formatPrice = (price: number) => `$${price.toFixed(2)}`

/** First sentence of a description, for compact cards. */
export const shortDescription = (text: string) => {
  const first = text.split(/(?<=\.)\s/)[0]
  return first.length > 110 ? `${first.slice(0, 107)}...` : first
}

/** A product match the agent attaches to a reply — matches backend models.ProductCard exactly. */
export interface ChatProductCard {
  product_id: string
  name: string
  price: number
  image_url: string
  in_stock: boolean
  short_description: string
}

export interface ChatTurn {
  role: 'user' | 'assistant'
  content: string
}

/** What the chat currently has in view — lets "do you have this in pink?" resolve on its own. */
export interface PageContext {
  path: string
  product_id: string | null
}

export interface ChatReply {
  reply: string
  products: ChatProductCard[]
}

/** Talks to the Handsome Dan agent (backend/agent.py) via POST /api/chat. */
export function sendChatMessage(
  message: string,
  history: ChatTurn[],
  userId: number | null,
  pageContext: PageContext,
): Promise<ChatReply> {
  return postJson<ChatReply>('/api/chat', {
    message,
    history,
    user_id: userId,
    page_context: pageContext,
  })
}

/** One saved turn from a signed-in shopper's history (Problem 8). */
export interface ChatHistoryEntry {
  role: 'user' | 'assistant'
  content: string
  products: ChatProductCard[]
}

/** Reloads a returning, signed-in shopper's conversation. Guests have nothing to fetch. */
export const fetchChatHistory = (userId: number) =>
  getJson<ChatHistoryEntry[]>(`/api/chat/history/${userId}`)

/** Problem 9: "save for later" favorites. Login-gated, same as chat history (Problem 8) — a
 * guest's picks have nowhere of their own to live yet, so the UI sends them to sign in instead. */
export const fetchFavorites = (userId: number) => getJson<Product[]>(`/api/favorites/${userId}`)

export async function addFavorite(userId: number, productId: string): Promise<void> {
  await postJson('/api/favorites', { user_id: userId, product_id: productId })
}

export async function removeFavorite(userId: number, productId: string): Promise<void> {
  const res = await fetch(
    `/api/favorites/${userId}/${encodeURIComponent(productId)}`,
    { method: 'DELETE' },
  )
  if (!res.ok) throw new Error(`Request failed (${res.status})`)
}
