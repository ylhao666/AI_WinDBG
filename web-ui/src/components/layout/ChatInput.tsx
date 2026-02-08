import React, { useState } from 'react';
import { Input, Button, Space, Select, message } from 'antd';
import { SendOutlined, ThunderboltOutlined } from '@ant-design/icons';
import '../../styles/vscode-theme.css';

const { TextArea } = Input;

interface ChatInputProps {
  onExecute: (command: string, mode: string, isNatural: boolean) => void;
  disabled?: boolean;
  loading?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onExecute,
  disabled = false,
  loading = false,
}) => {
  const [command, setCommand] = useState('');
  const [mode, setMode] = useState('smart');
  const [isNatural, setIsNatural] = useState(false);

  const handleExecute = () => {
    if (!command.trim()) {
      message.warning('Please enter a command');
      return;
    }

    onExecute(command, mode, isNatural);
    setCommand('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.ctrlKey && e.key === 'Enter') {
      e.preventDefault();
      handleExecute();
    }
  };

  return (
    <div className="vscode-chat-input">
      <div className="vscode-chat-input-inner">
        <div className="vscode-chat-input-controls">
          <Select
            value={isNatural ? 'natural' : 'command'}
            onChange={(value) => setIsNatural(value === 'natural')}
            style={{ width: 140 }}
            size="small"
          >
            <Select.Option value="command">
              <Space>
                <SendOutlined />
                Command
              </Space>
            </Select.Option>
            <Select.Option value="natural">
              <Space>
                <ThunderboltOutlined />
                Natural
              </Space>
            </Select.Option>
          </Select>

          <Select
            value={mode}
            onChange={setMode}
            style={{ width: 100 }}
            size="small"
          >
            <Select.Option value="raw">Raw</Select.Option>
            <Select.Option value="smart">Smart</Select.Option>
            <Select.Option value="both">Both</Select.Option>
          </Select>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <TextArea
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              isNatural
                ? 'Describe what you want to do...'
                : 'Enter WinDBG command...'
            }
            disabled={disabled || loading}
            autoSize={{ minRows: 2, maxRows: 4 }}
            style={{ flex: 1, fontFamily: 'var(--vscode-font-family-mono)' }}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleExecute}
            disabled={disabled || loading || !command.trim()}
            loading={loading}
            style={{ alignSelf: 'flex-end', height: 'auto', minHeight: '60px' }}
          >
            Send
          </Button>
        </div>
      </div>
    </div>
  );
};
