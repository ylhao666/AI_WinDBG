export interface ElectronAPI {
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

declare global {
  interface Window {
    electron?: ElectronAPI;
  }
}

export const isElectron = (): boolean => {
  return typeof window !== 'undefined' && window.electron?.isElectron === true;
};

export const validateWindowsPath = (filePath: string): { valid: boolean; error?: string } => {
  if (!filePath || typeof filePath !== 'string') {
    return { valid: false, error: '文件路径无效' };
  }

  if (filePath.length === 0) {
    return { valid: false, error: '文件路径为空' };
  }

  if (filePath.length > 260) {
    return { valid: false, error: '文件路径过长' };
  }

  const windowsPathRegex = /^[A-Za-z]:\\(?:[^<>:"|?*\n\r]+\\)*[^<>:"|?*\n\r]*$/;
  if (!windowsPathRegex.test(filePath)) {
    return { valid: false, error: '文件路径格式不正确' };
  }

  if (filePath.includes('..')) {
    return { valid: false, error: '文件路径包含非法字符' };
  }

  return { valid: true };
};

export const validateDmpExtension = (filePath: string): { valid: boolean; error?: string } => {
  if (!filePath || typeof filePath !== 'string') {
    return { valid: false, error: '文件路径无效' };
  }

  const lowerPath = filePath.toLowerCase();
  if (!lowerPath.endsWith('.dmp')) {
    return { valid: false, error: '文件扩展名必须是 .dmp' };
  }

  return { valid: true };
};

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
};

export const openFileSelector = async (): Promise<{
  success: boolean;
  filePath?: string;
  fileName?: string;
  fileSize?: number;
  error?: string;
}> => {
  if (!isElectron()) {
    return {
      success: false,
      error: '当前环境不支持 Electron API'
    };
  }

  try {
    console.log('[Electron Utils] 打开文件选择对话框');
    const result = await window.electron!.dialog.openFile();

    if (result.success) {
      console.log(`[Electron Utils] 文件已选择: ${result.filePath}`);
    } else {
      console.warn(`[Electron Utils] 文件选择失败: ${result.error}`);
    }

    return result;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '未知错误';
    console.error('[Electron Utils] 打开文件选择对话框错误:', errorMessage);
    return {
      success: false,
      error: errorMessage
    };
  }
};

export const validateFilePath = async (filePath: string): Promise<{
  success: boolean;
  filePath?: string;
  fileName?: string;
  fileSize?: number;
  error?: string;
}> => {
  if (!isElectron()) {
    return {
      success: false,
      error: '当前环境不支持 Electron API'
    };
  }

  try {
    console.log(`[Electron Utils] 验证文件路径: ${filePath}`);

    const pathValidation = validateWindowsPath(filePath);
    if (!pathValidation.valid) {
      return {
        success: false,
        error: pathValidation.error
      };
    }

    const extValidation = validateDmpExtension(filePath);
    if (!extValidation.valid) {
      return {
        success: false,
        error: extValidation.error
      };
    }

    const result = await window.electron!.file.validate(filePath);

    if (result.success) {
      console.log(`[Electron Utils] 文件验证成功: ${result.filePath}`);
    } else {
      console.warn(`[Electron Utils] 文件验证失败: ${result.error}`);
    }

    return result;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '未知错误';
    console.error('[Electron Utils] 验证文件路径错误:', errorMessage);
    return {
      success: false,
      error: errorMessage
    };
  }
};

export const getAppVersion = async (): Promise<string> => {
  if (!isElectron()) {
    return '0.1.0';
  }

  try {
    return await window.electron!.app.getVersion();
  } catch (error) {
    console.error('[Electron Utils] 获取应用版本错误:', error);
    return '0.1.0';
  }
};

export const logElectronInfo = () => {
  if (isElectron()) {
    console.log('[Electron Utils] 运行在 Electron 环境');
    console.log(`[Electron Utils] 平台: ${window.electron!.platform}`);
  } else {
    console.log('[Electron Utils] 运行在浏览器环境');
  }
};
