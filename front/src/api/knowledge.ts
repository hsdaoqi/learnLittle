import { request, ApiError } from './client'
import { useAuthStore } from '../stores/useAuthStore'
import type {
  KnowledgeDocument,
  KnowledgeDocumentList,
  KnowledgeSearchHit,
  KnowledgeUploadEvent,
} from '../types/knowledge'

export interface KnowledgeUploadHandlers {
  onProcessing?: (event: KnowledgeUploadEvent) => void
  onCompleted?: (event: KnowledgeUploadEvent) => void
  onError?: (message: string) => void
}

async function readJsonError(response: Response): Promise<never> {
  try {
    const body = (await response.json()) as { code?: number; message?: string }
    throw new ApiError(body.code ?? response.status, body.message ?? '上传失败')
  } catch (err) {
    if (err instanceof ApiError) throw err
    throw new ApiError(response.status, `上传失败: ${response.status}`)
  }
}

export const knowledgeApi = {
  list() {
    return request<KnowledgeDocumentList>('/knowledge/documents')
  },

  detail(id: number) {
    return request<KnowledgeDocument>(`/knowledge/documents/${id}`)
  },

  async upload(file: File, handlers: KnowledgeUploadHandlers = {}) {
    const token = useAuthStore.getState().accessToken
    const form = new FormData()
    form.append('file', file)
    const response = await fetch('/api/v1/knowledge/upload', {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: form,
    })
    const contentType = response.headers.get('content-type') || ''
    if (!response.ok) {
      await readJsonError(response)
    }
    if (!contentType.includes('text/event-stream') || !response.body) {
      throw new ApiError(-1, '上传响应不是进度流')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      for (const line of lines) {
        if (!line.startsWith('data:')) continue
        const raw = line.slice(5).trim()
        if (!raw) continue
        const event = JSON.parse(raw) as KnowledgeUploadEvent
        if (event.event_type === 'processing') handlers.onProcessing?.(event)
        else if (event.event_type === 'completed') handlers.onCompleted?.(event)
        else if (event.event_type === 'error') {
          handlers.onError?.(event.message || '上传失败')
          throw new ApiError(-1, event.message || '上传失败')
        }
      }
    }
  },

  remove(id: number) {
    return request<null>(`/knowledge/documents/${id}`, { method: 'DELETE' })
  },

  search(q: string, top_k = 5) {
    return request<{ items: KnowledgeSearchHit[]; total: number }>('/knowledge/search', {
      params: { q, top_k },
    })
  },
}
