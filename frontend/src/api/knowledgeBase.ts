import apiClient from '@/config/api'
import type { DocumentListResponse, DocumentDetail, KnowledgeStats } from '@/types/document'

export const knowledgeBaseApi = {
  upload: (files: File | File[]) => {
    const formData = new FormData()
    const fileList = Array.isArray(files) ? files : [files]
    fileList.forEach((file) => formData.append('files', file))
    return apiClient.post('/knowledge/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 300000, // 多文件上传 5 分钟超时
    })
  },

  listDocuments: (page = 1, pageSize = 20) =>
    apiClient.get<DocumentListResponse>('/knowledge/documents', {
      params: { page, page_size: pageSize },
    }),

  getDocument: (id: number) =>
    apiClient.get<DocumentDetail>(`/knowledge/documents/${id}`),

  deleteDocument: (id: number) =>
    apiClient.delete(`/knowledge/documents/${id}`),

  reindexDocument: (id: number) =>
    apiClient.post(`/knowledge/documents/${id}/reindex`),

  getStats: () =>
    apiClient.get<KnowledgeStats>('/knowledge/stats'),
}
