import { useState } from 'react';
import { Upload, message, Card, Space, Button } from 'antd';
import { InboxOutlined, FileTextOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';

const { Dragger } = Upload;

interface FileUploadProps {
  onLoad: (filepath: string) => void;
  loading?: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onLoad, loading }) => {
  const [fileList, setFileList] = useState<any[]>([]);

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
      </Space>
    </Card>
  );
};
