import React from 'react';
import { useNavigate } from 'react-router-dom';
import { SettingOutlined, CheckCircleOutlined, CloseCircleOutlined, MinusCircleOutlined } from '@ant-design/icons';
import type { SessionStatus as SessionStatusType } from '../../types';
import '../../styles/vscode-theme.css';

interface SlimHeaderProps {
  sessionStatus: SessionStatusType | null;
}

export const SlimHeader: React.FC<SlimHeaderProps> = ({ sessionStatus }) => {
  const navigate = useNavigate();

  const getStatusIcon = () => {
    if (!sessionStatus) {
      return <MinusCircleOutlined style={{ color: 'var(--vscode-fg-secondary)' }} />;
    }
    if (sessionStatus.session_active) {
      return <CheckCircleOutlined style={{ color: 'var(--vscode-success)' }} />;
    }
    return <CloseCircleOutlined style={{ color: 'var(--vscode-error)' }} />;
  };

  const getStatusText = () => {
    if (!sessionStatus) {
      return 'Inactive';
    }
    return sessionStatus.session_active ? 'Active' : sessionStatus.state.toUpperCase();
  };

  const getStatusBadgeClass = () => {
    if (!sessionStatus) {
      return 'vscode-status-badge-inactive';
    }
    return sessionStatus.session_active ? 'vscode-status-badge-active' : 'vscode-status-badge-inactive';
  };

  const formatFileName = (path: string) => {
    if (!path) return 'No file loaded';
    // 截取最后 40 个字符
    if (path.length > 40) {
      return '...' + path.slice(-40);
    }
    return path;
  };

  return (
    <div className="vscode-slim-header">
      <div className="vscode-slim-header-title">
        <span style={{ color: 'var(--vscode-accent)' }}>AI WinDBG</span>
        <span className="vscode-slim-header-file">
          {sessionStatus?.dump_file ? formatFileName(sessionStatus.dump_file) : 'No file loaded'}
        </span>
        <span className={`vscode-status-badge ${getStatusBadgeClass()}`}>
          {getStatusIcon()}
          <span style={{ marginLeft: '4px' }}>{getStatusText()}</span>
        </span>
      </div>
      <SettingOutlined
        style={{ color: 'var(--vscode-fg-primary)', fontSize: '20px', cursor: 'pointer' }}
        onClick={() => navigate('/llm-config')}
      />
    </div>
  );
};
