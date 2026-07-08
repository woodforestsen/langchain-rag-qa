import type { ChatRequest } from '@/types/chat'

export const chatApi = {
  /** 创建 SSE 连接进行流式问答 */
  streamChat: (
    conversationId: number,
    request: ChatRequest,
    onToken: (token: string) => void,
    onSources: (sources: unknown[]) => void,
    onDone: (data: unknown) => void,
    onError: (error: string) => void,
  ): AbortController => {
    const controller = new AbortController()
    const token = localStorage.getItem('access_token')

    fetch(`/api/chat/${conversationId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(request),
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          const errData = await response.json().catch(() => ({}))
          throw new Error(errData.detail || `HTTP ${response.status}`)
        }

        const reader = response.body?.getReader()
        if (!reader) throw new Error('不支持流式响应')

        const decoder = new TextDecoder()
        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const parsed = JSON.parse(line.slice(6))
                switch (parsed.event) {
                  case 'token':
                    onToken(parsed.data)
                    break
                  case 'sources':
                    onSources(parsed.data)
                    break
                  case 'done':
                    onDone(parsed.data)
                    break
                  case 'error':
                    onError(parsed.data)
                    break
                }
              } catch {
                // 跳过解析失败的行
              }
            }
          }
        }
      })
      .catch((err) => {
        if (err.name !== 'AbortError') {
          onError(err.message || '网络请求失败')
        }
      })

    return controller
  },

  /** 导出对话为 Markdown */
  exportConversation: (conversationId: number) =>
    fetch(`/api/chat/${conversationId}/export`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
    }).then((r) => r.json()),
}
