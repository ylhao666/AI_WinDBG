import { useState, useEffect } from 'react';
import { message } from 'antd';
import {
  SlimHeader,
  Sidebar,
  SplitPane,
  TerminalPanel,
  AIPanel,
  ChatInput,
} from '../components';
import { sessionAPI, commandAPI, analysisAPI } from '../api';
import { wsManager } from '../api/websocket';
import {
  AnalysisReport as AnalysisReportType,
  AnalysisProgress as AnalysisProgressType,
  AnalysisStatus,
  SessionStatus as SessionStatusType
} from '../types';

export const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [output, setOutput] = useState('');
  const [currentCommand, setCurrentCommand] = useState('');
  const [analysisReport, setAnalysisReport] = useState<AnalysisReportType | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [history, setHistory] = useState<string[]>([]);
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [analysisProgress, setAnalysisProgress] = useState<AnalysisProgressType | null>(null);
  const [sessionStatus, setSessionStatus] = useState<SessionStatusType | null>(null);

  useEffect(() => {
    wsManager.connect('ws://localhost:8000/ws/output', 'output');
    wsManager.connect('ws://localhost:8000/ws/session', 'session');

    const handleCommandOutput = (data: any) => {
      setOutput(data.output);
      setCurrentCommand(data.command);
      if (data.mode === 'smart' || data.mode === 'both') {
        analyzeOutputAsync(data.output, data.command);
      }
    };

    const handleAnalysisProgress = (data: any) => {
      setAnalysisProgress(data);
      if (data.status === AnalysisStatus.COMPLETED && data.result) {
        setAnalysisReport(data.result);
        setAnalyzing(false);
        setCurrentTaskId(null);
        setTimeout(() => {
          setAnalysisProgress(null);
        }, 2000);
        message.success('智能分析完成');
      } else if (data.status === AnalysisStatus.ERROR) {
        setAnalyzing(false);
        setCurrentTaskId(null);
        message.error(`分析失败: ${data.error}`);
      } else if (data.status === AnalysisStatus.CANCELLED) {
        setAnalyzing(false);
        setCurrentTaskId(null);
        message.info('分析已取消');
      }
    };

    const handleAnalysisReport = (data: any) => {
      setAnalysisReport(data.report);
      setAnalyzing(false);
    };

    const handleSessionLoaded = () => {
      message.success('转储文件加载成功');
      fetchHistory();
      fetchSessionStatus();
    };

    const handleSessionClosed = () => {
      message.info('会话已关闭');
      setOutput('');
      setAnalysisReport(null);
      setAnalysisProgress(null);
      setCurrentTaskId(null);
      fetchSessionStatus();
    };

    wsManager.onCommandOutput(handleCommandOutput);
    wsManager.onNaturalLanguageOutput(handleCommandOutput);
    wsManager.onAnalysisProgress(handleAnalysisProgress);
    wsManager.onAnalysisReport(handleAnalysisReport);
    wsManager.onSessionLoaded(handleSessionLoaded);
    wsManager.onSessionClosed(handleSessionClosed);

    fetchHistory();
    fetchSessionStatus();

    const statusInterval = setInterval(fetchSessionStatus, 5000);

    return () => {
      wsManager.offCommandOutput(handleCommandOutput);
      wsManager.offNaturalLanguageOutput(handleCommandOutput);
      wsManager.offAnalysisProgress(handleAnalysisProgress);
      wsManager.offAnalysisReport(handleAnalysisReport);
      wsManager.offSessionLoaded(handleSessionLoaded);
      wsManager.offSessionClosed(handleSessionClosed);
      wsManager.disconnect();
      clearInterval(statusInterval);
    };
  }, []);

  const fetchHistory = async () => {
    try {
      const data = await sessionAPI.getHistory();
      setHistory(data.history);
    } catch (error) {
      console.error('Failed to fetch history:', error);
    }
  };

  const fetchSessionStatus = async () => {
    try {
      const data = await sessionAPI.getStatus();
      setSessionStatus(data);
    } catch (error) {
      console.error('Failed to fetch session status:', error);
    }
  };

  const handleLoadDump = async (filepath: string) => {
    try {
      setLoading(true);
      await sessionAPI.loadDump(filepath);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '加载文件失败');
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async (command: string, mode: string, isNatural: boolean = false) => {
    try {
      setLoading(true);
      setOutput('');
      setAnalysisReport(null);
      setAnalysisProgress(null);
      setCurrentTaskId(null);

      const result = isNatural
        ? await commandAPI.executeNatural(command, mode)
        : await commandAPI.execute(command, mode);
      setOutput(result.output);
      setCurrentCommand(result.command);

      await fetchHistory();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '执行命令失败');
    } finally {
      setLoading(false);
    }
  };

  const analyzeOutputAsync = async (rawOutput: string, command: string) => {
    try {
      setAnalyzing(true);
      setAnalysisProgress(null);

      const response = await analysisAPI.analyzeAsync(rawOutput, command, true, true);
      setCurrentTaskId(response.task_id);

      message.info('分析任务已创建');
    } catch (error: any) {
      console.error('Analysis failed:', error);
      message.error('创建分析任务失败');
      setAnalyzing(false);
    }
  };

  const handleCancelAnalysis = async () => {
    if (currentTaskId) {
      try {
        await analysisAPI.cancelTask(currentTaskId);
        message.info('正在取消分析...');
      } catch (error: any) {
        message.error(error.response?.data?.detail || '取消分析失败');
      }
    }
  };

  const handleSelectHistory = (command: string) => {
    setCurrentCommand(command);
  };

  return (
    <div className="vscode-layout">
      <SlimHeader sessionStatus={sessionStatus} />

      <div className="vscode-main-workspace">
        <Sidebar
          history={history}
          onLoadDump={handleLoadDump}
          loading={loading}
          onSelectHistory={handleSelectHistory}
        />

        <SplitPane
          left={
            <div style={{ display: 'flex', flexDirection: 'column', height: '100%', position: 'relative' }}>
              <TerminalPanel output={output} command={currentCommand} />
              <ChatInput
                onExecute={handleExecute}
                disabled={loading}
                loading={loading}
              />
            </div>
          }
          right={
            <AIPanel
              report={analysisReport}
              progress={analysisProgress}
              analyzing={analyzing}
              onCancelAnalysis={handleCancelAnalysis}
            />
          }
        />
      </div>
    </div>
  );
};
