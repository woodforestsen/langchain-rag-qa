import { useEffect, useState, useCallback } from 'react'
import {
  Card,
  Table,
  Button,
  Upload,
  Space,
  Tag,
  Popconfirm,
  Typography,
  message,
  Row,
  Col,
  Statistic,
  Modal,
  Drawer,
} from 'antd'
import {
  UploadOutlined,
  DeleteOutlined,
  ReloadOutlined,
  FileTextOutlined,
  FilePdfOutlined,
  FileExcelOutlined,
  FileMarkdownOutlined,
  InboxOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { knowledgeBaseApi } from '@/api/knowledgeBase'
import type { DocumentItem, DocumentDetail, KnowledgeStats } from '@/types/document'

const { Title } = Typography
const { Dragger } = Upload

const fileIconMap: Record<string, React.ReactNode> = {
  pdf: <FilePdfOutlined style={{ color: '#ff4d4f' }} />,
  docx: <FileTextOutlined style={{ color: '#1677ff' }} />,
  txt: <FileTextOutlined />,
  md: <FileMarkdownOutlined style={{ color: '#52c41a' }} />,
  csv: <FileExcelOutlined style={{ color: '#52c41a' }} />,
  xlsx: <FileExcelOutlined style={{ color: '#52c41a' }} />,
}

const statusColorMap: Record<string, string> = {
  processing: 'processing',
  ready: 'success',
  error: 'error',
}

const statusLabelMap: Record<string, string> = {
  processing: '处理中',
  ready: '已完成',
  error: '失败',
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function KnowledgeBasePage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [stats, setStats] = useState<KnowledgeStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [uploadOpen, setUploadOpen] = useState(false)
  const [detailOpen, setDetailOpen] = useState(false)
  const [selectedDoc, setSelectedDoc] = useState<DocumentDetail | null>(null)
  const [uploading, setUploading] = useState(false)
  const [pendingFiles, setPendingFiles] = useState<File[]>([])

  const pageSize = 20

  const loadDocuments = useCallback(async () => {
    setLoading(true)
    try {
      const res = await knowledgeBaseApi.listDocuments(page, pageSize)
      setDocuments(res.data.items)
      setTotal(res.data.total)
    } catch {
      // 错误已处理
    } finally {
      setLoading(false)
    }
  }, [page])

  const loadStats = useCallback(async () => {
    try {
      const res = await knowledgeBaseApi.getStats()
      setStats(res.data)
    } catch {
      // 忽略
    }
  }, [])

  useEffect(() => {
    loadDocuments()
    loadStats()
  }, [loadDocuments, loadStats])

  const handleBatchUpload = async () => {
    if (pendingFiles.length === 0) return
    setUploading(true)
    try {
      const res = await knowledgeBaseApi.upload(pendingFiles)
      const data = res.data as any
      const results = data?.results
      if (results) {
        const ok = results.filter((r: any) => r.status === 'ok').length
        message.success(`上传完成: ${ok}/${results.length} 个成功`)
      }
      setUploadOpen(false)
      setPendingFiles([])
      loadDocuments()
      loadStats()
    } catch (err: any) {
      const detail = err?.response?.data?.detail || err?.response?.data?.error || '上传失败'
      message.error(detail)
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await knowledgeBaseApi.deleteDocument(id)
      message.success('文档已删除')
      loadDocuments()
      loadStats()
    } catch {
      // 错误已处理
    }
  }

  const handleViewDetail = async (id: number) => {
    try {
      const res = await knowledgeBaseApi.getDocument(id)
      setSelectedDoc(res.data)
      setDetailOpen(true)
    } catch {
      // 错误已处理
    }
  }

  const columns: ColumnsType<DocumentItem> = [
    {
      title: '文件名',
      dataIndex: 'filename',
      key: 'filename',
      render: (name: string, record) => (
        <Space>
          {fileIconMap[record.file_type] || <FileTextOutlined />}
          <a onClick={() => handleViewDetail(record.id)}>{name}</a>
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'file_type',
      key: 'file_type',
      width: 80,
      render: (type: string) => <Tag>{type.toUpperCase()}</Tag>,
    },
    {
      title: '大小',
      dataIndex: 'file_size',
      key: 'file_size',
      width: 100,
      render: (size: number) => formatFileSize(size),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={statusColorMap[status] || 'default'}>
          {statusLabelMap[status] || status}
        </Tag>
      ),
    },
    {
      title: '分块数',
      dataIndex: 'chunk_count',
      key: 'chunk_count',
      width: 80,
    },
    {
      title: '上传时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (time: string) => new Date(time).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 120,
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" onClick={() => handleViewDetail(record.id)}>
            查看
          </Button>
          <Popconfirm title="确定删除此文档？删除后不可恢复" onConfirm={() => handleDelete(record.id)}>
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div style={{ padding: 24, height: 'calc(100vh - 64px)', overflow: 'auto' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        {/* 统计卡片 */}
        {stats && (
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col span={6}>
              <Card>
                <Statistic title="文档总数" value={stats.total_documents} prefix={<FileTextOutlined />} />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic title="向量分块" value={stats.total_chunks} prefix={<InboxOutlined />} />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic title="总字符数" value={stats.total_chars} />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title="文档类型"
                  value={Object.keys(stats.documents_by_type).length}
                  suffix="种"
                />
              </Card>
            </Col>
          </Row>
        )}

        {/* 工具栏 */}
        <Card
          title={<Title level={5} style={{ margin: 0 }}>📁 知识库文档管理</Title>}
          extra={
            <Space>
              <Button icon={<ReloadOutlined />} onClick={() => { loadDocuments(); loadStats() }}>
                刷新
              </Button>
              <Button type="primary" icon={<UploadOutlined />} onClick={() => setUploadOpen(true)}>
                上传文档
              </Button>
            </Space>
          }
        >
          <Table
            columns={columns}
            dataSource={documents}
            rowKey="id"
            loading={loading}
            pagination={{
              current: page,
              pageSize,
              total,
              onChange: (p) => setPage(p),
              showSizeChanger: false,
              showTotal: (t) => `共 ${t} 个文档`,
            }}
          />
        </Card>

        {/* 上传弹窗 */}
        <Modal
          title="上传知识库文档"
          open={uploadOpen}
          onCancel={() => setUploadOpen(false)}
          footer={null}
          destroyOnClose
        >
          <Dragger
            accept=".pdf,.docx,.txt,.md,.csv,.xlsx"
            multiple
            showUploadList={pendingFiles.length > 0}
            fileList={pendingFiles.map((f, i) => ({
              uid: `${i}-${f.name}`,
              name: f.name,
              status: 'done' as const,
            }))}
            customRequest={() => {}} // 阻止默认上传行为
            onChange={(info) => {
              const files = info.fileList
                .map((f: any) => f.originFileObj as File)
                .filter(Boolean)
              setPendingFiles(files)
            }}
            onRemove={(file) => {
              setPendingFiles((prev) => prev.filter((f, i) => `${i}-${f.name}` !== file.uid))
            }}
            disabled={uploading}
          >
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">点击或拖拽文件到此区域选择</p>
            <p className="ant-upload-hint">
              支持 PDF、Word、Excel、CSV、Markdown、纯文本格式，单文件最大 400MB，可选多个文件
            </p>
          </Dragger>
          {pendingFiles.length > 0 && (
            <div style={{ marginTop: 16, textAlign: 'center' }}>
              <Button
                type="primary"
                size="large"
                icon={<UploadOutlined />}
                loading={uploading}
                onClick={handleBatchUpload}
              >
                开始上传（{pendingFiles.length} 个文件）
              </Button>
            </div>
          )}
        </Modal>

        {/* 文档详情抽屉 */}
        <Drawer
          title={selectedDoc?.filename}
          open={detailOpen}
          onClose={() => setDetailOpen(false)}
          width={640}
        >
          {selectedDoc && (
            <>
              <p><strong>文件类型：</strong>{selectedDoc.file_type}</p>
              <p><strong>文件大小：</strong>{formatFileSize(selectedDoc.file_size)}</p>
              <p><strong>分块数量：</strong>{selectedDoc.chunk_count}</p>
              <p><strong>状态：</strong>
                <Tag color={statusColorMap[selectedDoc.status]}>{statusLabelMap[selectedDoc.status]}</Tag>
              </p>
              {selectedDoc.error_message && (
                <p><strong>错误信息：</strong><Tag color="red">{selectedDoc.error_message}</Tag></p>
              )}

              <Title level={5} style={{ marginTop: 24 }}>文档分块预览</Title>
              {selectedDoc.chunks?.map((chunk) => (
                <Card key={chunk.id} size="small" style={{ marginBottom: 8 }} title={`分块 ${chunk.chunk_index + 1}（${chunk.char_count} 字符）`}>
                  <Typography.Paragraph
                    ellipsis={{ rows: 3, expandable: true, symbol: '展开' }}
                    style={{ whiteSpace: 'pre-wrap', fontSize: 13 }}
                  >
                    {chunk.content}
                  </Typography.Paragraph>
                </Card>
              ))}
            </>
          )}
        </Drawer>
      </div>
    </div>
  )
}
