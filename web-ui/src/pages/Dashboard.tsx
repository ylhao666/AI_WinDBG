import { useState, useEffect } from 'react';
import { Layout, message, Space, Typography, Spin } from 'antd';
import {
  SessionStatus,
  CommandInput,
  OutputDisplay,
  AnalysisReport,
  CommandHistory,
  FileUpload,
} from '../components';
import { sessionAPI, commandAPI, analysisAPI } from '../api';
import { wsManager } from '../api/websocket';
import { AnalysisReport as AnalysisReportType } from '../types';

const { Header, Content, Sider } = Layout;
const { Title } = Typography;

export const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [output, setOutput] = useState('');
  const [currentCommand, setCurrentCommand] = useState('');
  const [analysisReport, setAnalysisReport] = useState<AnalysisReportType | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [history, setHistory] = useState<string[]>([]);

  useEffect(() => {
    wsManager.connect('ws://localhost:8000/ws/output');
    wsManager.connect('ws://localhost:8000/ws/session');

    wsManager.on('command_output', (data) => {
      setOutput(data.output);
      setCurrentCommand(data.command);
      if (data.mode === 'smart' || data.mode === 'both') {
        analyzeOutput(data.output, data.command);
      }
    });

    wsManager.on('natural_language_output', (data) => {
      setOutput(data.output);
      setCurrentCommand(data.command);
      if (data.mode === 'smart' || data.mode === 'both') {
        analyzeOutput(data.output, data.command);
      }
    });

    wsManager.on('analysis_report', (data) => {
      setAnalysisReport(data.report);
      setAnalyzing(false);
    });

    wsManager.on('session_loaded', () => {
      message.success('转储文件加载成功');
      fetchHistory();
    });

    wsManager.on('session_closed', () => {
      message.info('会话已关闭');
      setOutput('');
      setAnalysisReport(null);
    });

    fetchHistory();

    return () => {
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

      const result = await commandAPI.execute(command, mode);
      setOutput(result.output);
      setCurrentCommand(result.command);

      if (mode === 'smart' || mode === 'both') {
        await analyzeOutput(result.output, result.command);
      }

      await fetchHistory();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '执行命令失败');
    } finally {
      setLoading(false);
    }
  };

  const analyzeOutput = async (rawOutput: string, command: string) => {
    try {
      setAnalyzing(true);
      const report = await analysisAPI.getReport(rawOutput, command);
      setAnalysisReport(report);
    } catch (error: any) {
      console.error('Analysis failed:', error);
      message.warning('智能分析失败');
    } finally {
      setAnalyzing(false);
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
            <SessionStatus onRefresh={fetchHistory} />
            <FileUpload onLoad={handleLoadDump} loading={loading} />
            <CommandHistory history={history} onSelect={handleSelectHistory} />
          </Space>
        </Sider>

        <Content style={{ padding: '24px', background: '#f0f2f5' }}>
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <CommandInput onExecute={handleExecute} disabled={loading} loading={loading} />

            {loading && (
              <div style={{ textAlign: 'center', padding: '24px' }}>
                <Spin size="large" />
              </div>
            )}

            <OutputDisplay output={output} command={currentCommand} />
            <AnalysisReport report={analysisReport} loading={analyzing} />
          </Space>
        </Content>
      </Layout>
    </Layout>
  );
};
