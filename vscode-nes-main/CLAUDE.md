# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个VSCode扩展插件，提供基于Sweep AI模型的智能代码补全功能（Next Edit Autocomplete）。插件通过本地服务器与AI模型通信，提供两种补全模式：

- **Inline Edit**: 光标位置的行内补全建议
- **Jump Edit**: 跨行的代码块补全，带可视化高亮和装饰

## 核心架构

### 扩展入口
- `src/extension/activate.ts`: 扩展激活入口，注册所有命令、事件监听器和provider

### 编辑器集成
- `src/editor/inline-edit-provider.ts`: 实现VSCode的InlineCompletionItemProvider接口，处理补全请求和响应
- `src/editor/jump-edit-manager.ts`: 管理跨行补全的显示、接受和取消逻辑
- `src/editor/edit-display-classifier.ts`: 分类补全显示方式（inline vs jump）
- `src/editor/syntax-highlight-renderer.ts`: 使用Shiki渲染语法高亮的补全预览

### API通信
- `src/api/client.ts`: 与本地autocomplete服务器通信的HTTP客户端
- `src/api/schemas.ts`: Zod schema定义，用于请求/响应验证
- `src/api/retrieval-chunks.ts`: 处理代码上下文检索和去重

### 本地服务
- `src/services/local-server.ts`: 管理本地Python服务器（通过uvx运行sweep-autocomplete）的生命周期

### 遥测追踪
- `src/telemetry/document-tracker.ts`: 追踪文档变更、光标移动、文件访问历史
- `src/telemetry/autocomplete-metrics.ts`: 收集补全指标（显示、接受、拒绝）
- `src/telemetry/edit-tracking-anchor.ts`: 追踪编辑位置的锚点
- `src/telemetry/unified-diff.ts`: 生成统一diff格式

### 配置和工具
- `src/core/config.ts`: 读取和管理扩展配置
- `src/core/constants.ts`: 全局常量定义
- `src/utils/path.ts`: 路径处理工具
- `src/utils/text.ts`: 文本处理工具（UTF-8/UTF-16转换、文件大小检查）

## 开发命令

### 构建
```bash
bun build
```
编译TypeScript到`out/extension.js`（CommonJS格式，target=node）

### 代码质量
```bash
bun lint          # 运行Biome linter检查
bun fix           # 自动修复lint问题
bun typecheck     # TypeScript类型检查（不生成文件）
```

### 测试
```bash
bun test          # 运行所有测试（test/目录）
```

测试文件：
- `test/autocomplete-metrics.test.ts`
- `test/edit-display-classifier.test.ts`
- `test/retrieval-chunks.test.ts`
- `test/unified-diff.test.ts`

## 技术栈

- **运行时**: Bun（开发和构建）
- **语言**: TypeScript（严格模式，使用tsgo预览版）
- **Linter**: Biome（tab缩进，双引号）
- **语法高亮**: Shiki（JavaScript引擎）
- **Schema验证**: Zod
- **本地服务**: Python（通过uvx运行sweep-autocomplete包）

## 关键配置

### TypeScript配置
- 使用`~/`作为`src/`的路径别名
- 启用所有严格检查（noUncheckedIndexedAccess、exactOptionalPropertyTypes等）
- 模块解析：bundler模式
- 不生成输出文件（noEmit: true）

### VSCode扩展配置
- 激活事件：`onStartupFinished`
- 主入口：`out/extension.js`
- 最低VSCode版本：1.108.0

### 用户配置项
- `sweep.enabled`: 启用/禁用补全
- `sweep.maxContextFiles`: 最大上下文文件数（默认5）
- `sweep.autocompleteExclusionPatterns`: 排除文件模式（默认排除.env、密钥文件等）
- `sweep.localPort`: 本地服务器端口（默认8081）

## 关键命令

- `sweep.triggerNextEdit`: 手动触发补全
- `sweep.acceptJumpEdit`: 接受跨行补全（快捷键：Tab/Alt+Tab）
- `sweep.dismissJumpEdit`: 拒绝跨行补全（快捷键：Escape）
- `sweep.toggleEnabled`: 切换启用状态
- `sweep.showMenu`: 显示菜单

## 开发注意事项

1. **本地服务器依赖**: 扩展需要`uvx`（来自uv包管理器）来运行Python服务器，首次启动会自动安装
2. **文件大小限制**: 超大文件会被跳过补全（见`utils/text.ts`的`isFileTooLarge`）
3. **UTF-8/UTF-16转换**: API使用UTF-8字节偏移，VSCode使用UTF-16，需要转换（见`utils/text.ts`）
4. **补全分类逻辑**: 根据光标位置和编辑范围自动选择inline或jump模式（见`edit-display-classifier.ts`）
5. **语法高亮渲染**: Jump edit使用SVG装饰器渲染带语法高亮的代码预览
6. **上下文收集**: 自动收集最近访问的文件、代码定义、使用位置、剪贴板内容作为补全上下文

## CI/CD

GitHub Actions工作流（`.github/workflows/ci.yml`）：
- 触发：push到main分支或PR
- 步骤：安装依赖 → lint → typecheck → test
- 运行环境：ubuntu-latest + Bun

## 发布流程

见`.github/workflows/release.yml`（具体内容未读取，但存在该文件）
