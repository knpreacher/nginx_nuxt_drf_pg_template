export interface CatalogItem {
  id: number
  name: string
  description: string
  image_url: string | null
  created_at: string
  updated_at: string
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// варианты сортировки для селекта
export const ORDER_OPTIONS = [
  { label: "Сначала новые", value: "-created_at" },
  { label: "Сначала старые", value: "created_at" },
  { label: "Название А-Я", value: "name" },
  { label: "Название Я-А", value: "-name" },
  { label: "Недавно изменённые", value: "-updated_at" },
]

export const PAGE_SIZE = 12
