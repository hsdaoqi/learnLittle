export interface KnowledgeDocument {
  id: number
  filename: string
  file_size: number
  file_type: string
  md5_hash: string
  chunk_count: number
  created_at: string
  updated_at: string
}

export interface KnowledgeDocumentList {
  documents: KnowledgeDocument[]
  total: number
}

export interface KnowledgeSearchHit {
  content: string
  score: number
  document_id: number
  filename: string
  section_title: string
  chunk_index: number
}

export interface KnowledgeUploadEvent {
  event_type: 'processing' | 'completed' | 'finish' | 'error' | string
  filename?: string
  progress?: number
  stage?: string
  message?: string
  document_id?: number
  document?: KnowledgeDocument
}
