import { Card, Progress, Button, Space, Typography, Tag, Alert, Spin } from 'antd';
import {
  LoadingOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  StopOutlined,
} from '@ant-design/icons';
import { AnalysisProgress, AnalysisStatus } from '../types';

const { Text } = Typography;

interface AnalysisProgressProps {
  progress: AnalysisProgress | null;
  onCancel?: () => void;
}

export const AnalysisProgressView: React.FC<AnalysisProgressProps> = ({
  progress,
  onCancel
}) => {

  if (!progress) {
    return null;
  }

  const getStatusIcon = () => {
    switch (progress.status) {
      case AnalysisStatus.PENDING:
        return <LoadingOutlined spin />;
      case AnalysisStatus.RUNNING:
        return <LoadingOutlined spin />;
      case AnalysisStatus.COMPLETED:
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case AnalysisStatus.ERROR:
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      case AnalysisStatus.CANCELLED:
        return <StopOutlined style={{ color: '#faad14' }} />;
      default:
        return <LoadingOutlined spin />;
    }
  };

  const getStatusText = () => {
    switch (progress.status) {
      case AnalysisStatus.PENDING:
        return '等待中';
      case AnalysisStatus.RUNNING:
        return '分析中';
      case AnalysisStatus.COMPLETED:
        return '已完成';
      case AnalysisStatus.ERROR:
        return '分析失败';
      case AnalysisStatus.CANCELLED:
        return '已取消';
      default:
        return '未知状态';
    }
  };

  const getStatusColor = () => {
    switch (progress.status) {
      case AnalysisStatus.PENDING:
        return 'default';
      case AnalysisStatus.RUNNING:
        return 'processing';
      case AnalysisStatus.COMPLETED:
        return 'success';
      case AnalysisStatus.ERROR:
        return 'error';
      case AnalysisStatus.CANCELLED:
        return 'warning';
      default:
        return 'default';
    }
  };

  const isRunning = progress.status === AnalysisStatus.RUNNING;
  const canCancel = isRunning || progress.status === AnalysisStatus.PENDING;

  return (
    <Card 
      title={
        <Space>
          {getStatusIcon()}
          <span>智能分析进度</span>
        </Space>
      }
      extra={
        canCancel && onCancel && (
          <Button 
            danger 
            size="small" 
            icon={<StopOutlined />}
            onClick={onCancel}
          >
            取消
          </Button>
        )
      }
    >
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <div>
          <Space direction="vertical" style={{ width: '100%' }} size="small">
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Text strong>状态</Text>
              <Tag color={getStatusColor()}>{getStatusText()}</Tag>
            </div>
            
            <Progress 
              percent={progress.progress} 
              status={getStatusColor() as any}
              strokeColor={{
                '0%': '#108ee9',
                '100%': '#87d068',
              }}
            />
            
            <Text type="secondary">{progress.message}</Text>
          </Space>
        </div>

        {progress.error && (
          <Alert
            message="分析失败"
            description={progress.error}
            type="error"
            showIcon
            icon={<CloseCircleOutlined />}
          />
        )}

        {isRunning && (
          <div style={{ textAlign: 'center', padding: '16px' }}>
            <Spin size="large" />
          </div>
        )}
      </Space>
    </Card>
  );
};