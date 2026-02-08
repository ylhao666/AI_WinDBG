import React from 'react';
import '../../styles/vscode-theme.css';

interface SplitPaneProps {
  left: React.ReactNode;
  right: React.ReactNode;
}

export const SplitPane: React.FC<SplitPaneProps> = ({ left, right }) => {
  return (
    <div className="vscode-split-pane">
      <div className="vscode-pane-left">
        {left}
      </div>
      <div className="vscode-pane-right">
        {right}
      </div>
    </div>
  );
};
