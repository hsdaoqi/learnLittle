export const UNCATEGORIZED_SENTINEL = '__uncategorized__'

export interface Category {
  id: string
  parent_id: string | null
  name: string
  icon: string | null
  color: string | null
  sort_order: number
  note_count: number
  created_at: string
  updated_at: string
  children: Category[]
}

export interface DeletedCategory {
  id: string
  name: string
  icon: string | null
  color: string | null
  parent_id: string | null
  deleted_at: string
  days_remaining: number
  descendant_count: number
}

export type NoteFormat = 'md' | 'txt'

export interface NoteSummary {
  id: string
  title: string
  format: string
  tags: string[] | null
  category_id: string | null
  is_pinned: boolean
  created_at: string
  updated_at: string
  days_remaining?: number | null
}

export interface NoteDetail extends NoteSummary {
  content: string
}

export interface NoteListResponse {
  items: NoteSummary[]
  total: number
  page: number
  page_size: number
}
