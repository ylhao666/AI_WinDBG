import api from './client';
import { AnalysisReport, AnalysisTask } from '../types';

export const analysisAPI = {
  getReport: async (rawOutput: string, command: string): Promise<AnalysisReport> => {
    const response = await api.post('/analysis/report', { raw_output: rawOutput, command });
    return response.data;
  },

  analyzeAsync: async (rawOutput: string, command: string, useCache: boolean = true, streaming: boolean = false): Promise<{ task_id: string; message: string }> => {
    const response = await api.post('/analysis/analyze-async', { 
      raw_output: rawOutput, 
      command,
      use_cache: useCache,
      streaming
    });
    return response.data;
  },

  getTaskStatus: async (taskId: string): Promise<AnalysisTask> => {
    const response = await api.get(`/analysis/task/${taskId}`);
    return response.data;
  },

  cancelTask: async (taskId: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.post(`/analysis/task/${taskId}/cancel`);
    return response.data;
  },

  clearCache: async () => {
    const response = await api.post('/analysis/clear-cache');
    return response.data;
  },
};
