import api from './client';
import { Config, LLMConfig, LLMTestResult } from '../types';

export const configAPI = {
  getConfig: async (): Promise<Config> => {
    const response = await api.get('/config/');
    return response.data;
  },

  getLLMStatus: async () => {
    const response = await api.get('/config/llm/status');
    return response.data;
  },

  getWinDBGStatus: async () => {
    const response = await api.get('/config/windbg/status');
    return response.data;
  },

  getLLMConfig: async (): Promise<LLMConfig> => {
    const response = await api.get('/config/llm');
    return response.data;
  },

  updateLLMConfig: async (config: LLMConfig): Promise<void> => {
    await api.put('/config/llm', config);
  },

  testLLMConnection: async (config: LLMConfig): Promise<LLMTestResult> => {
    const response = await api.post('/config/llm/test', config);
    return response.data;
  },
};
