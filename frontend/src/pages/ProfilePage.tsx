import { useState } from 'react'
import { Card, Descriptions, Button, Modal, Form, Input, message, Typography } from 'antd'
import { useAuthStore } from '@/stores/authStore'
import { authApi } from '@/api/auth'

const { Title } = Typography

export default function ProfilePage() {
  const { user } = useAuthStore()
  const [modalOpen, setModalOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [form] = Form.useForm()

  const handleChangePassword = async (values: { old_password: string; new_password: string }) => {
    setLoading(true)
    try {
      await authApi.changePassword(values)
      message.success('密码修改成功，请重新登录')
      setModalOpen(false)
      form.resetFields()
    } catch {
      // 错误已在拦截器中处理
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: 24, maxWidth: 800, margin: '0 auto' }}>
      <Title level={4} style={{ marginBottom: 24 }}>个人中心</Title>

      <Card>
        <Descriptions title="账号信息" column={1} bordered>
          <Descriptions.Item label="用户名">{user?.username}</Descriptions.Item>
          <Descriptions.Item label="角色">
            {user?.is_admin ? '管理员' : '普通用户'}
          </Descriptions.Item>
          <Descriptions.Item label="账号状态">
            {user?.is_active ? '正常' : '已禁用'}
          </Descriptions.Item>
        </Descriptions>

        <div style={{ marginTop: 24 }}>
          <Button type="primary" onClick={() => setModalOpen(true)}>
            修改密码
          </Button>
        </div>
      </Card>

      <Modal
        title="修改密码"
        open={modalOpen}
        onCancel={() => { setModalOpen(false); form.resetFields() }}
        footer={null}
        destroyOnClose
      >
        <Form form={form} onFinish={handleChangePassword} layout="vertical">
          <Form.Item
            name="old_password"
            label="旧密码"
            rules={[{ required: true, message: '请输入旧密码' }]}
          >
            <Input.Password />
          </Form.Item>
          <Form.Item
            name="new_password"
            label="新密码"
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 6, message: '密码至少6位' },
            ]}
          >
            <Input.Password />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              确认修改
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
