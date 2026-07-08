import apiClient from '@/config/api'
import type { Conversation, ConversationListResponse, ConversationDetail } from '@/types/chat'

export const conversationApi = {
  list: (page = 1, pageSize = 20) =>
    apiClient.get<ConversationListResponse>('/conversations', { params: { page, page_size: pageSize } }),

  create: (title = '新对话') =>
    apiClient.post<Conversation>('/conversations', { title }),

  getDetail: (id: number) =>
    apiClient.get<ConversationDetail>(`/conversations/${id}`),

  update: (id: number, title: string) =>
    apiClient.patch<Conversation>(`/conversations/${id}`, { title }),

  delete: (id: number) =>
    apiClient.delete(`/conversations/${id}`),
}
