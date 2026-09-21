export interface CatalogItem {
  id: number
  name: string
  description: string
  image_url: string | null
  is_public: boolean
  created_at: string
  updated_at: string
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// варианты сортировки: value — для API, key — ключ перевода (catalog.order.*)
export const ORDER_OPTIONS = [
  { value: "-created_at", key: "newest" },
  { value: "created_at", key: "oldest" },
  { value: "name", key: "nameAsc" },
  { value: "-name", key: "nameDesc" },
  { value: "-updated_at", key: "updated" },
]

export const PAGE_SIZE = 12
