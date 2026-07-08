import { Avatar, Typography, Space, Tag } from 'antd'
import { UserOutlined, RobotOutlined } from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import SourceCitation from './SourceCitation'
import type { Message } from '@/types/chat'

const { Text } = Typography

interface Props {
  message: Message
  isStreaming?: boolean
}

export default function MessageBubble({ message, isStreaming }: Props) {
  const isUser = message.role === 'user'

  return (
    <div
      style={{
        display: 'flex',
        gap: 12,
        padding: '16px 24px',
        flexDirection: isUser ? 'row-reverse' : 'row',
        background: isUser ? 'transparent' : 'rgba(0,0,0,0.02)',
      }}
    >
      <Avatar
        icon={isUser ? <UserOutlined /> : <RobotOutlined />}
        style={{
          backgroundColor: isUser ? '#1677ff' : '#52c41a',
          flexShrink: 0,
        }}
      />

      <div style={{ maxWidth: '75%', minWidth: 200 }}>
        <div style={{ marginBottom: 4 }}>
          <Text strong style={{ fontSize: 13 }}>
            {isUser ? '你' : 'AI 助手'}
          </Text>
        </div>

        <div className={`message-content ${isStreaming ? 'streaming-cursor' : ''}`}>
          {isUser ? (
            <Text style={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>{message.content}</Text>
          ) : (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          )}
        </div>

        {/* 知识库引用展示 */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div style={{ marginTop: 12 }}>
            <Space size={[4, 4]} wrap>
              <Text type="secondary" style={{ fontSize: 12 }}>📚 参考来源：</Text>
              {message.sources.map((source, idx) => (
                <SourceCitation key={idx} source={source} />
              ))}
            </Space>
          </div>
        )}
      </div>
    </div>
  )
}
