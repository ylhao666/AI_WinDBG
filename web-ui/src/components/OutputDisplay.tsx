import { useEffect, useRef } from 'react';
import { Card, Typography, Empty } from 'antd';
import { CodeOutlined } from '@ant-design/icons';

const { Text, Paragraph } = Typography;

interface OutputDisplayProps {
  output: string;
  command?: string;
}

export const OutputDisplay: React.FC<OutputDisplayProps> = ({ output, command }) => {
  const outputRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [output]);

  if (!output) {
    return (
      <Card
        title={
          <span>
            <CodeOutlined /> 输出
          </span>
        }
      >
        <Empty description="暂无输出" />
      </Card>
    );
  }

  return (
    <Card
      title={
        <span>
          <CodeOutlined /> 输出
        </span>
      }
    >
      {command && (
        <Paragraph>
          <Text strong>命令: </Text>
          <Text code>{command}</Text>
        </Paragraph>
      )}
      <div
        ref={outputRef}
        style={{
          backgroundColor: '#1e1e1e',
          color: '#d4d4d4',
          padding: '12px',
          borderRadius: '4px',
          maxHeight: '400px',
          overflow: 'auto',
          fontFamily: 'Consolas, Monaco, "Courier New", monospace',
          fontSize: '13px',
          lineHeight: '1.5',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-all',
        }}
      >
        {output}
      </div>
    </Card>
  );
};
