import { Layout, Button, Dropdown, Space, Avatar } from 'antd'
import {
  UserOutlined,
  LogoutOutlined,
  SettingOutlined,
  BulbOutlined,
  BulbFilled,
  DatabaseOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useThemeStore } from '@/stores/themeStore'

const { Header } = Layout

export default function HeaderBar() {
  const navigate = useNavigate()
  const { user, isAdmin, logout } = useAuthStore()
  const { isDark, toggle } = useThemeStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const userMenuItems = [
    {
      key: 'profile',
      icon: <SettingOutlined />,
      label: '个人中心',
      onClick: () => navigate('/profile'),
    },
    { type: 'divider' as const },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
      onClick: handleLogout,
    },
  ]

  return (
    <Header
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        background: isDark ? '#141414' : '#fff',
        borderBottom: '1px solid #f0f0f0',
        zIndex: 100,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <h1 style={{ margin: 0, fontSize: 18, fontWeight: 600, whiteSpace: 'nowrap' }}>
          📚 RAG 知识库问答系统
        </h1>
        {isAdmin && (
          <Button
            type="primary"
            icon={<DatabaseOutlined />}
            onClick={() => navigate('/knowledge')}
            size="small"
          >
            知识库管理
          </Button>
        )}
      </div>

      <Space>
        <Button
          type="text"
          icon={isDark ? <BulbFilled style={{ color: '#faad14' }} /> : <BulbOutlined />}
          onClick={toggle}
        />
        <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
          <Space style={{ cursor: 'pointer' }}>
            <Avatar size="small" icon={<UserOutlined />} />
            <span>{user?.username || '用户'}</span>
          </Space>
        </Dropdown>
      </Space>
    </Header>
  )
}
