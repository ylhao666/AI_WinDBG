# API 参考文档

## 目录

1. [核心模块](#核心模块)
2. [WinDBG 集成](#windbg-集成)
3. [NLP 处理](#nlp-处理)
4. [LLM 集成](#llm-集成)
5. [CLI 界面](#cli-界面)
6. [输出处理](#输出处理)

## 核心模块

### ConfigManager

配置管理器，负责加载和管理应用配置。

#### 方法

##### `__init__(config_path: str = "config.yaml")`

初始化配置管理器。

**参数**:
- `config_path`: 配置文件路径

**示例**:
```python
config = ConfigManager()
```

##### `get(key: str, default: Any = None) -> Any`

获取配置值。

**参数**:
- `key`: 配置键，支持点号分隔的嵌套键
- `default`: 默认值

**返回**: 配置值

**示例**:
```python
api_key = config.get("llm.api_key", "")
```

##### `set(key: str, value: Any)`

设置配置值。

**参数**:
- `key`: 配置键
- `value`: 配置值

**示例**:
```python
config.set("llm.model", "gpt-4")
```

### SessionManager

会话管理器，负责管理应用会话状态。

#### 方法

##### `load_dump(dump_path: str)`

加载转储文件。

**参数**:
- `dump_path`: 转储文件路径

**示例**:
```python
session.load_dump("crash.dmp")
```

##### `set_display_mode(mode: DisplayMode)`

设置显示模式。

**参数**:
- `mode`: 显示模式

**示例**:
```python
session.set_display_mode(DisplayMode.SMART)
```

##### `add_output(output: str, command: str, mode: DisplayMode)`

添加输出到历史。

**参数**:
- `output`: 输出内容
- `command`: 执行的命令
- `mode`: 显示模式

**示例**:
```python
session.add_output(output, command, DisplayMode.SMART)
```

## WinDBG 集成

### WinDBGEngine

WinDBG 调试引擎封装类。

#### 方法

##### `__init__(config: Optional[ConfigManager] = None)`

初始化 WinDBG 引擎。

**参数**:
- `config`: 配置管理器

**示例**:
```python
engine = WinDBGEngine(config)
```

##### `load_dump(dump_path: str) -> bool`

加载崩溃转储文件。

**参数**:
- `dump_path`: 转储文件路径

**返回**: 是否成功

**异常**:
- `DumpLoadError`: 加载失败

**示例**:
```python
engine.load_dump("crash.dmp")
```

##### `execute_command(command: str) -> CommandResult`

执行 WinDBG 命令。

**参数**:
- `command`: WinDBG 命令

**返回**: 命令执行结果

**异常**:
- `CommandExecutionError`: 执行失败

**示例**:
```python
result = engine.execute_command("k")
print(result.output)
```

### CommandExecutor

WinDBG 命令执行器。

#### 方法

##### `analyze_crash(verbose: bool = True) -> CommandResult`

执行崩溃分析。

**参数**:
- `verbose`: 是否详细输出

**返回**: 命令执行结果

**示例**:
```python
result = executor.analyze_crash()
```

##### `get_call_stack(verbose: bool = False) -> CommandResult`

获取调用栈。

**参数**:
- `verbose`: 是否详细输出

**返回**: 命令执行结果

**示例**:
```python
result = executor.get_call_stack(verbose=True)
```

## NLP 处理

### NLPProcessor

自然语言处理器。

#### 方法

##### `parse_input(user_input: str) -> Dict`

解析用户输入。

**参数**:
- `user_input`: 用户输入

**返回**: 解析结果字典

**异常**:
- `NLPError`: 解析失败

**示例**:
```python
result = processor.parse_input("帮我分析崩溃")
print(result['command'])  # !analyze -v
```

##### `classify_intent(text: str) -> Tuple[str, float]`

分类用户意图。

**参数**:
- `text`: 输入文本

**返回**: (意图, 置信度)

**示例**:
```python
intent, confidence = processor.classify("查看调用栈")
```

### IntentClassifier

意图分类器。

#### 方法

##### `classify(text: str) -> Tuple[Intent, float]`

分类用户意图。

**参数**:
- `text`: 输入文本

**返回**: (意图枚举, 置信度)

**示例**:
```python
intent, confidence = classifier.classify("分析崩溃")
```

## LLM 集成

### LLMClient

LLM 客户端。

#### 方法

##### `__init__(config: Optional[ConfigManager] = None)`

初始化 LLM 客户端。

**参数**:
- `config`: 配置管理器

**示例**:
```python
client = LLMClient(config)
```

##### `generate_completion(prompt: str, max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> str`

生成补全。

**参数**:
- `prompt`: 提示文本
- `max_tokens`: 最大 token 数
- `temperature`: 温度参数

**返回**: 生成的文本

**异常**:
- `APIError`: API 调用失败

**示例**:
```python
response = client.generate_completion("分析以下崩溃")
```

##### `generate_json_completion(prompt: str, max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> Dict[str, Any]`

生成 JSON 格式的补全。

**参数**:
- `prompt`: 提示文本
- `max_tokens`: 最大 token 数
- `temperature`: 温度参数

**返回**: 解析后的 JSON 字典

**异常**:
- `APIError`: API 调用失败
- `LLMError`: JSON 解析失败

**示例**:
```python
result = client.generate_json_completion(prompt)
```

### SmartAnalyzer

智能分析器。

#### 方法

##### `analyze_output(raw_output: str, command: str, use_cache: bool = True) -> AnalysisReport`

分析 WinDBG 输出。

**参数**:
- `raw_output`: WinDBG 原始输出
- `command`: 执行的命令
- `use_cache`: 是否使用缓存

**返回**: 分析报告

**异常**:
- `AnalysisError`: 分析失败

**示例**:
```python
report = analyzer.analyze_output(output, command)
print(report.summary)
```

## CLI 界面

### CLIInterface

CLI 界面主控制器。

#### 方法

##### `__init__(config: Optional[ConfigManager] = None)`

初始化 CLI 界面。

**参数**:
- `config`: 配置管理器

**示例**:
```python
cli = CLIInterface(config)
```

##### `run()`

运行主循环。

**示例**:
```python
cli.run()
```

##### `process_command(user_input: str)`

处理用户命令。

**参数**:
- `user_input`: 用户输入

**示例**:
```python
cli.process_command("帮我分析崩溃")
```

## 输出处理

### DisplayManager

显示管理器。

#### 方法

##### `print_raw_output(output: str)`

打印原始输出。

**参数**:
- `output`: 输出内容

**示例**:
```python
display.print_raw_output(output)
```

##### `print_smart_analysis(report: AnalysisReport)`

打印智能分析报告。

**参数**:
- `report`: 分析报告

**示例**:
```python
display.print_smart_analysis(report)
```

### AnalysisReport

分析报告数据类。

#### 属性

- `summary`: 崩溃摘要
- `crash_type`: 崩溃类型
- `exception_code`: 异常代码
- `exception_address`: 异常地址
- `call_stack`: 调用栈列表
- `root_cause`: 根本原因
- `suggestions`: 修复建议列表
- `confidence`: 置信度
- `raw_output`: 原始输出
- `timestamp`: 时间戳

**示例**:
```python
report = AnalysisReport()
report.summary = "程序发生了访问违规异常"
report.crash_type = "Access Violation"
```

## 异常类

### 核心异常

- `AIWinDBGError`: 基础异常类
- `ConfigError`: 配置错误
- `CLIError`: CLI 错误

### WinDBG 异常

- `WinDBGError`: WinDBG 基础异常
- `DumpLoadError`: 转储文件加载失败
- `CommandExecutionError`: 命令执行失败
- `SymbolLoadError`: 符号加载失败

### NLP 异常

- `NLPError`: 自然语言处理错误
- `IntentClassificationError`: 意图分类错误
- `CommandMappingError`: 命令映射错误

### LLM 异常

- `LLMError`: LLM 错误
- `APIError`: API 调用错误
- `AnalysisError`: 分析错误

### 输出异常

- `OutputError`: 输出处理错误
- `FormattingError`: 格式化错误
- `ExportError`: 导出错误

## 枚举类

### DisplayMode

显示模式枚举。

- `RAW`: 原始输出模式
- `SMART`: 智能分析模式
- `BOTH`: 同时显示两种模式

### SessionState

会话状态枚举。

- `IDLE`: 空闲状态
- `LOADING`: 加载中
- `READY`: 就绪
- `ANALYZING`: 分析中
- `ERROR`: 错误

### Intent

用户意图枚举。

- `ANALYZE_CRASH`: 分析崩溃
- `VIEW_STACK`: 查看调用栈
- `VIEW_EXCEPTION`: 查看异常
- `VIEW_MEMORY`: 查看内存
- `VIEW_MODULES`: 查看模块
- `VIEW_THREADS`: 查看线程
- `VIEW_REGISTERS`: 查看寄存器
- `DISASSEMBLE`: 反汇编
- `LOAD_SYMBOLS`: 加载符号
- `CUSTOM_COMMAND`: 自定义命令
- `HELP`: 帮助
- `EXIT`: 退出
