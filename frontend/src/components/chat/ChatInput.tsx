import { useState, useRef, useEffect } from 'react'
import { Input, Button, Space } from 'antd'
import { SendOutlined, StopOutlined } from '@ant-design/icons'

const { TextArea } = Input

interface Props {
  onSend: (question: string) => void
  onStop: () => void
  isStreaming: boolean
  disabled?: boolean
}

export default function ChatInput({ onSend, onStop, isStreaming, disabled }: Props) {
  const [value, setValue] = useState('')
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (!isStreaming) {
      inputRef.current?.focus()
    }
  }, [isStreaming])

  const handleSend = () => {
    const trimmed = value.trim()
    if (!trimmed || isStreaming) return
    onSend(trimmed)
    setValue('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div
      style={{
        padding: '16px 24px',
        borderTop: '1px solid #f0f0f0',
        background: '#fff',
      }}
    >
      <div style={{ display: 'flex', gap: 12, alignItems: 'flex-end', maxWidth: 900, margin: '0 auto' }}>
        <TextArea
          ref={inputRef as any}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={isStreaming ? 'AI 正在回答中...' : '输入您的问题，按 Enter 发送，Shift+Enter 换行'}
          autoSize={{ minRows: 1, maxRows: 5 }}
          disabled={isStreaming || disabled}
          style={{ flex: 1, borderRadius: 8 }}
        />

        {isStreaming ? (
          <Button
            danger
            icon={<StopOutlined />}
            onClick={onStop}
            style={{ height: 40, borderRadius: 8 }}
          >
            停止
          </Button>
        ) : (
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            disabled={!value.trim() || disabled}
            style={{ height: 40, borderRadius: 8 }}
          >
            发送
          </Button>
        )}
      </div>

      <div style={{ textAlign: 'center', marginTop: 8 }}>
        <span style={{ fontSize: 12, color: '#999' }}>
          AI 回答基于知识库内容生成，仅供参考
        </span>
      </div>
    </div>
  )
}
