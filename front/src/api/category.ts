import { request } from './client'
import type { Category, DeletedCategory } from '../types/notes'

export const categoryApi = {
  getTree() {
    return request<Category[]>('/category/tree')
  },

  create(data: { name: string; parent_id?: string | null; icon?: string; color?: string }) {
    return request<Category>('/category', { method: 'POST', data })
  },

  update(id: string, data: { name: string; icon?: string | null; color?: string | null }) {
    return request<Category>(`/category/${id}`, { method: 'PUT', data })
  },

  move(id: string, parentId: string | null) {
    return request<Category>(`/category/${id}/move`, {
      method: 'POST',
      data: { parent_id: parentId },
    })
  },

  remove(id: string) {
    return request<null>(`/category/${id}`, { method: 'DELETE' })
  },

  recycleBin() {
    return request<{ categories: DeletedCategory[]; total: number }>('/category/recycle-bin')
  },

  restore(id: string) {
    return request<{ restored_count: number }>(`/category/${id}/restore`, { method: 'POST' })
  },

  permanentDelete(id: string) {
    return request<{ deleted_name: string }>(`/category/${id}/permanent`, { method: 'DELETE' })
  },

  reorder(parentId: string | null, orderedIds: string[]) {
    return request<null>('/category/reorder', {
      method: 'POST',
      data: { parent_id: parentId, ordered_ids: orderedIds },
    })
  },

  batch(data: {
    category_ids: string[]
    operation: 'delete' | 'merge' | 'permanent_delete' | 'restore'
    merge_target_id?: string
  }) {
    return request<Record<string, unknown>>('/category/batch', { method: 'POST', data })
  },
}
