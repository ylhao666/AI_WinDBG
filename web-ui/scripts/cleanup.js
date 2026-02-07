/**
 * 优雅停止进程脚本
 * 用于停止 Vite 和 Electron 进程
 */

import { exec } from 'child_process';
import http from 'http';

/**
 * 获取占用指定端口的进程 ID（Windows）
 */
function getProcessByPort(port) {
  return new Promise((resolve, reject) => {
    exec(`netstat -ano | findstr :${port}`, (error, stdout) => {
      if (error) {
        resolve([]);
        return;
      }

      const lines = stdout.split('\n');
      const pids = new Set();

      for (const line of lines) {
        const parts = line.trim().split(/\s+/);
        if (parts.length >= 5 && parts[1].includes(`:${port}`)) {
          pids.add(parseInt(parts[parts.length - 1], 10));
        }
      }

      resolve(Array.from(pids));
    });
  });
}

/**
 * 检查端口是否为 Node.js/Vite/Electron 进程
 */
async function isTargetProcess(pid) {
  return new Promise((resolve) => {
    exec(`tasklist /FI "PID eq ${pid}" /FO CSV /NH`, (error, stdout) => {
      if (error || !stdout.trim()) {
        resolve(false);
        return;
      }

      const parts = stdout.split(',');
      if (parts.length > 0) {
        const processName = parts[0].replace(/"/g, '').toLowerCase();
        // 检查是否为 node.exe 或 electron.exe
        const isTarget = processName === 'node.exe' || processName === 'electron.exe';
        resolve(isTarget);
      } else {
        resolve(false);
      }
    });
  });
}

/**
 * 停止进程
 */
function killProcess(pid) {
  return new Promise((resolve) => {
    exec(`taskkill /PID ${pid} /F`, (error) => {
      if (error) {
        console.log(`  ⚠️  无法停止进程 ${pid}: ${error.message}`);
      } else {
        console.log(`  ✅ 已停止进程 ${pid}`);
      }
      resolve();
    });
  });
}

/**
 * 主函数
 */
async function main() {
  console.log('========================================');
  console.log('   清理开发服务器进程');
  console.log('========================================\n');

  // 检查端口 3000-3009
  const ports = Array.from({ length: 10 }, (_, i) => 3000 + i);
  let stoppedCount = 0;

  for (const port of ports) {
    try {
      const pids = await getProcessByPort(port);

      if (pids.length > 0) {
        console.log(`\n端口 ${port} 被占用:`);

        for (const pid of pids) {
          const isTarget = await isTargetProcess(pid);

          if (isTarget) {
            console.log(`  发现目标进程: PID ${pid}`);
            await killProcess(pid);
            stoppedCount++;
          } else {
            console.log(`  跳过非目标进程: PID ${pid}`);
          }
        }
      }
    } catch (error) {
      console.error(`检查端口 ${port} 时出错:`, error.message);
    }
  }

  console.log('\n========================================');
  if (stoppedCount > 0) {
    console.log(`   共停止 ${stoppedCount} 个进程`);
  } else {
    console.log('   没有找到需要停止的进程');
  }
  console.log('========================================\n');
}

main();
