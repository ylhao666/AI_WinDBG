import api from './client';
import { AnalysisReport } from '../types';

export const analysisAPI = {
  getReport: async (rawOutput: string, command: string): Promise<AnalysisReport> => {
    const response = await api.post('/analysis/report', { raw_output: rawOutput, command });
    return response.data;
  },

  clearCache: async () => {
    const response = await api.post('/analysis/clear-cache');
    return response.data;
  },
};
