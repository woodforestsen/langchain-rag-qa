import { Popover, Tag, Typography } from 'antd'
import { FileTextOutlined } from '@ant-design/icons'
import type { CitationSource } from '@/types/chat'

const { Text, Paragraph } = Typography

interface Props {
  source: CitationSource
}

export default function SourceCitation({ source }: Props) {
  const content = (
    <div style={{ maxWidth: 400 }}>
      <Text strong>{source.document_name}</Text>
      <Paragraph
        ellipsis={{ rows: 5, expandable: true, symbol: '展开' }}
        style={{ marginTop: 8, marginBottom: 4, fontSize: 13, color: '#666' }}
      >
        {source.excerpt}
      </Paragraph>
      <Text type="secondary" style={{ fontSize: 12 }}>
        相关度: {(source.score * 100).toFixed(0)}%
      </Text>
    </div>
  )

  return (
    <Popover content={content} title="知识库来源" trigger="click">
      <Tag
        icon={<FileTextOutlined />}
        color="blue"
        style={{ cursor: 'pointer', marginBottom: 4 }}
      >
        来源 {source.index}
      </Tag>
    </Popover>
  )
}
