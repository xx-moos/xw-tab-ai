# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 AI 代码补全系统的 monorepo，包含两个核心子项目：

1. **VSCode 扩展** (`vscode-nes-main/`): 提供编辑器集成的前端界面
2. **Python 后端服务** (`sweep_autocomplete-0.1.1/`): 基于 llama.cpp 的本地推理服务

两个项目通过 HTTP API 通信，VSCode 扩展调用本地 Python 服务获取代码补全建议。

## 项目结构

```
tab-ai/
├── vscode-nes-main/     # VSCode 扩展（TypeScript + Bun）
│   ├── src/                              # 源代码
│   │   ├── extension/                    # 扩展入口和状态栏
│   │   ├── editor/                       # 编辑器集成（补全provider、跳转管理）
│   │   ├── api/                          # HTTP客户端和schema定义
│   │   ├── services/                     # 本地服务器管理
│   │   ├── telemetry/                    # 指标追踪和文档监控
│   │   ├── core/                         # 配置和常量
│   │   └── utils/                        # 工具函数
│   ├── test/                             # 单元测试
│   ├── package.json                      # 依赖和脚本
│   ├── tsconfig.json                     # TypeScript配置
│   ├── biome.json                        # Linter配置
│   └── CLAUDE.md                         # VSCode扩展详细文档
│
└── sweep_autocomplete-0.1.1/  # Python后端
    ├── sweep_autocomplete/               # 主包
    │   ├── app.py                        # FastAPI应用入口
    │   ├── cli.py                        # 命令行接口
    │   ├── config.py                     # 配置管理
    │   ├── autocomplete/                 # 补全核心逻辑
    │   │   ├── llm_local.py              # llama.cpp集成
    │   │   ├── next_edit_autocomplete.py # 补全主逻辑
    │   │   ├── next_edit_autocomplete_retrieval.py  # 上下文检索
    │   │   ├── next_edit_autocomplete_service.py    # 服务层
    │   │   └── next_edit_autocomplete_utils.py      # 工具函数
    │   ├── dataclasses/                  # 数据模型
    │   └── utils/                        # 通用工具
    └── pyproject.toml                    # Python项目配置
```

## VSCode 扩展开发

### 常用命令

```bash
cd vscode-nes-main

# 构建扩展
bun build

# 代码检查
bun lint          # 运行 Biome linter
bun fix           # 自动修复 lint 问题
bun typecheck     # TypeScript 类型检查

# 测试
bun test          # 运行所有单元测试
```

### 技术栈
- **运行时**: Bun
- **语言**: TypeScript（严格模式）
- **Linter**: Biome
- **语法高亮**: Shiki
- **Schema验证**: Zod

### 关键特性
- **Inline Edit**: 光标位置的行内补全
- **Jump Edit**: 跨行代码块补全，带语法高亮预览
- **上下文收集**: 自动收集最近访问文件、代码定义、剪贴板内容
- **UTF-8/UTF-16转换**: API使用UTF-8偏移，VSCode使用UTF-16

详细架构和开发指南见 `vscode-nes-main/vscode-nes-main/CLAUDE.md`

## Python 后端开发

### 安装和运行

```bash
cd sweep_autocomplete-0.1.1

# 安装依赖（推荐使用 uv）
pip install -e .

# 启动服务器
sweep-autocomplete
# 或
python -m sweep_autocomplete.cli
```

### 技术栈
- **框架**: FastAPI + Uvicorn/Hypercorn
- **推理引擎**: llama-cpp-python
- **模型管理**: huggingface-hub
- **日志**: loguru
- **数据验证**: pydantic

### 核心模块
- `app.py`: FastAPI应用和路由定义
- `autocomplete/llm_local.py`: llama.cpp模型加载和推理
- `autocomplete/next_edit_autocomplete.py`: 补全算法核心
- `autocomplete/next_edit_autocomplete_retrieval.py`: 上下文检索和排序
- `autocomplete/next_edit_autocomplete_service.py`: 服务层封装

### API端点
- `POST /autocomplete`: 获取代码补全建议
- 默认端口: 8081（可通过VSCode配置修改）

## 开发工作流

### 1. 修改 VSCode 扩展
```bash
cd vscode-nes-main
bun install
bun typecheck && bun lint
bun build
# 在 VSCode 中按 F5 启动调试
```

### 2. 修改 Python 后端
```bash
cd sweep_autocomplete-0.1.1
pip install -e .
sweep-autocomplete  # 启动服务测试
```

### 3. 联调测试
1. 启动 Python 后端服务（端口 8081）
2. 在 VSCode 中启动扩展调试
3. 扩展会自动连接本地服务器

## 依赖关系

```
VSCode 扩展 (TypeScript)
    ↓ HTTP API
Python 后端 (FastAPI)
    ↓
llama.cpp (本地推理)
    ↓
Hugging Face 模型
```

## 注意事项

1. **本地服务器依赖**: VSCode扩展需要 `uvx`（来自uv包管理器）自动启动Python服务
2. **模型下载**: 首次运行会从 Hugging Face 下载模型文件
3. **文件大小限制**: 超大文件会被跳过补全
4. **敏感文件排除**: 默认排除 `.env`、`*.pem`、`*.key` 等敏感文件
5. **跨平台兼容**: 使用 Unix 风格路径分隔符（`/`）

## Git 工作流

- 主分支: `main`
- 当前状态: clean（无未提交更改）
- 最近提交: 
  - `4d975b1 init`
  - `4ec9563 first commit`
