/**
 * 智能 Electron 启动脚本
 * 自动检测可用端口，避免端口冲突
 */

import { spawn } from 'child_process';
import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

/**
 * 检查端口是否可用
 */
function isPortAvailable(port) {
  return new Promise((resolve) => {
    const server = http.createServer();

    server.once('error', (err) => {
      if (err.code === 'EADDRINUSE') {
        resolve(false);
      } else {
        resolve(true);
      }
    });

    server.once('listening', () => {
      server.close();
      resolve(true);
    });

    server.listen(port);
  });
}

/**
 * 获取可用端口
 */
async function getAvailablePort(startPort = 3000, maxAttempts = 10) {
  const portRange = [];
  for (let i = 0; i < maxAttempts; i++) {
    portRange.push(startPort + i);
  }

  for (const port of portRange) {
    if (await isPortAvailable(port)) {
      return port;
    }
  }

  throw new Error(`无法找到可用端口，已尝试 ${portRange[0]} 到 ${portRange[portRange.length - 1]}`);
}

/**
 * 等待端口就绪
 */
function waitForPort(port, timeout = 30000) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();

    const check = () => {
      const req = http.get(`http://localhost:${port}`, (res) => {
        res.resume();
        resolve();
      });

      req.on('error', () => {
        if (Date.now() - startTime < timeout) {
          setTimeout(check, 500);
        } else {
          reject(new Error(`等待端口 ${port} 超时`));
        }
      });

      req.setTimeout(2000, () => {
        req.destroy();
        if (Date.now() - startTime < timeout) {
          setTimeout(check, 500);
        } else {
          reject(new Error(`等待端口 ${port} 超时`));
        }
      });
    };

    check();
  });
}

/**
 * 创建临时 vite 配置
 */
function createTempViteConfig(port) {
  const template = `import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  base: './',
  server: {
    port: ${port},
    strictPort: false,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})`;

  const tempConfigPath = path.join(rootDir, 'vite.config.temp.ts');
  fs.writeFileSync(tempConfigPath, template);
  return tempConfigPath;
}

/**
 * 启动 Vite 开发服务器
 */
function startViteDevServer(port) {
  console.log(`\n📦 启动 Vite 开发服务器 (端口: ${port})...`);

  // 使用 --config 指定临时配置
  return spawn('npm', ['run', 'dev', '--', '--port', String(port)], {
    cwd: rootDir,
    shell: true,
    stdio: 'inherit',
  });
}

/**
 * 编译 Electron 主进程
 */
function compileElectron() {
  console.log('\n🔨 编译 Electron 主进程...');

  return new Promise((resolve, reject) => {
    const tscProcess = spawn('npm', ['run', 'build:electron'], {
      cwd: rootDir,
      shell: true,
      stdio: 'inherit',
    });

    tscProcess.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error('Electron 编译失败'));
      }
    });
  });
}

/**
 * 启动 Electron
 */
function startElectron(port) {
  console.log(`\n🚀 启动 Electron (加载: http://localhost:${port})...`);

  const electronPath = path.join(rootDir, 'node_modules', '.bin', 'electron');

  return spawn(electronPath, ['.'], {
    cwd: rootDir,
    shell: true,
    stdio: 'inherit',
    env: {
      ...process.env,
      NODE_ENV: 'development',
      ELECTRON_PORT: port, // 将端口传递给 Electron
    },
  });
}

/**
 * 主函数
 */
async function main() {
  try {
    console.log('========================================');
    console.log('   AI WinDBG Electron 启动器');
    console.log('========================================\n');

    // 1. 检测可用端口
    const preferredPort = 3000;
    const port = await getAvailablePort(preferredPort, 10);

    if (port !== preferredPort) {
      console.log(`⚠️  端口 ${preferredPort} 被占用，自动使用端口 ${port}`);
    } else {
      console.log(`✅ 端口 ${port} 可用`);
    }

    // 2. 编译 Electron 主进程
    await compileElectron();

    // 3. 启动 Vite 开发服务器
    const viteProcess = startViteDevServer(port);

    // 4. 等待 Vite 服务器就绪
    console.log(`\n⏳ 等待 Vite 服务器就绪...`);
    await waitForPort(port);
    console.log(`✅ Vite 服务器已就绪: http://localhost:${port}\n`);

    // 5. 启动 Electron
    const electronProcess = startElectron(port);

    // 6. 处理退出
    const cleanup = () => {
      console.log('\n\n🛑 正在停止所有进程...');
      viteProcess.kill();
      electronProcess.kill();
      console.log('✅ 已停止所有进程\n');
    };

    process.on('SIGINT', cleanup);
    process.on('SIGTERM', cleanup);

    // 等待 Electron 进程结束
    electronProcess.on('close', (code) => {
      console.log(`\nElectron 进程已退出 (code: ${code})`);
      viteProcess.kill();
      process.exit(code);
    });

  } catch (error) {
    console.error('\n❌ 启动失败:', error.message);
    process.exit(1);
  }
}

main();
