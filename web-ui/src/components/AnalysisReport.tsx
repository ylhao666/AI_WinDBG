import type { AnalysisReport, AnalysisProgress } from '../types';
import { Card, List, Tag, Space, Typography, Empty, Alert, Button, Table } from 'antd';
import {
  BulbOutlined,
  ExperimentOutlined,
  BugOutlined,
  CheckCircleOutlined,
  StopOutlined,
  CodeOutlined,
  FileOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import '../styles/vscode-theme.css';

const { Text, Paragraph } = Typography;

interface AnalysisReportProps {
  report: AnalysisReport | null;
  loading?: boolean;
  progress?: AnalysisProgress | null;
  onCancelAnalysis?: () => void;
}

export const AnalysisReportView: React.FC<AnalysisReportProps> = ({ 
  report, 
  loading, 
  progress,
  onCancelAnalysis 
}) => {
  if (loading && !progress) {
    return (
      <div className="vscode-dark-theme">
        <Card title={<span><BulbOutlined /> 智能分析</span>}>
          <Empty description="分析中..." />
        </Card>
      </div>
    );
  }

  if (!report && !progress) {
    return (
      <div className="vscode-dark-theme">
        <Card title={<span><BulbOutlined /> 智能分析</span>}>
          <Empty description="暂无分析报告" />
        </Card>
      </div>
    );
  }

  // 调用栈表格列定义
  const stackColumns = [
    {
      title: '地址',
      dataIndex: 'address',
      key: 'address',
      width: 120,
      render: (text: string) => <Text code>{text}</Text>,
    },
    {
      title: '函数',
      dataIndex: 'function',
      key: 'function',
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: '模块',
      dataIndex: 'module',
      key: 'module',
      width: 150,
      render: (text: string) => <Tag color="blue">{text}</Tag>,
    },
    {
      title: '偏移',
      dataIndex: 'offset',
      key: 'offset',
      width: 100,
    },
  ];

  // 模块信息表格列定义
  const moduleColumns = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      width: 150,
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: '基地址',
      dataIndex: 'base_address',
      key: 'base_address',
      width: 120,
      render: (text: string) => <Text code>{text}</Text>,
    },
    {
      title: '大小',
      dataIndex: 'size',
      key: 'size',
      width: 100,
    },
    {
      title: '版本',
      dataIndex: 'version',
      key: 'version',
      width: 120,
      render: (text: string) => text ? <Tag color="green">{text}</Tag> : '-',
    },
    {
      title: '符号',
      dataIndex: 'symbols_loaded',
      key: 'symbols_loaded',
      width: 80,
      render: (loaded: boolean) => loaded ? 
        <Tag color="success">已加载</Tag> : 
        <Tag color="warning">未加载</Tag>,
    },
  ];

  const hasCallStack = report?.call_stack && report.call_stack.length > 0;
  const hasModules = report?.modules && report.modules.length > 0;
  const hasExceptionInfo = report?.exception_info && 
    (report.exception_info.code || report.exception_info.description);

  return (
    <div className="vscode-dark-card">
      <Card
        title={
          <Space>
            <span><BulbOutlined /> 智能分析报告</span>
            {onCancelAnalysis && progress && (
              <Button
                danger
                size="small"
                icon={<StopOutlined />}
                onClick={onCancelAnalysis}
              >
                取消
              </Button>
            )}
          </Space>
        }
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
        {/* 分析摘要 */}
        {report?.summary && (
          <Alert
            message={report.summary}
            type="info"
            showIcon
            icon={<CheckCircleOutlined />}
          />
        )}

        {/* 崩溃类型和异常信息概览 */}
        {(report?.crash_type || report?.exception_code) && (
          <Card type="inner" title={<span><BugOutlined /> 崩溃概览</span>}>
            <Space direction="vertical" style={{ width: '100%' }}>
              {report.crash_type && (
                <div>
                  <Text strong>崩溃类型: </Text>
                  <Tag color="red">{report.crash_type}</Tag>
                </div>
              )}
              
              {report.exception_code && (
                <div>
                  <Text strong>异常代码: </Text>
                  <Text code>{report.exception_code}</Text>
                </div>
              )}
              
              {report.exception_address && (
                <div>
                  <Text strong>异常地址: </Text>
                  <Text code>{report.exception_address}</Text>
                </div>
              )}
              
              {report.exception_description && (
                <div>
                  <Text strong>异常描述: </Text>
                  <Paragraph>{report.exception_description}</Paragraph>
                </div>
              )}
            </Space>
          </Card>
        )}

        {/* 详细的异常信息 */}
        {hasExceptionInfo && (
          <Card type="inner" title={<span><ExclamationCircleOutlined /> 异常详情</span>}>
            <Space direction="vertical" style={{ width: '100%' }}>
              {report.exception_info!.code && (
                <div>
                  <Text strong>异常代码: </Text>
                  <Text code>{report.exception_info!.code}</Text>
                </div>
              )}
              {report.exception_info!.description && (
                <div>
                  <Text strong>描述: </Text>
                  <Paragraph>{report.exception_info!.description}</Paragraph>
                </div>
              )}
              {report.exception_info!.address && (
                <div>
                  <Text strong>地址: </Text>
                  <Text code>{report.exception_info!.address}</Text>
                </div>
              )}
              {report.exception_info!.flags && (
                <div>
                  <Text strong>标志: </Text>
                  <Text>{report.exception_info!.flags}</Text>
                </div>
              )}
            </Space>
          </Card>
        )}

        {/* 根本原因分析 */}
        {report?.root_cause && (
          <Card type="inner" title={<span><ExperimentOutlined /> 根本原因分析</span>}>
            <Paragraph>{report.root_cause}</Paragraph>
          </Card>
        )}

        {/* 调用栈信息 */}
        {hasCallStack && (
          <Card type="inner" title={<span><CodeOutlined /> 调用栈</span>}>
            <Table
              dataSource={report.call_stack}
              columns={stackColumns}
              rowKey="address"
              size="small"
              pagination={false}
              scroll={{ x: 'max-content' }}
            />
          </Card>
        )}

        {/* 模块信息 */}
        {hasModules && (
          <Card type="inner" title={<span><FileOutlined /> 模块信息</span>}>
            <Table
              dataSource={report.modules}
              columns={moduleColumns}
              rowKey="name"
              size="small"
              pagination={{ pageSize: 5 }}
              scroll={{ x: 'max-content' }}
            />
          </Card>
        )}

        {/* 建议解决方案 */}
        {report?.suggestions && report.suggestions.length > 0 && (
          <Card type="inner" title={<span><BulbOutlined /> 建议解决方案</span>}>
            <List
              dataSource={report.suggestions}
              renderItem={(item, index) => (
                <List.Item>
                  <Space align="start">
                    <Tag color="blue">{index + 1}</Tag>
                    <Text>{item}</Text>
                  </Space>
                </List.Item>
              )}
            />
          </Card>
        )}

        {/* 置信度 */}
        {report && (
          <div style={{ textAlign: 'right' }}>
            <Text type="secondary">
              分析置信度: <Tag color={report.confidence > 0.7 ? 'success' : report.confidence > 0.4 ? 'warning' : 'error'}>
                {(report.confidence * 100).toFixed(1)}%
              </Tag>
            </Text>
          </div>
        )}

        {/* 如果没有详细内容，显示提示 */}
        {report && !report.summary && !report.crash_type && !report.root_cause && 
         (!report.suggestions || report.suggestions.length === 0) && (
          <Alert
            message="分析报告内容为空"
            description="LLM 返回的分析结果为空，请检查 LLM 配置或重试分析。"
            type="warning"
            showIcon
          />
        )}
      </Space>
    </Card>
    </div>
  );
};
