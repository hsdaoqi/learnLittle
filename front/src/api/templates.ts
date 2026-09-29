import { request } from './client'

export interface NoteTemplate {
  id: number
  name: string
  content_structure: { markdown?: string; content?: string; body?: string } | null
  category: string | null
  sort_order: number
  created_at: string
  updated_at: string
}

export const templateApi = {
  list() {
    return request<{ templates: NoteTemplate[] }>('/note-template')
  },

  create(data: {
    name: string
    content_structure?: Record<string, unknown>
    category?: string | null
  }) {
    return request<NoteTemplate>('/note-template', { method: 'POST', data })
  },

  update(id: number, data: { name?: string; content_structure?: Record<string, unknown>; category?: string | null }) {
    return request<NoteTemplate>(`/note-template/${id}`, { method: 'PUT', data })
  },

  remove(id: number) {
    return request<null>(`/note-template/${id}`, { method: 'DELETE' })
  },

  apply(id: number, data: { title?: string; category_id?: string | null; format?: 'md' | 'txt' } = {}) {
    return request<{ id: string; title: string; format: string; created_at: string }>(
      `/note-template/${id}/apply`,
      { method: 'POST', data },
    )
  },
}
