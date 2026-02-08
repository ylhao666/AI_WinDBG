import React from 'react';
import { BulbOutlined } from '@ant-design/icons';
import type { AnalysisReport, AnalysisProgress } from '../../types';
import { AnalysisReportView } from '../AnalysisReport';
import { AnalysisProgressView } from '../AnalysisProgress';
import '../../styles/vscode-theme.css';

interface AIPanelProps {
  report: AnalysisReport | null;
  progress: AnalysisProgress | null;
  analyzing: boolean;
  onCancelAnalysis?: () => void;
}

export const AIPanel: React.FC<AIPanelProps> = ({ report, progress, analyzing, onCancelAnalysis }) => {
  const hasContent = report && (report.summary || report.crash_type || report.root_cause || (report.suggestions && report.suggestions.length > 0));

  if (!hasContent && !progress && !analyzing) {
    return (
      <div className="vscode-ai-panel">
        <div className="vscode-ai-header">
          <span style={{ display: 'flex', alignItems: 'center' }}>
            <BulbOutlined style={{ marginRight: '8px', color: 'var(--vscode-accent)' }} />
            <span>AI Insight</span>
          </span>
        </div>
        <div className="vscode-ai-placeholder">
          <BulbOutlined style={{ fontSize: '32px', marginBottom: '12px', color: 'var(--vscode-accent)' }} />
          <span>Waiting for AI analysis...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="vscode-ai-panel">
      <div className="vscode-ai-header">
        <span style={{ display: 'flex', alignItems: 'center' }}>
          <BulbOutlined style={{ marginRight: '8px', color: 'var(--vscode-accent)' }} />
          <span>AI Insight</span>
        </span>
        {analyzing && onCancelAnalysis && (
          <span style={{ fontSize: '12px', color: 'var(--vscode-fg-secondary)' }}>Analyzing...</span>
        )}
      </div>
      <div className="vscode-ai-content vscode-scrollbar">
        <div className="vscode-dark-theme" style={{ height: '100%' }}>
          {progress && (
            <AnalysisProgressView
              progress={progress}
              onCancel={onCancelAnalysis}
            />
          )}
          <AnalysisReportView
            report={report}
            loading={analyzing && !report}
            progress={progress}
            onCancelAnalysis={onCancelAnalysis}
          />
        </div>
      </div>
    </div>
  );
};
