export interface DocumentItem {
  id: number
  filename: string
  file_type: string
  file_size: number
  status: 'processing' | 'ready' | 'error'
  chunk_count: number
  error_message?: string
  uploader_id: number
  created_at: string
}

export interface DocumentChunk {
  id: number
  chunk_index: number
  content: string
  char_count: number
}

export interface DocumentDetail extends DocumentItem {
  chunks: DocumentChunk[]
}

export interface DocumentListResponse {
  items: DocumentItem[]
  total: number
  page: number
  page_size: number
}

export interface KnowledgeStats {
  total_documents: number
  total_chunks: number
  total_chars: number
  documents_by_type: Record<string, number>
  documents_by_status: Record<string, number>
}
