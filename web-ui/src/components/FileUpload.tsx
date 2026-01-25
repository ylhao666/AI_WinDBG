import { useState, useEffect } from 'react';
import { Upload, message, Card, Space, Button, Typography, Tag } from 'antd';
import { InboxOutlined, FileTextOutlined, FolderOpenOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import { isElectron, openFileSelector, validateFilePath, formatFileSize } from '../utils/electron';

const { Dragger } = Upload;
const { Text, Paragraph } = Typography;

interface FileUploadProps {
  onLoad: (filepath: string) => void;
  loading?: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onLoad, loading }) => {
  const [fileList, setFileList] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState<{
    path: string;
    name: string;
    size: number;
  } | null>(null);

  useEffect(() => {
    console.log('[FileUpload] 组件已挂载');
    console.log(`[FileUpload] Electron 环境: ${isElectron()}`);
  }, []);

  const handleElectronSelect = async () => {
    try {
      console.log('[FileUpload] 打开 Electron 文件选择对话框');
      const result = await openFileSelector();

      if (result.success && result.filePath) {
        setSelectedFile({
          path: result.filePath,
          name: result.fileName || '',
          size: result.fileSize || 0
        });
        console.log(`[FileUpload] 文件已选择: ${result.filePath}`);
        message.success(`已选择文件: ${result.fileName}`);
      } else if (result.error) {
        console.warn(`[FileUpload] 文件选择失败: ${result.error}`);
        message.warning(result.error);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '未知错误';
      console.error('[FileUpload] 文件选择错误:', errorMessage);
      message.error('选择文件失败');
    }
  };

  const props: UploadProps = {
    name: 'file',
    multiple: false,
    fileList,
    beforeUpload: (file) => {
      const isDmp = file.name.endsWith('.dmp');
      if (!isDmp) {
        message.error('只能上传 .dmp 文件');
        return false;
      }
      setFileList([file]);
      return false;
    },
    onRemove: () => {
      setFileList([]);
    },
  };

  const handleLoad = async () => {
    if (isElectron()) {
      if (!selectedFile) {
        message.warning('请先选择文件');
        return;
      }

      try {
        console.log(`[FileUpload] 验证文件路径: ${selectedFile.path}`);
        const validation = await validateFilePath(selectedFile.path);

        if (!validation.success) {
          message.error(validation.error || '文件验证失败');
          return;
        }

        console.log(`[FileUpload] 加载文件: ${selectedFile.path}`);
        onLoad(selectedFile.path);
        setSelectedFile(null);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : '未知错误';
        console.error('[FileUpload] 加载文件错误:', errorMessage);
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
        onLoad(filepath);
        setFileList([]);
      } catch (error) {
        message.error('加载文件失败');
      }
    }
  };

  return (
    <Card
      title={
        <span>
          <FileTextOutlined /> 加载转储文件
        </span>
      }
    >
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        {isElectron() ? (
          <>
            <Button
              type="primary"
              icon={<FolderOpenOutlined />}
              onClick={handleElectronSelect}
              block
              disabled={loading}
            >
              选择转储文件
            </Button>

            {selectedFile && (
              <Card size="small" style={{ backgroundColor: '#f5f5f5' }}>
                <Space direction="vertical" size="small" style={{ width: '100%' }}>
                  <Text strong>已选择文件:</Text>
                  <Paragraph
                    ellipsis={{ rows: 2, tooltip: selectedFile.path }}
                    style={{ margin: 0, fontSize: '12px' }}
                  >
                    {selectedFile.path}
                  </Paragraph>
                  <Space>
                    <Tag color="blue">{selectedFile.name}</Tag>
                    <Tag color="green">{formatFileSize(selectedFile.size)}</Tag>
                  </Space>
                  <Button
                    type="primary"
                    onClick={handleLoad}
                    loading={loading}
                    block
                  >
                    加载文件
                  </Button>
                </Space>
              </Card>
            )}
          </>
        ) : (
          <>
            <Dragger {...props}>
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
              <p className="ant-upload-hint">
                支持 .dmp 格式的崩溃转储文件
              </p>
            </Dragger>

            {fileList.length > 0 && (
              <Button
                type="primary"
                onClick={handleLoad}
                loading={loading}
                block
              >
                加载文件
              </Button>
            )}
          </>
        )}
      </Space>
    </Card>
  );
};
