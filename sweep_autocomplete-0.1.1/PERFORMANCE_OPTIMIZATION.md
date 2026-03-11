# Ollama 性能优化指南

艹，2.6秒太慢了！让老王我教你怎么提速！

## 方案1: Ollama 模型参数优化（推荐）

### 创建优化的模型
```bash
# 使用优化的 Modelfile 创建新模型
cd sweep_autocomplete-0.1.1
ollama create sweep-next-edit-fast -f Modelfile.optimized

# 设置环境变量使用优化模型
export OLLAMA_MODEL_NAME="sweep-next-edit-fast"
```

### 或者直接在 ollama 运行时设置参数
```bash
# 启动 ollama 时设置环境变量
OLLAMA_NUM_PARALLEL=4 OLLAMA_MAX_LOADED_MODELS=1 ollama serve
```

## 方案2: 代码层面优化

### 2.1 启用流式响应（最有效）
流式响应可以让用户更快看到结果，虽然总时间不变，但体验更好。

### 2.2 减少生成的 token 数量
代码补全通常不需要生成太多内容，可以减少 `max_tokens`。

### 2.3 调整 temperature
降低 temperature 可以加快生成速度（减少采样计算）。

## 方案3: 硬件优化

### GPU 加速
```bash
# 检查 GPU 是否被使用
ollama ps

# 如果有 NVIDIA GPU，确保安装了 CUDA
# ollama 会自动使用 GPU
```

### CPU 优化
```bash
# 设置 CPU 线程数（根据你的 CPU 核心数）
export OLLAMA_NUM_THREAD=8
```

## 方案4: 使用更小的模型

当前模型是 1.5B，可以考虑：
- 使用量化更激进的版本（Q4_0 比 Q8_0 快）
- 使用更小的模型（如果有 0.5B 版本）

## 方案5: Ollama 服务配置

编辑 ollama 配置（如果使用 systemd）：
```bash
# /etc/systemd/system/ollama.service
[Service]
Environment="OLLAMA_NUM_PARALLEL=4"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_FLASH_ATTENTION=1"
```

## 快速测试性能

```bash
# 测试当前性能
time curl http://localhost:11434/api/generate -d '{
  "model": "sweep-next-edit-1.5b:latest",
  "prompt": "def hello():\n    print(",
  "stream": false,
  "options": {
    "num_predict": 30,
    "temperature": 0.2
  }
}'
```

## 预期效果

- **原始**: 2.6秒
- **优化后**: 0.5-1.5秒（取决于硬件）

## 最简单的优化（立即生效）

```bash
# 1. 重启 ollama 服务，启用并行处理
export OLLAMA_NUM_PARALLEL=4
ollama serve

# 2. 使用优化的模型配置
ollama create sweep-next-edit-fast -f Modelfile.optimized

# 3. 更新环境变量
export OLLAMA_MODEL_NAME="sweep-next-edit-fast"

# 4. 重启你的服务
sweep-autocomplete
```

艹，先试试这些，看看能快多少！
