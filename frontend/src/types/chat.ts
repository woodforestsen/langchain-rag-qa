export interface Conversation {
  id: number
  title: string
  created_at: string
  updated_at: string
  message_count: number
}

export interface CitationSource {
  index: number
  document_name: string
  chunk_id: number
  excerpt: string
  score: number
}

export interface Message {
  id: number
  conversation_id: number
  role: 'user' | 'assistant'
  content: string
  sources?: CitationSource[]
  created_at: string
}

export interface ChatRequest {
  conversation_id: number
  question: string
}

export interface ConversationListResponse {
  items: Conversation[]
  total: number
  page: number
  page_size: number
}

export interface ConversationDetail extends Conversation {
  messages: Message[]
}
