import { useState, useEffect, useRef } from 'react';

const STORAGE_KEY = 'llm_provider_api_keys';
import { Layout, Typography, Form, Select, Input, InputNumber, Slider, Button, Space, Card, message, Spin, Divider, Tag } from 'antd';
import { SettingOutlined, ApiOutlined, CheckCircleOutlined, CloseCircleOutlined, ReloadOutlined, HomeOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { configAPI } from '../api';
import { LLMConfig, LLMTestResult } from '../types';

const { Title, Text } = Typography;
const { Option } = Select;

const PROVIDER_OPTIONS = [
  { label: 'OpenAI', value: 'openai' },
  { label: 'OpenRouter', value: 'openrouter' },
  { label: 'DeepSeek', value: 'deepseek' },
  { label: '自定义', value: 'custom' },
];

const PROVIDER_DEFAULTS: Record<string, Partial<LLMConfig>> = {
  openai: {
    provider: 'openai',
    model: 'gpt-4',
    base_url: null,
    site_url: null,
    site_name: null,
    max_tokens: 2000,
    temperature: 0.3,
  },
  openrouter: {
    provider: 'openrouter',
    model: 'openai/gpt-4',
    base_url: 'https://openrouter.ai/api/v1',
    site_url: 'https://github.com/ylhao666/AI_WinDBG',
    site_name: 'AI WinDBG',
    max_tokens: 2000,
    temperature: 0.3,
  },
  deepseek: {
    provider: 'deepseek',
    model: 'deepseek-chat',
    base_url: 'https://api.deepseek.com',
    site_url: null,
    site_name: null,
    max_tokens: 2000,
    temperature: 0.3,
  },
  custom: {
    provider: 'custom',
    model: '',
    base_url: null,
    site_url: null,
    site_name: null,
    max_tokens: 2000,
    temperature: 0.3,
  },
};

export const LLMConfigPage: React.FC = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<LLMTestResult | null>(null);
  const [originalConfig, setOriginalConfig] = useState<LLMConfig | null>(null);
  const providerApiKeysRef = useRef<Record<string, string>>({});
  const lastProviderRef = useRef<string>('');

  // 从 localStorage 加载 API Keys
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        providerApiKeysRef.current = JSON.parse(stored);
      } catch (e) {
        console.error('Failed to parse stored API keys:', e);
      }
    }
  }, []);

  useEffect(() => {
    fetchConfig();
  }, []);

  // 保存 API Keys 到 localStorage
  const saveApiKeysToStorage = () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(providerApiKeysRef.current));
  };

  const fetchConfig = async () => {
    try {
      setLoading(true);
      const config = await configAPI.getLLMConfig();
      setOriginalConfig(config);

      // 保存当前提供商的 API Key
      const currentProvider = config.provider || 'openai';
      providerApiKeysRef.current[currentProvider] = config.api_key;
      lastProviderRef.current = currentProvider;

      // 使用后端返回的真实 API Key
      form.setFieldsValue({
        ...config,
        api_key_hidden: config.api_key,
      });
    } catch (error: any) {
      message.error('加载配置失败');
      console.error('Failed to fetch config:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProviderChange = (provider: string) => {
    const defaults = PROVIDER_DEFAULTS[provider];
    if (defaults) {
      // 使用上一次的提供商来保存 API Key
      const prevProvider = lastProviderRef.current;
      const currentApiKey = form.getFieldValue('api_key_hidden');

      if (prevProvider && prevProvider !== provider && currentApiKey) {
        providerApiKeysRef.current[prevProvider] = currentApiKey;
        console.log('保存 API Key:', { provider: prevProvider, key: currentApiKey });
        saveApiKeysToStorage();
      }

      // 获取新提供商的 API Key
      const newApiKey = providerApiKeysRef.current[provider] || '';
      console.log('切换供应商:', { from: prevProvider, to: provider, newApiKey });

      // 更新表单
      form.setFieldsValue({
        provider,
        model: defaults.model,
        api_key_hidden: newApiKey,
        base_url: defaults.base_url,
        site_url: defaults.site_url,
        site_name: defaults.site_name,
        max_tokens: defaults.max_tokens,
        temperature: defaults.temperature,
      });

      // 更新上一个提供商记录
      lastProviderRef.current = provider;
    }
  };

  const handleTestConnection = async () => {
    try {
      setTesting(true);
      setTestResult(null);

      const values = form.getFieldsValue();
      const config: LLMConfig = {
        provider: values.provider,
        model: values.model,
        api_key: values.api_key_hidden || originalConfig?.api_key || '',
        base_url: values.base_url,
        site_url: values.site_url,
        site_name: values.site_name,
        max_tokens: values.max_tokens,
        temperature: values.temperature,
      };

      if (!config.api_key) {
        message.warning('请输入 API Key');
        return;
      }

      const result = await configAPI.testLLMConnection(config);
      setTestResult(result);

      if (result.success) {
        message.success(`连接成功！延迟: ${result.latency}ms`);
      } else {
        message.error(`连接失败: ${result.message}`);
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '测试连接失败');
      setTestResult({ success: false, message: '测试失败' });
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async () => {
    try {
      await form.validateFields();

      setLoading(true);
      const values = form.getFieldsValue();

      const config: LLMConfig = {
        provider: values.provider,
        model: values.model,
        api_key: values.api_key_hidden || originalConfig?.api_key || '',
        base_url: values.base_url,
        site_url: values.site_url,
        site_name: values.site_name,
        max_tokens: values.max_tokens,
        temperature: values.temperature,
      };

      // 保存到 localStorage
      providerApiKeysRef.current[config.provider] = config.api_key;
      saveApiKeysToStorage();

      await configAPI.updateLLMConfig(config);
      message.success('配置已保存并生效');

      // 重新加载配置
      await fetchConfig();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '保存配置失败');
      console.error('Failed to save config:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    if (originalConfig) {
      form.setFieldsValue({
        ...originalConfig,
        api_key_hidden: '',
      });
      setTestResult(null);
    }
  };

  const isOpenRouter = Form.useWatch('provider', form) === 'openrouter';

  if (loading && !originalConfig) {
    return (
      <Layout style={{ minHeight: '100vh' }}>
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
          <Spin size="large" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Layout>
        <div style={{ background: '#001529', padding: '0 24px', display: 'flex', alignItems: 'center' }}>
          <Title level={3} style={{ color: '#fff', margin: '14px 0' }}>
            <SettingOutlined /> LLM 配置
          </Title>
        </div>

        <div style={{ padding: '24px', background: '#f0f2f5', flex: 1 }}>
          <Card
            title={
              <Space>
                <ApiOutlined />
                <span>LLM 配置管理</span>
              </Space>
            }
            extra={
              <Space>
                <Button
                  icon={<HomeOutlined />}
                  onClick={() => navigate('/')}
                >
                  返回主页
                </Button>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={fetchConfig}
                  loading={loading}
                >
                  刷新
                </Button>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={handleReset}
                  disabled={!originalConfig}
                >
                  重置
                </Button>
              </Space>
            }
            style={{ maxWidth: 800, margin: '0 auto' }}
          >
            <Form
              form={form}
              layout="vertical"
              initialValues={{
                provider: 'openai',
                model: '',
                api_key_hidden: '',
                base_url: null,
                site_url: null,
                site_name: null,
                max_tokens: 2000,
                temperature: 0.3,
              }}
            >
              <Form.Item
                label="提供商"
                name="provider"
                rules={[{ required: true, message: '请选择提供商' }]}
              >
                <Select
                  placeholder="选择 LLM 提供商"
                  onChange={handleProviderChange}
                  size="large"
                >
                  {PROVIDER_OPTIONS.map(opt => (
                    <Option key={opt.value} value={opt.value}>
                      {opt.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              <Form.Item
                label="模型名称"
                name="model"
                rules={[{ required: true, message: '请输入模型名称' }]}
                tooltip="例如：gpt-4, deepseek-chat, openai/gpt-4"
              >
                <Input
                  placeholder="输入模型名称"
                  size="large"
                />
              </Form.Item>

              <Form.Item
                label="API Key"
                name="api_key_hidden"
                rules={[{ required: true, message: '请输入 API Key' }]}
                tooltip="您的 API 密钥，将被安全保存"
              >
                <Input.Password
                  placeholder={originalConfig?.api_key === '***' ? '保持原密钥不变' : '输入 API Key'}
                  size="large"
                />
              </Form.Item>

              <Form.Item
                label="Base URL"
                name="base_url"
                tooltip="自定义 API 端点地址，留空使用默认值"
              >
                <Input
                  placeholder="https://api.example.com/v1"
                  size="large"
                />
              </Form.Item>

              {isOpenRouter && (
                <>
                  <Divider />
                  <Text type="secondary">OpenRouter 专用配置</Text>

                  <Form.Item
                    label="Site URL"
                    name="site_url"
                    tooltip="您的网站 URL，用于 OpenRouter 排名"
                  >
                    <Input
                      placeholder="https://github.com/your-repo"
                      size="large"
                    />
                  </Form.Item>

                  <Form.Item
                    label="Site Name"
                    name="site_name"
                    tooltip="您的应用名称，用于 OpenRouter 排名"
                  >
                    <Input
                      placeholder="AI WinDBG"
                      size="large"
                    />
                  </Form.Item>

                  <Divider />
                </>
              )}

              <Form.Item
                label={
                  <Space>
                    <span>最大 Token 数</span>
                    <Tag color="blue">max_tokens</Tag>
                  </Space>
                }
                name="max_tokens"
                tooltip="生成文本的最大长度"
              >
                <InputNumber
                  min={1}
                  max={8000}
                  step={100}
                  style={{ width: '100%' }}
                  size="large"
                />
              </Form.Item>

              <Form.Item
                label={
                  <Space>
                    <span>温度</span>
                    <Tag color="green">temperature</Tag>
                  </Space>
                }
                name="temperature"
                tooltip="控制输出的随机性，0 更确定，1 更随机"
              >
                <Slider
                  min={0}
                  max={1}
                  step={0.1}
                  marks={{
                    0: '精确',
                    0.5: '平衡',
                    1: '创意',
                  }}
                />
              </Form.Item>

              <Divider />

              {testResult && (
                <div
                  style={{
                    padding: '16px',
                    borderRadius: '8px',
                    background: testResult.success ? '#f6ffed' : '#fff1f0',
                    marginBottom: '16px',
                  }}
                >
                  <Space>
                    {testResult.success ? (
                      <CheckCircleOutlined style={{ color: '#52c41a', fontSize: '20px' }} />
                    ) : (
                      <CloseCircleOutlined style={{ color: '#ff4d4f', fontSize: '20px' }} />
                    )}
                    <Text>
                      {testResult.message}
                      {testResult.success && testResult.latency && (
                        <Text type="secondary" style={{ marginLeft: 8 }}>
                          (延迟: {testResult.latency}ms)
                        </Text>
                      )}
                    </Text>
                  </Space>
                </div>
              )}

              <Form.Item>
                <Space size="large">
                  <Button
                    type="default"
                    icon={<ApiOutlined />}
                    onClick={handleTestConnection}
                    loading={testing}
                    size="large"
                  >
                    测试连接
                  </Button>
                  <Button
                    type="primary"
                    onClick={handleSave}
                    loading={loading}
                    size="large"
                    style={{ minWidth: '120px' }}
                  >
                    保存配置
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </Card>

          <div style={{ maxWidth: 800, margin: '24px auto', textAlign: 'center' }}>
            <Text type="secondary">
              配置将保存到 config.yaml 文件并立即生效，无需重启应用。
            </Text>
          </div>
        </div>
      </Layout>
    </Layout>
  );
};
