import { useState } from 'react'
import { Card, Form, Input, Button, Typography, message, Space } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { Link, useNavigate } from 'react-router-dom'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/authStore'
import type { LoginRequest } from '@/types/auth'

const { Title, Text } = Typography

export default function LoginPage() {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuthStore()

  const handleSubmit = async (values: LoginRequest) => {
    setLoading(true)
    try {
      const res = await authApi.login(values)
      const token = res.data.access_token

      // 先存 token，再获取用户信息（否则请求头里没有 Authorization）
      localStorage.setItem('access_token', token)
      const userRes = await authApi.getMe()
      login(token, userRes.data)

      message.success('登录成功')
      navigate('/chat')
    } catch {
      localStorage.removeItem('access_token')
      // 错误已在拦截器中处理
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-bg">
      <Card style={{ width: 400, borderRadius: 12, boxShadow: '0 8px 24px rgba(0,0,0,0.15)' }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <Title level={3} style={{ marginBottom: 4 }}>📚 知识库问答系统</Title>
          <Text type="secondary">请登录您的账号</Text>
        </div>

        <Form onFinish={handleSubmit} size="large" autoComplete="off">
          <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>

          <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              登 录
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: 'center' }}>
          <Space>
            <Text type="secondary">还没有账号？</Text>
            <Link to="/register">立即注册</Link>
          </Space>
        </div>

        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <Text type="secondary" style={{ fontSize: 12 }}>
            管理员账号: admin / 123456
          </Text>
        </div>
      </Card>
    </div>
  )
}
