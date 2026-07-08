import { useEffect, useRef } from 'react'
import { Empty, Spin } from 'antd'
import { LoadingOutlined } from '@ant-design/icons'
import MessageBubble from './MessageBubble'
import type { Message } from '@/types/chat'

interface Props {
  messages: Message[]
  isStreaming: boolean
  streamingContent: string
}

export default function ChatWindow({ messages, isStreaming, streamingContent }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  // 自动滚动到底部
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingContent])

  return (
    <div
      style={{
        flex: 1,
        overflow: 'auto',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {messages.length === 0 && !isStreaming ? (
        <div
          style={{
            flex: 1,
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
          }}
        >
          <Empty description="开始新的对话吧！输入您关于商品的问题" />
        </div>
      ) : (
        <>
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}

          {/* 流式响应实时展示 */}
          {isStreaming && streamingContent && (
            <MessageBubble
              message={{
                id: -1,
                conversation_id: 0,
                role: 'assistant',
                content: streamingContent,
                created_at: '',
              }}
              isStreaming
            />
          )}

          {/* 加载状态 */}
          {isStreaming && !streamingContent && (
            <div style={{ padding: '24px', textAlign: 'center' }}>
              <Spin indicator={<LoadingOutlined style={{ fontSize: 24 }} spin />} />
              <div style={{ marginTop: 8, color: '#999' }}>AI 正在思考...</div>
            </div>
          )}
        </>
      )}

      <div ref={bottomRef} />
    </div>
  )
}
