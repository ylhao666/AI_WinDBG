import { contextBridge, ipcRenderer } from 'electron';

interface ElectronAPI {
  dialog: {
    openFile: () => Promise<{
      success: boolean;
      filePath?: string;
      fileName?: string;
      fileSize?: number;
      error?: string;
    }>;
  };
  file: {
    validate: (filePath: string) => Promise<{
      success: boolean;
      filePath?: string;
      fileName?: string;
      fileSize?: number;
      error?: string;
    }>;
  };
  app: {
    getVersion: () => Promise<string>;
    getPath: (name: string) => Promise<string>;
    openExternal: (url: string) => Promise<{ success: boolean; error?: string }>;
  };
  platform: string;
  isElectron: boolean;
}

const electronAPI: ElectronAPI = {
  dialog: {
    openFile: () => ipcRenderer.invoke('dialog:open-file')
  },
  file: {
    validate: (filePath: string) => ipcRenderer.invoke('file:validate', filePath)
  },
  app: {
    getVersion: () => ipcRenderer.invoke('app:get-version'),
    getPath: (name: string) => ipcRenderer.invoke('app:get-path', name),
    openExternal: (url: string) => ipcRenderer.invoke('app:open-external', url)
  },
  platform: process.platform,
  isElectron: true
};

contextBridge.exposeInMainWorld('electron', electronAPI);

declare global {
  interface Window {
    electron: ElectronAPI;
  }
}

console.log('[Electron Preload] 预加载脚本已加载');
console.log(`[Electron Preload] 平台: ${process.platform}`);
