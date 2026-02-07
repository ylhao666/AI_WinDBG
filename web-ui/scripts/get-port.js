import http from 'http';

/**
 * 检查端口是否可用
 * @param {number} port - 端口号
 * @returns {Promise<boolean>} - true 表示可用
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
 * 获取可用端口，从指定端口开始尝试
 * @param {number} startPort - 起始端口
 * @param {number} maxAttempts - 最大尝试次数
 * @returns {Promise<number>} - 可用的端口号
 */
async function getAvailablePort(startPort = 3000, maxAttempts = 10) {
  for (let i = 0; i < maxAttempts; i++) {
    const port = startPort + i;
    if (await isPortAvailable(port)) {
      return port;
    }
  }
  throw new Error(`无法找到可用端口，已尝试 ${startPort} 到 ${startPort + maxAttempts - 1}`);
}

/**
 * 主函数
 */
async function main() {
  const port = await getAvailablePort(3000, 10);
  console.log(port);
}

main().catch(err => {
  console.error(err.message);
  process.exit(1);
});
