export interface KnowledgeBase {
  id: number
  name: string
  collection_name: string
  description: string | null
  created_at: string
}

export interface CreateKBRequest {
  name: string
  description?: string | null
}

export interface Document {
  id: number
  paper_id: string
  filename: string
  minio_path: string
  file_size: number
  chunk_count: number
  created_at: string
}

export interface ChatRequest {
  message: string
  session_id: string
  knowledge_base_id?: number | null
  collection_name?: string | null
}

export interface ChatResponse {
  session_id: string
  reply: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}
