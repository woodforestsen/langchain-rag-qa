import axios from 'axios'
import { message } from 'antd'

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器：自动附加 JWT token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// 响应拦截器：统一处理错误
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail || error.response?.data?.message

    if (status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      // 不在登录页面时才跳转
      if (window.location.pathname !== '/login') {
        message.error('登录已过期，请重新登录')
        window.location.href = '/login'
      }
    } else if (status === 403) {
      message.error('您没有权限执行此操作')
    } else if (status === 429) {
      message.error('请求过于频繁，请稍后再试')
    } else if (detail) {
      message.error(typeof detail === 'string' ? detail : '请求失败')
    }

    return Promise.reject(error)
  },
)

export default apiClient
