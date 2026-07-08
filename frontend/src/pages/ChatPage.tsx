import { useEffect, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { message } from 'antd'
import ChatWindow from '@/components/chat/ChatWindow'
import ChatInput from '@/components/chat/ChatInput'
import { useChatStore } from '@/stores/chatStore'
import { chatApi } from '@/api/chat'
import { conversationApi } from '@/api/conversation'
import type { Message, CitationSource } from '@/types/chat'

export default function ChatPage() {
  const { convId } = useParams<{ convId: string }>()
  const navigate = useNavigate()
  const abortControllerRef = useRef<AbortController | null>(null)

  const {
    currentConversationId,
    messages,
    isStreaming,
    streamingContent,
    setCurrentConversationId,
    setMessages,
    addMessage,
    setIsStreaming,
    appendStreamingContent,
    resetStreamingContent,
    setCitations,
    setLastAssistantMessageSources,
  } = useChatStore()

  // 加载会话详情
  useEffect(() => {
    if (!convId) return

    const id = Number(convId)
    setCurrentConversationId(id)

    conversationApi
      .getDetail(id)
      .then((res) => {
        setMessages(res.data.messages || [])
      })
      .catch(() => {
        message.error('会话不存在或无权访问')
        navigate('/chat')
      })
  }, [convId])

  // 发送消息
  const handleSend = useCallback(
    (question: string) => {
      if (!currentConversationId) return

      // 添加用户消息到列表
      const userMsg: Message = {
        id: Date.now(),
        conversation_id: currentConversationId,
        role: 'user',
        content: question,
        created_at: new Date().toISOString(),
      }
      addMessage(userMsg)

      // 开始流式接收
      setIsStreaming(true)
      resetStreamingContent()

      const controller = chatApi.streamChat(
        currentConversationId,
        { conversation_id: currentConversationId, question },
        // onToken
        (token) => {
          appendStreamingContent(token)
        },
        // onSources
        (sources) => {
          setCitations(sources as CitationSource[])
          setLastAssistantMessageSources(sources as CitationSource[])
        },
        // onDone
        (data: any) => {
          setIsStreaming(false)

          // 流式完成后添加完整的 AI 消息
          const content = useChatStore.getState().streamingContent
          if (content) {
            const sources = useChatStore.getState().citations
            // 用完整消息替换流式内容（保留 sources）
            useChatStore.setState((state) => {
              const msgs = [...state.messages]
              // 移除流式临时消息（id=-1 的）
              const filtered = msgs.filter((m) => m.id !== -1)
              // 添加最终消息
              const finalMsg: Message = {
                id: data?.message_id || Date.now(),
                conversation_id: currentConversationId,
                role: 'assistant',
                content: content,
                sources: sources,
                created_at: new Date().toISOString(),
              }
              return { messages: [...filtered, finalMsg] }
            })
            resetStreamingContent()
          }
        },
        // onError
        (error) => {
          setIsStreaming(false)
          message.error(error || '回答生成失败')
        },
      )

      abortControllerRef.current = controller
    },
    [currentConversationId],
  )

  // 停止生成
  const handleStop = useCallback(() => {
    abortControllerRef.current?.abort()
    setIsStreaming(false)
  }, [])

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: 'calc(100vh - 64px)',
        maxWidth: 1000,
        margin: '0 auto',
      }}
    >
      <ChatWindow
        messages={messages}
        isStreaming={isStreaming}
        streamingContent={streamingContent}
      />

      <ChatInput
        onSend={handleSend}
        onStop={handleStop}
        isStreaming={isStreaming}
        disabled={!currentConversationId}
      />
    </div>
  )
}
