export interface ChatSession {
  id: string
  title: string
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id: number
  session_id: string
  role: 'user' | 'assistant' | string
  content: string
  created_at: string
}

export interface ChatSource {
  content: string
  score: number
  source: 'knowledge' | 'note' | string
  document_id: number
  note_id: string
  filename: string
  section_title: string
  chunk_index: number
}

export interface ChatAskResult {
  session_id: string
  answer: string
  sources: ChatSource[]
  used_retrieval?: boolean
  route_distance?: number | null
  title?: string | null
  user_message: ChatMessage
  assistant_message: ChatMessage
}
