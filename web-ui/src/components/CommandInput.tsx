import { useState } from 'react';
import { Input, Button, Space, Select, message } from 'antd';
import { SendOutlined, ThunderboltOutlined } from '@ant-design/icons';

const { TextArea } = Input;

interface CommandInputProps {
  onExecute: (command: string, mode: string) => void;
  disabled?: boolean;
  loading?: boolean;
}

export const CommandInput: React.FC<CommandInputProps> = ({
  onExecute,
  disabled = false,
  loading = false,
}) => {
  const [command, setCommand] = useState('');
  const [mode, setMode] = useState('smart');
  const [isNatural, setIsNatural] = useState(false);

  const handleExecute = () => {
    if (!command.trim()) {
      message.warning('请输入命令');
      return;
    }

    onExecute(command, mode);
    setCommand('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.ctrlKey && e.key === 'Enter') {
      handleExecute();
    }
  };

  return (
    <div style={{
      position: 'fixed',
      bottom: '16px',
      left: '50%',
      transform: 'translateX(-50%)',
      width: 'calc(100% - 300px - 48px)',
      maxWidth: '800px',
      zIndex: 1000,
      backgroundColor: '#fff',
      padding: '16px 24px',
      borderRadius: '12px',
      boxShadow: '0 -4px 16px rgba(0, 0, 0, 0.12)',
      border: '1px solid #e8e8e8'
    }}>
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <Space style={{ width: '100%' }}>
          <Select
            value={isNatural ? 'natural' : 'command'}
            onChange={(value) => setIsNatural(value === 'natural')}
            style={{ width: 120 }}
          >
            <Select.Option value="command">
              <Space>
                <SendOutlined />
                WinDBG 命令
              </Space>
            </Select.Option>
            <Select.Option value="natural">
              <Space>
                <ThunderboltOutlined />
                自然语言
              </Space>
            </Select.Option>
          </Select>

          <Select
            value={mode}
            onChange={setMode}
            style={{ width: 100 }}
          >
            <Select.Option value="raw">Raw</Select.Option>
            <Select.Option value="smart">Smart</Select.Option>
            <Select.Option value="both">Both</Select.Option>
          </Select>
        </Space>

        <TextArea
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={
            isNatural
              ? '输入自然语言描述，例如：帮我分析崩溃'
              : '输入 WinDBG 命令，例如：!analyze -v'
          }
          disabled={disabled || loading}
          autoSize={{ minRows: 2, maxRows: 6 }}
        />

        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleExecute}
          disabled={disabled || loading || !command.trim()}
          loading={loading}
          block
        >
          执行命令 (Ctrl+Enter)
        </Button>
      </Space>
    </div>
  );
};
