import api from './client';
import { Config } from '../types';

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
};
