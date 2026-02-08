import React, { useEffect, useRef } from 'react';
import { CodeOutlined } from '@ant-design/icons';
import '../../styles/vscode-theme.css';

interface TerminalPanelProps {
  output: string;
  command?: string;
}

export const TerminalPanel: React.FC<TerminalPanelProps> = ({ output, command }) => {
  const outputRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [output]);

  const formatOutput = (text: string) => {
    // 简单的语法高亮
    return text
      .replace(/(0x[0-9a-fA-F]+)/g, '<span class="vscode-code-address">$1</span>')
      .replace(/!([a-zA-Z_][a-zA-Z0-9_]*)/g, '<span class="vscode-code-function">!$1</span>');
  };

  if (!output) {
    return (
      <div className="vscode-terminal-panel">
        <div className="vscode-terminal-header">
          <CodeOutlined style={{ marginRight: '8px' }} />
          <span>Terminal</span>
        </div>
        <div className="vscode-terminal-placeholder">
          <CodeOutlined style={{ fontSize: '32px', marginBottom: '12px' }} />
          <span>Waiting for output...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="vscode-terminal-panel">
      <div className="vscode-terminal-header">
        <CodeOutlined style={{ marginRight: '8px' }} />
        <span>Terminal</span>
        {command && (
          <span style={{ marginLeft: '16px', color: 'var(--vscode-fg-secondary)', fontFamily: 'var(--vscode-font-family-mono)' }}>
            {command}
          </span>
        )}
      </div>
      <div
        ref={outputRef}
        className="vscode-terminal-content vscode-scrollbar"
        dangerouslySetInnerHTML={{ __html: formatOutput(output) }}
      />
    </div>
  );
};
