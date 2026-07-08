import { Outlet } from 'react-router-dom'
import { Layout } from 'antd'
import Sidebar from './Sidebar'
import HeaderBar from './Header'

const { Content } = Layout

export default function MainLayout() {
  return (
    <Layout style={{ height: '100vh' }}>
      <HeaderBar />
      <Layout>
        <Sidebar />
        <Content style={{ padding: 0, overflow: 'auto', background: 'var(--bg-color, #f5f5f5)' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
