import { describe, it, expect, beforeEach } from 'vitest'
import { useChatStore } from './chatStore'
import type { Conversation, Message, CitationSource } from '@/types/chat'

describe('useChatStore', () => {
  beforeEach(() => {
    useChatStore.setState({
      conversations: [],
      currentConversationId: null,
      messages: [],
      isStreaming: false,
      streamingContent: '',
      citations: [],
    })
  })

  const makeConv = (id: number, title = '测试'): Conversation => ({
    id, title, created_at: '', updated_at: '', message_count: 0,
  })

  const makeMsg = (id: number, role: 'user' | 'assistant', content = 'hi'): Message => ({
    id, conversation_id: 1, role, content, created_at: '',
  })

  it('初始状态应该为空', () => {
    const state = useChatStore.getState()
    expect(state.conversations).toEqual([])
    expect(state.messages).toEqual([])
    expect(state.isStreaming).toBe(false)
    expect(state.streamingContent).toBe('')
  })

  it('setConversations 应该设置会话列表', () => {
    const convs = [makeConv(1), makeConv(2)]
    useChatStore.getState().setConversations(convs)
    expect(useChatStore.getState().conversations.length).toBe(2)
  })

  it('addConversation 应该把新会话放在最前面', () => {
    useChatStore.getState().setConversations([makeConv(1)])
    useChatStore.getState().addConversation(makeConv(2))
    const convs = useChatStore.getState().conversations
    expect(convs[0].id).toBe(2)
  })

  it('removeConversation 应该删除指定会话', () => {
    useChatStore.getState().setConversations([makeConv(1), makeConv(2)])
    useChatStore.getState().removeConversation(1)
    expect(useChatStore.getState().conversations.length).toBe(1)
    expect(useChatStore.getState().conversations[0].id).toBe(2)
  })

  it('removeConversation 如果删除当前会话，应该清空 currentConversationId', () => {
    useChatStore.getState().setCurrentConversationId(1)
    useChatStore.getState().setConversations([makeConv(1)])
    useChatStore.getState().removeConversation(1)
    expect(useChatStore.getState().currentConversationId).toBeNull()
  })

  it('setMessages 应该设置消息列表', () => {
    const msgs = [makeMsg(1, 'user'), makeMsg(2, 'assistant')]
    useChatStore.getState().setMessages(msgs)
    expect(useChatStore.getState().messages.length).toBe(2)
  })

  it('addMessage 应该追加消息', () => {
    useChatStore.getState().addMessage(makeMsg(1, 'user'))
    useChatStore.getState().addMessage(makeMsg(2, 'assistant'))
    expect(useChatStore.getState().messages.length).toBe(2)
  })

  it('setIsStreaming 应该设置流式状态', () => {
    useChatStore.getState().setIsStreaming(true)
    expect(useChatStore.getState().isStreaming).toBe(true)
  })

  it('appendStreamingContent 应该累积内容', () => {
    useChatStore.getState().appendStreamingContent('你好')
    useChatStore.getState().appendStreamingContent('世界')
    expect(useChatStore.getState().streamingContent).toBe('你好世界')
  })

  it('resetStreamingContent 应该清空内容和引用', () => {
    useChatStore.getState().setCitations([{ index: 1, document_name: 'a.pdf', chunk_id: 1, excerpt: '...', score: 0.9 }])
    useChatStore.getState().appendStreamingContent('test')
    useChatStore.getState().resetStreamingContent()
    expect(useChatStore.getState().streamingContent).toBe('')
    expect(useChatStore.getState().citations).toEqual([])
  })

  it('setLastAssistantMessageSources 应该更新最后一条 AI 消息的 sources', () => {
    useChatStore.getState().setMessages([
      makeMsg(1, 'user', '问题'),
      makeMsg(2, 'assistant', '回答'),
    ])
    const sources: CitationSource[] = [
      { index: 1, document_name: 'test.pdf', chunk_id: 1, excerpt: '原文', score: 0.95 },
    ]
    useChatStore.getState().setLastAssistantMessageSources(sources)
    const lastMsg = useChatStore.getState().messages[1]
    expect(lastMsg.sources).toEqual(sources)
  })

  it('appendToLastAssistantMessage 应该累积最后一条 AI 消息的内容', () => {
    useChatStore.getState().setMessages([
      makeMsg(1, 'user', '问题'),
      makeMsg(2, 'assistant', '第一段'),
    ])
    useChatStore.getState().appendToLastAssistantMessage('第二段')
    expect(useChatStore.getState().messages[1].content).toBe('第一段第二段')
  })
})
