# 示例转储文件说明

本目录包含用于测试的示例转储文件。

## 注意事项

- 示例转储文件仅供测试使用
- 请勿在生产环境中使用这些文件
- 这些文件可能包含敏感信息，请谨慎处理

## 获取示例转储文件

您可以从以下来源获取示例转储文件：

1. **微软官方示例**
   - https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/example-dump-files

2. **创建自己的转储文件**
   - 使用 Task Manager 创建转储文件
   - 使用 ProcDump 工具创建转储文件

3. **使用 WinDBG 示例**
   - WinDBG 安装目录中可能包含示例文件

## 使用示例

加载示例转储文件：

```
文件路径> examples/sample_dumps/example.dmp
```

## 测试命令

加载转储文件后，可以尝试以下命令：

```
> !analyze -v
> kv
> .exr -1
> lm
> ~*
```

## 注意

- 确保转储文件与您的系统架构匹配（x86 或 x64）
- 确保有足够的符号文件
- 某些转储文件可能需要特定的调试工具版本
