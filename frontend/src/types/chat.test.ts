import { describe, it, expect } from 'vitest'
import type { Message, Conversation, CitationSource, ChatRequest } from './chat'

describe('Chat Types', () => {
  it('Message 应该包含 role, content', () => {
    const msg: Message = {
      id: 1,
      conversation_id: 1,
      role: 'user',
      content: '你好',
      created_at: '2026-07-08T00:00:00Z',
    }
    expect(msg.role).toBe('user')
    expect(msg.content).toBe('你好')
  })

  it('Message role 只能是 user 或 assistant', () => {
    const userMsg: Message = {
      id: 1, conversation_id: 1, role: 'user', content: 'hi', created_at: ''
    }
    const aiMsg: Message = {
      id: 2, conversation_id: 1, role: 'assistant', content: 'hello', created_at: ''
    }
    expect(['user', 'assistant']).toContain(userMsg.role)
    expect(['user', 'assistant']).toContain(aiMsg.role)
  })

  it('CitationSource 应该包含来源信息', () => {
    const source: CitationSource = {
      index: 1,
      document_name: '商品介绍.pdf',
      chunk_id: 5,
      excerpt: '这是一段原文...',
      score: 0.92,
    }
    expect(source.score).toBeGreaterThan(0)
    expect(source.score).toBeLessThanOrEqual(1)
    expect(source.index).toBe(1)
    expect(source.document_name).toBe('商品介绍.pdf')
  })

  it('Conversation 应该包含标题和时间', () => {
    const conv: Conversation = {
      id: 1,
      title: '测试会话',
      created_at: '2026-07-08T00:00:00Z',
      updated_at: '2026-07-08T01:00:00Z',
      message_count: 5,
    }
    expect(conv.message_count).toBe(5)
    expect(conv.title).toBeTruthy()
  })

  it('ChatRequest 应该包含 conversation_id 和 question', () => {
    const req: ChatRequest = {
      conversation_id: 1,
      question: '这个商品多少钱？',
    }
    expect(req.question.length).toBeGreaterThan(0)
    expect(req.conversation_id).toBeGreaterThan(0)
  })

  it('Message 的 sources 为可选字段', () => {
    const msgWithoutSources: Message = {
      id: 1, conversation_id: 1, role: 'user', content: 'hi', created_at: ''
    }
    expect(msgWithoutSources.sources).toBeUndefined()

    const msgWithSources: Message = {
      id: 2, conversation_id: 1, role: 'assistant',
      content: '根据资料...', created_at: '',
      sources: [{ index: 1, document_name: 'a.pdf', chunk_id: 1, excerpt: '...', score: 0.9 }],
    }
    expect(msgWithSources.sources?.length).toBe(1)
  })
})
