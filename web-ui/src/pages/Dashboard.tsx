import { useState, useEffect } from 'react';
import { Layout, message, Space, Typography, Spin } from 'antd';
import {
  SessionStatus,
  CommandInput,
  OutputDisplay,
  AnalysisReport,
  AnalysisProgress,
  CommandHistory,
  FileUpload,
} from '../components';
import { sessionAPI, commandAPI, analysisAPI } from '../api';
import { wsManager } from '../api/websocket';
import { 
  AnalysisReport as AnalysisReportType, 
  AnalysisProgress as AnalysisProgressType,
  AnalysisStatus
} from '../types';

const { Header, Content, Sider } = Layout;
const { Title } = Typography;

export const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [output, setOutput] = useState('');
  const [currentCommand, setCurrentCommand] = useState('');
  const [analysisReport, setAnalysisReport] = useState<AnalysisReportType | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [history, setHistory] = useState<string[]>([]);
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [analysisProgress, setAnalysisProgress] = useState<AnalysisProgressType | null>(null);

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
        // 分析完成后，延迟清除进度显示，让用户能看到完成状态
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
    };

    const handleSessionClosed = () => {
      message.info('会话已关闭');
      setOutput('');
      setAnalysisReport(null);
      setAnalysisProgress(null);
      setCurrentTaskId(null);
    };

    wsManager.onCommandOutput(handleCommandOutput);
    wsManager.onAnalysisProgress(handleAnalysisProgress);
    wsManager.onAnalysisReport(handleAnalysisReport);
    wsManager.onSessionLoaded(handleSessionLoaded);
    wsManager.onSessionClosed(handleSessionClosed);

    fetchHistory();

    return () => {
      wsManager.offCommandOutput(handleCommandOutput);
      wsManager.offAnalysisProgress(handleAnalysisProgress);
      wsManager.offAnalysisReport(handleAnalysisReport);
      wsManager.offSessionLoaded(handleSessionLoaded);
      wsManager.offSessionClosed(handleSessionClosed);
      wsManager.disconnect();
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

  const handleExecute = async (command: string, mode: string) => {
    try {
      setLoading(true);
      setOutput('');
      setAnalysisReport(null);
      setAnalysisProgress(null);
      setCurrentTaskId(null);

      const result = await commandAPI.execute(command, mode);
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
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#001529', padding: '0 24px' }}>
        <Title level={3} style={{ color: '#fff', margin: '14px 0' }}>
          AI WinDBG 崩溃分析器
        </Title>
      </Header>

      <Layout>
        <Sider width={300} style={{ background: '#fff', padding: '16px' }}>
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            <FileUpload onLoad={handleLoadDump} loading={loading} />
            <CommandHistory history={history} onSelect={handleSelectHistory} />
          </Space>
        </Sider>

        <Content style={{ padding: '24px', background: '#f0f2f5', paddingBottom: '280px' }}>
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <SessionStatus onRefresh={fetchHistory} />

            {loading && (
              <div style={{ textAlign: 'center', padding: '24px' }}>
                <Spin size="large" />
              </div>
            )}

            <OutputDisplay output={output} command={currentCommand} />
            
            {analysisProgress && (
              <AnalysisProgress 
                progress={analysisProgress} 
                onCancel={handleCancelAnalysis}
              />
            )}
            
            {/* 始终显示分析报告，即使在分析中也可以显示之前的报告 */}
            <AnalysisReport 
              report={analysisReport} 
              loading={analyzing && !analysisReport}
              progress={analysisProgress}
              onCancelAnalysis={handleCancelAnalysis}
            />
          </Space>
        </Content>
      </Layout>

      <CommandInput onExecute={handleExecute} disabled={loading} loading={loading} />
    </Layout>
  );
};
