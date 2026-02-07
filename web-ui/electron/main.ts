import { app, BrowserWindow, ipcMain, dialog, shell } from 'electron';
import * as path from 'path';
import * as fs from 'fs';
import { URL } from 'url';

let mainWindow: BrowserWindow | null = null;
const isDev = process.env.NODE_ENV === 'development';
// 从环境变量读取端口，默认 3000
const devPort = parseInt(process.env.ELECTRON_PORT || '3000', 10);

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.cjs'),
      webSecurity: true,
      sandbox: false
    },
    show: false,
    backgroundColor: '#001529'
  });

  if (isDev) {
    mainWindow.loadURL(`http://localhost:${devPort}`);
    console.log(`[Electron Main] Loading from: http://localhost:${devPort}`);
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

ipcMain.handle('dialog:open-file', async () => {
  try {
    const result = await dialog.showOpenDialog(mainWindow!, {
      title: '选择转储文件',
      filters: [
        { name: '转储文件', extensions: ['dmp'] }
      ],
      properties: ['openFile'],
      defaultPath: app.getPath('home')
    });

    if (result.canceled || result.filePaths.length === 0) {
      return { success: false, error: '用户取消选择' };
    }

    const filePath = result.filePaths[0];

    if (!fs.existsSync(filePath)) {
      return { success: false, error: '文件不存在' };
    }

    const stats = fs.statSync(filePath);
    if (!stats.isFile()) {
      return { success: false, error: '选择的不是文件' };
    }

    if (!filePath.toLowerCase().endsWith('.dmp')) {
      return { success: false, error: '文件扩展名必须是 .dmp' };
    }

    console.log(`[Electron Main] File selected: ${filePath}`);

    return {
      success: true,
      filePath: filePath,
      fileName: path.basename(filePath),
      fileSize: stats.size
    };
  } catch (error) {
    console.error('[Electron Main] Open file dialog error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : '未知错误'
    };
  }
});

ipcMain.handle('file:validate', async (_, filePath: string) => {
  try {
    if (!filePath || typeof filePath !== 'string') {
      return { success: false, error: '无效的文件路径' };
    }

    if (!fs.existsSync(filePath)) {
      return { success: false, error: '文件不存在' };
    }

    const stats = fs.statSync(filePath);
    if (!stats.isFile()) {
      return { success: false, error: '路径不是文件' };
    }

    if (!filePath.toLowerCase().endsWith('.dmp')) {
      return { success: false, error: '文件扩展名必须是 .dmp' };
    }

    if (stats.size === 0) {
      return { success: false, error: '文件为空' };
    }

    if (stats.size > 10 * 1024 * 1024 * 1024) {
      return { success: false, error: '文件过大（超过 10GB）' };
    }

    const normalizedPath = path.normalize(filePath);
    if (normalizedPath !== filePath) {
      console.warn(`[Electron Main] Path normalized: ${filePath} -> ${normalizedPath}`);
    }

    console.log(`[Electron Main] File validation successful: ${normalizedPath}`);

    return {
      success: true,
      filePath: normalizedPath,
      fileName: path.basename(normalizedPath),
      fileSize: stats.size
    };
  } catch (error) {
    console.error('[Electron Main] File validation error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : '未知错误'
    };
  }
});

ipcMain.handle('app:get-version', () => {
  return app.getVersion();
});

ipcMain.handle('app:get-path', (_, name: string) => {
  return app.getPath(name as any);
});

ipcMain.handle('app:open-external', async (_, url: string) => {
  try {
    await shell.openExternal(url);
    return { success: true };
  } catch (error) {
    console.error('[Electron Main] Open external link error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : '未知错误'
    };
  }
});

console.log('[Electron Main] AI WinDBG Electron App Started');
console.log(`[Electron Main] Development Mode: ${isDev}`);
console.log(`[Electron Main] Electron Version: ${process.versions.electron}`);
console.log(`[Electron Main] Node Version: ${process.versions.node}`);
console.log(`[Electron Main] Chrome Version: ${process.versions.chrome}`);
