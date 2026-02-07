# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 常用命令

### 后端运行
```bash
# CLI 模式
python main.py --mode cli

# Web 模式
python main.py --mode web

# 双模式（CLI + Web 同时运行）
python main.py --mode both

# 指定端口
python main.py --mode web --port 8001
```

### 前端开发
```bash
cd web-ui
npm install
npm run dev          # 开发模式（热重载）
npm run dev:electron  # 启动 Electron 客户端（推荐）
npm run cleanup      # 清理旧的开发进程
npm run build        # 构建生产版本
npm run preview      # 预览构建结果
npm run lint         # 代码检查
npm test             # 运行测试
```

### 客户端启动
```bash
# 启动 Electron 桌面客户端（推荐）
cd web-ui && npm run dev:electron

# 智能启动脚本特性：
# - 自动检测可用端口（从 3000 开始尝试）
# - 端口被占用时自动使用 3001、3002...
# - 如果有旧进程阻塞，先运行 npm run cleanup 清理

# 清理旧的开发进程
cd web-ui && npm run cleanup
```

### 后端开发
```bash
pip install -r requirements.txt
black src/           # 代码格式化
flake8 src/         # 代码检查
mypy src/           # 类型检查
pytest tests/       # 运行测试
```

## 项目架构

### 核心设计理念

1. **持久会话机制**：使用 `subprocess.Popen` 和后台线程管理 cdb 进程，避免每次命令都重新加载 dump 文件。实现位置：`src/windbg/engine.py`

2. **共享组件模式**：CLI 和 Web 模式共享同一个 `SessionManager` 实例，通过 WebSocket 实现状态同步。入口：`main.py` 的 `initialize_components()`

3. **三层架构**：
   - **API 层** (`src/web/api/`)：REST API 端点
   - **服务层** (`src/web/services/`)：业务逻辑
   - **核心层** (`src/core/`, `src/windbg/`, `src/llm/`)：核心功能

### 关键模块

- **`src/windbg/engine.py`**：WinDBG 引擎封装，负责管理持久会话、命令执行、输出解析。使用队列和线程实现实时输出
- **`src/core/session.py`**：会话状态管理，跟踪 dump 文件、命令历史、cdb 进程状态
- **`src/web/app.py`**：FastAPI 应用入口，设置依赖注入和 WebSocket 端点
- **`src/web/websocket/manager.py`**：WebSocket 连接管理，支持输出流和会话状态推送
- **`src/llm/analyzer.py`**：智能分析器，使用 LLM 生成崩溃分析报告
- **`src/nlp/processor.py`**：自然语言处理，将中文命令映射到 WinDBG 命令

### WebSocket 通信

- `ws://localhost:8000/ws/output` - 实时推送命令执行输出
- `ws://localhost:8000/ws/session` - 实时推送会话状态变化

### 配置说明

主配置文件：`config.yaml`

- **WinDBG 路径**：需配置 `windbg.path` 指向 cdb.exe
- **LLM 配置**：支持 OpenAI、OpenRouter、DeepSeek 等提供商
  - 可通过 Web 界面的 LLM 配置页面进行配置（推荐）
  - 每个提供商独立保存 API Key，使用 localStorage 持久化
  - 支持测试连接功能验证配置有效性
  - 配置保存后立即生效，无需重启应用
  - 访问路径：`http://localhost:8000/llm-config`
- **符号路径**：支持本地和 Microsoft 符号服务器

### 开发注意事项

1. **WinDBG 依赖**：项目必须在 Windows 环境运行，且需安装 WinDBG（cdb.exe）

2. **前端构建**：修改 Web 界面后，需要重新构建：`cd web-ui && npm run build`，构建产物存放于 `src/web/static/frontend/`

3. **会话管理**：双模式运行时，CLI 和 Web 共享会话状态，修改需考虑两种模式的兼容性

4. **命令执行标记**：WinDBG 命令执行使用 `DoneDoneDone` 标记检测完成，修改命令执行逻辑时需保留此机制

5. **线程安全**：WinDBG 引擎使用 `threading.Lock` 保护共享状态，访问 `_process` 和 `_output_queue` 时需注意线程安全
