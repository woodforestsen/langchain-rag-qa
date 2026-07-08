import { create } from 'zustand'
import type { Conversation, Message, CitationSource } from '@/types/chat'

interface ChatState {
  conversations: Conversation[]
  currentConversationId: number | null
  messages: Message[]
  isStreaming: boolean
  streamingContent: string
  citations: CitationSource[]

  setConversations: (convs: Conversation[]) => void
  addConversation: (conv: Conversation) => void
  removeConversation: (id: number) => void
  updateConversation: (id: number, updates: Partial<Conversation>) => void
  setCurrentConversationId: (id: number | null) => void
  setMessages: (messages: Message[]) => void
  addMessage: (msg: Message) => void
  setIsStreaming: (v: boolean) => void
  appendStreamingContent: (token: string) => void
  resetStreamingContent: () => void
  setCitations: (citations: CitationSource[]) => void
  appendToLastAssistantMessage: (content: string) => void
  setLastAssistantMessageSources: (sources: CitationSource[]) => void
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  currentConversationId: null,
  messages: [],
  isStreaming: false,
  streamingContent: '',
  citations: [],

  setConversations: (convs) => set({ conversations: convs }),
  addConversation: (conv) =>
    set((state) => ({ conversations: [conv, ...state.conversations] })),
  removeConversation: (id) =>
    set((state) => ({
      conversations: state.conversations.filter((c) => c.id !== id),
      currentConversationId:
        state.currentConversationId === id ? null : state.currentConversationId,
    })),
  updateConversation: (id, updates) =>
    set((state) => ({
      conversations: state.conversations.map((c) =>
        c.id === id ? { ...c, ...updates } : c,
      ),
    })),

  setCurrentConversationId: (id) => set({ currentConversationId: id }),
  setMessages: (messages) => set({ messages }),
  addMessage: (msg) =>
    set((state) => ({ messages: [...state.messages, msg] })),

  setIsStreaming: (v) => set({ isStreaming: v }),
  appendStreamingContent: (token) =>
    set((state) => ({ streamingContent: state.streamingContent + token })),
  resetStreamingContent: () => set({ streamingContent: '', citations: [] }),

  setCitations: (citations) => set({ citations }),

  appendToLastAssistantMessage: (content) =>
    set((state) => {
      const msgs = [...state.messages]
      const lastMsg = msgs[msgs.length - 1]
      if (lastMsg && lastMsg.role === 'assistant') {
        msgs[msgs.length - 1] = { ...lastMsg, content: lastMsg.content + content }
      }
      return { messages: msgs }
    }),

  setLastAssistantMessageSources: (sources) =>
    set((state) => {
      const msgs = [...state.messages]
      const lastMsg = msgs[msgs.length - 1]
      if (lastMsg && lastMsg.role === 'assistant') {
        msgs[msgs.length - 1] = { ...lastMsg, sources }
      }
      return { messages: msgs }
    }),
}))
