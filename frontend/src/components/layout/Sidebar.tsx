import { useEffect, useState } from 'react'
import { Layout, Button, List, Typography, Popconfirm, Space, message } from 'antd'
import { PlusOutlined, DeleteOutlined, MessageOutlined } from '@ant-design/icons'
import { useNavigate, useParams } from 'react-router-dom'
import { useChatStore } from '@/stores/chatStore'
import { conversationApi } from '@/api/conversation'

const { Sider } = Layout
const { Text } = Typography

export default function Sidebar() {
  const navigate = useNavigate()
  const { convId } = useParams<{ convId: string }>()
  const [creating, setCreating] = useState(false)
  const {
    conversations,
    currentConversationId,
    setConversations,
    setCurrentConversationId,
    addConversation,
    removeConversation,
  } = useChatStore()

  useEffect(() => {
    loadConversations()
  }, [])

  // 从 URL 参数同步当前会话 ID
  useEffect(() => {
    if (convId) {
      setCurrentConversationId(Number(convId))
    }
  }, [convId])

  const loadConversations = async () => {
    try {
      const res = await conversationApi.list(1, 50)
      setConversations(res.data.items)
    } catch {
      // 加载失败忽略
    }
  }

  const handleCreate = async () => {
    if (creating) return
    setCreating(true)
    try {
      const res = await conversationApi.create()
      addConversation(res.data)
      navigate(`/chat/${res.data.id}`)
      message.success('新对话已创建')
    } catch (err: any) {
      console.error('创建对话失败:', err)
      const status = err?.response?.status
      const detail = err?.response?.data?.detail || err?.message || '创建对话失败'
      if (status === 401) {
        message.error('登录已过期，请重新登录')
      } else {
        message.error(`${detail}`)
      }
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await conversationApi.delete(id)
      removeConversation(id)
      if (currentConversationId === id) {
        navigate('/chat')
      }
    } catch {
      // 删除失败
    }
  }

  const handleSelect = (id: number) => {
    navigate(`/chat/${id}`)
  }

  return (
    <Sider
      width={260}
      style={{
        background: '#fafafa',
        borderRight: '1px solid #f0f0f0',
        display: 'flex',
        flexDirection: 'column',
        height: 'calc(100vh - 64px)',
        overflow: 'hidden',
      }}
    >
      <div style={{ padding: '12px 16px' }}>
        <Button
          type="dashed"
          icon={<PlusOutlined />}
          onClick={handleCreate}
          loading={creating}
          block
          style={{ height: 40 }}
        >
          新建对话
        </Button>
      </div>

      <div style={{ flex: 1, overflow: 'auto', padding: '0 8px' }}>
        <List
          dataSource={conversations}
          locale={{ emptyText: '暂无对话，点击上方创建' }}
          renderItem={(item) => (
            <List.Item
              key={item.id}
              onClick={() => handleSelect(item.id)}
              style={{
                padding: '10px 12px',
                borderRadius: 8,
                marginBottom: 4,
                cursor: 'pointer',
                background:
                  currentConversationId === item.id || Number(convId) === item.id
                    ? '#e6f4ff'
                    : 'transparent',
                border: 'none',
              }}
              actions={[
                <Popconfirm
                  key="delete"
                  title="确定删除此对话？"
                  onConfirm={(e) => {
                    e?.stopPropagation()
                    handleDelete(item.id)
                  }}
                  onCancel={(e) => e?.stopPropagation()}
                >
                  <Button
                    type="text"
                    size="small"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={(e) => e.stopPropagation()}
                  />
                </Popconfirm>,
              ]}
            >
              <List.Item.Meta
                avatar={<MessageOutlined style={{ color: '#1677ff' }} />}
                title={
                  <Text
                    ellipsis={{ tooltip: item.title }}
                    style={{ fontSize: 14, maxWidth: 160 }}
                  >
                    {item.title}
                  </Text>
                }
                description={
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {new Date(item.updated_at).toLocaleDateString('zh-CN')}
                  </Text>
                }
              />
            </List.Item>
          )}
        />
      </div>
    </Sider>
  )
}
