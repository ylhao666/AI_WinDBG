# AI WinDBG 崩溃分析器

<div align="center">

**基于 AI 与 WinDBG 内核结合的智能崩溃分析平台**

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/ylhao666/AI_WinDBG?style=social)](https://github.com/ylhao666/AI_WinDBG)

[功能特性](#功能特性) • [快速开始](#快速开始) • [使用指南](#使用指南) • [API 文档](#api-文档) • [贡献指南](#贡献指南)

</div>

---

## 项目概述

AI WinDBG 崩溃分析器是一个现代化的 Windows 崩溃转储分析工具，通过集成 WinDBG 调试引擎和大语言模型（LLM），提供智能化的崩溃分析能力。项目采用前后端分离架构，支持命令行界面（CLI）和可视化 Web 界面，帮助开发者快速定位和理解 Windows 应用程序的崩溃原因。

### 核心优势

- **持久会话机制**：保持 cdb 调试会话持续活跃，避免每次命令都重新加载 dump 文件，大幅提升调试效率
- **自然语言交互**：支持使用中文自然语言描述调试需求，自动生成对应的 WinDBG 命令
- **智能分析引擎**：基于 LLM 的智能分析功能，自动生成结构化的崩溃分析报告
- **双模式运行**：支持 CLI、Web 和双模式运行，满足不同使用场景
- **实时通信**：基于 WebSocket 的实时输出推送和状态同步
- **异步处理**：支持异步和流式分析，提供更好的用户体验

---

## 功能特性

### 核心功能

#### 1. WinDBG 深度集成

- **持久会话管理**：使用 Popen 和线程管理 cdb 进程，实现命令在同一调试会话中连续执行
- **符号文件支持**：自动配置和管理符号文件路径
- **命令执行引擎**：完整的 WinDBG 命令执行和输出解析
- **实时输出流**：命令执行时实时显示输出，无需等待命令完成

#### 2. 智能分析系统

- **LLM 驱动分析**：支持 OpenRouter、OpenAI 等多种 LLM 提供商
- **结构化报告**：自动生成包含崩溃类型、异常信息、调用栈、根本原因和修复建议的分析报告
- **缓存机制**：LLM 响应缓存，减少 API 调用次数和成本
- **异步分析**：支持异步分析，避免阻塞主线程
- **流式输出**：支持流式分析，实时显示分析进度

#### 3. 自然语言处理

- **意图识别**：自动识别用户的调试意图
- **命令映射**：将自然语言描述映射到 WinDBG 命令
- **参数提取**：智能提取命令参数
- **命令建议**：提供智能命令补全和建议

#### 4. 双模式界面

**CLI 模式**：
- 基于 Rich 库的现代化命令行界面
- 支持语法高亮和主题切换
- 命令历史和自动补全
- 三种显示模式（raw/smart/both）

**Web 模式**：
- 基于 React + TypeScript 的现代化 Web 界面
- Ant Design 组件库，美观易用
- 实时输出显示和状态同步
- 响应式设计，支持桌面、平板和移动设备
- WebSocket 实时通信

#### 5. 会话管理

- **状态跟踪**：实时跟踪会话状态（idle/loading/ready/analyzing/error）
- **历史记录**：自动保存命令历史和输出历史
- **元数据管理**：支持会话元数据的存储和查询
- **会话信息**：提供完整的会话信息查询接口

### 技术特点

- **模块化设计**：清晰的模块划分，易于扩展和维护
- **异步架构**：基于 FastAPI 的异步 Web 框架
- **类型安全**：完整的类型注解，支持 mypy 类型检查
- **错误处理**：完善的异常处理和错误提示
- **日志系统**：结构化日志记录，支持多级别日志
- **安全验证**：命令安全验证，防止恶意命令执行
- **配置管理**：灵活的 YAML 配置文件，支持环境变量

---

## 技术栈

### 后端技术

| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.10+ | 核心开发语言 |
| FastAPI | 0.104+ | 异步 Web 框架 |
| Uvicorn | 0.24+ | ASGI 服务器 |
| WebSockets | 12.0+ | 实时通信 |
| OpenAI SDK | 1.0+ | LLM 集成 |
| PyYAML | 6.0+ | 配置文件解析 |
| Rich | 13.0+ | CLI 界面美化 |
| Prompt Toolkit | 3.0+ | 命令行交互 |

### 前端技术

| 技术 | 版本 | 说明 |
|------|------|------|
| React | 18.2+ | UI 框架 |
| TypeScript | 5.2+ | 类型安全 |
| Vite | 5.0+ | 构建工具 |
| Ant Design | 5.12+ | UI 组件库 |
| Axios | 1.6+ | HTTP 客户端 |
| React Router | 7.13+ | 路由管理 |

### 调试工具

| 工具 | 说明 |
|------|------|
| WinDBG (cdb.exe) | Windows 调试工具 |
| Symbol Server | Microsoft 符号服务器 |

---

## 环境要求

### 必需环境

- **Python 3.10 或更高版本**
- **WinDBG (cdb.exe)** - 用于调试转储文件
  - 可从 [Windows SDK](https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/) 安装
  - 或从 [Microsoft Debugging Tools](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/) 下载
- **Node.js 18+** - 用于前端开发（可选，如使用预构建版本则不需要）

### 可选环境

- **LLM API Key** - 用于智能分析功能
  - 推荐使用 [OpenRouter](https://openrouter.ai/)（支持多种模型）
  - 或直接使用 [OpenAI API](https://openai.com/)

### 操作系统

- Windows 10/11（推荐）
- Windows Server 2016+

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/ylhao666/AI_WinDBG.git
cd AI_WinDBG
```

### 2. 安装后端依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并配置相关参数：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置 LLM API Key：

```env
# 推荐使用 OpenRouter（支持多种模型）
OPENROUTER_API_KEY=your_openrouter_api_key_here

# 或者使用 OpenAI 直接访问
# OPENAI_API_KEY=your_openai_api_key_here
```

### 4. 配置 WinDBG 路径

编辑 `config.yaml` 文件，设置 WinDBG 路径：

```yaml
windbg:
  path: "C:\\Program Files (x86)\\Windows Kits\\10\\Debuggers\\x64\\cdb.exe"
  symbol_path: "SRV*C:\\Symbols*https://msdl.microsoft.com/download/symbols"
```

### 5. 构建 Web 界面（可选）

如果需要使用 Web 界面，需要先构建前端：

```bash
cd web-ui
npm install
npm run build
cd ..
```

### 6. 运行应用

#### CLI 模式

```bash
python main.py --mode cli
```

#### Web 模式

```bash
python main.py --mode web
```

访问 http://localhost:8000

#### 双模式（CLI + Web）

```bash
python main.py --mode both
```

---

## 使用指南

### CLI 模式使用

#### 基本操作

1. **启动应用**

```bash
python main.py --mode cli
```

2. **加载转储文件**

启动后，输入转储文件路径：

```
文件路径> C:\path\to\crash.dmp
```

加载成功后，系统会自动启动 cdb 持久会话，所有后续命令将在同一会话中执行。

3. **执行命令**

##### 使用自然语言

```
> 帮我分析崩溃
> 查看调用栈
> 查看异常信息
> 查看模块列表
> 查看所有线程
```

##### 使用 WinDBG 命令

```
> !analyze -v
> kv
> .exr -1
> lmv
> ~*
```

#### 显示模式切换

应用支持三种显示模式：

- **raw**: 只显示 WinDBG 原始输出
- **smart**: 显示原始输出 + 智能分析报告
- **both**: 同时显示两种模式

切换模式：

```
> mode smart
> mode raw
> mode both
```

#### 常用命令

| 命令 | 说明 |
|------|------|
| `help` | 显示帮助信息 |
| `clear` | 清屏 |
| `status` | 显示当前状态（包括 cdb 会话状态和进程 ID） |
| `mode <raw|smart|both>` | 切换显示模式 |
| `exit` | 退出程序（自动关闭 cdb 会话） |

#### 自然语言示例

| 用户输入 | 生成的 WinDBG 命令 |
|---------|-------------------|
| 帮我分析崩溃 | `!analyze -v` |
| 查看调用栈 | `kv` |
| 查看异常 | `.exr -1` |
| 查看模块 | `lmv` |
| 查看线程 | `~*` |
| 查看寄存器 | `r` |
| 反汇编当前地址 | `u` |

### Web 模式使用

#### 访问界面

启动 Web 模式后，在浏览器中访问：

```
http://localhost:8000
```

#### 主要功能

1. **文件上传**：上传崩溃转储文件
2. **命令输入**：支持自然语言和 WinDBG 命令
3. **实时输出**：实时显示命令执行结果
4. **智能分析**：自动生成分析报告
5. **会话管理**：查看和管理当前会话状态
6. **命令历史**：查看历史命令记录

#### WebSocket 连接

Web 界面使用 WebSocket 实现实时通信：

- **输出流**：`ws://localhost:8000/ws/output` - 实时输出推送
- **会话状态**：`ws://localhost:8000/ws/session` - 会话状态同步

### 持久会话特性

本应用采用持久会话机制，具有以下优势：

- **快速响应**：首次加载 dump 文件后，后续命令无需重新加载，执行速度大幅提升
- **状态保持**：cdb 会话保持活跃，可以连续执行多个命令，保持调试上下文
- **资源优化**：避免频繁启动和关闭 cdb 进程，减少系统资源消耗
- **实时输出**：命令执行时实时显示输出，无需等待命令完成
- **会话管理**：使用 `status` 命令可查看当前 cdb 会话状态和进程 ID

**注意事项**：
- 加载新的 dump 文件会自动关闭当前会话并启动新会话
- 退出应用时会自动关闭 cdb 会话
- 如果 cdb 会话意外终止，下次执行命令时会自动重启会话

---

## 配置说明

### 配置文件位置

主配置文件位于 `config.yaml`，包含以下配置项：

### 应用配置

```yaml
app:
  name: "AI WinDBG 崩溃分析器"
  version: "0.1.0"
  debug: true
```

### WinDBG 配置

```yaml
windbg:
  path: "D:\\Windows Kits\\10\\Debuggers\\x64\\cdb.exe"
  symbol_path: "SRV*C:\\Symbols*https://msdl.microsoft.com/download/symbols"
  timeout: 120
```

**参数说明**：
- `path`: cdb.exe 的完整路径
- `symbol_path`: 符号文件路径，支持本地和远程符号服务器
- `timeout`: 命令执行超时时间（秒）

### LLM 配置

```yaml
llm:
  provider: "openrouter"
  model: "z-ai/glm-4.5-air:free"
  api_key: "${OPENROUTER_API_KEY}"
  base_url: "https://openrouter.ai/api/v1"
  site_url: "https://github.com/ylhao666/AI_WinDBG"
  site_name: "AI WinDBG"
  max_tokens: 2000
  temperature: 0.3
  timeout: 60
```

**支持的 LLM 提供商**：

#### OpenRouter（推荐）

支持多种模型，包括 OpenAI、Anthropic、Google 等。

**模型格式**：
- `openai/gpt-4`
- `anthropic/claude-3-opus`
- `google/gemini-pro`
- `z-ai/glm-4.5-air:free`

**优势**：
- 统一 API
- 自动回退
- 成本优化

#### OpenAI

直接使用 OpenAI API。

**模型格式**：
- `gpt-4`
- `gpt-3.5-turbo`

**配置**：
```yaml
llm:
  provider: "openai"
  model: "gpt-4"
  api_key: "${OPENAI_API_KEY}"
```

### CLI 配置

```yaml
cli:
  theme: "dark"
  history_size: 100
  auto_save_history: true
  history_file: "~/.ai_windbg_history"
```

### 显示配置

```yaml
display:
  default_mode: "smart"
  max_output_lines: 1000
  enable_syntax_highlight: true
  enable_colors: true
```

### 缓存配置

```yaml
cache:
  enabled: true
  ttl: 3600
  max_size: 100
```

### 日志配置

```yaml
logging:
  level: "INFO"
  file: "~/.ai_windbg.log"
  max_size: 10485760
  backup_count: 5
```

### 安全配置

```yaml
security:
  enable_command_validation: true
  allow_dangerous_commands: false
  max_command_length: 1000
```

### Web 界面配置

```yaml
web:
  enabled: true
  host: "0.0.0.0"
  port: 8000
  cors_origins: ["*"]
  static_files_path: "./src/web/static/frontend"
  reload: false
  log_level: "info"
```

---

## 项目结构

```
AI_WinDBG/
├── src/                          # 源代码目录
│   ├── cli/                      # CLI 界面模块
│   │   ├── __init__.py
│   │   ├── display.py           # 显示管理器
│   │   ├── history.py           # 命令历史
│   │   ├── interface.py         # CLI 主界面
│   │   ├── themes.py            # 主题配置
│   │   └── validation.py        # 命令验证
│   ├── core/                     # 核心功能模块
│   │   ├── __init__.py
│   │   ├── config.py            # 配置管理
│   │   ├── exceptions.py        # 异常定义
│   │   ├── logger.py            # 日志管理
│   │   └── session.py           # 会话管理
│   ├── llm/                      # LLM 集成模块
│   │   ├── __init__.py
│   │   ├── analyzer.py          # 智能分析器
│   │   ├── cache.py             # 响应缓存
│   │   └── client.py            # LLM 客户端
│   ├── nlp/                      # 自然语言处理模块
│   │   ├── __init__.py
│   │   ├── classifier.py        # 意图分类器
│   │   ├── intents.py           # 意图定义
│   │   ├── mapper.py            # 命令映射器
│   │   ├── processor.py         # NLP 处理器
│   │   └── templates.py         # 提示模板
│   ├── output/                   # 结果处理模块
│   │   ├── __init__.py
│   │   ├── models.py            # 数据模型
│   │   └── modes.py             # 显示模式
│   ├── utils/                    # 工具模块
│   │   └── __init__.py
│   ├── web/                      # Web 界面模块
│   │   ├── api/                 # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── analysis.py      # 分析 API
│   │   │   ├── command.py       # 命令 API
│   │   │   ├── config.py        # 配置 API
│   │   │   └── session.py       # 会话 API
│   │   ├── services/            # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── analysis_service.py
│   │   │   ├── async_analysis_service.py
│   │   │   ├── command_service.py
│   │   │   └── session_service.py
│   │   ├── websocket/           # WebSocket 管理
│   │   │   ├── __init__.py
│   │   │   └── manager.py
│   │   ├── static/              # 静态文件
│   │   │   └── frontend/        # 前端构建产物
│   │   └── app.py               # FastAPI 应用
│   └── windbg/                   # WinDBG 集成模块
│       ├── __init__.py
│       ├── commands_map.py      # 命令映射
│       ├── engine.py            # WinDBG 引擎
│       ├── executor.py          # 命令执行器
│       ├── parser.py            # 输出解析器
│       └── symbols.py           # 符号管理
├── web-ui/                       # 前端源代码
│   ├── src/
│   │   ├── api/                 # API 客户端
│   │   ├── components/          # React 组件
│   │   ├── pages/               # 页面组件
│   │   ├── types/               # TypeScript 类型
│   │   ├── utils/               # 工具函数
│   │   ├── App.tsx              # 主应用组件
│   │   └── main.tsx             # 入口文件
│   ├── electron/                # Electron 配置（可选）
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── tests/                        # 测试目录
│   └── __init__.py
├── docs/                         # 文档目录
│   ├── api_reference.md         # API 参考文档
│   └── user_guide.md            # 用户指南
├── examples/                     # 示例目录
│   ├── README.md
│   └── sample_commands.txt
├── config.yaml                   # 配置文件
├── requirements.txt              # Python 依赖
├── setup.py                      # 安装脚本
├── main.py                       # 应用入口
├── .env.example                  # 环境变量示例
├── .gitignore                    # Git 忽略文件
└── README.md                     # 项目说明
```

---

## API 文档

### REST API

项目提供完整的 REST API，支持以下端点：

#### 会话管理 API

- `GET /api/session/info` - 获取会话信息
- `POST /api/session/load` - 加载转储文件
- `DELETE /api/session/close` - 关闭会话
- `GET /api/session/history` - 获取命令历史

#### 命令执行 API

- `POST /api/command/execute` - 执行命令
- `POST /api/command/natural` - 自然语言命令

#### 分析 API

- `POST /api/analysis/analyze` - 分析输出
- `POST /api/analysis/async` - 异步分析
- `POST /api/analysis/stream` - 流式分析

#### 配置 API

- `GET /api/config` - 获取配置
- `PUT /api/config` - 更新配置

详细的 API 文档请参考 [docs/api_reference.md](docs/api_reference.md)

### WebSocket API

#### 输出流 WebSocket

**端点**：`ws://localhost:8000/ws/output`

**用途**：实时推送命令执行输出

#### 会话状态 WebSocket

**端点**：`ws://localhost:8000/ws/session`

**用途**：实时推送会话状态变化

---

## 开发指南

### 后端开发

#### 环境设置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装开发依赖
pip install -r requirements.txt
```

#### 代码规范

```bash
# 代码格式化
black src/

# 代码检查
flake8 src/

# 类型检查
mypy src/
```

#### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_windbg.py

# 生成覆盖率报告
pytest --cov=src tests/
```

### 前端开发

#### 环境设置

```bash
cd web-ui

# 安装依赖
npm install

# 开发模式（热重载）
npm run dev

# 构建生产版本
npm run build

# 预览构建结果
npm run preview
```

#### 代码规范

```bash
# 代码检查
npm run lint

# 运行测试
npm test

# 测试覆盖率
npm run test:coverage
```

### 调试技巧

#### 启用调试模式

在 `config.yaml` 中设置：

```yaml
app:
  debug: true
logging:
  level: "DEBUG"
```

#### 查看日志

日志文件位置：`~/.ai_windbg.log`

#### 使用 VS Code 调试

创建 `.vscode/launch.json`：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "args": ["--mode", "cli"]
    }
  ]
}
```

---

## 常见问题

### Q: WinDBG 未找到

**A**: 请确保已安装 WinDBG，并在 `config.yaml` 中配置正确的路径，或将 WinDBG 添加到系统 PATH。

### Q: LLM 功能不可用

**A**: 请确保已配置有效的 LLM API Key（OpenRouter 或 OpenAI），并检查网络连接。

### Q: 如何切换 LLM 提供商？

**A**: 编辑 `config.yaml` 文件中的 `llm.provider` 配置：
- 使用 OpenRouter: `provider: "openrouter"`，并设置 `OPENROUTER_API_KEY`
- 使用 OpenAI: `provider: "openai"`，并设置 `OPENAI_API_KEY`

### Q: 智能分析失败

**A**: 检查 LLM API Key 是否有效，以及是否有足够的 API 配额。如果使用 OpenRouter，请确保模型名称格式正确（如 `openai/gpt-4`）。

### Q: Web 界面无法访问

**A**: 检查以下几点：
1. 确认已构建前端：`cd web-ui && npm run build`
2. 检查 `config.yaml` 中的 `web.port` 配置
3. 确认防火墙允许访问指定端口
4. 查看控制台日志获取详细错误信息

### Q: 如何在开发模式下运行 Web 界面？

**A**: 使用以下命令：
```bash
cd web-ui
npm run dev
```

开发服务器运行在 `http://localhost:3000`，支持热重载。

### Q: 双模式运行时，CLI 和 Web 界面如何同步？

**A**: 双模式运行时，CLI 和 Web 界面共享同一个 `SessionManager` 实例，会话状态自动同步。通过 WebSocket 实现实时输出推送。

### Q: cdb 会话意外终止怎么办？

**A**: 应用会自动检测会话状态，如果发现会话已终止，会在下次执行命令时自动重启会话。你也可以使用 `status` 命令查看会话状态。

### Q: 如何查看详细的调试信息？

**A**: 在 `config.yaml` 中设置日志级别为 `DEBUG`：

```yaml
logging:
  level: "DEBUG"
```

---

## 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 遵循 PEP 8 Python 代码规范
- 使用 Black 进行代码格式化
- 添加适当的类型注解
- 编写单元测试
- 更新相关文档

### 提交规范

使用语义化提交信息：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式（不影响功能）
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具相关

示例：
```
feat: 添加流式分析功能
fix: 修复 cdb 会话超时问题
docs: 更新 API 文档
```

---

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 联系方式

- **项目主页**: https://github.com/ylhao666/AI_WinDBG
- **问题反馈**: https://github.com/ylhao666/AI_WinDBG/issues
- **文档**: [docs/api_reference.md](docs/api_reference.md) | [docs/user_guide.md](docs/user_guide.md)

---

## 致谢

感谢以下开源项目和工具：

- [WinDBG](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/) - Windows 调试工具
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [React](https://react.dev/) - 用于构建用户界面的 JavaScript 库
- [Ant Design](https://ant.design/) - 企业级 UI 设计语言和 React UI 库
- [OpenAI](https://openai.com/) - 提供强大的 LLM 能力
- [OpenRouter](https://openrouter.ai/) - 统一的 LLM API 接口

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐️ Star 支持一下！**

Made with ❤️ by [ylhao666](https://github.com/ylhao666)

</div>
