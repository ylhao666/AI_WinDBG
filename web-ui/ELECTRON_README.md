# Electron 桌面应用

本项目已支持 Electron 桌面应用模式，可以直接访问本地文件系统，获取转储文件的完整绝对路径。

## 功能特性

- ✅ 原生文件选择对话框
- ✅ 获取完整的本地文件路径
- ✅ 文件路径验证（格式、扩展名、大小）
- ✅ 安全的 IPC 通信机制
- ✅ 详细的日志记录
- ✅ 向后兼容 Web 模式

## 安装依赖

```bash
cd web-ui
npm install
```

## 开发模式

### Web 模式（浏览器）

```bash
npm run dev
```

访问 http://localhost:3000

### Electron 模式（桌面应用）

```bash
npm run dev:electron
```

这将同时启动：
1. Vite 开发服务器（端口 3000）
2. Electron 桌面应用

## 构建生产版本

### 构建 Web 版本

```bash
npm run build
```

输出目录：`../src/web/static/frontend`

### 构建 Electron 版本

```bash
npm run build:electron
```

这将：
1. 构建前端资源到 `dist/`
2. 编译 Electron 主进程到 `dist-electron/`

### 打包 Electron 应用

```bash
npm run electron:pack
```

输出目录：`dist-electron-app/`

生成可执行文件：
- Windows: `dist-electron-app/AI WinDBG Setup.exe` (NSIS 安装程序)
- Windows Portable: `dist-electron-app/AI-WinDBG-Portable-0.1.0.exe`

## 测试

### 运行单元测试

```bash
npm run test
```

### 运行测试 UI

```bash
npm run test:ui
```

### 生成测试覆盖率报告

```bash
npm run test:coverage
```

## 文件路径验证

### 前端验证

在 `src/utils/electron.ts` 中实现：

- Windows 路径格式验证（`^[A-Za-z]:\\`）
- 文件扩展名验证（`.dmp`）
- 路径长度限制（最大 260 字符）
- 防止路径遍历攻击（检查 `..`）

### 后端验证

在 `src/web/api/session.py` 中实现：

- 文件存在性检查
- 文件类型验证
- 文件大小限制（最大 10GB）
- 详细的日志记录

## 安全策略

### Electron 安全配置

- ✅ `contextIsolation: true` - 启用上下文隔离
- ✅ `nodeIntegration: false` - 禁用 Node.js 集成
- ✅ `enableRemoteModule: false` - 禁用远程模块
- ✅ `webSecurity: true` - 启用 Web 安全
- ✅ 使用预加载脚本暴露安全的 API

### IPC 通信

所有 IPC 调用都通过预加载脚本进行，确保：

- 主进程和渲染进程隔离
- 只暴露必要的 API
- 参数验证和错误处理

## 日志记录

### 前端日志

- 文件选择操作
- 路径验证结果
- API 调用状态

### 后端日志

- 文件加载请求
- 路径验证结果
- 错误和异常信息

## 项目结构

```
web-ui/
├── electron/
│   ├── main.ts              # Electron 主进程
│   ├── preload.ts           # 预加载脚本
│   └── tsconfig.json       # TypeScript 配置
├── src/
│   ├── components/
│   │   └── FileUpload.tsx  # 文件上传组件（支持 Electron）
│   ├── utils/
│   │   ├── electron.ts     # Electron 工具函数
│   │   └── __tests__/
│   │       └── electron.test.ts  # 单元测试
│   └── test/
│       └── setup.ts       # 测试配置
├── dist/                  # 前端构建输出
├── dist-electron/         # Electron 主进程构建输出
├── dist-electron-app/     # 打包的应用
├── package.json
├── vite.config.ts
├── vitest.config.ts
└── electron-builder.json   # 打包配置
```

## 使用示例

### 在 Electron 中选择文件

1. 点击"选择转储文件"按钮
2. 系统打开原生文件选择对话框
3. 选择 `.dmp` 文件
4. 显示文件信息（路径、名称、大小）
5. 点击"加载文件"按钮

### API 调用

前端通过 `/api/session/load` 接口传递完整文件路径：

```typescript
await sessionAPI.loadDump('C:\\Users\\test\\crash.dmp');
```

后端验证路径后加载转储文件：

```python
# 验证文件路径
is_valid, error_msg = validate_file_path(request.filepath)

# 加载转储文件
success = windbg_engine.load_dump(request.filepath)
```

## 故障排除

### Electron 无法启动

确保已安装所有依赖：
```bash
npm install
```

### 文件选择对话框不显示

检查 Electron 主进程是否正确配置预加载脚本：
```typescript
webPreferences: {
  preload: path.join(__dirname, 'preload.js'),
  contextIsolation: true,
  nodeIntegration: false,
}
```

### 路径验证失败

检查：
1. 文件路径格式是否正确（Windows 绝对路径）
2. 文件扩展名是否为 `.dmp`
3. 文件是否存在
4. 文件大小是否在限制范围内

## 开发注意事项

1. **环境检测**：使用 `isElectron()` 函数检测运行环境
2. **向后兼容**：Web 模式和 Electron 模式都应正常工作
3. **错误处理**：所有异步操作都应包含错误处理
4. **日志记录**：关键操作都应记录日志
5. **安全验证**：所有输入都应进行验证

## 许可证

本项目采用 MIT 许可证。
