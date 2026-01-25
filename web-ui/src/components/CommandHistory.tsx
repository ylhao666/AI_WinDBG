import { useState } from 'react';
import { Card, List, Typography, Empty, Tag, Space } from 'antd';
import { HistoryOutlined, CopyOutlined } from '@ant-design/icons';
import { message } from 'antd';

const { Text } = Typography;

interface CommandHistoryProps {
  history: string[];
  onSelect: (command: string) => void;
}

export const CommandHistory: React.FC<CommandHistoryProps> = ({ history, onSelect }) => {
  const [copied, setCopied] = useState<number | null>(null);

  const handleCopy = async (command: string, index: number) => {
    try {
      await navigator.clipboard.writeText(command);
      setCopied(index);
      message.success('已复制到剪贴板');
      setTimeout(() => setCopied(null), 2000);
    } catch (error) {
      message.error('复制失败');
    }
  };

  if (history.length === 0) {
    return (
      <Card
        title={
          <span>
            <HistoryOutlined /> 命令历史
          </span>
        }
      >
        <Empty description="暂无命令历史" />
      </Card>
    );
  }

  return (
    <Card
      title={
        <span>
          <HistoryOutlined /> 命令历史
        </span>
      }
    >
      <List
        dataSource={history.slice().reverse()}
        renderItem={(command, index) => (
          <List.Item
            key={history.length - 1 - index}
            onClick={() => onSelect(command)}
            style={{ cursor: 'pointer' }}
            actions={[
              <CopyOutlined
                key="copy"
                onClick={(e) => {
                  e.stopPropagation();
                  handleCopy(command, history.length - 1 - index);
                }}
                style={{ color: copied === history.length - 1 - index ? '#52c41a' : undefined }}
              />,
            ]}
          >
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <Text code ellipsis style={{ width: '100%' }}>
                {command}
              </Text>
              <Tag color="blue">#{history.length - index}</Tag>
            </Space>
          </List.Item>
        )}
      />
    </Card>
  );
};
