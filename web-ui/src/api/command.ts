import api from './client';
import { CommandResult } from '../types';

export const commandAPI = {
  execute: async (command: string, mode: string = 'smart'): Promise<CommandResult> => {
    const response = await api.post('/command/execute', { command, mode });
    return response.data;
  },

  executeNatural: async (input: string, mode: string = 'smart'): Promise<CommandResult> => {
    const response = await api.post('/command/natural', { input, mode });
    return response.data;
  },
};
