import type { AnalysisReport } from '../types';
import { Card, List, Tag, Space, Typography, Empty, Alert } from 'antd';
import {
  BulbOutlined,
  ExperimentOutlined,
  BugOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';

const { Text, Paragraph, Title } = Typography;

interface AnalysisReportProps {
  report: AnalysisReport | null;
  loading?: boolean;
}

export const AnalysisReportView: React.FC<AnalysisReportProps> = ({ report, loading }) => {
  if (loading) {
    return (
      <Card title={<span><BulbOutlined /> 智能分析</span>}>
        <Empty description="分析中..." />
      </Card>
    );
  }

  if (!report) {
    return (
      <Card title={<span><BulbOutlined /> 智能分析</span>}>
        <Empty description="暂无分析报告" />
      </Card>
    );
  }

  return (
    <Card title={<span><BulbOutlined /> 智能分析</span>}>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {report.summary && (
          <Alert
            message={report.summary}
            type="info"
            showIcon
            icon={<CheckCircleOutlined />}
          />
        )}

        {report.crash_type && (
          <div>
            <Title level={5}>
              <BugOutlined /> 崩溃类型
            </Title>
            <Tag color="red">{report.crash_type}</Tag>
          </div>
        )}

        {report.exception_code && (
          <div>
            <Title level={5}>
              <ExperimentOutlined /> 异常信息
            </Title>
            <Space direction="vertical" size="small">
              <Text>
                <Text strong>异常代码:</Text> <Text code>{report.exception_code}</Text>
              </Text>
              {report.exception_address && (
                <Text>
                  <Text strong>异常地址:</Text> <Text code>{report.exception_address}</Text>
                </Text>
              )}
              {report.exception_description && (
                <Paragraph>{report.exception_description}</Paragraph>
              )}
            </Space>
          </div>
        )}

        {report.root_cause && (
          <div>
            <Title level={5}>根本原因</Title>
            <Paragraph>{report.root_cause}</Paragraph>
          </div>
        )}

        {report.suggestions && report.suggestions.length > 0 && (
          <div>
            <Title level={5}>
              <BulbOutlined /> 建议解决方案
            </Title>
            <List
              dataSource={report.suggestions}
              renderItem={(item, index) => (
                <List.Item>
                  <Space>
                    <Tag color="blue">{index + 1}</Tag>
                    <Text>{item}</Text>
                  </Space>
                </List.Item>
              )}
            />
          </div>
        )}

        <div>
          <Text type="secondary">
            置信度: {(report.confidence * 100).toFixed(1)}%
          </Text>
        </div>
      </Space>
    </Card>
  );
};
