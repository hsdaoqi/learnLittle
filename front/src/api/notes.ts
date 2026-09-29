import { request } from './client'
import type { NoteDetail, NoteFormat, NoteListResponse, NoteSummary } from '../types/notes'

export const notesApi = {
  list(params?: {
    page?: number
    page_size?: number
    category_id?: string
    uncategorized?: boolean
    keyword?: string
  }) {
    return request<NoteListResponse>('/note', { params })
  },

  detail(id: string) {
    return request<NoteDetail>(`/note/${id}`)
  },

  create(data: {
    title: string
    content: string
    category_id?: string | null
    tags?: string[]
    format?: NoteFormat
  }) {
    return request<{ id: string; title: string; format: string; created_at: string }>('/note', {
      method: 'POST',
      data,
    })
  },

  update(
    id: string,
    data: {
      title?: string
      content?: string
      category_id?: string | null
      tags?: string[]
      is_pinned?: boolean
    },
  ) {
    return request<NoteDetail>(`/note/${id}`, { method: 'PUT', data })
  },

  move(id: string, categoryId: string | null) {
    return request<NoteDetail>(`/note/${id}/category`, {
      method: 'PUT',
      data: { category_id: categoryId },
    })
  },

  remove(id: string) {
    return request<null>(`/note/${id}`, { method: 'DELETE' })
  },

  recycleBin() {
    return request<NoteSummary[]>('/note/recycle-bin')
  },

  restore(id: string) {
    return request<null>(`/note/${id}/restore`, { method: 'POST' })
  },

  permanentDelete(id: string) {
    return request<null>(`/note/${id}/permanent`, { method: 'DELETE' })
  },

  search(query: string, topK = 20) {
    return request<{
      query: string
      results: { note: NoteSummary; score: number }[]
    }>('/note/search', { method: 'POST', data: { query, top_k: topK } })
  },

  autocomplete(content: string, cursorPosition = 0) {
    return request<{ completion: string }>('/note/autocomplete', {
      method: 'POST',
      data: { content, cursor_position: cursorPosition },
    })
  },

  writeAssistant(content: string, mode: 'continue' | 'expand' | 'summary' = 'continue') {
    return request<{ result: string }>('/note/write-assistant', {
      method: 'POST',
      data: { content, mode },
    })
  },

  autoTag(title: string, content: string) {
    return request<{ tags: string[] }>('/note/auto-tag', {
      method: 'POST',
      data: { title, content },
    })
  },

  exportEmail(id: string, data: { to?: string; format?: 'md' | 'txt' } = {}) {
    return request<{ to: string; filename: string }>(`/note/${id}/export-email`, {
      method: 'POST',
      data,
    })
  },

  batch(data: {
    note_ids: string[]
    operation: 'delete' | 'pin' | 'unpin' | 'move' | 'permanent_delete' | 'restore'
    target_category_id?: string | null
  }) {
    return request<{
      operation: string
      total: number
      success_count: number
      error_count: number
      errors: { note_id: string; error: string }[] | null
    }>('/note/batch', { method: 'POST', data })
  },
}
