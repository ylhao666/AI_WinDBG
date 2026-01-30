import { useState, useEffect, useRef } from 'react';
import type { SessionStatus } from '../types';
import { sessionAPI } from '../api/session';
import { Card, Badge, Space, Typography, Button, Spin, Row, Col } from 'antd';
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
  const [isUpdating, setIsUpdating] = useState(false);
  const isFirstLoad = useRef(true);
  const prevStatusRef = useRef<SessionStatus | null>(null);

  const fetchStatus = async (showLoading: boolean = false) => {
    try {
      if (showLoading) {
        setLoading(true);
      } else {
        setIsUpdating(true);
      }
      
      const data = await sessionAPI.getStatus();
      
      setStatus(data);
      prevStatusRef.current = data;
    } catch (error) {
      console.error('Failed to fetch session status:', error);
    } finally {
      setLoading(false);
      setIsUpdating(false);
    }
  };

  useEffect(() => {
    fetchStatus(true);
    isFirstLoad.current = false;

    const interval = setInterval(() => {
      fetchStatus(false);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleClose = async () => {
    try {
      await sessionAPI.closeSession();
      await fetchStatus(true);
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
          {isUpdating && (
            <Spin size="small" style={{ marginLeft: 8 }} />
          )}
        </Space>
      }
      extra={
        status.session_active && (
          <Button size="small" danger onClick={handleClose}>
            关闭会话
          </Button>
        )
      }
      className={`session-status-transition ${isUpdating ? 'session-status-updating' : ''}`}
      style={{ width: '100%' }}
    >
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Space>
            <Text strong>状态:</Text>
            <Badge
              status={status.session_active ? 'success' : 'default'}
              text={status.state.toUpperCase()}
              className="session-status-badge"
            />
          </Space>
        </Col>

        <Col xs={24} sm={12} md={16} lg={18}>
          <div style={{ width: '100%', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            <Space style={{ width: '100%' }}>
              <Text strong>转储文件:</Text>
              <Text code style={{ wordBreak: 'break-all' }}>{status.dump_file}</Text>
            </Space>
          </div>
        </Col>

        <Col xs={24} sm={12} md={8} lg={6}>
          <Space>
            <Text strong>显示模式:</Text>
            <Badge color="blue" text={status.display_mode} className="session-status-badge" />
          </Space>
        </Col>

        <Col xs={24} sm={12} md={8} lg={6}>
          <Space>
            <Text strong>WinDBG:</Text>
            {status.windbg_available ? (
              <CheckCircleOutlined style={{ color: '#52c41a' }} />
            ) : (
              <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
            )}
          </Space>
        </Col>

        {status.session_active && status.session_pid && (
          <Col xs={24} sm={12} md={8} lg={6}>
            <Space>
              <Text strong>进程 ID:</Text>
              <Text code>{status.session_pid}</Text>
            </Space>
          </Col>
        )}
      </Row>
    </Card>
  );
};
