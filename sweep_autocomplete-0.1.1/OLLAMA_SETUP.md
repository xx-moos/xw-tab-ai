# Ollama 集成配置说明

艹，这个文档告诉你怎么用 ollama 替换掉原来的 llama-cpp-python！

## 前置条件

1. **Ollama 服务必须运行**
   ```bash
   # 确保 ollama 服务在运行
   curl http://localhost:11434/api/tags
   ```

2. **模型必须已经加载到 ollama**
   ```bash
   # 检查模型列表
   ollama list

   # 应该能看到 sweep-next-edit-1.5b 或类似的模型
   ```

## 环境变量配置

可以通过环境变量自定义配置：

```bash
# Ollama 服务地址（默认: http://localhost:11434）
export OLLAMA_BASE_URL="http://localhost:11434"

# 模型名称（默认: sweep-next-edit-1.5b）
export OLLAMA_MODEL_NAME="sweep-next-edit-1.5b"
```

## 安装和运行

```bash
cd sweep_autocomplete-0.1.1

# 安装依赖（已经移除了 llama-cpp-python 和 huggingface-hub）
pip install -e .

# 启动服务
sweep-autocomplete
# 或者
python -m sweep_autocomplete.cli
```

## 测试 API

```bash
# 测试补全接口
curl -X POST http://localhost:8081/backend/next_edit_autocomplete \
  -H "Content-Type: application/json" \
  -d '{
   "file_path": "test.py",
   "file_contents": "def hello():\n    print(\"",
   "cursor_position": 30,
   "recent_changes": "",
   "file_chunks": [],
   "retrieval_chunks": [],
   "recent_user_actions": []
  }'
```

## 主要改动

1. **llm_local.py**:
   - 移除了 llama-cpp-python 依赖
   - 改用 requests 调用 ollama 的 `/api/generate` 接口
   - 保持了原有的函数签名和返回格式

2. **pyproject.toml**:
   - 移除 `llama-cpp-python>=0.2.0`
   - 移除 `huggingface-hub>=0.20.0`
   - 描述改为 "powered by ollama"

3. **config.py**:
   - 新增 `OLLAMA_BASE_URL` 配置
   - 新增 `OLLAMA_MODEL_NAME` 配置

## 故障排查

### 1. 连接失败
```
艹！连接 ollama 服务失败: ...
```
**解决**: 确保 ollama 服务在运行，检查端口是否正确

### 2. 模型不存在
```
艹！模型 sweep-next-edit-1.5b 不在 ollama 中
```
**解决**:
- 检查模型名称是否正确：`ollama list`
- 如果模型名称不同，设置环境变量：`export OLLAMA_MODEL_NAME="你的模型名"`

### 3. API 调用失败
```
艹！调用 ollama API 失败: ...
```
**解决**:
- 检查 ollama 服务日志
- 确认模型已经加载
- 检查网络连接

## 性能对比

- **原 llama-cpp-python**: 需要下载模型，占用大量内存，启动慢
- **现 ollama**: 不需要下载，共享 ollama 服务，启动快，内存占用小

艹，就这么简单！
