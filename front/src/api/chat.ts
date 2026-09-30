import { request } from './client'
import { useAuthStore } from '../stores/useAuthStore'
import type { ChatAskResult, ChatMessage, ChatSession, ChatSource } from '../types/chat'

function dispatchChatEvent(eventName: string, payload: Record<string, unknown>, handlers: ChatStreamHandlers) {
  const type = (payload.type as string | undefined) || eventName
  if (type === 'meta') handlers.onMeta?.(payload as never)
  else if (type === 'token') handlers.onToken?.(String(payload.text ?? payload.content ?? ''))
  else if (type === 'response') handlers.onToken?.(String(payload.content ?? ''))
  else if (type === 'thinking') {
    handlers.onThinking?.({
      stage: payload.stage as string | undefined,
      content: String(payload.content ?? ''),
    })
  } else if (
    type === 'plan_start' ||
    type === 'plan_step_start' ||
    type === 'plan_step_end' ||
    type === 'plan_synthesize' ||
    type === 'plan_complete' ||
    type === 'plan_fallback' ||
    type === 'reflection'
  ) {
    handlers.onPlan?.({
      type,
      goal: payload.goal as string | undefined,
      step: payload.step as number | undefined,
      action: payload.action as string | undefined,
      reason: payload.reason as string | undefined,
      stage: payload.stage as string | undefined,
    })
  } else if (type === 'tool_start') handlers.onToolStart?.(payload as never)
  else if (type === 'tool_end') handlers.onToolEnd?.(payload as never)
  else if (type === 'error') handlers.onError?.(String(payload.content ?? '生成失败，请稍后重试'))
  else if (type === 'done') handlers.onDone?.(payload as never)
}

async function consumeChatSSE(response: Response, handlers: ChatStreamHandlers) {
  const reader = response.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let eventName = 'message'
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split('\n')
    buffer = parts.pop() || ''
    for (const line of parts) {
      if (line.startsWith('event:')) {
        eventName = line.slice(6).trim()
        continue
      }
      if (!line.startsWith('data:')) continue
      const raw = line.slice(5).trim()
      if (!raw) continue
      const payload = JSON.parse(raw)
      dispatchChatEvent(eventName, payload, handlers)
      eventName = 'message'
    }
  }
}

export interface ChatStreamHandlers {
  onMeta?: (data: {
    session_id: string
    sources: ChatSource[]
    used_retrieval?: boolean
    used_agent?: boolean
    route_distance?: number | null
    user_message: ChatMessage
  }) => void
  onToken?: (text: string) => void
  onToolStart?: (data: { name: string }) => void
  onToolEnd?: (data: { name: string; result?: string; error?: string | null }) => void
  onThinking?: (data: { stage?: string; content: string }) => void
  onPlan?: (data: {
    type: string
    goal?: string
    step?: number
    action?: string
    reason?: string
    stage?: string
  }) => void
  onError?: (content: string) => void
  onDone?: (data: {
    session_id: string
    answer: string
    used_retrieval?: boolean
    used_agent?: boolean
    enable_thinking?: boolean
    thinking_requested?: boolean
    thinking_reason?: string
    title?: string | null
    assistant_message?: ChatMessage
  }) => void
}

export const chatApi = {
  ask(message: string, sessionId?: string | null) {
    return request<ChatAskResult>('/chat/ask', {
      method: 'POST',
      data: { message, session_id: sessionId || undefined },
    })
  },

  async stream(message: string, sessionId: string | null | undefined, handlers: ChatStreamHandlers) {
    const token = useAuthStore.getState().accessToken
    const response = await fetch('/api/v1/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ message, session_id: sessionId || undefined }),
    })
    if (!response.ok || !response.body) {
      throw new Error(`流式请求失败: ${response.status}`)
    }
    await consumeChatSSE(response, handlers)
  },

  async query(
    message: string,
    sessionId: string | null | undefined,
    handlers: ChatStreamHandlers,
    options?: { enableThinking?: boolean },
  ) {
    const token = useAuthStore.getState().accessToken
    const response = await fetch('/api/v1/chat/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({
        message,
        session_id: sessionId || undefined,
        enable_thinking: Boolean(options?.enableThinking),
      }),
    })
    if (!response.ok || !response.body) {
      throw new Error(`流式请求失败: ${response.status}`)
    }
    await consumeChatSSE(response, handlers)
  },

  sessions() {
    return request<ChatSession[]>('/chat/sessions')
  },

  messages(sessionId: string) {
    return request<ChatMessage[]>(`/chat/sessions/${sessionId}/messages`)
  },

  rename(sessionId: string, title: string) {
    return request<{ id: string; title: string }>(`/chat/sessions/${sessionId}/title`, {
      method: 'PUT',
      data: { title },
    })
  },

  remove(sessionId: string) {
    return request<null>(`/chat/sessions/${sessionId}`, { method: 'DELETE' })
  },
}
