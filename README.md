# AI WinDBG 崩溃分析器

基于 AI 与 WinDBG 内核结合的崩溃分析应用程序，帮助用户快速分析和理解 Windows 崩溃转储文件。

## 功能特性

### 核心功能

- **WinDBG 集成**: 完整集成 WinDBG 调试引擎，支持加载和分析崩溃转储文件
- **持久会话**: 保持 cdb 调试会话持续活跃，避免每次命令都重新加载 dump 文件，大幅提升调试效率
- **自然语言交互**: 支持使用自然语言描述调试需求，自动生成对应的 WinDBG 命令
- **智能分析**: 基于 LLM 的智能分析功能，自动生成结构化的崩溃分析报告
- **双模式显示**: 支持原始输出和智能分析两种显示模式
- **命令历史**: 自动保存命令历史，方便重复使用

### 技术特点

- **模块化设计**: 清晰的模块划分，易于扩展和维护
- **异步处理**: 支持异步命令执行，提高响应速度
- **缓存机制**: LLM 响应缓存，减少 API 调用次数
- **安全验证**: 命令安全验证，防止恶意命令执行
- **持久会话管理**: 使用 Popen 和线程管理 cdb 进程，实现命令在同一调试会话中连续执行

## 安装

### 环境要求

- Python 3.10 或更高版本
- WinDBG (cdb.exe) - 用于调试转储文件
- LLM API Key (可选) - 用于智能分析功能（推荐使用 OpenRouter）

### 安装步骤

1. 克隆仓库

```bash
git clone https://github.com/yourusername/ai-windbg.git
cd ai-windbg
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 配置环境变量

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

4. 运行应用

```bash
python main.py
```

## 使用指南

### 基本使用

1. **启动应用**

```bash
python main.py
```

2. **加载转储文件**

启动后，输入转储文件路径：

```
文件路径> C:\path\to\crash.dmp
```

加载成功后，系统会自动启动 cdb 持久会话，所有后续命令将在同一会话中执行，无需重新加载 dump 文件。

3. **执行命令**

#### 使用自然语言

```
> 帮我分析崩溃
> 查看调用栈
> 查看异常信息
```

#### 使用 WinDBG 命令

```
> !analyze -v
> kv
> .exr -1
```

### 持久会话特性

本应用采用持久会话机制，具有以下优势：

- **快速响应**: 首次加载 dump 文件后，后续命令无需重新加载，执行速度大幅提升
- **状态保持**: cdb 会话保持活跃，可以连续执行多个命令，保持调试上下文
- **资源优化**: 避免频繁启动和关闭 cdb 进程，减少系统资源消耗
- **实时输出**: 命令执行时实时显示输出，无需等待命令完成，提供更好的交互体验
- **会话管理**: 使用 `status` 命令可查看当前 cdb 会话状态和进程 ID

**注意事项**:
- 加载新的 dump 文件会自动关闭当前会话并启动新会话
- 退出应用时会自动关闭 cdb 会话
- 如果 cdb 会话意外终止，下次执行命令时会自动重启会话

### 显示模式

应用支持三种显示模式：

- **raw**: 只显示 WinDBG 原始输出
- **smart**: 显示原始输出 + 智能分析报告
- **both**: 同时显示两种模式

切换模式：

```
> mode smart
```

### 常用命令

| 命令 | 说明 |
|------|------|
| `help` | 显示帮助信息 |
| `clear` | 清屏 |
| `status` | 显示当前状态（包括 cdb 会话状态和进程 ID） |
| `mode <raw|smart|both>` | 切换显示模式 |
| `exit` | 退出程序（自动关闭 cdb 会话） |

### 自然语言示例

| 用户输入 | 生成的 WinDBG 命令 |
|---------|-------------------|
| 帮我分析崩溃 | `!analyze -v` |
| 查看调用栈 | `kv` |
| 查看异常 | `.exr -1` |
| 查看模块 | `lmv` |
| 查看线程 | `~*` |

## 配置

配置文件位于 `config.yaml`，包含以下配置项：

### 应用配置

```yaml
app:
  name: "AI WinDBG 崩溃分析器"
  version: "0.1.0"
  debug: false
```

### WinDBG 配置

```yaml
windbg:
  path: "C:\\Program Files (x86)\\Windows Kits\\10\\Debuggers\\x64\\cdb.exe"
  symbol_path: "SRV*C:\\Symbols*https://msdl.microsoft.com/download/symbols"
  timeout: 30
```

### LLM 配置

```yaml
llm:
  provider: "openrouter"
  model: "openai/gpt-4"
  api_key: "${OPENROUTER_API_KEY}"
  base_url: "https://openrouter.ai/api/v1"
  site_url: "https://github.com/yourusername/ai-windbg"
  site_name: "AI WinDBG"
  max_tokens: 2000
  temperature: 0.3
  timeout: 60
```

**支持的 LLM 提供商**:

- **OpenRouter** (推荐): 支持多种模型，包括 OpenAI、Anthropic、Google 等
  - 模型格式: `openai/gpt-4`, `anthropic/claude-3-opus`, `google/gemini-pro` 等
  - 优势: 统一 API、自动回退、成本优化
  
- **OpenAI**: 直接使用 OpenAI API
  - 模型格式: `gpt-4`, `gpt-3.5-turbo` 等
  - 需要设置 `provider: "openai"` 和 `api_key: "${OPENAI_API_KEY}"`

### CLI 配置

```yaml
cli:
  theme: "dark"
  history_size: 100
  auto_save_history: true
  history_file: "~/.ai_windbg_history"
```

## 项目结构

```
AI_WinDBG/
├── src/                    # 源代码目录
│   ├── cli/                # CLI 界面模块
│   ├── windbg/             # WinDBG 集成模块
│   ├── nlp/                # 自然语言处理模块
│   ├── llm/                # LLM 集成模块
│   ├── output/             # 结果处理模块
│   ├── core/               # 核心功能模块
│   └── utils/              # 工具模块
├── tests/                  # 测试目录
├── docs/                   # 文档目录
├── examples/               # 示例目录
├── config.yaml             # 配置文件
├── requirements.txt        # 依赖清单
├── main.py                 # 应用入口
└── README.md               # 项目说明
```

## 开发

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black src/
```

### 代码检查

```bash
flake8 src/
```

## 常见问题

### Q: WinDBG 未找到

A: 请确保已安装 WinDBG，并在 `config.yaml` 中配置正确的路径，或将 WinDBG 添加到系统 PATH。

### Q: LLM 功能不可用

A: 请确保已配置有效的 LLM API Key（OpenRouter 或 OpenAI），并检查网络连接。

### Q: 如何切换 LLM 提供商？

A: 编辑 `config.yaml` 文件中的 `llm.provider` 配置：
- 使用 OpenRouter: `provider: "openrouter"`，并设置 `OPENROUTER_API_KEY`
- 使用 OpenAI: `provider: "openai"`，并设置 `OPENAI_API_KEY`

### Q: 智能分析失败

A: 检查 LLM API Key 是否有效，以及是否有足够的 API 配额。如果使用 OpenRouter，请确保模型名称格式正确（如 `openai/gpt-4`）。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

- 项目主页: https://github.com/yourusername/ai-windbg
- 问题反馈: https://github.com/yourusername/ai-windbg/issues
