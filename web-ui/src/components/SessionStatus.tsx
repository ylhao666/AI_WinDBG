import { useState, useEffect } from 'react';
import type { SessionStatus } from '../types';
import { sessionAPI } from '../api/session';
import { Card, Badge, Space, Typography, Button, Spin } from 'antd';
import {
  DatabaseOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';

const { Text } = Typography;

interface SessionStatusProps {
  onRefresh?: () => void;
}

export const SessionStatusView: React.FC<SessionStatusProps> = ({ onRefresh }) => {
  const [status, setStatus] = useState<SessionStatus | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      const data = await sessionAPI.getStatus();
      setStatus(data);
    } catch (error) {
      console.error('Failed to fetch session status:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleClose = async () => {
    try {
      await sessionAPI.closeSession();
      await fetchStatus();
      onRefresh?.();
    } catch (error) {
      console.error('Failed to close session:', error);
    }
  };

  if (loading) {
    return (
      <Card>
        <Space>
          <Spin />
          <Text>加载中...</Text>
        </Space>
      </Card>
    );
  }

  if (!status) {
    return null;
  }

  return (
    <Card
      title={
        <Space>
          <DatabaseOutlined />
          <span>会话状态</span>
        </Space>
      }
      extra={
        status.session_active && (
          <Button size="small" danger onClick={handleClose}>
            关闭会话
          </Button>
        )
      }
    >
      <Space direction="vertical" style={{ width: '100%' }} size="small">
        <Space>
          <Text strong>状态:</Text>
          <Badge
            status={status.session_active ? 'success' : 'default'}
            text={status.state.toUpperCase()}
          />
        </Space>

        {status.dump_file && (
          <Space>
            <Text strong>转储文件:</Text>
            <Text code>{status.dump_file}</Text>
          </Space>
        )}

        <Space>
          <Text strong>显示模式:</Text>
          <Badge color="blue" text={status.display_mode} />
        </Space>

        <Space>
          <Text strong>WinDBG:</Text>
          {status.windbg_available ? (
            <CheckCircleOutlined style={{ color: '#52c41a' }} />
          ) : (
            <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
          )}
        </Space>

        {status.session_active && status.session_pid && (
          <Space>
            <Text strong>进程 ID:</Text>
            <Text code>{status.session_pid}</Text>
          </Space>
        )}
      </Space>
    </Card>
  );
};
