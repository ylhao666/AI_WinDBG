import React, { useState } from 'react';
import { message, Button, Space, Typography, Empty } from 'antd';
import { InboxOutlined, FileTextOutlined, FolderOpenOutlined, HistoryOutlined } from '@ant-design/icons';
import { isElectron, openFileSelector, validateFilePath } from '../../utils/electron';
import '../../styles/vscode-theme.css';

const { Text } = Typography;

interface SidebarProps {
  history: string[];
  onLoadDump: (filepath: string) => void;
  loading?: boolean;
  onSelectHistory: (command: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ history, onLoadDump, loading, onSelectHistory }) => {
  const [fileList, setFileList] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState<{
    path: string;
    name: string;
    size: number;
  } | null>(null);

  const handleElectronSelect = async () => {
    try {
      const result = await openFileSelector();

      if (result.success && result.filePath) {
        setSelectedFile({
          path: result.filePath,
          name: result.fileName || '',
          size: result.fileSize || 0
        });
        message.success(`已选择文件: ${result.fileName}`);
      } else if (result.error) {
        message.warning(result.error);
      }
    } catch (error) {
      message.error('选择文件失败');
    }
  };

  const handleLoad = async () => {
    if (isElectron()) {
      if (!selectedFile) {
        message.warning('请先选择文件');
        return;
      }

      try {
        const validation = await validateFilePath(selectedFile.path);

        if (!validation.success) {
          message.error(validation.error || '文件验证失败');
          return;
        }

        onLoadDump(selectedFile.path);
        setSelectedFile(null);
      } catch (error) {
        message.error('加载文件失败');
      }
    } else {
      if (fileList.length === 0) {
        message.warning('请先选择文件');
        return;
      }

      const file = fileList[0];
      const filepath = file.name;

      try {
        onLoadDump(filepath);
        setFileList([]);
      } catch (error) {
        message.error('加载文件失败');
      }
    }
  };

  return (
    <div className="vscode-sidebar">
      <div className="vscode-sidebar-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--vscode-fg-primary)', fontWeight: 500 }}>
          <FileTextOutlined />
          <span>Load Dump</span>
        </div>
      </div>
      <div className="vscode-sidebar-content">
        <div style={{ marginBottom: '16px' }}>
          {isElectron() ? (
            <Space direction="vertical" style={{ width: '100%' }} size="small">
              <Button
                icon={<FolderOpenOutlined />}
                onClick={handleElectronSelect}
                block
                disabled={loading}
                style={{
                  backgroundColor: 'var(--vscode-bg-secondary)',
                  borderColor: 'var(--vscode-border)',
                  color: 'var(--vscode-fg-primary)'
                }}
              >
                Select File
              </Button>

              {selectedFile && (
                <div style={{
                  backgroundColor: 'var(--vscode-bg-tertiary)',
                  border: '1px solid var(--vscode-border)',
                  borderRadius: '4px',
                  padding: '8px'
                }}>
                  <Text ellipsis style={{
                    display: 'block',
                    fontSize: '12px',
                    color: 'var(--vscode-fg-secondary)',
                    marginBottom: '4px'
                  }}>
                    {selectedFile.path}
                  </Text>
                  <Button
                    type="primary"
                    onClick={handleLoad}
                    loading={loading}
                    block
                    size="small"
                  >
                    Load Dump
                  </Button>
                </div>
              )}
            </Space>
          ) : (
            <Space direction="vertical" style={{ width: '100%' }} size="small">
              <div style={{
                border: '1px dashed var(--vscode-border)',
                borderRadius: '4px',
                padding: '16px',
                textAlign: 'center',
                backgroundColor: 'var(--vscode-bg-secondary)',
                cursor: 'pointer'
              }}>
                <InboxOutlined style={{ fontSize: '24px', color: 'var(--vscode-fg-secondary)', marginBottom: '8px' }} />
                <div style={{ fontSize: '12px', color: 'var(--vscode-fg-secondary)' }}>
                  Click or drag .dmp file here
                </div>
              </div>

              {fileList.length > 0 && (
                <Button
                  type="primary"
                  onClick={handleLoad}
                  loading={loading}
                  block
                  size="small"
                >
                  Load Dump
                </Button>
              )}
            </Space>
          )}
        </div>

        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--vscode-fg-primary)', fontWeight: 500, marginBottom: '8px' }}>
            <HistoryOutlined />
            <span>History</span>
          </div>
          {history.length === 0 ? (
            <Empty description="No history" style={{ color: 'var(--vscode-fg-secondary)' }} image={Empty.PRESENTED_IMAGE_SIMPLE} />
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              {history.slice().reverse().map((command, index) => (
                <div
                  key={history.length - 1 - index}
                  className="vscode-history-item"
                  onClick={() => onSelectHistory(command)}
                >
                  <span className="vscode-history-item-number">#{history.length - index}</span>
                  <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {command}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
