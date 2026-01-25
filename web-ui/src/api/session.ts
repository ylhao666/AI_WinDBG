import api from './client';
import { SessionStatus } from '../types';

export const sessionAPI = {
  loadDump: async (filepath: string) => {
    const response = await api.post('/session/load', { filepath });
    return response.data;
  },

  getStatus: async (): Promise<SessionStatus> => {
    const response = await api.get('/session/status');
    return response.data;
  },

  closeSession: async () => {
    const response = await api.post('/session/close');
    return response.data;
  },

  getHistory: async (): Promise<{ history: string[]; count: number }> => {
    const response = await api.get('/session/history');
    return response.data;
  },
};
